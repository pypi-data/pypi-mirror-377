"""
command line interface application for the ETA MISTRAL software.
"""

__author__ = ["Michael Frank (MFr)", "Lukas Theisinger (LT)", "Fabian Borst (FBo)"]
__maintainer__ = "Michael Frank (MFr)"
__email__ = "m.frank@ptw.tu-darmstadt.de"
__project__ = "MISTRAL FKZ: 03EN4098A-E "
__subject__ = "Cluster 2: Software solution"
__version__ = "0.0.1"
__status__ = "Work in progress"

import json
import logging
import pickle
import shutil
import time
from pathlib import Path

import dash_bootstrap_components as dbc
import networkx as nx
import pandas as pd
import plotly.graph_objects as go
from dash import Dash, Input, Output, State, dcc, html
from plotly.graph_objs import Figure, Layout, Scatter
from plotly.subplots import make_subplots
from pyomo.environ import SolverFactory

from eta_mistral.backend.optimization.mistral_optimizer import MistralOptimizer
from eta_mistral.backend.simulation.simulator import Simulator

logger = logging.getLogger("cli_app")
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(message)s")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


class CommandLineApplication:
    def __init__(self):
        self.running = True
        self.goto = ""
        self.base_dir = Path(__file__).resolve().parent.parent
        self.input_dir = self.base_dir / "backend" / "input"

    def run(self):
        self.goto = "1"
        while self.running is True:
            if self.goto == "1":
                self.goto = "2"
            if self.goto == "2":
                self.user()
                self.goto = "3"
            if self.goto == "3":
                self.project()
                self.goto = "4"
            if self.goto == "4":
                self.variant()
                self.goto = input(
                    "[VARIANT] back to project selection/creation (2),"
                    "variant selection/creation (3), plotting (5) or exit app (6) "
                )
            if self.goto == "5":
                self.plotting()
                self.goto = input(
                    "[PLOTTNG] back to project selection/creation (2),variant selection/creation (3) or exit app (6) "
                )
            if self.goto == "6":
                self.running = False
            if self.goto not in ["1", "2", "3", "4", "5", "6"]:
                self.goto = input("[ERROR] please retry ")

    def user(self):
        logger.info("[USER] existing projects: ")
        for project in Path(self.input_dir).iterdir():
            logger.info(project.name)
        if input("[PROJECT] choose existing project (e) or create new project (n) ") == "n":
            self.project_title = input("[USER] enter new project title: ")
            example_path = Path.cwd() / "backend" / "input" / "example_project"
            logger.info("[USER] example csv file for input data is located at: %s", example_path)
            logger.info("[USER] comply with the following notation: ")
            logger.info("[USER] time at first column in 900-seconds-steps [s]")
            logger.info("[USER] power of heating demands (e.g. space heating)--> XYZ.heatDemand.heat_flow in [kW]")
            logger.info(
                "[USER] flow temperature of heating demands (e.g. space heating)--> XYZ.heatDemand.temp_in in [K]"
            )
            logger.info(
                "[USER] return temperature of heating demands (e.g. space heating)--> XYZ.heatDemand.temp_out in [K]"
            )
            logger.info("[USER] power of cooling demands (e.g. machine tool)--> XYZ.coolDemand.heat_flow in [kW]")
            logger.info(
                "[USER] flow temperature of cooling demands (e.g. machine tool)--> XYZ.coolDemand.temp_in in [K]"
            )
            logger.info(
                "[USER] return temperature of cooling demands (e.g. machine tool)--> XYZ.coolDemand.temp_out in [K]"
            )
            abs_input_path = input("[USER] enter absolute path to input file: ")
            (Path(self.input_dir) / self.project_title).mkdir(parents=True, exist_ok=True)
            (Path(self.base_dir) / "backend" / "results" / "optimization_results" / self.project_title).mkdir(
                parents=True, exist_ok=True
            )
            (Path(self.base_dir) / "backend" / "results" / "simulation_results" / self.project_title).mkdir(
                parents=True, exist_ok=True
            )
            (Path(self.base_dir) / "backend" / "results" / "topology_description" / self.project_title).mkdir(
                parents=True, exist_ok=True
            )
            target_path = Path(self.base_dir) / "backend" / "input" / self.project_title / f"{self.project_title}.csv"
            shutil.copyfile(abs_input_path, target_path)
        else:
            self.project_title = input("[PROJECT] enter title of existing project (without file extension): ")

    def _load_existing_variants(self):
        csv_path = Path(self.input_dir) / self.project_title / f"{self.project_title}.csv"
        self.analyze_project_data(csv_path)

        logger.info("[PROJECT] existing variants: ")
        for variant_path in (Path(self.input_dir) / self.project_title).iterdir():
            if variant_path.suffix == ".json":
                logger.info(variant_path.name)

    def _define_demands(self):
        logger.info("[PROJECT] the following heating demands belong to this project: ")
        for _hd in self.heatDemandTemperatures:
            pass
        for _cd in self.coolDemandTemperatures:
            pass

    def _define_nodes(self):
        self.nodes = []
        while True:
            self.nodes.append(
                input(
                    "[PROJECT] enter node-name (e.g. production_hall1 as string) for spatial distribution of demands: "
                )
            )
            if input("[PROJECT] further nodes? (y/n) ") == "n":
                break

    def _allocate_demands_to_nodes(self):
        self.source_sink_node_allocation = {}
        logger.info("[PROJECT] define at which node each demand is located - use valid node-names only")
        logger.info("[PROJECT] valid node-names: %s", self.nodes)
        for hd in self.heatDemandTemperatures:
            self.source_sink_node_allocation[hd] = input("[PROJECT] enter node at which " + hd + " is located: ")
        for cd in self.coolDemandTemperatures:
            self.source_sink_node_allocation[cd] = input("[PROJECT] enter node at which " + cd + " is located: ")

    def _define_crosslinking_nodes(self):
        logger.info("[PROJECT] define wheter crosslinking-technologies (e.g. heatpumps) can be placed at each nodes")
        self.is_crosslink_node = {}
        for node in self.nodes:
            if input("[PROJECT] is " + node + " a crosslinking-node? (y/n) ") == "y":
                self.is_crosslink_node[node] = 1
            else:
                self.is_crosslink_node[node] = 0

    def _define_networks(self):
        logger.info("[PROJECT] define thermal networks which should be considered (existing and new)")
        self.networks = []
        while True:
            self.networks.append(input("[PROJECT] enter name of thermal network (e.g. heating_network): "))
            if input("[PROJECT] further thermal networks? (y/n) ") == "n":
                break

    def _define_network_characteristics(self):
        logger.info("[PROJECT] define characteristics of the thermal networks")
        self.T_heat = {}
        self.T_cool = {}
        self.E_th_storage_cap_max = {}
        self.network_node_allocation = {}
        for network in self.networks:
            self.T_heat[network] = float(
                input("[PROJECT] enter temperature level for heating purposes of " + network + " in [K]: ")
            )
            self.T_cool[network] = float(
                input("[PROJECT] enter temperature level for cooling purposes of " + network + " in [K]: ")
            )
            self.E_th_storage_cap_max[network] = float(
                input("[PROJECT] enter maximum allowed thermal storage capacity of " + network + " in [kWh]: ")
            )

            local_dict = {}
            for node in self.nodes:
                if input("[PROJECT] is " + network + " located at node " + node + "? (y/n) ") == "y":
                    local_dict[node] = 1
                else:
                    local_dict[node] = 0
            self.network_node_allocation[network] = local_dict

        logger.info("[PROJECT] define converters of the thermal networks")
        logger.info("[PROJECT] generated thermal power P_th = eta_th * (P_gas + P_el)")
        logger.info("[PROJECT] generated electric power P_el = eta_el * (P_gas + P_el)")

        logger.info("[PROJECT] heating converters (e.g. gas boiler)")

    def _define_converters(self):
        self.hot_utilities = {}
        local_dict = {}
        for network in self.networks:
            local_dict["P_gas_nom"] = float(
                input(
                    "[PROJECT] enter nominal gas power of heating converter in thermal network "
                    + network
                    + " in [kW]: "
                )
            )
            local_dict["P_el_nom"] = float(
                input(
                    "[PROJECT] enter nominal electric power of heating converter in thermal network "
                    + network
                    + " in [kW]: "
                )
            )
            local_dict["eta_th_nom"] = float(
                input(
                    "[PROJECT] enter nominal thermal efficiency of heating converter in thermal network "
                    + network
                    + " in [-]: "
                )
            )
            local_dict["eta_el_nom"] = float(
                input(
                    "[PROJECT] enter nominal electric efficiency of heating converter in thermal network "
                    + network
                    + " in [-]: "
                )
            )
            self.hot_utilities[network] = local_dict
            local_dict = {}

        logger.info("[PROJECT] cooling converters (e.g. compression chiller)")
        self.cold_utilities = {}
        local_dict = {}
        for network in self.networks:
            local_dict["P_gas_nom"] = float(
                input(
                    "[PROJECT] enter nominal gas power of cooling converter in thermal network "
                    + network
                    + " in [kW]: "
                )
            )
            local_dict["P_el_nom"] = float(
                input(
                    "[PROJECT] enter nominal electric power of cooling converter in thermal network "
                    + network
                    + " in [kW]: "
                )
            )
            local_dict["eta_th_nom"] = float(
                input(
                    "[PROJECT] enter nominal thermal efficiency of cooling converter in thermal network "
                    + network
                    + " in [-]: "
                )
            )
            local_dict["eta_el_nom"] = float(
                input(
                    "[PROJECT] enter nominal electric efficiency of cooling converter in thermal network "
                    + network
                    + " in [-]: "
                )
            )
            self.cold_utilities[network] = local_dict
            local_dict = {}

    def _define_emission_factors(self):
        logger.info("[PROJECT] define external factors")
        self.spec_co2_el = float(input("[PROJECT] enter specific carbon footprint of the electricity mix in [g/kWh]:"))
        self.spec_co2_gas = float(input("[PROJECT] enter specific carbon footprint of natural gas in [g/kWh]:"))

    def _create_new_variant(self):
        self.variant_title = input("[PROJECT] enter new variant title: ")

        self._define_demands()
        self._define_nodes()
        self._allocate_demands_to_nodes()
        self._define_crosslinking_nodes()
        self._define_networks()
        self._define_network_characteristics()
        self._define_converters()
        self._define_emission_factors()

        self.config = {}
        self.config["nodes"] = self.nodes
        self.config["networks"] = self.networks
        self.config["T_heat"] = self.T_heat
        self.config["T_cool"] = self.T_cool
        self.config["E_th_storage_cap_max"] = self.E_th_storage_cap_max
        self.config["network_node_allocation"] = self.network_node_allocation
        self.config["source_sink_node_allocation"] = self.source_sink_node_allocation
        self.config["is_crosslink_node"] = self.is_crosslink_node
        self.config["hot_utilities"] = self.hot_utilities
        self.config["cold_utilities"] = self.cold_utilities
        self.config["spec_co2_el"] = self.spec_co2_el
        self.config["spec_co2_gas"] = self.spec_co2_gas

        if input("[PROJECT] show variant? (y/n) ") == "y":
            pass

        if input("[PROJECT] save variant? (y/n) ") == "y":
            outfile_path = Path(self.input_dir) / self.project_title / f"{self.variant_title}.json"
            with outfile_path.open("w", encoding="utf-8") as outfile:
                json.dump(self.config, outfile)

    def project(self):
        self._load_existing_variants()

        choice = input("[PROJECT] choose existing variant (e) or create new variant (n) ")
        if choice == "n":
            self._create_new_variant()
        else:
            self.variant_title = input("[PROJECT] enter title of existing variant (without file extension): ")

    def variant(self):
        if input("[VARIANT] start optimization process? (y/n) ") == "y":
            optimizer = MistralOptimizer(self.project_title, self.variant_title)
            logger.info("[VARIANT] optimizer instanciated")
            optimizer.load_input_data()
            logger.info("[VARIANT] data loaded")
            optimizer.input_data_to_pyomo_input()
            logger.info("[VARIANT] data transformed")
            model = optimizer.setup_optimization_model()
            logger.info("[VARIANT] model set-up")
            opt = SolverFactory("cplex")
            tee_var = input("[VARIANT] show solver dialog? (y/n) ") == "y"
            logger.info("[VARIANT] started solving")
            opt.solve(model, tee=tee_var)
            logger.info("[VARIANT] model solved")
            optimizer.save_results(model)
            logger.info("[VARIANT] results saved")
            optimizer.save_topology()
            logger.info("[VARIANT] topology saved")
            optimizer.convert_results()
            logger.info("[VARIANT] results converted")

        if input("[VARIANT] start simulation process? (y/n) ") == "y":
            simulator = Simulator(self.start_time, self.stop_time, 1, 3600)
            simulator.load_fmu(self.project_title, self.variant_title)
            simulator.simulate_model()
            simulator.shutdown_simulation()
            simulator.export_results()
            simulator.convert_results()

    def _load_project_list(self):
        return [p.name for p in Path(self.input_dir).iterdir() if p.is_dir()]

    def _create_network_selector(self, copy, project_list):
        canv_placement = "start" if copy == 1 else "end"
        return dbc.Col(
            [
                html.Div(
                    [
                        dbc.Button(
                            dbc.Spinner(
                                html.Div("Make selection", id=f"loading-output_{copy}", style={"font-size": "1.5em"})
                            ),
                            id=f"open_offcanvas_{copy}",
                            color="secondary",
                            n_clicks=0,
                        )
                    ],
                    className="d-grid gap-2",
                ),
                dbc.Offcanvas(
                    html.Div(
                        [
                            dcc.Dropdown(
                                options=project_list,
                                placeholder="Select a Project",
                                id=f"project-dropdown_{copy}",
                                style={"width": "100%", "margin": "auto"},
                            ),
                            html.Br(),
                            dcc.Dropdown(
                                options=[],
                                placeholder="Select a Variant",
                                id=f"json-dropdown_{copy}",
                                style={"width": "100%", "margin": "auto"},
                            ),
                            html.Br(),
                            dcc.Dropdown(
                                options=[],
                                placeholder="Select a Network",
                                id=f"network-dropdown_{copy}",
                                style={"width": "100%", "margin": "auto"},
                            ),
                            html.Br(),
                        ]
                    ),
                    id=f"offcanvas_{copy}",
                    title=f"Selection {copy}",
                    placement=canv_placement,
                ),
                dbc.Breadcrumb(
                    id=f"breadcrumb-network-selection_{copy}",
                    items=[
                        {"label": "selected project", "active": True},
                        {"label": "selected variant", "active": True},
                        {"label": "selected network", "active": True},
                    ],
                    style={"padding-left": "1rem"},
                ),
            ],
            width=6,
        )

    def _create_network_graph_placeholder(self, copy):
        axis = {"showline": False, "zeroline": False, "showgrid": False, "showticklabels": False}
        layout = Layout(
            title={"text": "Topology of the networks", "y": 0.9, "x": 0.5, "xanchor": "center", "yanchor": "top"},
            font={"size": 21},
            showlegend=False,
            autosize=True,
            xaxis=axis,
            yaxis=axis,
            hovermode="closest",
            annotations=[
                {
                    "showarrow": False,
                    "xref": "paper",
                    "yref": "paper",
                    "x": 0,
                    "y": -0.1,
                    "xanchor": "left",
                    "yanchor": "bottom",
                    "font": {"size": 14},
                }
            ],
        )
        fig = Figure(layout=layout)
        return dbc.Col(dbc.Card(dcc.Graph(figure=fig, id=f"network-tree-graph_{copy}"), body=True), width=6)

    def _create_chart_placeholder(self, copy):
        detail_line_plot = make_subplots(specs=[[{"secondary_y": True}]])
        detail_line_plot.update_layout(
            title={"text": "Detailed", "y": 0.9, "x": 0.5, "xanchor": "center", "yanchor": "top"}, title_font_size=21
        )
        detail_line_plot.update_xaxes(title_text="<b>time</b>", title_font={"size": 21})
        detail_line_plot.update_yaxes(title_text="<b>Energy</b> in kWh", secondary_y=False, title_font={"size": 21})
        detail_line_plot.update_yaxes(title_text="<b>Temperature</b> in K", secondary_y=True, title_font={"size": 21})
        detail_line_plot.update_layout(legend={"yanchor": "top", "y": -0.25, "xanchor": "left", "x": 0})
        detail_line_plot.update_layout(paper_bgcolor="rgba(205, 225, 255, 0)")

        sum_bar_plot = make_subplots(specs=[[{"secondary_y": True}]])
        sum_bar_plot.update_layout(
            title={"text": "Summary", "y": 0.9, "x": 0.5, "xanchor": "center", "yanchor": "top"}, title_font_size=21
        )
        sum_bar_plot.update_yaxes(title_text="<b>Power</b> in kW", secondary_y=False, title_font={"size": 21})
        sum_bar_plot.update_yaxes(
            title_text="<b>CO<sub>2</sub> emissions</b> in kg", secondary_y=True, title_font={"size": 21}
        )
        sum_bar_plot.update_layout(legend={"yanchor": "top", "y": -0.25, "xanchor": "left", "x": 0})
        sum_bar_plot.update_layout(paper_bgcolor="rgba(205, 225, 255, 0)")

        tab1_content = dbc.Card(
            dbc.CardBody([dcc.Graph(id=f"sum_bar_plot_{copy}", figure=sum_bar_plot)]), className="mt-3"
        )
        tab2_content = dbc.Card(
            dbc.CardBody([dcc.Graph(id=f"det_line_plot_{copy}", figure=detail_line_plot)]), className="mt-3"
        )

        tabs = dbc.Tabs([dbc.Tab(tab1_content, label="Summary"), dbc.Tab(tab2_content, label="Detailed")])
        return dbc.Col([tabs], width=6)

    def _define_layout(self, project_list):
        network_selection_module_1 = self._create_network_selector(1, project_list)
        network_selection_module_2 = self._create_network_selector(2, project_list)
        igraph_network_module_1 = self._create_network_graph_placeholder(1)
        igraph_network_module_2 = self._create_network_graph_placeholder(2)
        detail_summary_graph_1 = self._create_chart_placeholder(1)
        detail_summary_graph_2 = self._create_chart_placeholder(2)

        row_style = {"padding-left": "2rem", "padding-right": "2rem", "padding-top": "0rem", "padding-bottom": "1rem"}

        return html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            html.A(
                                html.Img(
                                    src="/assets/MISTRAL-Logo-color-rgb.png",
                                    style={"height": "60px", "margin-right": "20px"},
                                ),
                                href="https://www.ptw.tu-darmstadt.de/forschung_ptw/eta/aktuelle_projekte_eta/mistral/standardseite_347.de.jsp",
                                target="_blank",
                            ),
                            width="auto",
                        ),
                        dbc.Col(
                            html.H1(
                                "Web-Interface for the paired comparison of optimization and simulation results",
                                style={
                                    "textAlign": "left",
                                    "color": "#535353",
                                    "font-family": "Tahoma",
                                    "padding-top": "10px",
                                    "padding-bottom": "10px",
                                },
                            )
                        ),
                    ],
                    style={"background-color": "rgba(153,192,0,0.5)", "padding-left": "30px", "padding-right": "30px"},
                    align="center",
                ),
                html.Br(),
                dbc.Row([network_selection_module_1, network_selection_module_2], align="start", style=row_style),
                dbc.Row([igraph_network_module_1, igraph_network_module_2], style=row_style),
                dbc.Row([detail_summary_graph_1, detail_summary_graph_2], style=row_style),
                html.Br(),
                html.Div(
                    dbc.Row(
                        [
                            dbc.Col(
                                html.Div(
                                    [
                                        html.A(
                                            html.Img(
                                                src="/assets/ETA-Logo.png",
                                                style={"height": "50px", "margin-right": "20px"},
                                            ),
                                            href="https://www.ptw.tu-darmstadt.de/eta-fabrik/",
                                            target="_blank",
                                        ),
                                        html.A(
                                            html.Img(
                                                src="/assets/Discrete_Optimization-Logo.png",
                                                style={"height": "40px", "margin-right": "20px"},
                                            ),
                                            href="https://www.mathematik.tu-darmstadt.de/optimierung/forschung/discrete_optimization_1/index.de.jsp",
                                            target="_blank",
                                        ),
                                        html.A(
                                            html.Img(src="/assets/GFAI-Logo.png", style={"height": "40px"}),
                                            href="https://www.gfai.de/",
                                            target="_blank",
                                        ),
                                    ],
                                    style={"display": "flex", "align-items": "center"},
                                ),
                                width=6,
                                style={"display": "flex", "align-items": "center"},
                            ),
                            dbc.Col(
                                html.Div(
                                    [
                                        html.A(
                                            html.Img(
                                                src="/assets/BMWe-Logo.png",
                                                style={"height": "190px", "margin-right": "30px"},
                                            ),
                                            href="https://www.bmwk.de/",
                                            target="_blank",
                                        ),
                                        html.A(
                                            html.Img(src="/assets/ptj-Logo.png", style={"height": "80px"}),
                                            href="https://www.ptj.de/",
                                            target="_blank",
                                        ),
                                    ],
                                    style={"display": "flex", "justify-content": "flex-end", "align-items": "center"},
                                ),
                                width=6,
                                style={"display": "flex", "align-items": "center", "justify-content": "flex-end"},
                            ),
                        ],
                        style={"padding": "5px"},
                    ),
                    style={"background-color": "white", "border-top": "1px solid #ccc", "margin-top": "30px"},
                ),
            ]
        )

    def _initialize_dash_app(self, layout):
        app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
        app.layout = layout
        return app

    def _register_summary_callbacks(self, app):
        @app.callback(
            Output("offcanvas_1", "is_open"), Input("open_offcanvas_1", "n_clicks"), [State("offcanvas_1", "is_open")]
        )
        def toggle_offcanvas_left(n1, is_open):
            if n1:
                return not is_open
            return is_open

        @app.callback(
            Output("offcanvas_2", "is_open"), Input("open_offcanvas_2", "n_clicks"), [State("offcanvas_2", "is_open")]
        )
        def toggle_offcanvas_right(n1, is_open):
            if n1:
                return not is_open
            return is_open

        # dropdown lists
        @app.callback(Output("json-dropdown_1", "options"), Input("project-dropdown_1", "value"))
        def update_json_dropdown_left(selected_project):
            if not selected_project:
                return []
            file_path = Path(self.input_dir) / selected_project
            if not file_path.exists():
                return []
            file_list = [f.name for f in file_path.iterdir() if f.is_file()]
            return [fn for fn in file_list if fn.endswith(".json")]

        @app.callback(Output("json-dropdown_2", "options"), Input("project-dropdown_2", "value"))
        def update_json_dropdown_right(selected_project):
            if not selected_project:
                return []
            file_path = Path(self.input_dir) / selected_project
            if not file_path.exists():
                return []
            file_list = [f.name for f in file_path.iterdir() if f.is_file()]
            return [fn for fn in file_list if fn.endswith(".json")]

        @app.callback(
            Output("network-dropdown_1", "options"),
            Input("project-dropdown_1", "value"),
            Input("json-dropdown_1", "value"),
        )
        def update_network_dropdown_left(selected_project, selected_json):
            if not selected_project or not selected_json:
                return []
            json_path = Path(self.input_dir) / selected_project / selected_json
            try:
                with Path.open(json_path, encoding="utf-8") as f:
                    return json.load(f).get("networks", [])
            except Exception:
                return []

        @app.callback(
            Output("network-dropdown_2", "options"),
            Input("project-dropdown_2", "value"),
            Input("json-dropdown_2", "value"),
        )
        def update_network_dropdown_right(selected_project, selected_json):
            if not selected_project or not selected_json:
                return []
            json_path = Path(self.input_dir) / selected_project / selected_json
            try:
                with Path.open(json_path, encoding="utf-8") as f:
                    return json.load(f).get("networks", [])
            except Exception:
                return []

        # breadcrumbs
        @app.callback(
            Output("breadcrumb-network-selection_1", "items"),
            Input("project-dropdown_1", "value"),
            Input("json-dropdown_1", "value"),
            Input("network-dropdown_1", "value"),
        )
        def update_breadcrumb_network_selection_left(selected_project, selected_json, selected_network):
            proj = selected_project or "selected project"
            var = selected_json[:-5] if selected_json else "selected variant"
            net = selected_network or "selected network"
            return [{"label": proj, "active": True}, {"label": var, "active": True}, {"label": net, "active": True}]

        @app.callback(
            Output("breadcrumb-network-selection_2", "items"),
            Input("project-dropdown_2", "value"),
            Input("json-dropdown_2", "value"),
            Input("network-dropdown_2", "value"),
        )
        def update_breadcrumb_network_selection_right(selected_project, selected_json, selected_network):
            proj = selected_project or "selected project"
            var = selected_json[:-5] if selected_json else "selected variant"
            net = selected_network or "selected network"
            return [{"label": proj, "active": True}, {"label": var, "active": True}, {"label": net, "active": True}]

        @app.callback(Output("loading-output_1", "children"), Input("det_line_plot_1", "figure"))
        def update_button_state_left(figure):
            time.sleep(1)
            return "Selection"

        @app.callback(Output("loading-output_2", "children"), Input("det_line_plot_2", "figure"))
        def update_button_state_right(figure):
            time.sleep(1)
            return "Selection"

    def _register_graph_callbacks(self, app):
        @app.callback(
            Output("network-tree-graph_1", "figure"),
            [
                Input("project-dropdown_1", "value"),
                Input("json-dropdown_1", "value"),
                Input("network-dropdown_1", "value"),
            ],
        )
        def update_tree_graph_left(selected_project, selected_json, selected_network):
            if not selected_project or not selected_json or not selected_network:
                return Figure()
            filepath = (
                Path(self.base_dir)
                / "backend"
                / "results"
                / "topology_description"
                / selected_project
                / f"graph_{selected_json[:-5]}.gpickle"
            )
            if not filepath.exists():
                return Figure()

            with filepath.open("rb") as f:
                h_graph = pickle.load(f)

            labels = [h_graph.nodes[node]["id"] for node in h_graph.nodes]

            layt = nx.planar_layout(h_graph)
            xn = [layt[k][0] for k in h_graph.nodes]
            yn = [layt[k][1] for k in h_graph.nodes]

            xe, ye = [], []
            for e in h_graph.edges:
                xe += [layt[e[0]][0], layt[e[1]][0], None]
                ye += [layt[e[0]][1], layt[e[1]][1], None]

            trace1 = Scatter(x=xe, y=ye, mode="lines", line={"color": "rgb(210,210,210)", "width": 5}, hoverinfo="none")
            trace2 = Scatter(
                x=xn,
                y=yn,
                mode="markers",
                name="ntw",
                marker={
                    "symbol": "circle-dot",
                    "size": 40,
                    "color": "rgb(62,87,121)",
                    "line": {"color": "rgb(50,50,50)", "width": 1},
                },
                text=labels,
                hoverinfo="text",
            )

            axis = {"showline": False, "zeroline": False, "showgrid": False, "showticklabels": False}
            layout = Layout(
                title={"text": "Topology of the networks", "y": 0.9, "x": 0.5, "xanchor": "center", "yanchor": "top"},
                font={"size": 21},
                showlegend=False,
                autosize=True,
                xaxis=axis,
                yaxis=axis,
                hovermode="closest",
            )

            return Figure(data=[trace1, trace2], layout=layout)

        @app.callback(
            Output("network-tree-graph_2", "figure"),
            [
                Input("project-dropdown_2", "value"),
                Input("json-dropdown_2", "value"),
                Input("network-dropdown_2", "value"),
            ],
        )
        def update_tree_graph_right(selected_project, selected_json, selected_network):
            if not selected_project or not selected_json or not selected_network:
                return Figure()
            filepath = (
                Path(self.base_dir)
                / "backend"
                / "results"
                / "topology_description"
                / selected_project
                / f"graph_{selected_json[:-5]}.gpickle"
            )
            if not filepath.exists():
                return Figure()
            with filepath.open("rb") as f:
                h_graph = pickle.load(f)

            labels = [h_graph.nodes[node]["id"] for node in h_graph.nodes]
            layt = nx.planar_layout(h_graph)
            xn = [layt[k][0] for k in h_graph.nodes]
            yn = [layt[k][1] for k in h_graph.nodes]

            xe, ye = [], []
            for e in h_graph.edges:
                xe += [layt[e[0]][0], layt[e[1]][0], None]
                ye += [layt[e[0]][1], layt[e[1]][1], None]

            trace1 = Scatter(x=xe, y=ye, mode="lines", line={"color": "rgb(210,210,210)", "width": 5}, hoverinfo="none")
            trace2 = Scatter(
                x=xn,
                y=yn,
                mode="markers",
                name="ntw",
                marker={
                    "symbol": "circle-dot",
                    "size": 40,
                    "color": "rgb(62,87,121)",
                    "line": {"color": "rgb(50,50,50)", "width": 1},
                },
                text=labels,
                hoverinfo="text",
            )

            axis = {"showline": False, "zeroline": False, "showgrid": False, "showticklabels": False}
            layout = Layout(
                title={"text": "Topology of the networks", "y": 0.9, "x": 0.5, "xanchor": "center", "yanchor": "top"},
                font={"size": 21},
                showlegend=False,
                autosize=True,
                xaxis=axis,
                yaxis=axis,
                hovermode="closest",
            )

            return Figure(data=[trace1, trace2], layout=layout)

    def _register_evaluation_figure_callbacks(self, app):  # noqa: PLR0915
        """Read xlsx files from backend and feed data into the Summary/Detailed charts."""

        def to_num(series):
            """Robust numeric conversion: handles comma decimals and strips spaces; non-convertible -> NaN."""
            return pd.to_numeric(series.astype(str).str.replace(",", ".", regex=False).str.strip(), errors="coerce")

        def build_summary_figure(optm_df, sim_df):
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.update_layout(
                title={"text": "Summary", "y": 0.9, "x": 0.5, "xanchor": "center", "yanchor": "top"},
                paper_bgcolor="rgba(205, 225, 255, 0)",
                legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1},
            )
            fig.update_yaxes(title_text="<b>Power</b> in kW", secondary_y=False, title_font={"size": 21})
            fig.update_yaxes(
                title_text="<b>CO<sub>2</sub> emissions</b> in kg", secondary_y=True, title_font={"size": 21}
            )

            # Column selection
            sum_bar_pow_optm_x_labels = [c for c in getattr(optm_df, "columns", []) if c.lower().startswith("pth")]
            sum_bar_pow_sim_x_labels = [c for c in getattr(sim_df, "columns", []) if c.lower().startswith("pth")]
            sum_bar_co2_optm_x_label = [c for c in getattr(optm_df, "columns", []) if c.startswith("CO2")]
            sum_bar_co2_sim_x_label = [c for c in getattr(sim_df, "columns", []) if c.startswith("CO2")]

            try:
                if sum_bar_pow_optm_x_labels:
                    fig.add_trace(
                        go.Bar(
                            x=sum_bar_pow_optm_x_labels,
                            y=[to_num(optm_df[c]).mean() for c in sum_bar_pow_optm_x_labels],
                            name="Optimization results of thermal power",
                            hovertemplate=("Optimization<br><b>%{x}</b><br>Power in kW: %{y:.2f}<br><extra></extra>"),
                        ),
                        secondary_y=False,
                    )
                if sum_bar_pow_sim_x_labels:
                    fig.add_trace(
                        go.Bar(
                            x=sum_bar_pow_sim_x_labels,
                            y=[abs(to_num(sim_df[c]).mean() / 1000) for c in sum_bar_pow_sim_x_labels],
                            name="Simulation results of thermal power",
                            hovertemplate=("Simulation<br><b>%{x}</b><br>Power in kW: %{y:.2f}<br><extra></extra>"),
                        ),
                        secondary_y=False,
                    )
                if sum_bar_co2_optm_x_label:
                    fig.add_trace(
                        go.Bar(
                            x=sum_bar_co2_optm_x_label,
                            y=[to_num(optm_df[c]).sum() / 1000 for c in sum_bar_co2_optm_x_label],
                            name="Optimization results of CO<sub>2</sub> emissions",
                            hovertemplate=(
                                "Optimization<br><b>%{x}</b><br>Emissions in kg: %{y:.2f}<br><extra></extra>"
                            ),
                        ),
                        secondary_y=True,
                    )
                if sum_bar_co2_sim_x_label:
                    fig.add_trace(
                        go.Bar(
                            x=sum_bar_co2_sim_x_label,
                            y=[to_num(sim_df[c]).sum() / 4000 for c in sum_bar_co2_sim_x_label],
                            name="Simulation results of CO<sub>2</sub> emissions",
                            hovertemplate=("Simulation<br><b>%{x}</b><br>Emissions in kg: %{y:.2f}<br><extra></extra>"),
                        ),
                        secondary_y=True,
                    )
            except Exception as e:
                logger.info("[SUMMARY] building bars failed: %s", e)

            if len(fig.data) == 0:
                fig.add_annotation(
                    text="No summary data available for selected inputs.",
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=0.5,
                    showarrow=False,
                )
            return fig

        def build_detail_figure(optm_df, sim_df, network):
            detail_line_plot_y1_label = f"Eth_storage_{network}"
            detail_line_plot_y2_label = f"T_mid_buffer_storage_{network}"

            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.update_layout(
                title={"text": "Detailed", "y": 0.9, "x": 0.5, "xanchor": "center", "yanchor": "top"},
                paper_bgcolor="rgba(205, 225, 255, 0)",
                legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1},
            )
            fig.update_xaxes(title_text="<b>time</b> in s", title_font={"size": 21})
            fig.update_yaxes(title_text="<b>Energy</b> in kWh", secondary_y=False, title_font={"size": 21})
            fig.update_yaxes(title_text="<b>Temperature</b> in K", secondary_y=True, title_font={"size": 21})

            try:
                if isinstance(optm_df, pd.DataFrame) and "times" in getattr(optm_df, "columns", []):
                    opt_times = to_num(optm_df["times"]) * 3600
                else:
                    opt_times = pd.Series(dtype=float)

                if isinstance(sim_df, pd.DataFrame) and "times" in getattr(sim_df, "columns", []):
                    sim_times = to_num(sim_df["times"])
                else:
                    sim_times = pd.Series(dtype=float)

                if isinstance(optm_df, pd.DataFrame) and detail_line_plot_y1_label in getattr(optm_df, "columns", []):
                    fig.add_trace(
                        go.Scatter(
                            x=opt_times,
                            y=to_num(optm_df[detail_line_plot_y1_label]),
                            name=detail_line_plot_y1_label,
                            hovertemplate=(
                                f"<b>{detail_line_plot_y1_label}</b><br><br>"
                                "time in s: %{x:.2f}<br>"
                                "Energy in kWh: %{y:.2f}<br>"
                                "<extra></extra>"
                            ),
                        ),
                        secondary_y=False,
                    )
                if isinstance(sim_df, pd.DataFrame) and detail_line_plot_y2_label in getattr(sim_df, "columns", []):
                    fig.add_trace(
                        go.Scatter(
                            x=sim_times,
                            y=to_num(sim_df[detail_line_plot_y2_label]),
                            name=detail_line_plot_y2_label,
                            hovertemplate=(
                                f"<b>{detail_line_plot_y2_label}</b><br><br>"
                                "time in s: %{x:.2f}<br>"
                                "Temperature in K: %{y:.2f}<br>"
                                "<extra></extra>"
                            ),
                        ),
                        secondary_y=True,
                    )
            except Exception as e:
                logger.info("[DETAIL] building lines failed: %s", e)

            if len(fig.data) == 0:
                fig.add_annotation(
                    text="No detailed data available for selected inputs.",
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=0.5,
                    showarrow=False,
                )
            return fig

        @app.callback(
            [Output("det_line_plot_1", "figure"), Output("sum_bar_plot_1", "figure")],
            [
                Input("project-dropdown_1", "value"),
                Input("json-dropdown_1", "value"),
                Input("network-dropdown_1", "value"),
            ],
        )
        def update_figure_left(selected_project, selected_json, selected_network):
            if not selected_project or not selected_json or not selected_network:
                return (go.Figure(), go.Figure())
            try:
                optm_path = (
                    Path(self.base_dir)
                    / "backend"
                    / "results"
                    / "optimization_results"
                    / selected_project
                    / f"plot_{selected_json[:-5]}.xlsx"
                )
                sim_path = (
                    Path(self.base_dir)
                    / "backend"
                    / "results"
                    / "simulation_results"
                    / selected_project
                    / f"plot_{selected_json[:-5]}.xlsx"
                )

                # Load each file if present (fallback to empty DataFrame otherwise)
                optm_df = pd.read_excel(optm_path, dtype=str) if optm_path.exists() else pd.DataFrame()
                sim_df = pd.read_excel(sim_path, dtype=str) if sim_path.exists() else pd.DataFrame()

                detail_fig = build_detail_figure(optm_df, sim_df, selected_network)
                summary_fig = build_summary_figure(optm_df, sim_df)
                return (detail_fig, summary_fig)
            except Exception as e:
                logger.info("[LEFT] update failed: %s", e)
                return (go.Figure(), build_summary_figure(pd.DataFrame(), pd.DataFrame()))

        @app.callback(
            [Output("det_line_plot_2", "figure"), Output("sum_bar_plot_2", "figure")],
            [
                Input("project-dropdown_2", "value"),
                Input("json-dropdown_2", "value"),
                Input("network-dropdown_2", "value"),
            ],
        )
        def update_figure_right(selected_project, selected_json, selected_network):
            if not selected_project or not selected_json or not selected_network:
                return (go.Figure(), go.Figure())
            try:
                optm_path = (
                    Path(self.base_dir)
                    / "backend"
                    / "results"
                    / "optimization_results"
                    / selected_project
                    / f"plot_{selected_json[:-5]}.xlsx"
                )
                sim_path = (
                    Path(self.base_dir)
                    / "backend"
                    / "results"
                    / "simulation_results"
                    / selected_project
                    / f"plot_{selected_json[:-5]}.xlsx"
                )

                # Load each file if present (fallback to empty DataFrame otherwise)
                optm_df = pd.read_excel(optm_path, dtype=str) if optm_path.exists() else pd.DataFrame()
                sim_df = pd.read_excel(sim_path, dtype=str) if sim_path.exists() else pd.DataFrame()

                detail_fig = build_detail_figure(optm_df, sim_df, selected_network)
                summary_fig = build_summary_figure(optm_df, sim_df)
                return (detail_fig, summary_fig)
            except Exception as e:
                logger.info("[RIGHT] update failed: %s", e)
                return (go.Figure(), build_summary_figure(pd.DataFrame(), pd.DataFrame()))

    def _register_callbacks(self, app):
        self._register_summary_callbacks(app)
        self._register_graph_callbacks(app)
        self._register_evaluation_figure_callbacks(app)

    def plotting(self):
        project_list = self._load_project_list()
        layout = self._define_layout(project_list)
        app = self._initialize_dash_app(layout)
        self._register_callbacks(app)
        app.run(debug=False)

    def analyze_project_data(self, path):
        self.project_data = pd.read_csv(path, delimiter=";", decimal=",")
        heating_and_cooling_demands = [key.replace(".heat_flow", "") for key in self.project_data if "heat_flow" in key]

        self.start_time = self.project_data["time"][0]
        self.stop_time = self.project_data["time"][-1:].to_numpy()[0]
        self.heatDemandTemperatures = {}
        self.coolDemandTemperatures = {}

        for demand in heating_and_cooling_demands:
            if "heatDemand" in demand:
                self.heatDemandTemperatures[demand] = [
                    self.project_data[demand + ".temp_in"].max(),
                    self.project_data[demand + ".temp_out"].max(),
                ]
            else:
                self.coolDemandTemperatures[demand] = [
                    self.project_data[demand + ".temp_in"].min(),
                    self.project_data[demand + ".temp_out"].min(),
                ]


if __name__ == "__main__":
    cli_app = CommandLineApplication()
    cli_app.plotting()
