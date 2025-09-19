"""
Class for fmu simulator in eta tqsa
"""

__author__ = ["Fabian Borst (FBo)", "Lukas Theisinger (LT)", "Michael Frank (MFr)"]
__maintainer__ = "Michael Frank (MFr)"
__email__ = "m.frank@ptw.tu-darmstadt.de"
__project__ = "MISTRAL FKZ: 03EN4098A-E "
__subject__ = "Cluster 1: Modeling"
__status__ = "Work in progress"

import json
import logging
import pickle
import shutil
from pathlib import Path

import numpy as np
import pandas as pd
from fmpy import extract, read_model_description
from fmpy.fmi2 import FMU2Slave

logger = logging.getLogger("simulator")
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)


class Simulator:
    """fmu simulator class"""

    def __init__(self, start_time, stop_time, step_size, print_time):
        """constructor

        Args:
            start_time (_float_): start time for simulation in seconds
            stop_time (_float_): stop time for simulation in seconds
            step_size (_float_): step size in seconds
            print_time (_float_): time step to be printed in terminal
        """
        self.__main_path = Path(__file__).parents[2]
        self.__start_time = start_time
        self.__stop_time = stop_time
        self.__step_size = step_size
        self.__print_time = print_time
        self.__networks = {}

    def load_fmu(self, project, variant):
        """load fmu from file

        Args:
            project (_str_): project name
            variant (_str_): variant name
        """

        def fmu_setup(
            fmu_id,
            fmu_type,
            internal_variables,
            internal_inputs,
            external_inputs,
            internal_outputs,
            external_outputs,
            parameters,
            linkage=None,
        ):
            """prepare all fmus for simulation

            Args:
                fmu_id (_string_): name of instance
                fmu_type (_string_): instance type (e.g. sink, source)
                internal_variables (_list_): port variables for flow coupling (e.g. m_flow,T)
                internal_inputs (_list_): internal inputs for coupling (e.g. T_Buffer)
                external_inputs (_list_): time-dependent input variables which are read from
                topology description (e.g. Q_demand)
                internal_outputs (_list_): internal outputs for coupling (e.g. T_Buffer)
                external_outputs (_list_): time-dependent output variables which are defined
                in topology description (e.g. results)
                parameters (_list_): model parameters
                linkage (_dict_): Dict describing component from which waste heat comes
                {network: aa,id: bb} or None

            Returns:
                _dict_: fmu with all needed information
            """

            # Read the model description, instantiate and initialize all a fmu
            fmu = {}
            fmu["id"] = fmu_id
            fmu["type"] = fmu_type
            fmu_path = self.__main_path / "backend" / "simulation" / "fmu" / (fmu_type + ".fmu")
            fmu["model_description"] = read_model_description(fmu_path)
            fmu["unzipdir"] = extract(fmu_path)
            fmu["fmu2slave"] = FMU2Slave(
                guid=fmu["model_description"].guid,
                unzipDirectory=fmu["unzipdir"],
                modelIdentifier=fmu["model_description"].coSimulation.modelIdentifier,
                instanceName=fmu_id,
            )

            # read all references
            refs = {}
            for variable in fmu["model_description"].modelVariables:
                refs[variable.name] = variable.valueReference

            # create list with all needed variables
            var_names = (
                internal_variables
                + internal_inputs
                + list(external_inputs.keys())
                + internal_outputs
                + external_outputs
                + list(parameters.keys())
            )

            # save all needed references
            fmu["refs"] = {variable: refs[variable] for variable in var_names}

            # save linkage if there is one
            fmu["linkage"] = linkage

            # save external inputs

            fmu["external_inputs"] = external_inputs

            # create output dict with empty list for needed outputs
            fmu["external_outputs"] = {key: [] for key in ["time", *var_names]}
            # set parameters
            fmu["fmu2slave"].instantiate()
            parameters = {fmu["refs"][parameter]: parameters[parameter] for parameter in list(parameters.keys())}
            fmu["fmu2slave"].setupExperiment(startTime=self.__start_time)
            fmu["fmu2slave"].setReal(list(parameters.keys()), list(parameters.values()))
            fmu["fmu2slave"].enterInitializationMode()
            fmu["fmu2slave"].exitInitializationMode()
            return fmu

        # Read xml connection descriptions
        # Convert the xml description file to a dictionary
        self.project_name = project
        self.variant_name = variant
        description_path = self.__main_path / "backend" / "results" / "topology_description"
        con_file = project + "/" + variant + ".pickle"
        with Path.open(description_path / con_file, "rb") as f:
            topology_description = pickle.load(f)

        # Iterate over every network
        for network in topology_description:
            producers = []
            consumers = []
            # iterate over every instance in network
            for physical_instance in topology_description[network]:
                if physical_instance["fmu_type"] == "source":
                    fmu = fmu_setup(
                        fmu_id=physical_instance["id"],
                        fmu_type=physical_instance["fmu_type"],
                        internal_variables=["inlet.T", "inlet.m_flow", "outlet.T", "outlet.m_flow"],
                        internal_inputs=["Q_demand"],
                        external_inputs=physical_instance["inputs"],
                        internal_outputs=[],
                        external_outputs=physical_instance["outputs"],
                        parameters=physical_instance["parameters"],
                        linkage=physical_instance["link_p_th_to"],
                    )
                    producers.append(fmu)
                elif physical_instance["fmu_type"] == "hot_utility":
                    fmu = fmu_setup(
                        fmu_id=physical_instance["id"],
                        fmu_type=physical_instance["fmu_type"],
                        internal_variables=["inlet.T", "inlet.m_flow", "outlet.T", "outlet.m_flow"],
                        internal_inputs=["T_BufferStorage"],
                        external_inputs=physical_instance["inputs"],
                        internal_outputs=[],
                        external_outputs=physical_instance["outputs"],
                        parameters=physical_instance["parameters"],
                    )
                    producers.append(fmu)
                elif physical_instance["fmu_type"] == "cold_utility":  # consumer
                    fmu = fmu_setup(
                        fmu_id=physical_instance["id"],
                        fmu_type=physical_instance["fmu_type"],
                        internal_variables=["inlet.T", "inlet.m_flow", "outlet.T", "outlet.m_flow"],
                        internal_inputs=["T_BufferStorage"],
                        external_inputs=physical_instance["inputs"],
                        internal_outputs=["P_th", "P_el"],
                        external_outputs=physical_instance["outputs"],
                        parameters=physical_instance["parameters"],
                    )
                    consumers.append(fmu)
                elif physical_instance["fmu_type"] == "sink":  # consumer
                    fmu = fmu_setup(
                        fmu_id=physical_instance["id"],
                        fmu_type=physical_instance["fmu_type"],
                        internal_variables=["inlet.T", "inlet.m_flow", "outlet.T", "outlet.m_flow"],
                        internal_inputs=[],
                        external_inputs=physical_instance["inputs"],
                        internal_outputs=[],
                        external_outputs=physical_instance["outputs"],
                        parameters=physical_instance["parameters"],
                    )
                    consumers.append(fmu)
                elif physical_instance["fmu_type"] == "buffer_storage":
                    fmu = fmu_setup(
                        fmu_id=physical_instance["id"],
                        fmu_type=physical_instance["fmu_type"],
                        internal_variables=[
                            "hot_out.T",
                            "hot_out.m_flow",
                            "cold_in.T",
                            "cold_in.m_flow",
                            "cold_out.T",
                            "cold_out.m_flow",
                            "cold_out.m_flow",
                            "hot_in.T",
                            "hot_in.m_flow",
                        ],
                        internal_inputs=[],
                        external_inputs=physical_instance["inputs"],
                        internal_outputs=["T"],
                        external_outputs=physical_instance["outputs"],
                        parameters=physical_instance["parameters"],
                    )
                    buffer_storage = fmu
                else:
                    pass
            self.__networks[network] = {
                "producers": producers,
                "consumers": consumers,
                "buffer_storage": buffer_storage,
            }

    def _initialize_result_buffers(self):
        return {}, {}, {}

    def _update_results_from_consumers(self, network, result_consumers, time):
        result_consumers[network] = []
        for consumer in self.__networks[network]["consumers"]:
            refs = consumer["refs"].values()
            res = dict(zip(consumer["refs"].keys(), consumer["fmu2slave"].getReal(refs), strict=False))
            result_consumers[network].append(res)

            consumer["external_outputs"]["time"].append(time)
            for ref in consumer["refs"]:
                consumer["external_outputs"][ref].append(res[ref])

    def _update_results_from_producers(self, network, result_producers, time):
        result_producers[network] = []
        for producer in self.__networks[network]["producers"]:
            refs = producer["refs"].values()
            res = dict(zip(producer["refs"].keys(), producer["fmu2slave"].getReal(refs), strict=False))
            result_producers[network].append(res)

            producer["external_outputs"]["time"].append(time)
            for ref in producer["refs"]:
                producer["external_outputs"][ref].append(res[ref])

    def _update_buffer_storage_inputs(self, network, result_consumers, result_producers):
        cons_res = self._couple_mass_flow(
            temperatures=[result["outlet.T"] for result in result_consumers[network]],
            mass_flows=[result["outlet.m_flow"] for result in result_consumers[network]],
        )
        prod_res = self._couple_mass_flow(
            temperatures=[result["outlet.T"] for result in result_producers[network]],
            mass_flows=[result["outlet.m_flow"] for result in result_producers[network]],
        )

        storage = self.__networks[network]["buffer_storage"]
        storage["fmu2slave"].setReal([storage["refs"]["cold_in.T"], storage["refs"]["cold_in.m_flow"]], cons_res)
        storage["fmu2slave"].setReal([storage["refs"]["hot_in.T"], storage["refs"]["hot_in.m_flow"]], prod_res)

    def _save_buffer_storage_results(self, network, result_buffer_storages, time):
        result_buffer_storages[network] = []
        storage = self.__networks[network]["buffer_storage"]
        refs = storage["refs"].values()
        res = dict(zip(storage["refs"].keys(), storage["fmu2slave"].getReal(refs), strict=False))
        result_buffer_storages[network].append(res)

        storage["external_outputs"]["time"].append(time)
        for ref in storage["refs"]:
            storage["external_outputs"][ref].append(res[ref])

    def _step_buffer_storage(self, network, time):
        """Performs simulation step for the buffer storage unit in a given network."""
        try:
            storage = self.__networks[network]["buffer_storage"]

            # Perform simulation step (inputs already set earlier)
            storage["fmu2slave"].doStep(currentCommunicationPoint=time, communicationStepSize=self.__step_size)
            return True
        except Exception as e:
            logger.error("[SIMULATION] Error during buffer storage step at t=%s: %s", time, e)
            return False

    def _step_consumers(self, network, result_buffer_storages, time):
        for consumer in self.__networks[network]["consumers"]:
            try:
                consumer["fmu2slave"].setReal(
                    [consumer["refs"][var] for var in ["inlet.T", "inlet.m_flow"]],
                    [
                        result_buffer_storages[network][0]["hot_out.T"],
                        consumer["external_outputs"]["outlet.m_flow"][-1],
                    ],
                )

                consumer["fmu2slave"].setReal(
                    [consumer["refs"][var] for var in consumer["external_inputs"]],
                    [
                        self._read_external_input(time_series=ts, sim_time=time)
                        for ts in consumer["external_inputs"].values()
                    ],
                )

                if consumer["type"] == "cold_utility":
                    consumer["fmu2slave"].setReal(
                        [consumer["refs"]["T_BufferStorage"]],
                        [result_buffer_storages[network][0]["T"]],
                    )

                consumer["fmu2slave"].doStep(currentCommunicationPoint=time, communicationStepSize=self.__step_size)
            except Exception:
                return False
        return True

    def _step_producers(self, network, result_buffer_storages, time):
        for producer in self.__networks[network]["producers"]:
            try:
                producer["fmu2slave"].setReal(
                    [producer["refs"][var] for var in ["inlet.T", "inlet.m_flow"]],
                    [
                        result_buffer_storages[network][0]["cold_out.T"],
                        producer["external_outputs"]["outlet.m_flow"][-1],
                    ],
                )

                producer["fmu2slave"].setReal(
                    [producer["refs"][var] for var in producer["external_inputs"]],
                    [
                        self._read_external_input(time_series=ts, sim_time=time)
                        for ts in producer["external_inputs"].values()
                    ],
                )

                if producer["type"] == "hot_utility":
                    producer["fmu2slave"].setReal(
                        [producer["refs"]["T_BufferStorage"]],
                        [result_buffer_storages[network][0]["T"]],
                    )

                if producer["type"] == "source" and producer.get("linkage"):
                    linked_network = producer["linkage"]["network"]
                    system_id = producer["linkage"]["id"]
                    system = next(
                        item for item in self.__networks[linked_network]["consumers"] if item["id"] == system_id
                    )
                    try:
                        thermal_power = -system["external_outputs"]["P_th"][-1] + system["external_outputs"]["P_el"][-1]
                    except IndexError:
                        thermal_power = 0

                    producer["fmu2slave"].setReal([producer["refs"]["Q_demand"]], [thermal_power])

                producer["fmu2slave"].doStep(currentCommunicationPoint=time, communicationStepSize=self.__step_size)
            except Exception as e:
                logger.warning("Simulation step failed at time %s: %s", time, e)
                return False
        return True

    def _couple_mass_flow(self, mass_flows, temperatures):
        """function for mass flow coupling and mean temperatures

        Args:
            mass_flows (_list_): list with mass flows for coupling
            temperatures (_list_): list with temperatures for coupling

        Returns:
            _list_: [mean temperature, total mass flow]
        """
        mass_flows = [0.0001 if mass_flow <= 0 else mass_flow for mass_flow in mass_flows]
        mass_flow = sum(mass_flows)
        temperature = np.dot(temperatures, mass_flows) / mass_flow
        return [temperature, mass_flow]

    def _read_external_input(self, time_series, sim_time):
        """function to read time dependent input

        Args:
            time_series (_list_): list of tuples [(time1,value1),(time2,value2)]
            time (_float_): current time
        Returns:
            _float_: value at time
        """
        for entry in time_series:
            val = entry[1]
            if entry[0] > sim_time:
                break
        return val

    def simulate_model(self):
        """simulates coupled fmu models"""
        time = self.__start_time
        self.__time = [0]
        while time < self.__stop_time:
            result_consumers, result_producers, result_buffer_storages = self._initialize_result_buffers()

            for network in self.__networks:
                self._update_results_from_consumers(network, result_consumers, time)
                self._update_results_from_producers(network, result_producers, time)
                self._update_buffer_storage_inputs(network, result_consumers, result_producers)

                if not self._step_buffer_storage(network, time):
                    return

                self._save_buffer_storage_results(network, result_buffer_storages, time)

                if not self._step_consumers(network, result_buffer_storages, time):
                    return

                if not self._step_producers(network, result_buffer_storages, time):
                    return

            time += self.__step_size
            self.__time.append(time)

    def shutdown_simulation(self):
        """
        simulation shutdown
        """
        for network in self.__networks.values():
            for consumer in network["consumers"]:
                consumer["fmu2slave"].terminate()
                consumer["fmu2slave"].freeInstance()
                shutil.rmtree(consumer["unzipdir"], ignore_errors=True)
            for producer in network["producers"]:
                producer["fmu2slave"].terminate()
                producer["fmu2slave"].freeInstance()
                shutil.rmtree(producer["unzipdir"], ignore_errors=True)
            network["buffer_storage"]["fmu2slave"].terminate()
            network["buffer_storage"]["fmu2slave"].freeInstance()
            shutil.rmtree(network["buffer_storage"]["unzipdir"], ignore_errors=True)

    def _export_networks(self, var_names, results_con):
        for network in self.__networks:
            # consumers
            for consumer in self.__networks[network]["consumers"]:
                for var_name in var_names:
                    if var_name in consumer["external_outputs"]:
                        if "Hp" in consumer["id"] and "P_el" not in var_name:
                            results_con[var_name + "_cool_" + consumer["id"] + "_" + network] = consumer[
                                "external_outputs"
                            ][var_name]
                        if "Hp" in consumer["id"] and "P_el" in var_name:
                            results_con[var_name + consumer["id"] + "_" + network] = consumer["external_outputs"][
                                var_name
                            ]
                        elif "Hex" in consumer["id"]:
                            results_con[var_name + "_cool_" + consumer["id"] + "_" + network] = consumer[
                                "external_outputs"
                            ][var_name]
                        else:
                            results_con[var_name + "_" + consumer["id"]] = consumer["external_outputs"][var_name]

    def _export_producers(self, var_names, results_prod, network):
        for producer in self.__networks[network]["producers"]:
            for var_name in var_names:
                if var_name in producer["external_outputs"]:
                    if "Hp" in producer["id"] or "Hex" in producer["id"]:
                        results_prod[var_name + "_heat_" + producer["id"] + "_" + network] = producer[
                            "external_outputs"
                        ][var_name]
                    else:
                        results_prod[var_name + "_" + producer["id"]] = producer["external_outputs"][var_name]

    def _export_buffer_storage(self, var_names, network):
        storage = self.__networks[network]["buffer_storage"]["external_outputs"]
        return {
            var_name + "_buffer_storage_" + network: storage[var_name] for var_name in var_names if var_name in storage
        }

    def export_results(self):
        """
        export results as csv file
        """
        result_path = self.__main_path / "backend" / "results" / "simulation_results" / self.project_name
        output_file = result_path / f"{self.variant_name}.xlsx"

        # write results to excel
        writer = pd.ExcelWriter(output_file)
        var_names = ["T_in", "T_out", "P_th", "P_el", "P_gs", "T_upper", "T_mid", "T_lower"]

        results = {"idx": range(0, len(self.__time)), "times": self.__time}

        results_con = {}
        results_prod = {}
        results_storage = {}

        self._export_networks(var_names, results_con)

        # export producers and storage per network
        for network in self.__networks:
            self._export_producers(var_names, results_prod, network)
            results_storage.update(self._export_buffer_storage(var_names, network))

        # combine all
        results.update(results_con)
        results.update(results_prod)
        results.update(results_storage)

        res_df_export = pd.DataFrame.from_dict(results, orient="index").transpose()
        res_df_export.to_excel(writer, sheet_name="Sheet1", index=False)
        writer.close()

    def _add_co2_contributions(self, df, spec_co2_el, spec_co2_gas):
        for col in df.columns:
            if "P_gs" in col:
                df["CO2"] += (df[col] / 1000) * spec_co2_gas
            elif "P_el_Cold" in col:
                df["CO2"] += (df[col] / 1000) * spec_co2_el
            elif "P_el_Hot" in col:
                df["CO2"] -= (df[col] / 1000) * spec_co2_el
            elif "P_el" in col and "heatpump" in col:
                df["CO2"] += (df[col] / 1000) * spec_co2_el

    def convert_results(self):
        xlsx_path = (
            self.__main_path
            / "backend"
            / "results"
            / "simulation_results"
            / self.project_name
            / f"{self.variant_name}.xlsx"
        )
        res_df = pd.read_excel(xlsx_path)
        # delete idx column
        res_df = res_df.drop("idx", axis=1)
        # calculate rolling mean
        for key in res_df:
            if "T_in" in key or "T_out" in key or "T_upper" in key or "T_lower" in key:
                res_df = res_df.drop(key, axis=1)
            elif "times" in key:
                # Skip time columns
                pass

        rename_map = {
            "P_th_Hot_util": "Pth_heat_utility",
            "P_th_Cold_util": "Pth_cool_utility",
            "P_th_heat_Hp": "Pth_heat_heatpump",
            "P_th_cool_Hp": "Pth_cool_heatpump",
            "P_el_Hp": "P_el_heatpump",
            "P_th_heat_Hex": "Pth_heat_heatexchanger",
            "P_th_cool_Hex": "Pth_cool_heatexchanger",
        }

        for old, new in rename_map.items():
            res_df.rename(columns={col: col.replace(old, new) for col in res_df.columns if old in col})

        for key in res_df:
            if key != "times":
                res_df[key] = res_df[key].rolling(900).mean()
        # select only every 900th row
        res_df = res_df.iloc[::900, :]
        # get co2 values
        json_path = Path(self.__main_path) / "backend" / "input" / self.project_name / f"{self.variant_name}.json"
        with json_path.open() as json_file:
            config_dict = json.load(json_file)
        spec_co2_el = config_dict["spec_co2_el"]
        spec_co2_gas = config_dict["spec_co2_gas"]

        res_df.insert(0, "CO2", 0)
        res_df.fillna(0)

        self._add_co2_contributions(res_df, spec_co2_el, spec_co2_gas)

        output_path = Path.cwd() / f"plot_{self.variant_name}.xlsx"
        res_df.to_excel(output_path)


if __name__ == "__main__":

    def main():
        # Customize these based on your test case
        project = "eta_production_week"
        variant = "two_sep_net_434"

        simulator = Simulator(start_time=0, stop_time=604800, step_size=900, print_time=86400)

        simulator.load_fmu(project, variant)

        simulator.simulate_model()

        simulator.export_results()

        simulator.convert_results()

        simulator.shutdown_simulation()

    main()
