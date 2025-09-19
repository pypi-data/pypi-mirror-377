#!/usr/bin/env python3
from __future__ import annotations

import logging
import re
import sys
from pathlib import Path

import matplotlib

matplotlib.use("TkAgg")  # interactive backend for plt.show()

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import AutoMinorLocator

# --------------------- Logging --------------------- #
logging.basicConfig(level=logging.INFO, format="%(message)s")
# Suppress verbose glyph subsetting logs when saving PDFs
logging.getLogger("fontTools.subset").setLevel(logging.WARNING)
logging.getLogger("matplotlib.backends.backend_pdf").setLevel(logging.WARNING)

# --------------------- Figure style --------------------- #
FIG_W_IN = 522.0 / 72.0  # ~7.25 in
FIG_H_IN = 227.1 / 72.0  # ~3.15 in

plt.rcParams.update(
    {
        "font.family": "Times New Roman",
        "font.size": 10,  # everything size 10: ticks, labels, legend
        "axes.titlesize": 10,
        "axes.labelsize": 10,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 10,
        "axes.linewidth": 0.8,
        "xtick.major.width": 0.8,
        "ytick.major.width": 0.8,
        "xtick.minor.width": 0.6,
        "ytick.minor.width": 0.6,
        "savefig.dpi": 300,
        "pdf.fonttype": 42,  # embed as TrueType (good for editing)
        "ps.fonttype": 42,
    }
)

_NUM = re.compile(r"-?\d+(?:[.,]\d+)?")


def _to_num(arr_like) -> pd.Series:
    """Convert array-like (including numeric strings with commas) to float; keep NaNs."""
    if arr_like is None:
        return pd.Series(dtype=float)
    s = pd.Series(arr_like)

    def _one(x):
        if pd.isna(x):
            return float("nan")
        if isinstance(x, int | float):
            return float(x)
        m = _NUM.search(str(x))
        return float(m.group(0).replace(",", ".")) if m else float("nan")

    return s.map(_one).astype(float)


def _has_cols(df: pd.DataFrame | None, *cols: str) -> bool:
    return isinstance(df, pd.DataFrame) and all(c in df.columns for c in cols)


def _natural_key(s: str):
    """Sort helper: 'file_2.xlsx' < 'file_10.xlsx'."""
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]


def _pick_from_list(items: list[str], header: str) -> int:
    logging.info("\n%s\n%s", header, "-" * len(header))
    for i, name in enumerate(items, 1):
        logging.info("[%2d] %s", i, name)
    choice = input("\nEnter the number to select (or 'q' to quit): ").strip()
    if choice.lower() in {"q", "quit", "exit"}:
        logging.info("Aborted by user.")
        sys.exit(0)
    if not choice.isdigit():
        raise ValueError(f"Invalid selection: {choice!r}")
    idx = int(choice)
    if not (1 <= idx <= len(items)):
        raise IndexError(f"Selection {idx} out of range")
    return idx - 1


def _detect_networks(df: pd.DataFrame) -> list[str]:
    prefix = "Eth_storage_"
    nets = {c[len(prefix) :] for c in df.columns if isinstance(c, str) and c.startswith(prefix)}
    return sorted(nets, key=_natural_key)


