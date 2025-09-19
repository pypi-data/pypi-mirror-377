#!/usr/bin/env python3

from __future__ import annotations

import logging
import math
import os
import pickle
import random
import re
from pathlib import Path

# --- Robust Matplotlib backend selection BEFORE importing pyplot ---
os.environ.pop("MPLBACKEND", None)

import matplotlib

SELECTED_BACKEND = None
for candidate in ("QtAgg", "TkAgg", "Agg"):
    try:
        matplotlib.use(candidate, force=True)
        SELECTED_BACKEND = candidate
        break
    except Exception:
        continue

import matplotlib.pyplot as plt  # noqa: E402
import networkx as nx  # noqa: E402

# --------------------- Logging --------------------- #
logging.basicConfig(level=logging.INFO, format="%(message)s")

# --------------------- Figure style --------------------- #
FIG_W_IN = 522.0 / 72.0  # 7.25 in
FIG_H_IN = 227.10092 / 72.0  # ~3.15418 in

plt.rcParams.update(
    {
        "font.family": "Times New Roman",
        "font.size": 8,
    }
)

# --------------------- Number formatting helpers --------------------- #
_NUM_RE = re.compile(r"-?\d+\.?\d*")


def _fmt_at_most_one_decimal(num: float) -> str:
    r = round(num, 1)
    return str(int(r)) if r.is_integer() else f"{r:.1f}"


def _format_numbers_in_text(value):
    try:
        n = float(value)
        return _fmt_at_most_one_decimal(n)
    except Exception:
        pass
    s = str(value)
    return _NUM_RE.sub(lambda m: _fmt_at_most_one_decimal(float(m.group())), s)


def _shorten_label(raw) -> str:
    """
    Shortens raw node IDs for nicer plotting.
    Keeps base name, then physical quantities with values, adding proper units.
    """
    s = str(raw)

    # split into base and attributes
    parts = re.split(r"[;]", s)
    base = re.split(r"[._]", parts[0])[0]  # before first _ . ;

    attrs_out = []
    for part in parts[1:]:
        p = part.strip()
        if not p:
            continue
        if ":" not in p:
            continue
        key, val = [x.strip() for x in p.split(":", 1)]
        try:
            num = float(val)
        except Exception:
            num = None

        if num is not None:
            # Energy quantities
            if any(k in key for k in ("E_th", "E_el")):
                attrs_out.append(f"{key}: {_fmt_at_most_one_decimal(num)} kWh")
            # Power quantities
            elif any(k in key for k in ("P_th", "P_el", "power_el")):
                attrs_out.append(f"{key}: {_fmt_at_most_one_decimal(num)} kW")
            else:
                attrs_out.append(f"{key}: {_fmt_at_most_one_decimal(num)}")
        else:
            # Keep non-numeric attributes (e.g. COP: 2.3 stays)
            attrs_out.append(f"{key}: {val}")

    if attrs_out:
        return base + "; " + "; ".join(attrs_out)
    return base

    # --- Default rule: keep text before first '.', '_' or ';' ---
    return re.split(r"[._;]", s, maxsplit=1)[0]


# --------------------- Edge label selector --------------------- #
def _auto_edge_label(edge_data: dict, preferred_attr: str | None = None):
    if not edge_data:
        return None
    if preferred_attr and preferred_attr in edge_data:
        return _format_numbers_in_text(edge_data[preferred_attr])
    for key in ("label", "weight", "value"):
        if key in edge_data:
            return _format_numbers_in_text(edge_data[key])
    return None


# --------------------- Geometry helpers for labels --------------------- #
def _centroid(points):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return (sum(xs) / len(xs), sum(ys) / len(ys)) if points else (0.0, 0.0)


def _unit(vx, vy, eps=1e-9):
    n = (vx * vx + vy * vy) ** 0.5
    return (vx / (n + eps), vy / (n + eps))


