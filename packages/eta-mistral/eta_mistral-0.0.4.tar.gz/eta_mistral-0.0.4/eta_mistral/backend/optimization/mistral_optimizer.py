import json
import pickle
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd
from pyomo.environ import (
    AbstractModel,
    Binary,
    Constraint,
    NonNegativeReals,
    Objective,
    Param,
    Set,
    SolverFactory,
    Var,
    minimize,
)

__author__ = ["Lukas Theisinger (LT)", "Michael Frank (MFr)"]
__maintainer__ = "Michael Frank (MFr)"
__email__ = "m.frank@ptw.tu-darmstadt.de"
__project__ = "MISTRAL FKZ: 03EN4098A-E"
__subject__ = "Cluster 1: Optimization algorithm"
__status__ = "Work in progress"


class MistralOptimizer:
    def __init__(self, project_title, variant_title):
        self.project_title = project_title
        self.variant_title = variant_title
        self.base_dir = Path(__file__).resolve().parent.parent
        self.input_dir = self.base_dir / "input"

    def setup_optimization_model(self):
        """
        optimization model used to find optimal configurations of industrial thermal energy
        supply systems - analyzing demand data, temperature limits and spatial constraints
        the optimization model consists of sources (waste heat / cooling demand),
        sinks (heating demand), hot- and cold-utilities (energy converters) as well as
        crosslinking technologies (heatpumps and heatexchangers)
        """
        self._define_abstract_model_hot_utility()
        self._define_abstract_model_cold_utility()
        self._define_abstract_model_heatpump()
        self._define_abstract_model_heatexchanger()
        self._define_abstract_model_system()  # combines all above components in one optimization model

        return self.optimization_model  # returns the "model" so it is accessible by the solver interface

    def _define_abstract_model_hot_utility(self):
        self.hot_utility = AbstractModel()
        """
            abstract model of a hot utility (converter for heat supply)
            operational behavior defined by nominal gas and electric power and efficiencies
        """

        self.hot_utility.networks = Set(doc="thermal networks for heating and cooling supply")
        self.hot_utility.times = Set(doc="time steps")

        self.hot_utility.power_gas_nom = Param(
            self.hot_utility.networks, within=NonNegativeReals, doc="nominal gas power of hot utility"
        )
        self.hot_utility.power_el_nom = Param(
            self.hot_utility.networks, within=NonNegativeReals, doc="nominal electric power of hot utility"
        )
        self.hot_utility.eta_th_nom = Param(
            self.hot_utility.networks, within=NonNegativeReals, doc="nomial thermal efficiency of hot utility"
        )
        self.hot_utility.eta_el_nom = Param(
            self.hot_utility.networks, within=NonNegativeReals, doc="nomial electric efficiency of hot utility"
        )

        self.hot_utility.p_gas = Var(
            self.hot_utility.networks,
            self.hot_utility.times,
            within=NonNegativeReals,
            doc="gas power consumption of hot utility",
        )
        self.hot_utility.p_el = Var(
            self.hot_utility.networks,
            self.hot_utility.times,
            within=NonNegativeReals,
            doc="electric power consumption of hot utility",
        )
        self.hot_utility.p_th_heat_gen = Var(
            self.hot_utility.networks,
            self.hot_utility.times,
            within=NonNegativeReals,
            doc="heating power generation of hot utility",
        )
        self.hot_utility.p_el_gen = Var(
            self.hot_utility.networks,
            self.hot_utility.times,
            within=NonNegativeReals,
            doc="electric power generation of hot utility",
        )

        def nominal_gas_limitation(model, network, times):
            # limit gas consumption by nominal to_numpy()
            return model.power_gas_nom[network] >= model.p_gas[network, times]

        self.hot_utility.nominal_gas_limitation = Constraint(
            self.hot_utility.networks, self.hot_utility.times, rule=nominal_gas_limitation
        )

        def nominal_el_limitation(model, network, times):
            # limit electricity consumption by nominal to_numpy()
            return model.power_el_nom[network] >= model.p_el[network, times]

        self.hot_utility.nominal_el_limitation = Constraint(
            self.hot_utility.networks, self.hot_utility.times, rule=nominal_el_limitation
        )

        def consumption_rule(model, network, times):
            # compute gas and electricity consumtion
            return (model.p_gas[network, times] + model.p_el[network, times]) * model.eta_th_nom[
                network
            ] == model.p_th_heat_gen[network, times]

        self.hot_utility.consumption_rule = Constraint(
            self.hot_utility.networks, self.hot_utility.times, rule=consumption_rule
        )

        def el_generation_rule(model, network, times):
            # compute electricity generation
            return model.p_gas[network, times] * model.eta_el_nom[network] == model.p_el_gen[network, times]

        self.hot_utility.el_generation_rule = Constraint(
            self.hot_utility.networks, self.hot_utility.times, rule=el_generation_rule
        )
        return self.hot_utility

    def _define_abstract_model_cold_utility(self):
        self.cold_utility = AbstractModel()
        """
            abstract model of a cold utility (converter for cooling supply)
            operational behavior defined by nominal gas and electric power and efficiencies
        """

        self.cold_utility.networks = Set(doc="thermal networks for heating and cooling supply")
        self.cold_utility.times = Set(doc="time steps")

        self.cold_utility.power_gas_nom = Param(
            self.cold_utility.networks, within=NonNegativeReals, doc="nominal gas power of cold utility"
        )
        self.cold_utility.power_el_nom = Param(
            self.cold_utility.networks, within=NonNegativeReals, doc="nominal electric power of cold utility"
        )
        self.cold_utility.eta_th_nom = Param(
            self.cold_utility.networks, within=NonNegativeReals, doc="nomial thermal efficiency of cold utility"
        )
        self.cold_utility.eta_el_nom = Param(
            self.cold_utility.networks, within=NonNegativeReals, doc="nomial electric efficiency of cold utility"
        )

        self.cold_utility.p_gas = Var(
            self.cold_utility.networks,
            self.cold_utility.times,
            within=NonNegativeReals,
            doc="gas power consumption of cold utility",
        )
        self.cold_utility.p_el = Var(
            self.cold_utility.networks,
            self.cold_utility.times,
            within=NonNegativeReals,
            doc="electric power consumption of cold utility",
        )
        self.cold_utility.p_th_cool_gen = Var(
            self.cold_utility.networks,
            self.cold_utility.times,
            within=NonNegativeReals,
            doc="cooling power generation of cold utility",
        )
        self.cold_utility.p_el_gen = Var(
            self.cold_utility.networks,
            self.cold_utility.times,
            within=NonNegativeReals,
            doc="electric power generation of cold utility",
        )

        def nominal_gas_limitation(model, network, times):
            # limit gas consumption by nominal to_numpy()
            return model.power_gas_nom[network] >= model.p_gas[network, times]

        self.cold_utility.nominal_gas_limitation = Constraint(
            self.cold_utility.networks, self.cold_utility.times, rule=nominal_gas_limitation
        )

        def nominal_el_limitation(model, network, times):
            # limit electricity consumption by nominal to_numpy()
            return model.power_el_nom[network] >= model.p_el[network, times]

        self.cold_utility.nominal_el_limitation = Constraint(
            self.cold_utility.networks, self.cold_utility.times, rule=nominal_el_limitation
        )

        def consumption_rule(model, network, times):
            # compute gas and electricity consumption
            return (model.p_gas[network, times] + model.p_el[network, times]) * model.eta_th_nom[
                network
            ] == model.p_th_cool_gen[network, times]

        self.cold_utility.consumption_rule = Constraint(
            self.cold_utility.networks, self.cold_utility.times, rule=consumption_rule
        )

        def el_generation_rule(model, network, times):
            # compute electricity generation
            return model.p_gas[network, times] * model.eta_el_nom[network] == model.p_el_gen[network, times]

        self.cold_utility.el_generation_rule = Constraint(
            self.cold_utility.networks, self.cold_utility.times, rule=el_generation_rule
        )
        return self.cold_utility

    def _define_abstract_model_heatpump(self):
        self.heatpump = AbstractModel()
        """
            abstract model for heatpump as crosslinking technology (between two thermal networks)
            operational behavior primarily defined by cop
            allowance of placement "between" two thermal networks depends on temperature limits
        """

        self.heatpump.networks = Set(doc="thermal networks for heating and cooling supply")
        self.heatpump.nodes = Set(doc="physical locations of sources and sinks")

        self.heatpump.times = Set(doc="time steps")

        self.heatpump.temp_heat = Param(
            self.heatpump.networks, within=NonNegativeReals, doc="temperature levels of networks for heat supply"
        )
        self.heatpump.temp_cool = Param(
            self.heatpump.networks, within=NonNegativeReals, doc="temperature levels of networks for cool supply"
        )
        self.heatpump.cop = Param(
            self.heatpump.networks, self.heatpump.networks, default=0.0, within=NonNegativeReals, doc="cop"
        )
        self.heatpump.bigm_temp = 100
        self.heatpump.bigm_power = 1000

        self.heatpump.p_th_heat_crosslink_supply = Var(
            self.heatpump.nodes,
            self.heatpump.networks,
            self.heatpump.networks,
            self.heatpump.times,
            within=NonNegativeReals,
            doc="heat supplied by heatpump from one network into another",
        )
        self.heatpump.p_th_cool_crosslink_supply = Var(
            self.heatpump.nodes,
            self.heatpump.networks,
            self.heatpump.networks,
            self.heatpump.times,
            within=NonNegativeReals,
            doc="cooling supplied by heatpump from one network into another",
        )
        self.heatpump.p_el_crosslink_demand = Var(
            self.heatpump.nodes,
            self.heatpump.networks,
            self.heatpump.networks,
            self.heatpump.times,
            within=NonNegativeReals,
            doc="electricity demand of heatpump",
        )

        self.heatpump.alpha_allow_crosslinking = Var(
            self.heatpump.networks,
            self.heatpump.networks,
            within=Binary,
            doc="binary to determine wheter heatpump between networks is allowed",
        )

        def energy_balance(model, nodes, source_network, sink_network, times):
            # generic energy balance
            return (
                model.p_th_heat_crosslink_supply[nodes, source_network, sink_network, times]
                == model.p_th_cool_crosslink_supply[nodes, sink_network, source_network, times]
                + model.p_el_crosslink_demand[nodes, source_network, sink_network, times]
            )

        self.heatpump.energy_balance = Constraint(
            self.heatpump.nodes,
            self.heatpump.networks,
            self.heatpump.networks,
            self.heatpump.times,
            rule=energy_balance,
        )

        def cop_equation(model, nodes, source_network, sink_network, times):
            # cop equation
            return (
                model.p_th_heat_crosslink_supply[nodes, source_network, sink_network, times]
                == model.cop[source_network, sink_network]
                * model.p_el_crosslink_demand[nodes, source_network, sink_network, times]
            )

        self.heatpump.cop_equation = Constraint(
            self.heatpump.nodes, self.heatpump.networks, self.heatpump.networks, self.heatpump.times, rule=cop_equation
        )

        def alpha_constraint1(model, sink_network, source_network):
            # BigM constraint for Sink.temp_heat > Source.temp_cool
            return model.temp_heat[sink_network] >= model.temp_cool[source_network] - model.bigm_temp * (
                1 - model.alpha_allow_crosslinking[source_network, sink_network]
            )

        self.heatpump.alpha_constraint1 = Constraint(
            self.heatpump.networks, self.heatpump.networks, rule=alpha_constraint1
        )

        def alpha_constraint2(model, sink_network, source_network):
            # BigM constraint for Sink.temp_heat > Source.temp_cool
            return (
                model.temp_cool[source_network]
                >= model.temp_heat[sink_network]
                - model.bigm_temp * model.alpha_allow_crosslinking[source_network, sink_network]
            )

        self.heatpump.alpha_constraint2 = Constraint(
            self.heatpump.networks, self.heatpump.networks, rule=alpha_constraint2
        )

        def allowance_limitation(model, nodes, sink_network, source_network, times):
            # determine allowance of heatpump placement depending on BigM constraint
            return (
                model.p_th_heat_crosslink_supply[nodes, source_network, sink_network, times]
                <= model.alpha_allow_crosslinking[source_network, sink_network] * model.bigm_power
            )

        self.heatpump.allowance_limitation = Constraint(
            self.heatpump.nodes,
            self.heatpump.networks,
            self.heatpump.networks,
            self.heatpump.times,
            rule=allowance_limitation,
        )
        return self.heatpump

    def _define_abstract_model_heatexchanger(self):
        self.heatexchanger = AbstractModel()
        """
            abstract model for heatexchanger as crosslinking technology (between two thermal networks)
            allowance of placement "between" two thermal networks depends on temperature limits
        """

        self.heatexchanger.networks = Set(doc="thermal networks for heating and cooling supply")
        self.heatexchanger.nodes = Set(doc="physical locations of sources and sinks")

        self.heatexchanger.times = Set(doc="time steps")

        self.heatexchanger.temp_heat = Param(
            self.heatexchanger.networks, within=NonNegativeReals, doc="temperature levels of networks for heat supply"
        )
        self.heatexchanger.temp_cool = Param(
            self.heatexchanger.networks, within=NonNegativeReals, doc="temperature levels of networks for cool supply"
        )
        self.heatexchanger.efficiency = 1  # efficiency for heat exchanger --> heat_supply < cool_supply
        self.heatexchanger.bigm_temp = 100
        self.heatexchanger.bigm_power = 1000

        self.heatexchanger.p_th_heat_crosslink_supply = Var(
            self.heatexchanger.nodes,
            self.heatexchanger.networks,
            self.heatexchanger.networks,
            self.heatexchanger.times,
            within=NonNegativeReals,
            doc="heat supplied by heatexchanger from one network into another",
        )
        self.heatexchanger.p_th_cool_crosslink_supply = Var(
            self.heatexchanger.nodes,
            self.heatexchanger.networks,
            self.heatexchanger.networks,
            self.heatexchanger.times,
            within=NonNegativeReals,
            doc="cooling supplied by heatexchanger from one network into another",
        )

        self.heatexchanger.alpha_allow_crosslinking = Var(
            self.heatexchanger.networks,
            self.heatexchanger.networks,
            within=Binary,
            doc="binary to determine wheter heatexchanger between networks is allowed",
        )

        def energy_balance(model, nodes, source_network, sink_network, times):
            # generic energy balance
            return (
                model.p_th_heat_crosslink_supply[nodes, source_network, sink_network, times]
                == model.efficiency * model.p_th_cool_crosslink_supply[nodes, sink_network, source_network, times]
            )

        self.heatexchanger.energy_balance = Constraint(
            self.heatexchanger.nodes,
            self.heatexchanger.networks,
            self.heatexchanger.networks,
            self.heatexchanger.times,
            rule=energy_balance,
        )

        def alpha_constraint1(model, sink_network, source_network):
            # BigM constraint for Sink.temp_heat < Source.temp_cool
            return model.temp_cool[source_network] >= model.temp_heat[sink_network] - model.bigm_temp * (
                1 - model.alpha_allow_crosslinking[source_network, sink_network]
            )

        self.heatexchanger.alpha_constraint1 = Constraint(
            self.heatexchanger.networks, self.heatexchanger.networks, rule=alpha_constraint1
        )

        def alpha_constraint2(model, sink_network, source_network):
            # BigM constraint for Sink.temp_heat < Source.temp_cool
            return (
                model.temp_heat[sink_network]
                >= model.temp_cool[source_network]
                - model.bigm_temp * model.alpha_allow_crosslinking[source_network, sink_network]
            )

        self.heatexchanger.alpha_constraint2 = Constraint(
            self.heatexchanger.networks, self.heatexchanger.networks, rule=alpha_constraint2
        )

        def allowance_limitation(model, nodes, sink_network, source_network, times):
            # determine allowance of heatexchanger placement depending on BigM constraint
            return (
                model.p_th_heat_crosslink_supply[nodes, source_network, sink_network, times]
                <= model.alpha_allow_crosslinking[source_network, sink_network] * model.bigm_power
            )

        self.heatexchanger.allowance_limitation = Constraint(
            self.heatexchanger.nodes,
            self.heatexchanger.networks,
            self.heatexchanger.networks,
            self.heatexchanger.times,
            rule=allowance_limitation,
        )
        return self.heatexchanger

    def _define_abstract_model_system(self):
        self.system = AbstractModel()
        """
            General idea:
            thermal supply systems consist of sources (cooling demands, e.g. tooling machines
            -> waste heat) and sinks (heating demands, e.g. space heating).
            Sources and sinks are aggregated into nodes which define their physical location.
            Likewise, nodes are used to describe the thermal networks.
            Each source or sink is described by its specific supply and target temperature. Thermal
            networks exhibit specific temperatures for heating and cooling applications.
            Within the thermal networks hot- and cold-utilities as well as crosslinking
            technologies and storages are placed.
            by solving the optimization model the following decisions are made:
            - allocation of sources and sinks to thermal networks ->building networks
            - allocation of crosslinking technologies to thermal networks and dimensioning
            - dimensioning and operational optimization of storages within the thermal networks
        """

        self.system.networks = Set(doc="thermal networks for heating and cooling supply")
        self.system.nodes = Set(doc="physical locations of sources and sinks")
        self.system.sources = Set(doc="sources within systems")
        self.system.sinks = Set(doc="sinks within systems")

        self.system.times = Set(doc="time steps")
        self.system.dt = Param(within=NonNegativeReals, doc="length of one timestep")

        self.system.temp_heat = Param(
            self.system.networks, within=NonNegativeReals, doc="temperature levels of networks for heat supply"
        )
        self.system.temp_cool = Param(
            self.system.networks, within=NonNegativeReals, doc="temperature levels of networks for cool supply"
        )

        self.system.power_th_heat_dem = Param(
            self.system.sinks,
            self.system.nodes,
            self.system.times,
            within=NonNegativeReals,
            default=0.0,
            doc="heat demand of sink located at node",
        )
        self.system.power_th_cool_dem = Param(
            self.system.sources,
            self.system.nodes,
            self.system.times,
            within=NonNegativeReals,
            default=0.0,
            doc="cool demand of source located at node",
        )
        self.system.temp_heat_supply = Param(
            self.system.sinks,
            self.system.nodes,
            within=NonNegativeReals,
            default=0.0,
            doc="supply (return) temperature of specific sink",
        )
        self.system.temp_heat_target = Param(
            self.system.sinks,
            self.system.nodes,
            within=NonNegativeReals,
            default=0.0,
            doc="target (flow) temperature of specific sink",
        )
        self.system.temp_cool_supply = Param(
            self.system.sources,
            self.system.nodes,
            within=NonNegativeReals,
            default=0.0,
            doc="supply (return) temperature of specific source",
        )
        self.system.temp_cool_target = Param(
            self.system.sources,
            self.system.nodes,
            within=NonNegativeReals,
            default=0.0,
            doc="target (flow) temperature of specific source",
        )
        self.system.spec_co2_el = Param(doc="specific carbon-factor of electricity [g/kWh]")
        self.system.spec_co2_gas = Param(doc="specific carbon-factor of gas [g/kWh]")

        self.system.thermal_energy_storage_cap_max = Param(
            self.system.networks, within=NonNegativeReals, doc="maximum storage capacity"
        )

        self.system.alpha_netw_cont_node = Param(
            self.system.networks,
            self.system.nodes,
            within=Binary,
            default=0,
            doc="binary which defines wheter specific network contains specific node",
        )
        self.system.delta_crosslink_node = Param(
            self.system.nodes,
            within=Binary,
            default=0,
            doc="binary which defines wheter crosslinking technology can be placed at specific node",
        )

        self.system.p_th_heat_sink_netw_supply = Var(
            self.system.sinks,
            self.system.nodes,
            self.system.networks,
            self.system.times,
            within=NonNegativeReals,
            doc="heating power which is supplied to specific sink from specific network",
        )
        self.system.p_th_cool_source_netw_supply = Var(
            self.system.sources,
            self.system.nodes,
            self.system.networks,
            self.system.times,
            within=NonNegativeReals,
            doc="cooling power which is supplied to specific source from specific network",
        )

        self.system.gamma_ext_heat_supply_temp_fit = Var(
            self.system.sinks,
            self.system.nodes,
            self.system.networks,
            within=Binary,
            doc="binary variable which defines wheter temp_heat_supply < temp_cool of sink-network combination",
        )
        self.system.gamma_ext_heat_target_temp_fit = Var(
            self.system.sinks,
            self.system.nodes,
            self.system.networks,
            within=Binary,
            doc="binary variable which defines wheter temp_heat_target < temp_heat of sink-network combination",
        )
        self.system.gamma_ext_heat_temp_fit = Var(
            self.system.sinks,
            self.system.nodes,
            self.system.networks,
            within=Binary,
            doc="binary variable which defines wheter supply/target temperatures allow sink integration into network",
        )
        self.system.gamma_ext_cool_supply_temp_fit = Var(
            self.system.sources,
            self.system.nodes,
            self.system.networks,
            within=Binary,
            doc="binary variable which defines wheter temp_cool_supply > temp_heat of source-network combination",
        )
        self.system.gamma_ext_cool_target_temp_fit = Var(
            self.system.sources,
            self.system.nodes,
            self.system.networks,
            within=Binary,
            doc="binary variable which defines wheter temp_cool_target < temp_cool of source-network combination",
        )
        self.system.gamma_ext_cool_temp_fit = Var(
            self.system.sources,
            self.system.nodes,
            self.system.networks,
            within=Binary,
            doc="binary variable which defines wheter supply/target temperatures allow source integration into network",
        )

        self.system.sigma_ext_heat_supply = Var(
            self.system.sinks,
            self.system.nodes,
            self.system.networks,
            within=Binary,
            doc="variable which defines if sink is supplied by network",
        )
        self.system.sigma_ext_cool_supply = Var(
            self.system.sources,
            self.system.nodes,
            self.system.networks,
            within=Binary,
            doc="variable which defines if source is supplied by network",
        )

        self.system.p_th_heat_netw_dem = Var(
            self.system.networks, self.system.times, within=NonNegativeReals, doc="residual heat demand of network"
        )
        self.system.p_th_cool_netw_dem = Var(
            self.system.networks, self.system.times, within=NonNegativeReals, doc="residual cooling demand of network"
        )

        self.system.thermal_energy_storage_capnom = Var(
            self.system.networks, within=NonNegativeReals, doc="nominal thermal storage capacity"
        )
        self.system.E_th_storage_cap = Var(
            self.system.networks,
            self.system.times,
            initialize=0.0,
            within=NonNegativeReals,
            doc="actual thermal storage capacity at specific timestep",
        )
        self.system.p_th_storage_in = Var(
            self.system.networks, self.system.times, within=NonNegativeReals, doc="thermal power into thermal storage"
        )
        self.system.p_th_storage_out = Var(
            self.system.networks, self.system.times, within=NonNegativeReals, doc="thermal power out of thermal storage"
        )

        self.system.co2 = Var(self.system.times, within=NonNegativeReals, doc="carbon demand of one timestep")

        self.system.hps = self.heatpump.create_instance(self.hp_data)
        self.system.hexs = self.heatexchanger.create_instance(self.hex_data)
        self.system.hot_utils = self.hot_utility.create_instance(self.hot_utility_data)
        self.system.cold_utils = self.cold_utility.create_instance(self.cold_utility_data)

        self.system.bigm_temp = 100
        self.system.bigm_power = 1000

        def sink_balance(model, sinks, nodes, time):
            # the heat demand of a sink must be either supplied by the thermal networks
            return model.power_th_heat_dem[sinks, nodes, time] == sum(
                model.p_th_heat_sink_netw_supply[sinks, nodes, n, time] for n in model.networks
            )

        self.system.sink_balance = Constraint(
            self.system.sinks, self.system.nodes, self.system.times, rule=sink_balance
        )

        def source_balance(model, sources, nodes, time):
            # the cooling demand of a source must be either supplied by the thermal networks
            return model.power_th_cool_dem[sources, nodes, time] == sum(
                model.p_th_cool_source_netw_supply[sources, nodes, n, time] for n in model.networks
            )

        self.system.source_balance = Constraint(
            self.system.sources, self.system.nodes, self.system.times, rule=source_balance
        )

        self._define_network_specific_constraints()
        self._define_temperature_specific_constraints()
        self._define_storage_constraints()
        self._define_emission_balance_constraint()
        self._define_objective_constraint()

        self.optimization_model = self.system.create_instance(self.system_data)
        path = Path("model_structure_mistral_optimizer.txt")
        with path.open("w") as f:
            self.optimization_model.pprint(ostream=f)

    def _define_network_specific_constraints(self):
        """
        Below mostly network specific constraints are listed
        1. netw_connections: allow network utilization only if node is located in network
        2. netw_crosslinking: allow crosslinking converter to be placed at specific node
        3. netw_balances: energy balances of networks

        """

        def netw_connection_heat1(model, sinks, nodes, networks, time):
            # allow heat utilization of network only if node is located in network
            return (
                model.p_th_heat_sink_netw_supply[sinks, nodes, networks, time]
                <= model.alpha_netw_cont_node[networks, nodes] * model.bigm_power
            )

        self.system.netw_connection_heat1 = Constraint(
            self.system.sinks, self.system.nodes, self.system.networks, self.system.times, rule=netw_connection_heat1
        )

        def netw_connection_heat2(model, sinks, nodes, networks, time):
            # allow heat utilization of network only if node is located in network
            return (
                model.p_th_heat_sink_netw_supply[sinks, nodes, networks, time]
                <= model.gamma_ext_heat_temp_fit[sinks, nodes, networks] * model.bigm_power
            )

        self.system.netw_connection_heat2 = Constraint(
            self.system.sinks, self.system.nodes, self.system.networks, self.system.times, rule=netw_connection_heat2
        )

        def netw_utilization_heat1(model, sinks, nodes, networks, time):
            # determine wheter network is used to supply sink/source
            return (
                model.sigma_ext_heat_supply[sinks, nodes, networks] * model.bigm_power
                >= model.p_th_heat_sink_netw_supply[sinks, nodes, networks, time]
            )

        self.system.netw_utilization_heat1 = Constraint(
            self.system.sinks, self.system.nodes, self.system.networks, self.system.times, rule=netw_utilization_heat1
        )

        def netw_utilization_heat2(model, sinks, nodes):
            # allow each sink to be supplied only by one network
            return sum(model.sigma_ext_heat_supply[sinks, nodes, net] for net in model.networks) <= 1

        self.system.netw_utilization_heat2 = Constraint(
            self.system.sinks, self.system.nodes, rule=netw_utilization_heat2
        )

        def netw_connection_cool1(model, sources, nodes, networks, time):
            # allow cooling utilization of network only if node is located in network
            return (
                model.p_th_cool_source_netw_supply[sources, nodes, networks, time]
                <= model.alpha_netw_cont_node[networks, nodes] * model.bigm_power
            )

        self.system.netw_connection_cool1 = Constraint(
            self.system.sources, self.system.nodes, self.system.networks, self.system.times, rule=netw_connection_cool1
        )

        def netw_connection_cool2(model, sources, nodes, networks, time):
            # allow cooling utilization of network only if node is located in network
            return (
                model.p_th_cool_source_netw_supply[sources, nodes, networks, time]
                <= model.gamma_ext_cool_temp_fit[sources, nodes, networks] * model.bigm_power
            )

        self.system.netw_connection_cool2 = Constraint(
            self.system.sources, self.system.nodes, self.system.networks, self.system.times, rule=netw_connection_cool2
        )

        def netw_utilization_cool1(model, sources, nodes, networks, time):
            # determine wheter network is used to supply sink/source
            return (
                model.sigma_ext_cool_supply[sources, nodes, networks] * model.bigm_power
                >= model.p_th_cool_source_netw_supply[sources, nodes, networks, time]
            )

        self.system.netw_utilization_cool1 = Constraint(
            self.system.sources, self.system.nodes, self.system.networks, self.system.times, rule=netw_utilization_cool1
        )

        def netw_utilization_cool2(model, sources, nodes):
            # allow each source to be supplied only by one network
            return sum(model.sigma_ext_cool_supply[sources, nodes, net] for net in model.networks) <= 1

        self.system.netw_utilization_cool2 = Constraint(
            self.system.sources, self.system.nodes, rule=netw_utilization_cool2
        )

        def netw_crosslinking_heat(model, nodes, source_network, sink_network, time):
            # allow heatpump and heatexchanger placement of if node is crosslinking node
            return (
                model.hps.p_th_heat_crosslink_supply[nodes, source_network, sink_network, time]
                + model.hexs.p_th_heat_crosslink_supply[nodes, source_network, sink_network, time]
                <= model.delta_crosslink_node[nodes] * model.bigm_power
            )

        self.system.netw_crosslinking_heat = Constraint(
            self.system.nodes,
            self.system.networks,
            self.system.networks,
            self.system.times,
            rule=netw_crosslinking_heat,
        )

        def netw_crosslinking_cool(model, nodes, source_network, sink_network, time):
            # allow heatpump placement of if node is crosslinking node
            return (
                model.hps.p_th_cool_crosslink_supply[nodes, sink_network, source_network, time]
                + model.hexs.p_th_cool_crosslink_supply[nodes, sink_network, source_network, time]
                <= model.delta_crosslink_node[nodes] * model.bigm_power
            )

        self.system.netw_crosslinking_cool = Constraint(
            self.system.nodes,
            self.system.networks,
            self.system.networks,
            self.system.times,
            rule=netw_crosslinking_cool,
        )

        def netw_balance1(model, networks, time):
            # network energy balance for heating
            return model.p_th_heat_netw_dem[networks, time] == model.p_th_cool_netw_dem[networks, time] + sum(
                model.hps.p_th_cool_crosslink_supply[no, net, networks, time]
                + model.hexs.p_th_cool_crosslink_supply[no, net, networks, time]
                for net in model.networks
                for no in model.nodes
            ) + model.p_th_storage_in[networks, time] - model.p_th_storage_out[networks, time] - sum(
                model.hps.p_th_heat_crosslink_supply[no, net, networks, time]
                + model.hexs.p_th_heat_crosslink_supply[no, net, networks, time]
                for net in model.networks
                for no in model.nodes
            ) + sum(
                sum(model.p_th_heat_sink_netw_supply[sink, no, networks, time] for sink in model.sinks)
                - sum(model.p_th_cool_source_netw_supply[sou, no, networks, time] for sou in model.sources)
                for no in model.nodes
            )

        self.system.netw_balance1 = Constraint(self.system.networks, self.system.times, rule=netw_balance1)

        def netw_balance2(model, networks, time):
            # network energy balance for hot utilities
            return model.p_th_heat_netw_dem[networks, time] == model.hot_utils.p_th_heat_gen[networks, time]

        self.system.netw_balance2 = Constraint(self.system.networks, self.system.times, rule=netw_balance2)

        def netw_balance3(model, networks, time):
            # network energy balance for hot utilities
            return model.p_th_cool_netw_dem[networks, time] == model.cold_utils.p_th_cool_gen[networks, time]

        self.system.netw_balance3 = Constraint(self.system.networks, self.system.times, rule=netw_balance3)

    def _define_temperature_specific_constraints(self):
        """
        Below mostly temperature constraints are listed
        1. beta_int_heat_supply_constraints: node-specific constraint to determine wheter temp_cool_target >
        temp_heat_supply of source-sink combination for waste heat utilization
        2. beta_int_heat_target_constraints: node-specific constraint to determine wheter temp_cool_supply >
        temp_heat_target of source-sink combination for waste heat utilization
        3. beta_int_temp_fit_constraints: node-specific constraint to combine heat_supply and
        heat_target constraint
        4. gamma_ext_heat_supply_constraints: node-specific constraint to determine wheter temp_cool >
        temp_heat_supply of sink-network combination for waste heat utilization
        5. gamma_ext_heat_target_constraints: node-specific constraint to determine wheter temp_heat >
        temp_heat_target of sink-network combination for waste heat utilization
        6. gamma_ext_heat_temp_fit_constrains: node-specific constraint to combine heat_supply and
        heat_target constraint
        7. gamma_ext_cool_supply_constraints: node-specific constraint to determine wheter temp_cool_supply >
        temp_heat of source-network combination for waste heat utilization
        8. gamma_ext_cool_target_constraints: node-specific constraint to determine wheter temp_cool >
        temp_cool_target of cool-network combination for waste heat utilization
        9. gamma_ext_cool_temp_fit_constrains: node-specific constraint to combine cool_supply and
        cool_target constraint
        """

        def gamma_ext_heat_supply_constraint1(model, sinks, nodes, networks):
            # BigM constraint for temp_cool > temp_heat_supply
            return model.temp_cool[networks] >= model.temp_heat_supply[sinks, nodes] - model.bigm_temp * (
                1 - model.gamma_ext_heat_supply_temp_fit[sinks, nodes, networks]
            )

        self.system.gamma_ext_heat_supply_constraint1 = Constraint(
            self.system.sinks, self.system.nodes, self.system.networks, rule=gamma_ext_heat_supply_constraint1
        )

        def gamma_ext_heat_supply_constraint2(model, sinks, nodes, networks):
            # BigM constraint for temp_cool > temp_heat_supply
            return (
                model.temp_heat_supply[sinks, nodes]
                >= model.temp_cool[networks]
                - model.bigm_temp * model.gamma_ext_heat_supply_temp_fit[sinks, nodes, networks]
            )

        self.system.gamma_ext_heat_supply_constraint2 = Constraint(
            self.system.sinks, self.system.nodes, self.system.networks, rule=gamma_ext_heat_supply_constraint2
        )

        def gamma_ext_heat_target_constraint1(model, sinks, nodes, networks):
            # BigM constraint for temp_heat > temp_heat_target
            return model.temp_heat[networks] >= model.temp_heat_target[sinks, nodes] - model.bigm_temp * (
                1 - model.gamma_ext_heat_target_temp_fit[sinks, nodes, networks]
            )

        self.system.gamma_ext_heat_target_constraint1 = Constraint(
            self.system.sinks, self.system.nodes, self.system.networks, rule=gamma_ext_heat_target_constraint1
        )

        def gamma_ext_heat_target_constraint2(model, sinks, nodes, networks):
            # BigM constraint for temp_heat > temp_heat_target
            return (
                model.temp_heat_target[sinks, nodes]
                >= model.temp_heat[networks]
                - model.bigm_temp * model.gamma_ext_heat_target_temp_fit[sinks, nodes, networks]
            )

        self.system.gamma_ext_heat_target_constraint2 = Constraint(
            self.system.sinks, self.system.nodes, self.system.networks, rule=gamma_ext_heat_target_constraint2
        )

        def gamma_ext_heat_temp_fit_constraint1(model, sinks, nodes, networks):
            # combine heat_supply and heat_target constraint
            return (
                1 + model.gamma_ext_heat_temp_fit[sinks, nodes, networks]
                >= model.gamma_ext_heat_supply_temp_fit[sinks, nodes, networks]
                + model.gamma_ext_heat_target_temp_fit[sinks, nodes, networks]
            )

        self.system.gamma_ext_heat_temp_fit_constraint1 = Constraint(
            self.system.sinks, self.system.nodes, self.system.networks, rule=gamma_ext_heat_temp_fit_constraint1
        )

        def gamma_ext_heat_temp_fit_constraint2(model, sinks, nodes, networks):
            # combine heat_supply and heat_target constraint
            return model.gamma_ext_heat_temp_fit[sinks, nodes, networks] <= 0.5 * (
                model.gamma_ext_heat_supply_temp_fit[sinks, nodes, networks]
                + model.gamma_ext_heat_target_temp_fit[sinks, nodes, networks]
            )

        self.system.gamma_ext_heat_temp_fit_constraint2 = Constraint(
            self.system.sinks, self.system.nodes, self.system.networks, rule=gamma_ext_heat_temp_fit_constraint2
        )

        def gamma_ext_cool_supply_constraint1(model, sources, nodes, networks):
            # BigM constraint for temp_cool_supply > temp_heat
            return model.temp_cool_supply[sources, nodes] >= model.temp_heat[networks] - model.bigm_temp * (
                1 - model.gamma_ext_cool_supply_temp_fit[sources, nodes, networks]
            )

        self.system.gamma_ext_cool_supply_constraint1 = Constraint(
            self.system.sources, self.system.nodes, self.system.networks, rule=gamma_ext_cool_supply_constraint1
        )

        def gamma_ext_cool_supply_constraint2(model, sources, nodes, networks):
            # BigM constraint for temp_cool_supply > temp_heat
            return (
                model.temp_heat[networks]
                >= model.temp_cool_supply[sources, nodes]
                - model.bigm_temp * model.gamma_ext_cool_supply_temp_fit[sources, nodes, networks]
            )

        self.system.gamma_ext_cool_supply_constraint2 = Constraint(
            self.system.sources, self.system.nodes, self.system.networks, rule=gamma_ext_cool_supply_constraint2
        )

        def gamma_ext_cool_target_constraint1(model, sources, nodes, networks):
            # BigM constraint for temp_cool_target > temp_cool
            return model.temp_cool_target[sources, nodes] >= model.temp_cool[networks] - model.bigm_temp * (
                1 - model.gamma_ext_cool_target_temp_fit[sources, nodes, networks]
            )

        self.system.gamma_ext_cool_target_constraint1 = Constraint(
            self.system.sources, self.system.nodes, self.system.networks, rule=gamma_ext_cool_target_constraint1
        )

        def gamma_ext_cool_target_constraint2(model, sources, nodes, networks):
            # BigM constraint for temp_cool_target > temp_cool
            return (
                model.temp_cool[networks]
                >= model.temp_cool_target[sources, nodes]
                - model.bigm_temp * model.gamma_ext_cool_target_temp_fit[sources, nodes, networks]
            )

        self.system.gamma_ext_cool_target_constraint2 = Constraint(
            self.system.sources, self.system.nodes, self.system.networks, rule=gamma_ext_cool_target_constraint2
        )

        def gamma_ext_cool_temp_fit_constraint1(model, sources, nodes, networks):
            # combine cool_supply and cool_target constraint
            return (
                1 + model.gamma_ext_cool_temp_fit[sources, nodes, networks]
                >= model.gamma_ext_cool_supply_temp_fit[sources, nodes, networks]
                + model.gamma_ext_cool_target_temp_fit[sources, nodes, networks]
            )

        self.system.gamma_ext_cool_temp_fit_constraint1 = Constraint(
            self.system.sources, self.system.nodes, self.system.networks, rule=gamma_ext_cool_temp_fit_constraint1
        )

        def gamma_ext_cool_temp_fit_constraint2(model, sources, nodes, networks):
            # combine cool_supply and cool_target constraint
            return model.gamma_ext_cool_temp_fit[sources, nodes, networks] <= 0.5 * (
                model.gamma_ext_cool_supply_temp_fit[sources, nodes, networks]
                + model.gamma_ext_cool_target_temp_fit[sources, nodes, networks]
            )

        self.system.gamma_ext_cool_temp_fit_constraint2 = Constraint(
            self.system.sources, self.system.nodes, self.system.networks, rule=gamma_ext_cool_temp_fit_constraint2
        )

    def _define_storage_constraints(self):
        """
        below only storage constraints
        """

        def storage_balance(model, networks, time):
            # generic storage balance
            if time == 0:
                return (
                    model.E_th_storage_cap[networks, time]
                    == (model.p_th_storage_in[networks, time] - model.p_th_storage_out[networks, time]) * model.dt
                )
            return (
                model.E_th_storage_cap[networks, time] - model.E_th_storage_cap[networks, time - model.dt]
                == (model.p_th_storage_in[networks, time] - model.p_th_storage_out[networks, time]) * model.dt
            )

        self.system.storage_balance = Constraint(self.system.networks, self.system.times, rule=storage_balance)

        def storage_limit(model, networks, time):
            # storage capacity limit
            return model.E_th_storage_cap[networks, time] <= model.thermal_energy_storage_capnom[networks]

        self.system.storage_limit = Constraint(self.system.networks, self.system.times, rule=storage_limit)

        def max_storage_cap(model, networks):
            # maximum storage capacity limit
            return model.thermal_energy_storage_cap_max[networks] >= model.thermal_energy_storage_capnom[networks]

        self.system.max_storage_cap = Constraint(self.system.networks, rule=max_storage_cap)

        def storage_deload(model, networks):
            # deload storage at the end of timeperiod
            return (
                sum(model.p_th_storage_in[networks, t] for t in model.times)
                - sum(model.p_th_storage_out[networks, t] for t in model.times)
                == 0
            )

        self.system.storage_deload = Constraint(self.system.networks, rule=storage_deload)

        def storage_load_limit(model, networks, time):
            # only load storage with wasteheat or crosslinking technologies
            return model.p_th_storage_in[networks, time] <= sum(
                model.hps.p_th_heat_crosslink_supply[no, net, networks, time]
                + model.hexs.p_th_heat_crosslink_supply[no, net, networks, time]
                for net in model.networks
                for no in model.nodes
            ) + sum(
                sum(model.p_th_cool_source_netw_supply[sou, no, networks, time] for sou in model.sources)
                for no in model.nodes
            )

        self.system.storage_load_limit = Constraint(self.system.networks, self.system.times, rule=storage_load_limit)

        def storage_deload_limit(model, networks, time):
            # only deload storage for sinks of crosslinking technologies
            return model.p_th_storage_out[networks, time] <= sum(
                model.hps.p_th_cool_crosslink_supply[no, net, networks, time]
                + model.hexs.p_th_cool_crosslink_supply[no, net, networks, time]
                for net in model.networks
                for no in model.nodes
            ) + sum(
                sum(model.p_th_heat_sink_netw_supply[sink, no, networks, time] for sink in model.sinks)
                for no in model.nodes
            )

        self.system.storage_deload_limit = Constraint(
            self.system.networks, self.system.times, rule=storage_deload_limit
        )

    def _define_emission_balance_constraint(self):
        """
        below emission balances and objective function
        """

        def carbon_balance(model, time):
            return model.co2[time] == sum(
                model.hot_utils.p_gas[ne1, time] * model.spec_co2_gas * model.dt
                + (model.hot_utils.p_el[ne1, time] - model.hot_utils.p_el_gen[ne1, time]) * model.spec_co2_el * model.dt
                + model.cold_utils.p_gas[ne1, time] * model.spec_co2_gas * model.dt
                + (model.cold_utils.p_el[ne1, time] - model.cold_utils.p_el_gen[ne1, time])
                * model.spec_co2_el
                * model.dt
                + sum(
                    model.hps.p_el_crosslink_demand[no, ne1, net2, time] * model.dt * model.spec_co2_el
                    for no in model.nodes
                    for net2 in model.networks
                )
                for ne1 in model.networks
            )

        self.system.carbon_balance = Constraint(self.system.times, rule=carbon_balance)

    def _define_objective_constraint(self):
        def objective(model):
            return sum(model.co2[t] for t in model.times)

        self.system.obj = Objective(rule=objective, sense=minimize)

    def load_input_data(self):
        csv_path = Path(self.input_dir) / self.project_title / f"{self.project_title}.csv"
        self.input_df = pd.read_csv(csv_path, delimiter=";", decimal=",")
        self.sources_and_sinks = [key.replace(".heat_flow", "") for key in self.input_df if "heat_flow" in key]

    def input_data_to_pyomo_input(self):
        json_path = Path(self.input_dir) / self.project_title / f"{self.variant_title}.json"
        with json_path.open() as json_file:
            self.config_dict = json.load(json_file)

        self.dt = 0.25  # TODO @MFr: (#1) fix hardcoding
        self.times = [entry / 3600 for entry in self.input_df["time"]]
        self.power_th_cool_dem = {}
        self.power_th_heat_dem = {}
        self.temp_heat_supply = {}
        self.temp_heat_target = {}
        self.temp_cool_supply = {}
        self.temp_cool_target = {}

        # create demand data for heat and cold demand including temperature levels depending on input data
        for ss in self.sources_and_sinks:
            if "coolDemand" in ss:
                for timestep in self.times:
                    self.power_th_cool_dem[(ss, self.config_dict["source_sink_node_allocation"][ss], timestep)] = (
                        self.input_df.loc[self.input_df["time"] == timestep * 3600, ss + ".heat_flow"]._values[0]
                    )
                for node in self.config_dict["nodes"]:
                    self.temp_cool_supply[(ss, node)] = self.input_df[ss + ".temp_out"].max()
                    self.temp_cool_target[(ss, node)] = self.input_df[ss + ".temp_in"].min()
            if "heatDemand" in ss:
                for timestep in self.times:
                    self.power_th_heat_dem[(ss, self.config_dict["source_sink_node_allocation"][ss], timestep)] = (
                        self.input_df.loc[self.input_df["time"] == timestep * 3600, ss + ".heat_flow"]._values[0]
                    )
                for node in self.config_dict["nodes"]:
                    self.temp_heat_supply[(ss, node)] = self.input_df[ss + ".temp_out"].max()
                    self.temp_heat_target[(ss, node)] = self.input_df[ss + ".temp_in"].min()

        self.system_data = {
            None: {
                "networks": {None: self.config_dict["networks"]},
                "nodes": {None: self.config_dict["nodes"]},
                "sources": {
                    None: [sas for sas in self.sources_and_sinks if "coolDemand" in sas]
                },  # source = waste heat
                "sinks": {None: [sas for sas in self.sources_and_sinks if "heatDemand" in sas]},  # sink = heat demand
                "times": {None: self.times},
                "dt": {None: self.dt},
                "thermal_energy_storage_cap_max": self.config_dict["thermal_energy_storage_cap_max"],
                "spec_co2_el": {None: self.config_dict["spec_co2_el"]},
                "spec_co2_gas": {None: self.config_dict["spec_co2_gas"]},
                "alpha_netw_cont_node": {
                    (key1, key2): self.config_dict["network_node_allocation"][key1][key2]
                    for key1 in self.config_dict["network_node_allocation"]
                    for key2 in self.config_dict["network_node_allocation"][key1]
                },
                "delta_crosslink_node": self.config_dict["is_crosslink_node"],
                "temp_heat": self.config_dict["temp_heat"],
                "temp_cool": self.config_dict["temp_cool"],
                "power_th_heat_dem": self.power_th_heat_dem,
                "power_th_cool_dem": self.power_th_cool_dem,
                "temp_heat_supply": self.temp_heat_supply,
                "temp_heat_target": self.temp_heat_target,
                "temp_cool_supply": self.temp_cool_supply,
                "temp_cool_target": self.temp_cool_target,
            }
        }

        self.hp_data = {
            None: {
                "networks": self.config_dict["networks"],
                "nodes": self.config_dict["nodes"],
                "times": {None: self.times},
                "temp_heat": self.config_dict["temp_heat"],
                "temp_cool": self.config_dict["temp_cool"],
                "cop": {
                    (ne1, net2): (
                        self.config_dict["temp_heat"][net2]
                        * 0.5
                        / (self.config_dict["temp_heat"][net2] - self.config_dict["temp_cool"][ne1])
                        if self.config_dict["temp_heat"][net2] > self.config_dict["temp_cool"][ne1]
                        else 0
                    )
                    for ne1 in self.config_dict["networks"]
                    for net2 in self.config_dict["networks"]
                },
            }
        }

        self.hex_data = {
            None: {
                "networks": self.config_dict["networks"],
                "nodes": self.config_dict["nodes"],
                "times": {None: self.times},
                "temp_heat": self.config_dict["temp_heat"],
                "temp_cool": self.config_dict["temp_cool"],
            }
        }

        self.hot_utility_data = {
            None: {
                "networks": self.config_dict["networks"],
                "times": {None: self.times},
                "power_gas_nom": {
                    (key): self.config_dict["hot_utilities"][key]["power_gas_nom"]
                    for key in self.config_dict["networks"]
                },
                "power_el_nom": {
                    (key): self.config_dict["hot_utilities"][key]["power_el_nom"]
                    for key in self.config_dict["networks"]
                },
                "eta_th_nom": {
                    (key): self.config_dict["hot_utilities"][key]["eta_th_nom"] for key in self.config_dict["networks"]
                },
                "eta_el_nom": {
                    (key): self.config_dict["hot_utilities"][key]["eta_el_nom"] for key in self.config_dict["networks"]
                },
            }
        }

        self.cold_utility_data = {
            None: {
                "networks": self.config_dict["networks"],
                "times": {None: self.times},
                "power_gas_nom": {
                    (key): self.config_dict["cold_utilities"][key]["power_gas_nom"]
                    for key in self.config_dict["networks"]
                },
                "power_el_nom": {
                    (key): self.config_dict["cold_utilities"][key]["power_el_nom"]
                    for key in self.config_dict["networks"]
                },
                "eta_th_nom": {
                    (key): self.config_dict["cold_utilities"][key]["eta_th_nom"] for key in self.config_dict["networks"]
                },
                "eta_el_nom": {
                    (key): self.config_dict["cold_utilities"][key]["eta_el_nom"] for key in self.config_dict["networks"]
                },
            }
        }

    def save_results(self, model):
        """Refactor: idea: use save_results as an orchestrator and extract
        each inner store function into a self._store* methode
        pass model and res_dict as arguments to the helper functions.

        Args:
            model (_type_): _description_
        """
        all_res_dict = {}

        self._store_hot_utilities(model, all_res_dict)
        self._store_cold_utilities(model, all_res_dict)
        self._store_storage_capacities(model, all_res_dict)
        self._store_storage_loading_unloading(model, all_res_dict)
        self._store_heating_supply_of_networks(model, all_res_dict)
        self._store_cooling_supply_of_networks(model, all_res_dict)
        self._store_cool_network_demand(model, all_res_dict)
        self._store_heat_network_demand(model, all_res_dict)
        self._store_cooling_electricity_heat_pumps(model, all_res_dict)
        self._store_heating_heat_pumps(model, all_res_dict)
        self._store_cooling_heat_exchangers(model, all_res_dict)
        self._store_heating_heat_exchangers(model, all_res_dict)
        self._store_carbon_footprint(model, all_res_dict)

        # timesteps
        times_list = []
        for time_step in model.times._values:
            times_list.append(time_step)
        all_res_dict["times"] = times_list

        res_df = pd.DataFrame.from_dict(all_res_dict)
        output_path = (
            Path(self.base_dir) / "results" / "optimization_results" / self.project_title / f"{self.variant_title}.xlsx"
        )

        # create dir, if it doesnt already exist
        output_path.parent.mkdir(parents=True, exist_ok=True)

        res_df.to_excel(output_path)

    def _store_hot_utilities(self, model, all_res_dict):
        for network in self.system_data[None]["networks"][None]:
            el_list = []
            el_gen_list = []
            gas_list = []
            th_list = []
            for key in model.hot_utils.p_el._data:
                if network in key:
                    el_list.append(model.hot_utils.p_el._data[key].value)
                    el_gen_list.append(model.hot_utils.p_el_gen._data[key].value)
                    gas_list.append(model.hot_utils.p_gas._data[key].value)
                    th_list.append(model.hot_utils.p_th_heat_gen._data[key].value)
            all_res_dict["hot_util_p_el_" + network] = el_list
            all_res_dict["hot_util_p_el_gen_" + network] = el_gen_list
            all_res_dict["hot_util_p_gas_" + network] = gas_list
            all_res_dict["hot_util_p_th_" + network] = th_list

    def _store_cold_utilities(self, model, all_res_dict):
        for network in self.system_data[None]["networks"][None]:
            el_list = []
            el_gen_list = []
            gas_list = []
            th_list = []
            for key in model.cold_utils.p_el._data:
                if network in key:
                    el_list.append(model.cold_utils.p_el._data[key].value)
                    el_gen_list.append(model.cold_utils.p_el_gen._data[key].value)
                    gas_list.append(model.cold_utils.p_gas._data[key].value)
                    th_list.append(model.cold_utils.p_th_cool_gen._data[key].value)
            all_res_dict["cold_util_p_el_" + network] = el_list
            all_res_dict["cold_util_p_el_gen_" + network] = el_gen_list
            all_res_dict["cold_util_p_gas_" + network] = gas_list
            all_res_dict["cold_util_p_th_" + network] = th_list

    def _store_storage_capacities(self, model, all_res_dict):
        for network in self.system_data[None]["networks"][None]:
            stor_list = []
            for key in model.E_th_storage_cap._data:
                if network in key:
                    stor_list.append(model.E_th_storage_cap._data[key].value)
            all_res_dict["thermal_energy_storage_cap" + network] = stor_list

    def _store_storage_loading_unloading(self, model, all_res_dict):
        for network in self.system_data[None]["networks"][None]:
            stor_loading_list = []
            stor_deloading_list = []
            for key in model.p_th_storage_in._data:
                if network in key:
                    stor_loading_list.append(model.p_th_storage_in._data[key].value)
                    stor_deloading_list.append(model.p_th_storage_out._data[key].value)
            all_res_dict["p_th_storage_in_" + network] = stor_loading_list
            all_res_dict["p_th_storage_out_" + network] = stor_deloading_list

    def _store_heating_supply_of_networks(self, model, all_res_dict):
        for sink in model.sinks:
            for no in model.nodes:
                for net in model.networks:
                    sink_netw_list = []
                    for time_step in model.times:
                        sink_netw_list.append(model.p_th_heat_sink_netw_supply._data[(sink, no, net, time_step)].value)
                    all_res_dict["p_th_heat_" + sink + "_" + no + "_" + net] = sink_netw_list

    def _store_cooling_supply_of_networks(self, model, all_res_dict):
        for source in model.sources:
            for no in model.nodes:
                for net in model.networks:
                    source_netw_list = []
                    for time_step in model.times:
                        source_netw_list.append(
                            model.p_th_cool_source_netw_supply._data[(source, no, net, time_step)].value
                        )
                    all_res_dict["p_th_cool_" + source + "_" + no + "_" + net] = source_netw_list

    def _store_cool_network_demand(self, model, all_res_dict):
        for network in self.system_data[None]["networks"][None]:
            net_dem_list = []
            for key in model.p_th_cool_netw_dem._data:
                if network in key:
                    net_dem_list.append(model.p_th_cool_netw_dem._data[key].value)
            all_res_dict["p_th_cool_netw_dem_" + network] = net_dem_list

    def _store_heat_network_demand(self, model, all_res_dict):
        for network in self.system_data[None]["networks"][None]:
            net_dem_list = []
            for key in model.p_th_heat_netw_dem._data:
                if network in key:
                    net_dem_list.append(model.p_th_heat_netw_dem._data[key].value)
            all_res_dict["p_th_heat_netw_dem_" + network] = net_dem_list

    def _store_cooling_electricity_heat_pumps(self, model, all_res_dict):
        for node in self.system_data[None]["nodes"][None]:
            for network1 in self.system_data[None]["networks"][None]:
                for network2 in self.system_data[None]["networks"][None]:
                    if network1 == network2:
                        continue
                    cool_cross = []
                    el_cross = []
                    for key in model.hps.p_th_cool_crosslink_supply._data:
                        if node == key[0] and network1 == key[1] and network2 == key[2]:
                            cool_cross.append(model.hps.p_th_cool_crosslink_supply._data[key].value)
                            el_cross.append(model.hps.p_el_crosslink_demand._data[key].value)
                    all_res_dict["p_th_cool_hp_supply_" + node + "_" + network1 + "_" + network2] = cool_cross
                    all_res_dict["p_el_hp_" + node + "_" + network1 + "_" + network2] = el_cross

    def _store_heating_heat_pumps(self, model, all_res_dict):
        for node in self.system_data[None]["nodes"][None]:
            for network1 in self.system_data[None]["networks"][None]:
                for network2 in self.system_data[None]["networks"][None]:
                    if network1 == network2:
                        continue
                    heat_cross = []
                    for key in model.hps.p_th_heat_crosslink_supply._data:
                        if node == key[0] and network1 == key[1] and network2 == key[2]:
                            heat_cross.append(model.hps.p_th_heat_crosslink_supply._data[key].value)
                    all_res_dict["p_th_heat_hp_supply_" + node + "_" + network1 + "_" + network2] = heat_cross

    def _store_cooling_heat_exchangers(self, model, all_res_dict):
        for node in self.system_data[None]["nodes"][None]:
            for network1 in self.system_data[None]["networks"][None]:
                for network2 in self.system_data[None]["networks"][None]:
                    if network1 == network2:
                        continue
                    cool_cross = []
                    for key in model.hexs.p_th_cool_crosslink_supply._data:
                        if node == key[0] and network1 == key[1] and network2 == key[2]:
                            cool_cross.append(model.hexs.p_th_cool_crosslink_supply._data[key].value)
                    all_res_dict["p_th_cool_hex_supply_" + node + "_" + network1 + "_" + network2] = cool_cross

    def _store_heating_heat_exchangers(self, model, all_res_dict):
        for node in self.system_data[None]["nodes"][None]:
            for network1 in self.system_data[None]["networks"][None]:
                for network2 in self.system_data[None]["networks"][None]:
                    if network1 == network2:
                        continue
                    heat_cross = []
                    for key in model.hexs.p_th_heat_crosslink_supply._data:
                        if node == key[0] and network1 == key[1] and network2 == key[2]:
                            heat_cross.append(model.hexs.p_th_heat_crosslink_supply._data[key].value)
                    all_res_dict["p_th_heat_hex_supply_" + node + "_" + network1 + "_" + network2] = heat_cross

    def _store_carbon_footprint(self, model, all_res_dict):
        co2 = []
        for key in model.co2._data:
            co2.append(model.co2._data[key].value)
        all_res_dict["co2"] = co2

    def save_topology(self):
        output_path = (
            Path(self.base_dir) / "results" / "optimization_results" / self.project_title / f"{self.variant_title}.xlsx"
        )
        res_df = pd.read_excel(output_path)

        topology_description = {}
        topology_plot = {}
        graph = nx.Graph()

        networks = self.system_data[None]["networks"][None]
        nodes = self.system_data[None]["nodes"][
            None
        ]  # TODO @MFr: (#2) change naming of geographical "nodes" because confusing to nodes in graph theory

        # add for each netwok the relevant components as nodes
        for net in networks:
            topology_description[net] = []
            topology_plot[net] = []
            graph.add_node(net, id=net, root_nodes=[])
            self._add_sources(net, topology_description, topology_plot, graph, res_df, nodes)
            self._add_sinks(net, topology_description, topology_plot, graph, res_df, nodes)
            self._add_storage(net, topology_description, topology_plot, graph, res_df)
            self._add_hot_utility(net, topology_description, topology_plot, graph, res_df)
            self._add_cold_utility(net, topology_description, topology_plot, graph, res_df)
            self._add_heat_exchangers(net, networks, topology_description, topology_plot, graph, res_df, nodes)
            self._add_heat_pumps(net, networks, topology_description, topology_plot, graph, res_df, nodes)

        # add edges between nodes
        for node in graph.nodes:
            roots = graph.nodes[node]["root_nodes"]
            if len(roots) == 2:
                graph.add_edge(node, roots[0])
                graph.add_edge(node, roots[1])
            elif len(roots) == 1:
                graph.add_edge(node, roots[0])

        graph_path = (
            Path(self.base_dir)
            / "results"
            / "topology_description"
            / self.project_title
            / f"graph_{self.variant_title}.gpickle"
        )
        pickle_path = (
            Path(self.base_dir)
            / "results"
            / "topology_description"
            / self.project_title
            / f"{self.variant_title}.pickle"
        )
        graph_path.parent.mkdir(parents=True, exist_ok=True)
        pickle_path.parent.mkdir(parents=True, exist_ok=True)
        self._save_pickle(graph, graph_path)
        self._save_pickle(topology_description, pickle_path)

    def _save_pickle(self, obj, path):
        with path.open("wb") as f:
            pickle.dump(obj, f)

    def _get_supply_temp(self, supply_dict, key):
        """Returns default temperature if not found in input data.

        Args:
            supply_dict (_type_): _description_
            key (_type_): _description_
        """
        for entry in supply_dict:
            if key in entry:
                return supply_dict[entry]
        return 273.15 + 20

    def _time_series_list(self, res_df, value_array, col_time="times", multiplier=1):
        """Returns a lsit of tuples (time, value).

        Args:
            res_df (_type_): _description_
            value_array (_type_): _description_
            col_time (str, optional): _description_. Defaults to "times".
            multiplier (int, optional): _description_. Defaults to 1.
        """
        return [(row[col_time] * 3600, value_array[idx] * multiplier) for idx, row in res_df.iterrows()]

    def _add_sources(self, net, topology_description, topology_plot, graph, res_df, nodes):
        for source in self.system_data[None]["sources"][None]:
            temp_cool_supply = self._get_supply_temp(self.system_data[None]["temp_cool_supply"], source)
            summed_cool_supply = np.zeros(len(self.times))
            for node in nodes:
                summed_cool_supply += res_df[f"p_th_cool_{source}_{node}_{net}"].to_numpy()
            if summed_cool_supply.max() > 1.0:
                entry = {
                    "id": source,
                    "fmu_type": "source",
                    "parameters": {"dT_min": 5, "T_start": temp_cool_supply},
                    "inputs": {
                        "T_return_target": [(row["times"] * 3600, temp_cool_supply) for idx, row in res_df.iterrows()],
                        "Q_demand": self._time_series_list(res_df, summed_cool_supply, multiplier=1000),
                    },
                    "outputs": ["temp_in", "temp_out", "thermal_power"],
                    "link_p_th_to": None,
                }
                topology_description[net].append(entry)
                topology_plot[net].append({"id": source})
                graph.add_node(source, id=source, root_nodes=[net])

    def _add_sinks(self, net, topology_description, topology_plot, graph, res_df, nodes):
        for sink in self.system_data[None]["sinks"][None]:
            temp_heat_supply = self._get_supply_temp(self.system_data[None]["temp_heat_supply"], sink)
            summed_heat_supply = np.zeros(len(self.times))
            for node in nodes:
                summed_heat_supply += res_df[f"p_th_heat_{sink}_{node}_{net}"].to_numpy()
            if summed_heat_supply.max() > 1.0:
                entry = {
                    "id": sink,
                    "fmu_type": "sink",
                    "parameters": {"dT_min": 5, "T_start": temp_heat_supply},
                    "inputs": {
                        "T_return_target": [(row["times"] * 3600, temp_heat_supply) for idx, row in res_df.iterrows()],
                        "Q_demand": self._time_series_list(res_df, summed_heat_supply, multiplier=1000),
                    },
                    "outputs": ["temp_in", "temp_out", "thermal_power"],
                    "link_p_th_to": None,
                }
                topology_description[net].append(entry)
                topology_plot[net].append({"id": sink})
                graph.add_node(sink, id=sink, root_nodes=[net])

    def _add_storage(self, net, topology_description, topology_plot, graph, res_df):
        cap = res_df[f"thermal_energy_storage_cap{net}"].to_numpy().max()
        v = min(
            1,
            (max(1, cap) * 3600000)
            / (
                1000
                * 4200
                * max(10, self.system_data[None]["temp_cool"][net] - self.system_data[None]["temp_heat"][net])
            ),
        )
        entry = {
            "id": f"Storage_{net}",
            "fmu_type": "buffer_storage",
            "parameters": {
                "V": v,
                "T_start": self.system_data[None]["temp_cool"][net],
            },
            "inputs": {},
            "outputs": ["T_upper", "T_mid", "T_lower"],
        }
        topology_description[net].append(entry)
        topology_plot[net].append({"id": f"Storage_{net}", "E_th_cap": cap})
        graph.add_node(
            f"Storage_{net}",
            id=f"Storage_{net}; E_th_cap: {cap}",
            root_nodes=[net],
        )

    def _add_hot_utility(self, net, topology_description, topology_plot, graph, res_df):
        hot_utility = self.hot_utility_data[None]
        p_th_nom = (hot_utility["power_el_nom"][net] + hot_utility["power_gas_nom"][net]) * hot_utility["eta_th_nom"][
            net
        ]
        entry = {
            "id": f"Hot_util_{net}",
            "fmu_type": "hot_utility",
            "parameters": {
                "power_el_nom": hot_utility["power_el_nom"][net] * 1000,
                "power_gas_nom": hot_utility["power_gas_nom"][net] * 1000,
                "eta_th": hot_utility["eta_th_nom"][net],
                "eta_el": hot_utility["eta_el_nom"][net],
                "dT": 5,
                "T_start": self.system_data[None]["temp_heat"][net],
            },
            "inputs": {
                "temp_flow": [
                    (row["times"] * 3600, self.system_data[None]["temp_heat"][net]) for idx, row in res_df.iterrows()
                ]
            },
            "outputs": ["temp_in", "temp_out", "thermal_power", "power_gas", "power_el"],
        }
        topology_description[net].append(entry)
        topology_plot[net].append({"id": f"Hot_util_{net}", "P_th_nom": p_th_nom})
        graph.add_node(
            f"Hot_util_{net}",
            id=f"Hot_util_{net}; P_th_nom: {p_th_nom}",
            root_nodes=[net],
        )

    def _add_cold_utility(self, net, topology_description, topology_plot, graph, res_df):
        cold_utility = self.cold_utility_data[None]
        p_th_nom = cold_utility["power_el_nom"][net] * cold_utility["eta_th_nom"][net]
        entry = {
            "id": f"Cold_util_{net}",
            "fmu_type": "cold_utility",
            "parameters": {
                "power_el_nom": cold_utility["power_el_nom"][net] * 1000,
                "eta_th": cold_utility["eta_th_nom"][net],
                "dT": 5,
                "T_start": self.system_data[None]["temp_cool"][net],
            },
            "inputs": {
                "temp_flow": [
                    (row["times"] * 3600, self.system_data[None]["temp_cool"][net]) for idx, row in res_df.iterrows()
                ]
            },
            "outputs": ["temp_in", "temp_out", "thermal_power", "power_el"],
        }
        topology_description[net].append(entry)
        topology_plot[net].append({"id": f"Cold_util_{net}", "P_th_nom": p_th_nom})
        graph.add_node(
            f"Cold_util_{net}",
            id=f"Cold_util_{net}; P_th_nom: {p_th_nom}",
            root_nodes=[net],
        )

    def _add_heat_exchangers(self, net, networks, topology_description, topology_plot, graph, res_df, nodes):
        for net2 in networks:
            for node in nodes:
                if net == net2:
                    continue
                col = f"p_th_heat_hex_supply_{node}_{net}_{net2}"
                if res_df[col].to_numpy().max() > 1.0:
                    max_p_th = res_df[f"p_th_cool_hex_supply_{node}_{net2}_{net}"].to_numpy().max()
                    # On net side
                    entry_net = {
                        "id": f"Hex_{node}_{net}_{net2}",
                        "fmu_type": "cold_utility",
                        "parameters": {
                            "power_el_nom": max_p_th * 1000,
                            "eta_th": 1,
                            "dT": 5,
                            "T_start": self.system_data[None]["temp_cool"][net],
                        },
                        "inputs": {
                            "T_flow": [
                                (row["times"] * 3600, self.system_data[None]["temp_cool"][net])
                                for idx, row in res_df.iterrows()
                            ]
                        },
                        "outputs": ["temp_in", "temp_out", "thermal_power", "power_el"],
                    }
                    topology_description[net].append(entry_net)
                    topology_plot[net].append({"id": f"Hex_{node}_{net}_{net2}", "P_th_nom": max_p_th})
                    topology_plot[net2].append({"id": f"Hex_{node}_{net}_{net2}", "P_th_nom": max_p_th})

                    # On net2 side
                    entry_ne2 = {
                        "id": f"Hex_{node}_{net}_{net2}",
                        "fmu_type": "source",
                        "parameters": {"dT_min": 5, "T_start": self.system_data[None]["temp_heat"][net2]},
                        "inputs": {
                            "T_return_target": [
                                (row["times"] * 3600, self.system_data[None]["temp_heat"][net2])
                                for idx, row in res_df.iterrows()
                            ]
                        },
                        "outputs": ["temp_in", "temp_out", "thermal_power"],
                        "link_p_th_to": {"network": net, "id": f"Hex_{node}_{net}_{net2}"},
                    }
                    topology_description[net2].append(entry_ne2)
                    graph.add_node(
                        f"Hex_{node}_{net}_{net2}",
                        id=f"Hex_{node}_{net}_{net2}; P_th_nom: {max_p_th}",
                        root_nodes=[net, net2],
                    )

    def _add_heat_pumps(self, net, networks, topology_description, topology_plot, graph, res_df, nodes):
        for net2 in networks:
            for node in nodes:
                if net == net2:
                    continue
                col = f"p_th_heat_hp_supply_{node}_{net}_{net2}"
                if res_df[col].to_numpy().max() > 1.0:
                    max_p_el = res_df[f"p_el_hp_{node}_{net}_{net2}"].to_numpy().max()
                    cop = self.hp_data[None]["cop"][(net, net2)] - 1
                    entry_net = {
                        "id": f"Hp_{node}_{net}_{net2}",
                        "fmu_type": "cold_utility",
                        "parameters": {
                            "power_el_nom": max_p_el * 1000,
                            "eta_th": cop,
                            "dT": 5,
                            "T_start": self.system_data[None]["temp_cool"][net],
                        },
                        "inputs": {
                            "T_flow": [
                                (row["times"] * 3600, self.system_data[None]["temp_cool"][net])
                                for idx, row in res_df.iterrows()
                            ]
                        },
                        "outputs": ["temp_in", "temp_out", "thermal_power", "power_el"],
                    }
                    topology_description[net].append(entry_net)
                    topology_plot[net].append({"id": f"Hp_{node}_{net}_{net2}", "power_el_nom": max_p_el, "cop": cop})
                    topology_plot[net2].append({"id": f"Hp_{node}_{net}_{net2}", "power_el_nom": max_p_el, "cop": cop})

                    entry_ne2 = {
                        "id": f"Hp_{node}_{net}_{net2}",
                        "fmu_type": "source",
                        "parameters": {"dT_min": 5, "T_start": self.system_data[None]["temp_heat"][net2]},
                        "inputs": {
                            "T_return_target": [
                                (row["times"] * 3600, self.system_data[None]["temp_heat"][net2])
                                for idx, row in res_df.iterrows()
                            ]
                        },
                        "outputs": ["temp_in", "temp_out", "thermal_power"],
                        "link_p_th_to": {"network": net, "id": f"Hp_{node}_{net}_{net2}"},
                    }
                    topology_description[net2].append(entry_ne2)
                    graph.add_node(
                        f"Hp_{node}_{net}_{net2}",
                        id=f"Hp_{node}_{net}_{net2}; power_el_nom: {max_p_el}; COP: {cop}",
                        root_nodes=[net, net2],
                    )

    def convert_results(self):
        excel_path = (
            Path(self.base_dir) / "results" / "optimization_results" / self.project_title / f"{self.variant_title}.xlsx"
        )
        res_df = pd.read_excel(excel_path)

        plot_dict = {}

        plot_dict["times"] = res_df["times"].to_numpy()
        plot_dict["CO2"] = res_df["co2"].to_numpy()

        for network1 in self.system_data[None]["networks"][None]:
            plot_dict["Pth_heat_utility_" + network1] = np.zeros(res_df["times"].to_numpy().shape)
            plot_dict["Pth_cool_utility_" + network1] = np.zeros(res_df["times"].to_numpy().shape)
            plot_dict["Eth_storage_" + network1] = res_df["thermal_energy_storage_cap" + network1].to_numpy()

            for key in res_df:
                # utilities
                if "Hot_util" in key and "p_th" in key and key.split("_")[len(key.split("_")) - 1] == network1:
                    plot_dict["Pth_heat_utility_" + network1] += res_df[key].to_numpy()
                if "Cold_util" in key and "p_th" in key and key.split("_")[len(key.split("_")) - 1] == network1:
                    plot_dict["Pth_cool_utility_" + network1] += res_df[key].to_numpy()

            for network2 in self.system_data[None]["networks"][None]:
                plot_dict["Pth_cool_heatpump_" + network1 + "_" + network2] = np.zeros(res_df["times"].to_numpy().shape)
                plot_dict["Pth_heat_heatpump_" + network1 + "_" + network2] = np.zeros(res_df["times"].to_numpy().shape)
                plot_dict["Pth_cool_heatexchanger_" + network1 + "_" + network2] = np.zeros(
                    res_df["times"].to_numpy().shape
                )
                plot_dict["Pth_heat_heatexchanger_" + network1 + "_" + network2] = np.zeros(
                    res_df["times"].to_numpy().shape
                )

                for key in res_df:
                    # heatpumps
                    if (
                        "p_th_heat_hp" in key
                        and key.split("_")[len(key.split("_")) - 2] == network1
                        and key.split("_")[len(key.split("_")) - 1] == network2
                    ):  # check if network is target
                        plot_dict["Pth_heat_heatpump_" + network1 + "_" + network2] += res_df[key].to_numpy()
                    if (
                        "p_th_cool_hp" in key
                        and key.split("_")[len(key.split("_")) - 2] == network1
                        and key.split("_")[len(key.split("_")) - 1] == network2
                    ):  # check if network is target
                        plot_dict["Pth_cool_heatpump_" + network1 + "_" + network2] += res_df[key].to_numpy()
                    # heatexchangers
                    if (
                        "p_th_heat_hex" in key
                        and key.split("_")[len(key.split("_")) - 2] == network1
                        and key.split("_")[len(key.split("_")) - 1] == network2
                    ):  # check if network is target
                        plot_dict["Pth_heat_heatexchanger_" + network1 + "_" + network2] += res_df[key].to_numpy()
                    if (
                        "p_th_cool_hex" in key
                        and key.split("_")[len(key.split("_")) - 2] == network1
                        and key.split("_")[len(key.split("_")) - 1] == network2
                    ):  # check if network is target
                        plot_dict["Pth_cool_heatexchanger_" + network1 + "_" + network2] += res_df[key].to_numpy()

        clean_plot_dict = plot_dict.copy()
        for key in plot_dict:
            if clean_plot_dict[key].max() < 0.0001 and key not in ("CO2", "times"):
                clean_plot_dict.pop(key)

        drop_df = pd.DataFrame.from_dict(clean_plot_dict)
        output_path = (
            Path(self.base_dir)
            / "results"
            / "optimization_results"
            / self.project_title
            / f"plot_{self.variant_title}.xlsx"
        )
        drop_df.to_excel(output_path)


if __name__ == "__main__":

    def main():
        # Example project and variant, you can adjust or parse these via argparse
        project_title = "eta_production_week"
        variant_title = "three_linked_net_434"

        optimizer = MistralOptimizer(project_title, variant_title)
        optimizer.load_input_data()
        optimizer.input_data_to_pyomo_input()
        model = optimizer.setup_optimization_model()
        SolverFactory("cplex").solve(model)
        optimizer.save_results(model)
        optimizer.save_topology()
        optimizer.convert_results()

    main()