def build_detail_figure_bw_from_single_df(
    df: pd.DataFrame,
    network: str,
    *,
    save_path: str | None = None,
):
    """Plot lines (B/W) with x-axis in minutes, legend inside, semi-transparent background."""
    y1_col = f"Eth_storage_{network}"
    y2_col = f"T_mid_buffer_storage_{network}"

    times_min = _to_num(df["times"]) * 60 if _has_cols(df, "times") else pd.Series(dtype=float)
    y1 = _to_num(df[y1_col]) if _has_cols(df, y1_col) else pd.Series(dtype=float)
    has_temp = _has_cols(df, y2_col)
    y2 = _to_num(df[y2_col]) if has_temp else pd.Series(dtype=float)

    fig = plt.figure(figsize=(FIG_W_IN, FIG_H_IN), constrained_layout=True)
    ax_energy = fig.add_subplot(1, 1, 1)
    ax_temp = ax_energy.twinx() if has_temp else None

    if len(times_min) and len(y1):
        ax_energy.plot(times_min.values, y1.values, linestyle="-", linewidth=1.2, color="black", label=y1_col)
    if has_temp and len(times_min) and len(y2):
        ax_temp.plot(times_min.values, y2.values, linestyle="--", linewidth=1.2, color="black", label=y2_col)

    ax_energy.set_xlabel("Time in min", fontname="Times New Roman", fontsize=10)
    ax_energy.set_ylabel("Energy in kWh", fontname="Times New Roman", fontsize=10)
    if has_temp:
        ax_temp.set_ylabel("Temperature in K", fontname="Times New Roman", fontsize=10)

    ax_energy.grid(True, which="major", linestyle=":", linewidth=0.7, alpha=0.6)
    ax_energy.grid(True, which="minor", linestyle=":", linewidth=0.5, alpha=0.4)
    ax_energy.xaxis.set_minor_locator(AutoMinorLocator(2))
    ax_energy.yaxis.set_minor_locator(AutoMinorLocator(2))
    if has_temp:
        ax_temp.yaxis.set_minor_locator(AutoMinorLocator(2))

    # Legend inside plot, semi-transparent background
    handles, labels = ax_energy.get_legend_handles_labels()
    if has_temp:
        h2, l2 = ax_temp.get_legend_handles_labels()
        handles.extend(h2)
        labels.extend(l2)
    if handles:
        leg = ax_energy.legend(
            handles,
            labels,
            loc="upper right",
            framealpha=0.6,
            facecolor="white",
            edgecolor="none",
            fontsize=10,
            prop={"family": "Times New Roman", "size": 10},
        )
        # ensure legend text uses TNR size 10 even with system defaults
        for txt in leg.get_texts():
            txt.set_fontfamily("Times New Roman")
            txt.set_fontsize(10)

    plt.show()
    if save_path:
        fig.savefig(save_path, bbox_inches="tight")
        logging.info("Saved figure to: %s", Path(save_path).resolve())
    return fig


if __name__ == "__main__":
    base_dir_candidates = [
        (
            Path(__file__).parent
            / "eta_mistral"
            / "backend"
            / "results"
            / "optimization_results"
            / "eta_production_week"
        ),
        (
            Path(__file__).parent.parent
            / "eta_mistral"
            / "backend"
            / "results"
            / "optimization_results"
            / "eta_production_week"
        ),
    ]

    base_dir = next((p for p in base_dir_candidates if p.exists()), None)
    if base_dir is None:
        logging.info("Could not find 'eta_production_week' directory near this script.")
        sys.exit(1)

    xlsx_files = sorted(base_dir.glob("plot_*.xlsx"), key=lambda p: _natural_key(p.name))
    if not xlsx_files:
        logging.info("No 'plot_*.xlsx' files found under %s", base_dir)
        sys.exit(1)

    names = [f.name for f in xlsx_files]
    fidx = _pick_from_list(names, "Select OPTIMIZATION Excel file")
    xlsx_path = xlsx_files[fidx]
    stem = xlsx_path.stem

    logging.info("\nLoading: %s", xlsx_path)
    data = pd.read_excel(xlsx_path, dtype=str)

    networks = _detect_networks(data)
    if not networks:
        logging.info("No networks detected.")
        net = input("Enter network suffix manually: ").strip()
        if not net:
            logging.info("No network provided. Exiting.")
            sys.exit(1)
        network = net
    else:
        nidx = _pick_from_list(networks, "Select NETWORK")
        network = networks[nidx]

    out_pdf = Path(__file__).with_name(f"detailed_{stem}__{network}.pdf")
    build_detail_figure_bw_from_single_df(data, network=network, save_path=str(out_pdf))