# --------------------- Initial/repelled node label placement --------------------- #
def _initial_label_positions(pos: dict, radius_frac: float = 0.08) -> dict:
    xs = [p[0] for p in pos.values()]
    ys = [p[1] for p in pos.values()]
    (minx, maxx), (miny, maxy) = (min(xs), max(xs)), (min(ys), max(ys))
    rx = (maxx - minx) or 1.0
    ry = (maxy - miny) or 1.0
    cx, cy = _centroid(list(pos.values()))
    out = {}
    for n, (x, y) in pos.items():
        ux, uy = _unit(x - cx, y - cy)
        if abs(ux) < 1e-6 and abs(uy) < 1e-6:
            ux, uy = _unit(0.3, 0.7)
        out[n] = (x + ux * rx * radius_frac, y + uy * ry * radius_frac)
    return out


def _texts_bboxes(ax, texts):
    fig = ax.figure
    # Ensure the renderer exists
    fig.canvas.draw()
    out = {}
    renderer = fig.canvas.get_renderer()
    for t in texts:
        bb_disp = t.get_window_extent(renderer=renderer).expanded(1.05, 1.2)
        out[t] = bb_disp.transformed(ax.transData.inverted())
    return out


def _bbox_intersection(bb1, bb2):
    return not (bb1.x1 < bb2.x0 or bb2.x1 < bb1.x0 or bb1.y1 < bb2.y0 or bb2.y1 < bb1.y0)


def _repel_node_labels(
    ax,
    node_pos,
    labels,
    iters: int | None = None,
    repel_strength: float = 0.012,
    spring_strength: float = 0.0025,
    max_step: float = 0.07,
    draw_every: int = 8,
):
    n = max(len(labels), 1)
    if iters is None:
        iters = min(200, 10 * int(math.sqrt(n)))  # scale with graph size

    label_pos = _initial_label_positions(node_pos, radius_frac=0.095)
    artists = []
    for k, text in labels.items():
        x, y = label_pos[k]
        t = ax.text(
            x,
            y,
            text,
            fontsize=8,
            ha="center",
            va="center",
            color="black",
            clip_on=False,
            bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.85, "pad": 0.22},
            zorder=5,
        )
        artists.append(t)

    keys = list(labels.keys())
    fig = ax.figure
    fig.canvas.draw()  # initial draw
    renderer = fig.canvas.get_renderer()

    def bboxes():
        # no draw here; rely on periodic draws
        return {
            t: t.get_window_extent(renderer=renderer).expanded(1.05, 1.2).transformed(ax.transData.inverted())
            for t in artists
        }

    for it in range(iters):
        if it % draw_every == 0:
            fig.canvas.draw()
            renderer = fig.canvas.get_renderer()
        bbs = bboxes()

        moved_any = False
        # pairwise repulsion
        for i in range(len(artists)):
            ti = artists[i]
            bi = bbs[ti]
            xi, yi = ti.get_position()
            for j in range(i + 1, len(artists)):
                tj = artists[j]
                bj = bbs[tj]
                if _bbox_intersection(bi, bj):
                    xj, yj = tj.get_position()
                    ux, uy = _unit(xi - xj, yi - yj)
                    dx, dy = repel_strength * ux, repel_strength * uy
                    mag = (dx * dx + dy * dy) ** 0.5
                    if mag > max_step:
                        dx *= max_step / (mag + 1e-12)
                        dy *= max_step / (mag + 1e-12)
                    ti.set_position((xi + dx, yi + dy))
                    tj.set_position((xj - dx, yj - dy))
                    moved_any = True

        # weak springs
        for k, t in zip(keys, artists, strict=False):
            x, y = t.get_position()
            nx_, ny_ = node_pos[k]
            t.set_position((x + (nx_ - x) * spring_strength, y + (ny_ - y) * spring_strength))
            moved_any = True

        if not moved_any:
            break

    # leader lines…
    for k, t in zip(keys, artists, strict=False):
        x, y = t.get_position()
        nx_, ny_ = node_pos[k]
        ax.annotate(
            "",
            xy=(x, y),
            xytext=(nx_, ny_),
            arrowprops={"arrowstyle": "-", "lw": 0.5, "color": "black", "shrinkA": 0, "shrinkB": 0},
            zorder=4,
        )
    return dict(zip(keys, artists, strict=False))


