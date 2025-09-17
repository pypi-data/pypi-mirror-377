import datetime as dt
from pathlib import Path
from c_module.user_io.default_parameters import user_input
from c_module.parameters.defines import ParamNames

current_dt = dt.datetime.now().strftime("%Y%m%dT%H-%M-%S")


def extract_scenarios(input_folder, output_folder, sc_num):
    """
    Extract scenario names from Excel files in a folder and merge them with 'DataContainer_Sc_' prefix.
    :param input_folder: Path to the folder containing scenario files.
    :param output_folder: Path to the folder where the output files will be stored.
    :param sc_num: Number of scenarios to extract.
    :return: List of merged scenario names.
    """
    scenarios = []
    if sc_num is None:
        folder_path = Path(input_folder)
        for file in folder_path.glob("*.xlsx"):
            scenario_name = f"DataContainer_Sc_{file.stem}.pkl"
            scenario_path = Path(output_folder) / Path(scenario_name)
            scenarios.append(scenario_path)

    else:
        folder_path = Path(output_folder)
        files = list(folder_path.glob("*.pkl"))
        files.sort(key=lambda f: f.stat().st_mtime)
        files = files[-user_input[ParamNames.sc_num.value]:]
        scenarios = files

    return scenarios


def cmodule_is_standalone():
    """
    Check if cmodule is standalone or not, covering if the code is run as the main program, covering CLI, script, IDE,
     and entry point runs.
    :return: Bool if cmodule is standalone or not.
    """
    import __main__
    import sys

    if getattr(__main__, "__file__", None):
        main_file = Path(__main__.__file__).resolve()
        package_root = Path(__file__).resolve().parents[1]

        if package_root in main_file.parents:
            return True

        if "pytest" in sys.modules and Path.cwd().resolve() == package_root.parent:
            return True

        if any("unittest" in mod for mod in sys.modules):
            return True

    return False


PACKAGEDIR = Path(__file__).parent.parent.absolute()
TIMBADIR = Path(__file__).parent.parent.parent.parent.parent.parent.absolute()
TIMBADIR_INPUT = TIMBADIR / Path("TiMBA") / Path("data") / Path("input") / Path("01_Input_Files")
TIMBADIR_OUTPUT = TIMBADIR / Path("TiMBA") / Path("data") / Path("output")
INPUT_FOLDER = PACKAGEDIR / Path("data") / Path("input")

if user_input[ParamNames.add_on_activated.value] or not cmodule_is_standalone():
    # output paths for add-on c-module
    OUTPUT_FOLDER = TIMBADIR_OUTPUT

else:
    # output paths for standalone c-module
    OUTPUT_FOLDER = PACKAGEDIR / Path("data") / Path("output")


# Official statistics from the Food and Agriculture Organization
FAO_DIR = INPUT_FOLDER / Path("historical_data")
FAOSTAT_URL = "https://bulks-faostat.fao.org/production/Forestry_E_All_Data.zip"
FAOSTAT_DATA = INPUT_FOLDER / Path("historical_data") / Path("Forestry_E_All_Data_NOFLAG")
FRA_URL = "https://fra-data.fao.org/api/file/bulk-download?assessmentName=fra&cycleName=2020&countryIso=WO"
FRA_DATA = INPUT_FOLDER / Path("historical_data") / Path(f"FRA_Years_All_Data")

# additional information
ADD_INFO_FOLDER = PACKAGEDIR / INPUT_FOLDER / Path("additional_information")
ADD_INFO_CARBON_PATH = ADD_INFO_FOLDER / Path("carbon_additional_information")
PKL_ADD_INFO_CARBON_PATH = ADD_INFO_FOLDER / Path("carbon_additional_information")
ADD_INFO_COUNTRY = ADD_INFO_FOLDER / Path("country_data")
PKL_ADD_INFO_START_YEAR = ADD_INFO_FOLDER / Path("hist_hwp_carbon_start_year")

LOGGING_OUTPUT_FOLDER = OUTPUT_FOLDER
