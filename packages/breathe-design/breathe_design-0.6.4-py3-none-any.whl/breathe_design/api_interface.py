import logging
from typing import Literal, Union, List
import requests
import tempfile
import pandas as pd
from .utilities import _transform_key
from .results import SingleSimulationResults, BatchSimulationResults
from concurrent.futures import ThreadPoolExecutor
from .device_flow_auth import device_auth
from packaging.version import Version
import json
from .api_utils import (
    BreatheException,
    make_design_names_map,
    map_design_names__human_to_machine,
    map_fields_in_place,
    convert_none_strings_to_none,
)
from .parameter_validator import parameter_validator
import os
import dotenv
from .__init__ import __version__
import re

dotenv.load_dotenv()

_logger = logging.getLogger(__name__)

temp_dir = tempfile.mkdtemp(prefix="myapp_")


class BreatheDesignModel:
    """
    A class for interacting with the Breathe Design API.
    """

    def __init__(self):
        self._auth = device_auth
        if "API_URL" in os.environ:
            self._api_url = os.environ["API_URL"]
            _logger.info(f"API_URL set from environment to {self._api_url}")
        else:
            self._api_url = (
                "https://breathe-platform-backend-service-prod.azurewebsites.net/api/v1"
            )

    def ensure_logged_in(self):
        """
        Checks if a valid token is available and refreshes it if necessary.
        """
        device_auth.get_token()

    def _make_api_call(
        self, verb: Literal["POST", "GET"], endpoint: str, payload: dict | None
    ) -> dict:
        token = device_auth.get_token()
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {token}",
        }
        if payload is not None:
            headers["Content-Type"] = "application/json"

        try:
            if verb == "POST":
                func = requests.post
            elif verb == "GET":
                func = requests.get
            else:
                raise Exception(f"Unsupported method: {verb} for {endpoint}")
            response = func(
                f"{self._api_url}{endpoint}",
                json=payload,
                headers=headers,
            )
            if response.status_code == 200:
                return response.json()
            else:
                raise BreatheException(f"Error {response.status_code}: {response.text}")
        except Exception as e:
            raise BreatheException(f"Error {e}")

    def _make_model_api_call(self, endpoint: str, payload: dict | None) -> dict:
        full_endpoint = f"/model-services/pbm/{endpoint}"
        return self._make_api_call("POST", full_endpoint, payload)

    def get_service_version(self) -> Version:
        """Get the version number of the API

        Returns:
            _type_: _description_
        """
        response = self._make_model_api_call("get_version", payload={})

        version_str = response["versionStr"]
        return Version(version_str)

    def get_batteries(self) -> list[str]:
        """
        Gets a list of all batteries in your library.

        Returns:
            (list[str]): list of the available battery models.  Use these strings in subsequent functions for the "base_battery" argument.
        """
        _logger.info("Getting batteries...")
        batteries = self._make_api_call("GET", "/cells/", None)

        # unpack the ID and model name
        return [b["pbm_model_name"] for b in batteries]

    def get_battery_format(self, base_battery: str) -> dict:
        """
        Gets the battery format for a base battery. These are the form factor and cell casing parameters available for change in the api.

        Args:
            base_battery (str): The base battery model for the battery format.

        Returns:
            (dict): containing the battery format.
        """
        _logger.info(f"Getting battery format for {base_battery}...")
        return self._make_model_api_call(
            "get_battery_format", {"base_battery": base_battery}
        )

    def get_updated_format(self, base_battery: str, **kwargs) -> dict:
        """
        Gets the battery format for a base battery and updates it with the additional keywords. These are the form factor and cell casing parameters available for change in the api.
        Args:
            base_battery (str): The base battery model for the battery format.

        Returns:
            (dict): containing the battery format.
        """
        _logger.info(f"Getting battery format for {base_battery}...")
        format = self._make_model_api_call(
            "get_battery_format", {"base_battery": base_battery}
        )
        for key in kwargs.keys():
            if key in format or key == "name":
                format[key] = kwargs[key]
            else:
                raise BreatheException(f"Key {key} not found in the battery format.")
        return format

    def get_active_materials(self):
        """
        Gets a list of all acive materials.

        Returns:
            (pandas.Dataframe): containing the battery active materials.
        """
        _logger.info("Getting active materials...")
        am = self._make_model_api_call("get_active_materials", {})
        return pd.DataFrame(am)

    def get_design_parameters(self, base_battery: str):
        """
        Gets the design parameters for a base battery.

        Args:
            base_battery (str): The base battery model for the design parameters.

        Returns:
            (dict): containing the design parameters.
        """
        _logger.info(f"Getting design parameters for {base_battery}...")
        return self._make_model_api_call(
            "get_design_parameters", {"base_battery": base_battery}
        )

    def download_designs(
        self,
        base_battery: str,
        designs: list[dict] = [],
        formats: list[dict] = [],
        output_tag: str = "",
        folder: str = ".",
    ):
        """Send the design parameters for a given battery to the API, and get the resulting design, to be used with the Simulink blocks.

        Args:
            base_battery (str): The base battery to use to generate the design
            designs (list[str], optional): The designs for the simulation.
            formats (list[str], optional): The formats for the simulation.
            output_tag (str): A tag to be included in the metadata description.
            folder (str): The folder where design files will be saved. Defaults to current directory.
        Raises:
            BreatheException: _description_
        """
        import glob

        map_h2m, map_m2h = make_design_names_map(designs)
        designs_mapped = map_design_names__human_to_machine(designs, map_h2m)
        design_dict_mapped = self._make_model_api_call(
            "download_design",
            {
                "base_battery": base_battery,
                "designs": designs_mapped,
                "formats": formats,
            },
        )

        # undo design name mapping
        design_dict = {}
        for k, v in design_dict_mapped.items():
            key_human = map_m2h.get(k, k)
            design_dict[key_human] = v
            design_dict[key_human]["Meta"]["cellName"] = key_human

        # Ensure folder exists
        os.makedirs(folder, exist_ok=True)

        # Find any existing files in the provided directory (to avoid trying to save with the same name and overwriting)
        existing_files = glob.glob(os.path.join(folder, "BMJN_*.json"))
        existing_numbers = set()
        pattern = re.compile(r"BMJN_(\d+)\.json$")
        for file_path in existing_files:
            filename = os.path.basename(file_path)
            match = pattern.match(filename)
            if match:
                try:
                    number = int(match.group(1))
                    existing_numbers.add(number)
                except ValueError:
                    continue

        # Find the next available number
        next_number = 0
        while next_number in existing_numbers:
            next_number += 1

        design_names = design_dict.keys()

        # Prepare metadata for description
        metadata_items = [
            f"breathe_design version: {__version__}",
            f"base_battery: {base_battery}",
        ]
        if output_tag:
            metadata_items.append(f"output_tag: {output_tag}")
        if formats:
            format_names = [fmt.get("name", "unnamed_format") for fmt in formats]
            metadata_items.append(f"formats: {', '.join(format_names)}")

        for i, design_name in enumerate(design_names):
            # Use BMJN_XXXX naming convention
            filename = f"BMJN_{next_number + i:04d}.json"
            filepath = os.path.join(folder, filename)

            # Add metadata to the design
            design_data = design_dict[design_name].copy()
            if "Meta" not in design_data:
                design_data["Meta"] = {}
            if "description" not in design_data["Meta"]:
                design_data["Meta"]["description"] = []

            # Add the metadata items to description
            for item in metadata_items:
                if item not in design_data["Meta"]["description"]:
                    design_data["Meta"]["description"].append(item)

            with open(filepath, "w") as f:
                json.dump(design_data, f)

    def get_ocv(self, base_battery: str) -> pd.DataFrame:
        """
        Gets the OCV summary table for a base battery.

        Args:
            base_battery (str): The base battery model for the design parameters.

        Returns:
            (pandas.DataFrame): containing the OCV summary table.
        """
        _logger.info(f"Getting OCV for {base_battery}...")
        ocv_data = self._make_model_api_call("get_ocv", {"base_battery": base_battery})

        ocv_df = pd.DataFrame(ocv_data)
        return ocv_df

    def get_aged_ocv(
        self,
        base_battery: str,
        LAMPE: float = 0.0,
        LAMNE: float = 0.0,
        LLI: float = 0.0,
    ) -> pd.DataFrame:
        """
        Gets the OCV summary table for a base battery.

        Args:
            base_battery (str): The base battery model for the design parameters.
            LAMPE (float, optional): The electrolyte loss at positive electrode (PE) side.
            LAMNE (float, optional): The electrolyte loss at negative electrode (NE) side.
            LLI (float, optional): The loss of lithium inventory.

        Returns:
            (pandas.DataFrame): containing the OCV summary table.
        """
        _logger.info(f"Getting aged OCV for {base_battery}...")
        ocv_data = self._make_model_api_call(
            "get_aged_ocv",
            {"base_battery": base_battery, "LAMPE": LAMPE, "LAMNE": LAMNE, "LLI": LLI},
        )

        ocv_df = pd.DataFrame(ocv_data)
        return ocv_df

    def _format_kpis(self, results: dict) -> pd.DataFrame:
        kpis = results["KPIs"]
        kpi_names = [_transform_key(key) for key in results["KPInames"]]
        results_df = pd.DataFrame(kpis)
        # Add KPI names as a column to the DataFrame
        results_df["KPI"] = kpi_names
        results_df = results_df[
            ["KPI"] + [col for col in results_df.columns if col != "KPI"]
        ]
        return results_df.set_index("KPI")

    def get_eqm_kpis(
        self, base_battery: str, designs: list[dict] = [], formats: list[dict] = []
    ) -> "SingleSimulationResults":
        """
        Gets the equilibrium kpis for a given base battery, designs, and initial conditions.

        Args:
            base_battery (str): The base battery model for the simulation.
            designs (list[dict], optional): The designs for the simulation.
            formats (list[dict], optional): The battery formats for the simulation.

        Returns:
            (SingleSimulationResults): A results handler object containing the equilibrium KPIs.
                Use the plot_sensitivities() method to generate sensitivity plots.
        """
        _logger.info(f"Getting equilibrium kpis for {base_battery}...")
        map_h2m, map_m2h = make_design_names_map(designs)
        designs_mapped = map_design_names__human_to_machine(designs, map_h2m)
        results = self._make_model_api_call(
            "run_sim",
            {
                "base_battery": base_battery,
                "designs": designs_mapped,
                "formats": formats,
            },
        )

        # unmap the KPIs
        map_fields_in_place(results, "KPIs", map_m2h)

        # Add input parameters to the result for easy access
        results["input_parameters"] = {
            "base_battery": base_battery,
            "designs": designs,
            "formats": formats,
        }

        return SingleSimulationResults(results)

    def run_sim(
        self,
        base_battery: str,
        cycler: dict,
        designs: list[dict] = [],
        formats: list[dict] = [],
        initialSoC: Union[int, float, List[Union[int, float]]] = 0.5,
        initialTemperature_degC: Union[int, float, List[Union[int, float]]] = 25.0,
        ambientTemperature_degC: Union[int, float, List[Union[int, float]]] = 25.0,
    ) -> Union["SingleSimulationResults", "BatchSimulationResults"]:
        """
        Runs a simulation for a given base battery, cycler, designs, and initial conditions.

        Args:
            base_battery (str): The base battery model for the simulation.
            cycler (dict): The cycler parameters for the simulation.
            designs (list[dict], optional): The design parameters for the simulation.
            formats (list[dict], optional): The battery formats for the simulation.
            initialSoC (int | float | list[int | float], optional): The initial state of charge for the simulation.
                If a single value is provided, it will be used for all simulations.
                If a list of values is provided, multiple simulations will be run with each value.
            initialTemperature_degC (int | float | list[int | float], optional): The initial temperature for the simulation in degC.
                If a single value is provided, it will be used for all simulations.
                If a list of values is provided, multiple simulations will be run with each value.
            ambientTemperature_degC (int | float | list[int | float], optional): The ambient temperature for the simulation in degC.
                If a single value is provided, it will be used for all simulations.
                If a list of values is provided, multiple simulations will be run with each value.

        Returns:
            (SimulationResults): A results handler object containing the simulation results.
                This automatically handles both single and batch simulations.
        """
        # Validate and format design parameters
        validated_designs = parameter_validator.validate_and_format_designs(designs)

        # Validate and format format parameters
        validated_formats = parameter_validator.validate_and_format_formats(formats)

        # map the designs to machine names
        map_h2m, map_m2h = make_design_names_map(validated_designs)
        designs_mapped = map_design_names__human_to_machine(validated_designs, map_h2m)

        if (
            isinstance(initialSoC, (int, float))
            and isinstance(initialTemperature_degC, (int, float))
            and isinstance(ambientTemperature_degC, (int, float))
        ):
            # Single value for initialSoC and initialTemperature_degC
            payload = {
                "base_battery": base_battery,
                "cycler": cycler,
                "designs": designs_mapped,
                "formats": validated_formats,
                "initial_conditions": {
                    "socCell_0": initialSoC,
                    "initialTemperature_degC": initialTemperature_degC,
                    "ambientTemperature_degC": ambientTemperature_degC,
                },
            }

            result = self._make_model_api_call("run_sim", payload)

            # Convert "none" strings to Python None in dynamic data
            if "dynamicData" in result:
                result["dynamicData"] = convert_none_strings_to_none(
                    result["dynamicData"]
                )

            map_fields_in_place(result, "KPIs", map_m2h)
            map_fields_in_place(result, "dynamicData", map_m2h)

            # Add input parameters to the result for easy access
            result["input_parameters"] = {
                "base_battery": base_battery,
                "cycler": cycler,
                "designs": designs,
                "initialSoC": initialSoC,
                "initialTemperature_degC": initialTemperature_degC,
                "ambientTemperature_degC": ambientTemperature_degC,
            }

            return SingleSimulationResults(result)
        else:
            # make sure we are logged in first.  We need to do this because we are about to spawn multiple
            # threads, and if we do that when we are logged out, each thread will independencly try to log back in.
            self.ensure_logged_in()

            initialSoCs = (
                [initialSoC] if not isinstance(initialSoC, list) else initialSoC
            )
            initialTemperature_degC = (
                [initialTemperature_degC]
                if not isinstance(initialTemperature_degC, list)
                else initialTemperature_degC
            )
            ambientTemperature_degC = (
                [ambientTemperature_degC]
                if not isinstance(ambientTemperature_degC, list)
                else ambientTemperature_degC
            )
            max_workers = min(4, len(initialSoCs) * len(initialTemperature_degC))
            results = []
            all_payloads = [
                {
                    "base_battery": base_battery,
                    "cycler": cycler,
                    "designs": designs_mapped,
                    "formats": validated_formats,
                    "initial_conditions": {
                        "socCell_0": isc,
                        "initialTemperature_degC": itmp,
                        "ambientTemperature_degC": atmp,
                    },
                }
                for isc in initialSoCs
                for itmp in initialTemperature_degC
                for atmp in ambientTemperature_degC
            ]

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                for i, result in enumerate(
                    executor.map(
                        self._make_model_api_call,
                        ["run_sim"] * len(all_payloads),
                        all_payloads,
                    )
                ):
                    if result is None:
                        raise BreatheException(
                            f"Simulation run for conditions {all_payloads[i]} failed!"
                        )

                    # Convert "none" strings to Python None in dynamic data
                    if "dynamicData" in result:
                        result["dynamicData"] = convert_none_strings_to_none(
                            result["dynamicData"]
                        )

                    map_fields_in_place(result, "KPIs", map_m2h)
                    map_fields_in_place(result, "dynamicData", map_m2h)

                    # Add input parameters to each result for easy access
                    result["input_parameters"] = {
                        "base_battery": base_battery,
                        "cycler": cycler,
                        "designs": designs,
                        "initialSoC": all_payloads[i]["initial_conditions"][
                            "socCell_0"
                        ],
                        "initialTemperature_degC": all_payloads[i][
                            "initial_conditions"
                        ]["initialTemperature_degC"],
                        "ambientTemperature_degC": all_payloads[i][
                            "initial_conditions"
                        ]["ambientTemperature_degC"],
                    }

                    results.append(result)

            return BatchSimulationResults(results)


api_interface = BreatheDesignModel()