# --------------------- Node layout helpers (better distribution) --------------------- #
def _auto_layout(g: nx.Graph, layout: str = "auto") -> dict:  # noqa: PLR0911
    """
    Choose a good layout automatically; respects explicit choices:
      - "planar" -> planar (fallback KK -> spring)
      - "kk"     -> Kamada-Kawai
      - "spring" -> Fruchterman-Reingold with tuned (larger) k
      - "auto"   -> planar -> KK -> spring
    """
    if layout == "planar":
        try:
            return nx.planar_layout(g)
        except nx.NetworkXException:
            try:
                return nx.kamada_kawai_layout(g)
            except Exception:
                n = max(g.number_of_nodes(), 1)
                k = 1.7 / math.sqrt(n)  # looser
                return nx.spring_layout(g, seed=42, k=k, iterations=400)

    if layout == "kk":
        return nx.kamada_kawai_layout(g)

    if layout == "spring":
        n = max(g.number_of_nodes(), 1)
        k = 1.7 / math.sqrt(n)
        return nx.spring_layout(g, seed=42, k=k, iterations=400)

    # "auto"
    try:
        return nx.planar_layout(g)
    except nx.NetworkXException:
        try:
            return nx.kamada_kawai_layout(g)
        except Exception:
            n = max(g.number_of_nodes(), 1)
            k = 1.7 / math.sqrt(n)
            return nx.spring_layout(g, seed=42, k=k, iterations=400)


def _normalize_and_pad(pos: dict, pad: float = 0.04) -> dict:
    """
    Linearly map positions to [0,1] x [0,1], then add symmetric padding.
    """
    xs = [p[0] for p in pos.values()]
    ys = [p[1] for p in pos.values()]
    minx, maxx = (min(xs), max(xs))
    miny, maxy = (min(ys), max(ys))
    rx = (maxx - minx) or 1.0
    ry = (maxy - miny) or 1.0

    out = {}
    for k, (x, y) in pos.items():
        nx_ = (x - minx) / rx
        ny_ = (y - miny) / ry
        out[k] = (pad + nx_ * (1 - 2 * pad), pad + ny_ * (1 - 2 * pad))
    return out


def _min_pair_distance(p: dict) -> float:
    keys = list(p.keys())
    m = float("inf")
    for i in range(len(keys)):
        xi, yi = p[keys[i]]
        for j in range(i + 1, len(keys)):
            xj, yj = p[keys[j]]
            d = math.hypot(xi - xj, yi - yj)
            m = min(m, d)
    return 0.0 if m == float("inf") else m


def _expand_about_centroid(p: dict, factor: float = 1.04) -> dict:
    cx, cy = _centroid(list(p.values()))
    out = {}
    for k, (x, y) in p.items():
        out[k] = (cx + (x - cx) * factor, cy + (y - cy) * factor)
    return _normalize_and_pad(out, pad=0.04)


def _deoverlap_positions(
    pos: dict,
    *,
    passes: tuple[tuple[float, float, float, int], ...] = (
        (0.14, 0.010, 0.045, 380),  # coarse: big push
        (0.11, 0.007, 0.035, 300),  # refine
        (0.09, 0.005, 0.030, 240),  # polish
    ),
    jitter: float = 1e-4,
) -> dict:
    """
    Multi-pass de-overlap in normalized space (0..1). Treat nodes as disks
    of increasing fidelity; if still tight, apply global expansion and repeat.
    """
    p = _normalize_and_pad(pos, pad=0.04)
    keys = list(p.keys())

    for radius_frac, k_rep, max_step, iterations in passes:
        for _ in range(iterations):
            moved = False
            for i in range(len(keys)):
                xi, yi = p[keys[i]]
                fx, fy = 0.0, 0.0
                for j in range(len(keys)):
                    if i == j:
                        continue
                    xj, yj = p[keys[j]]
                    dx, dy = xi - xj, yi - yj
                    dist2 = dx * dx + dy * dy + 1e-12
                    dist = math.sqrt(dist2)

                    if dist < radius_frac:
                        ux, uy = dx / dist, dy / dist
                        overlap = (radius_frac - dist) / max(radius_frac, 1e-12)
                        f = k_rep * (1.0 + 3.0 * overlap) / dist2
                        fx += ux * f
                        fy += uy * f

                if fx or fy:
                    step = math.sqrt(fx * fx + fy * fy)
                    if step > max_step:
                        fx *= max_step / (step + 1e-12)
                        fy *= max_step / (step + 1e-12)

                    nx_, ny_ = xi + fx + (random.uniform(-1, 1) * jitter), yi + fy + (random.uniform(-1, 1) * jitter)
                    nx_ = min(1.0, max(0.0, nx_))
                    ny_ = min(1.0, max(0.0, ny_))
                    if abs(nx_ - xi) > 1e-9 or abs(ny_ - yi) > 1e-9:
                        p[keys[i]] = (nx_, ny_)
                        moved = True

            if not moved:
                break

        if _min_pair_distance(p) < 0.6 * radius_frac:
            p = _expand_about_centroid(p, factor=1.06)

    return p


