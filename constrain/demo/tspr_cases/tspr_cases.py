"""The goal of this demo cases is to showcase how verification cases can be semi-automatically created for building energy simulation timeseries.
"""

import matplotlib.pyplot as plt
import json, glob

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

import constrain as cs
from constrain.workflowsteps import *
from constrain.library import *
from constrain.libcases import *

# Input/Output params
# Change the following according to your system configuration
energy_plus_simulation = False
energy_plus_path = "/Applications/EnergyPlus-25-1-0/energyplus"
energy_plus_idd = "../../../resources/Energy+V25_1_0.idd"
energy_plus_weather_file = (
    "/Applications/EnergyPlus-25-1-0/WeatherData/USA_CO_Golden-NREL.724666_TMY3.epw"
)
energy_plus_output_file_name = "eplusout.csv"

# Verification cases intialization
verification_case_list = {"sat_reset": "SupplyAirTempReset", "chw_reset": "CHWReset"}
verification_case_file = "./tspr_verification_cases.json"
cases = {}
cases["cases"] = []
case_counter = 0
for idf in glob.glob("./sat_reset/*.idf"):
    if not "injected" in idf:
        sat_case = {}
        sat_case["no"] = case_counter

        idf_json = json.load(open(idf.replace(".idf", ".epJSON")))

        # Retrieve supply inlet node name of first airloop
        airloops = idf_json["AirLoopHVAC"]
        airloop = list(airloops.keys())[0]
        sat_node = airloops[airloop]["supply_side_outlet_node_names"]
        if sat_node in idf_json["NodeList"]:
            sat_node = idf_json["NodeList"][sat_node]["nodes"][0]["node_name"]
        # Retrieve zone design cooling temperature
        schs = idf_json["Schedule:Day:Interval"]
        sch = [
            s for s in list(schs.keys()) if "_Cooling_Schedule_Summer_Design_Day" in s
        ][0]
        tz_coo = 99
        for d in schs[sch]["data"]:
            if d["value_until_time"] < tz_coo:
                tz_coo = d["value_until_time"]
        # Define simulation IO
        sat_case["run_simulation"] = energy_plus_simulation
        sat_case["simulation_IO"] = {
            "idf": "{}".format(idf.split("\\")[-1]),
            "idd": f"{energy_plus_idd}",
            "weather": f"{energy_plus_weather_file}",
            "output": f"{energy_plus_output_file_name}",
            "ep_path": f"{energy_plus_path}",
        }
        sat_case["expected_result"] = "pass"
        sat_case["verification_class"] = verification_case_list["sat_reset"]
        sat_case["datapoints_source"] = {
            "idf_output_variables": {
                "temperature_air_supply_setpoint": {
                    "subject": f"{sat_node}",
                    "variable": "System Node Setpoint Temperature",
                    "frequency": "detailed",
                }
            },
            "parameters": {"temperature_air_zone_design_cool_setpoint": tz_coo},
        }
        cases["cases"].append(sat_case)
        case_counter += 1
json.dump(cases, open("./tspr_verification_cases.json", "w"), indent=4)

for idf in glob.glob("./chw_reset/*.idf"):
    if not "injected" in idf:
        chw_case = {}
        chw_case["no"] = case_counter

        idf_json = json.load(open(idf.replace(".idf", ".epJSON")))

        # Retrieve supply inlet node name of first airloop
        plantloops = idf_json["PlantLoop"]
        chloop = [p for p in plantloops if "chiller" in p.lower()][0]
        chw_node = plantloops[chloop]["loop_temperature_setpoint_node_name"]

        # Get chiller name
        chillers = idf_json["Chiller:Electric:EIR"]
        chiller = list(chillers.keys())[0]

        # Retrieve zone design cooling temperature
        spm_rt_oa = idf_json["SetpointManager:OutdoorAirReset"]
        for s, v in spm_rt_oa.items():
            if chw_node in v["setpoint_node_or_nodelist_name"]:
                t_oa_max = v["outdoor_high_temperature"]
                t_oa_min = v["outdoor_low_temperature"]
                t_chw_max_st = v["setpoint_at_outdoor_low_temperature"]
                t_chw_min_st = v["setpoint_at_outdoor_high_temperature"]
        # Define simulation IO
        chw_case["run_simulation"] = energy_plus_simulation
        chw_case["simulation_IO"] = {
            "idf": "{}".format(idf.split("\\")[-1]),
            "idd": f"{energy_plus_idd}",
            "weather": f"{energy_plus_weather_file}",
            "output": f"{energy_plus_output_file_name}",
            "ep_path": f"{energy_plus_path}",
        }
        chw_case["expected_result"] = "pass"
        chw_case["verification_class"] = verification_case_list["chw_reset"]
        chw_case["datapoints_source"] = {
            "idf_output_variables": {
                "temperature_air_outdoor": {
                    "subject": "Environment",
                    "variable": "Site Outdoor Air Drybulb Temperature",
                    "frequency": "TimeStep",
                },
                "temperature_water_chilled": {
                    "subject": f"{chw_node}",
                    "variable": "System Node Setpoint Temperature",
                    "frequency": "TimeStep",
                },
                "flow_mass_water_chilled": {
                    "subject": f"{chiller}",
                    "variable": "Chiller Evaporator Mass Flow Rate",
                    "frequency": "TimeStep",
                },
            },
            "parameters": {
                "temperature_air_outdoor_max": t_oa_max,
                "temperature_air_outdoor_min": t_oa_min,
                "temperature_water_chilled_setpoint_max": t_chw_max_st,
                "temperature_water_chilled_setpoint_min": t_chw_min_st,
            },
        }
        cases["cases"].append(chw_case)
        case_counter += 1
json.dump(cases, open(verification_case_file, "w"), indent=4)

# Loading the verification cases
cases = cs.api.VerificationCase(json_case_path=verification_case_file)
assert cases.validate(), "Verification case file is not valid."

# Configure verification
verif = cs.api.Verification(verifications=cases)
verif.configure(
    output_path="./",
    lib_items_path="../../schema/library.json",
    plot_option="all-expand",
    time_series_csv_export_name_prefix="verifs_out",
    fig_size=(10, 5),
    num_threads=1,
)

# Run verification and create reports
verif.run()
reporting = cs.api.Reporting(
    verification_json="./*_md.json",
    result_md_name="report_summary.md",
    report_format="markdown",
)
reporting.report_multiple_cases()