# --------------------- Main plotter --------------------- #
def plot_topology_matplotlib(  # noqa: PLR0912, PLR0915
    g: nx.Graph,
    *,
    layout: str = "auto",  # "planar" | "kk" | "spring" | "auto"
    node_size: int = 300,
    edge_width: float = 1.0,
    highlight_roots: bool = True,  # kept for signature compatibility; not used here
    edge_label_attr=None,
    draw_edge_labels: bool = True,
    edge_label_fontsize: int = 7,
    legend: bool = True,
    deoverlap: bool = True,  # run node de-overlap pass
):
    # --- layout ---
    pos_raw = _auto_layout(g, layout=layout)
    pos = _normalize_and_pad(pos_raw, pad=0.06)  # start with generous padding
    if deoverlap:
        pos = _deoverlap_positions(pos)  # multi-pass, strong

    fig = plt.figure(figsize=(FIG_W_IN, FIG_H_IN), constrained_layout=True)
    ax = fig.add_subplot(1, 1, 1)

    # ---------------- draw edges (STRAIGHT) ---------------- #
    nx.draw_networkx_edges(g, pos, ax=ax, width=edge_width, edge_color="black")

    # ---------------- classify nodes ---------------- #
    networks, producers, consumers = [], [], []
    for n, d in g.nodes(data=True):
        name = str(d.get("id", n))
        if "util" in name:
            producers.append(n)
        elif "Demand" in name:
            consumers.append(n)
        else:
            networks.append(n)

    # ---------------- draw nodes (white + greys) ---------------- #
    grey_network = "#FFFFFF"  # white fill for networks
    grey_producer = "#CCCCCC"  # lighter grey for producers
    grey_consumer = "#888888"  # dark grey for consumers

    if networks:
        nx.draw_networkx_nodes(
            g,
            pos,
            ax=ax,
            nodelist=networks,
            node_size=node_size,
            node_color=grey_network,
            edgecolors="black",
            linewidths=0.8,
        )
    if producers:
        nx.draw_networkx_nodes(
            g,
            pos,
            ax=ax,
            nodelist=producers,
            node_size=node_size,
            node_color=grey_producer,
            edgecolors="black",
            linewidths=0.8,
        )
    if consumers:
        nx.draw_networkx_nodes(
            g,
            pos,
            ax=ax,
            nodelist=consumers,
            node_size=node_size,
            node_color=grey_consumer,
            edgecolors="black",
            linewidths=0.8,
        )

    # ---------------- node labels (repelled with leader lines) ---------------- #
    node_labels_text = {n: _shorten_label(d.get("id", n)) for n, d in g.nodes(data=True)}
    node_texts = _repel_node_labels(ax, pos, node_labels_text)

    # ---------------- optional edge labels ---------------- #
    edge_texts = {}
    if draw_edge_labels:
        edge_labels = {}
        for u, v, edata in g.edges(data=True):
            lab = _auto_edge_label(edata, preferred_attr=edge_label_attr)
            if lab is not None:
                edge_labels[(u, v)] = lab
        if edge_labels:
            edge_texts = nx.draw_networkx_edge_labels(
                g,
                pos,
                edge_labels=edge_labels,
                ax=ax,
                font_size=edge_label_fontsize,
                font_color="black",
                rotate=False,
                bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.85, "pad": 0.18},
                clip_on=False,
            )

    # ---------------- legend (compact, publication-friendly) ---------------- #
    if legend:
        import matplotlib.patches as mpatches

        handles = []
        if networks:
            handles.append(mpatches.Patch(facecolor=grey_network, edgecolor="black", label="Network"))
        if producers:
            handles.append(mpatches.Patch(facecolor=grey_producer, edgecolor="black", label="Producer"))
        if consumers:
            handles.append(mpatches.Patch(facecolor=grey_consumer, edgecolor="black", label="Consumer"))
        if handles:
            ax.legend(
                handles=handles,
                loc="upper right",
                frameon=False,
                fontsize=8,
                handlelength=1.2,
                handleheight=1.0,
                borderpad=0.2,
                labelspacing=0.4,
            )

    # ---------------- clean axes ---------------- #
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_frame_on(False)

    # ---------------- tighten axes to include label bboxes ---------------- #
    fig.canvas.draw()
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    for t in list(node_texts.values()) + list(edge_texts.values()):
        if t is None:
            continue
        bb_disp = t.get_window_extent(renderer=fig.canvas.get_renderer())
        bb = bb_disp.transformed(ax.transData.inverted())
        x0 = min(x0, bb.x0)
        x1 = max(x1, bb.x1)
        y0 = min(y0, bb.y0)
        y1 = max(y1, bb.y1)
    xr, yr = (x1 - x0), (y1 - y0)
    ax.set_xlim(x0 - 0.01 * xr, x1 + 0.01 * xr)
    ax.set_ylim(y0 - 0.01 * yr, y1 + 0.01 * yr)

    return fig


# --------------------- Bottom: interactive .gpickle chooser --------------------- #
def _natural_key(s: str):
    """Sort helper: 'net_2.gpickle' < 'net_10.gpickle'."""
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]


if __name__ == "__main__":
    # Base directory containing .gpickle graphs
    base_dir_candidates = [
        Path(__file__).parent / "eta_mistral" / "backend" / "results" / "topology_description" / "eta_production_week",
        Path(__file__).parent.parent
        / "eta_mistral"
        / "backend"
        / "results"
        / "topology_description"
        / "eta_production_week",
    ]
    base_dir = next((p for p in base_dir_candidates if p.exists()), None)
    if base_dir is None:
        raise FileNotFoundError("Could not find 'eta_production_week' directory near this script.")

    # Recursively find all .gpickle files
    files: list[Path] = sorted(
        (p for p in base_dir.rglob("*.gpickle")),
        key=lambda p: _natural_key(str(p.relative_to(base_dir))),
    )

    if not files:
        raise FileNotFoundError(f"No .gpickle files found under {base_dir}")

    # Numbered list
    logging.info("\nFound .gpickle files:")
    for i, p in enumerate(files, start=1):
        logging.info("[%d] %s", i, p.relative_to(base_dir))
    logging.info("\nEnter the number of the file to load (or 'q' to quit): ")

    # Read user choice
    choice = input().strip()
    if choice.lower() in ("q", "quit", "exit"):
        logging.info("Aborted by user.")
        raise SystemExit(0)

    if not choice.isdigit():
        raise ValueError(f"Invalid selection: {choice!r}. Please enter a number from 1 to {len(files)}.")

    idx = int(choice)
    if not (1 <= idx <= len(files)):
        raise IndexError(f"Selection {idx} out of range. Valid: 1..{len(files)}")

    gpickle_path = files[idx - 1]
    logging.info("\nLoading: %s", gpickle_path)

    # Load graph
    with gpickle_path.open("rb") as f:
        g = pickle.load(f)

    # Plot
    fig = plot_topology_matplotlib(g, layout="auto", deoverlap=True)

    # Save PDF next to this script with the chosen stem in the filename
    out_pdf = Path(__file__).with_name(f"topology_{gpickle_path.stem}.pdf")
    fig.savefig(out_pdf, dpi=300)
    logging.info("Saved figure to: %s", out_pdf.resolve())

    if SELECTED_BACKEND in ("QtAgg", "TkAgg"):
        plt.show()
    else:
        plt.close(fig)
