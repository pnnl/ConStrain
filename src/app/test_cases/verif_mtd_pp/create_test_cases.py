# Import auxiliary packages
import matplotlib.pyplot as plt
import json, six, glob, os, sys

sys.path.insert(0, "../../src")

# Import ANIMATE
from workflowsteps import *
from library import *
from libcases import *
from datetimeep import DateTimeEP
from eppy.modeleditor import IDF

# IDF.setiddname("C:/EnergyPlusV9-0-1/Energy+.idd")
IDF.setiddname("../../resources/Energy+V9_0_1.idd")


def chwreset(idf, idf_f, id, cases):
    # Get SP node name
    plantloops = idf.idfobjects["PlantLoop".upper()]
    chwloops = [p for p in plantloops if "cool" in p.Name.lower()]
    if len(chwloops):
        print(
            "Adding CHWReset verification items for {}".format(
                idf_f.split("/")[-1].replace(".idf", "")
            )
        )

        chw_node = chwloops[0].Loop_Temperature_Setpoint_Node_Name

        # Get chiller name
        air_cooled_chillers = idf.idfobjects["Chiller:Electric:EIR".upper()]
        water_cooled_chillers = idf.idfobjects[
            "Chiller:Electric:REformulatedEIR".upper()
        ]
        if len(air_cooled_chillers) > 0:
            chiller_name = air_cooled_chillers[0].Name
        else:
            chiller_name = water_cooled_chillers[0].Name

        # CHW reset settings
        t_oa_max = 21.11
        t_oa_min = 12.78
        t_chw_max_st = 8.89
        t_chw_min_st = 6.7

        chw_case = {}
        chw_case["no"] = str(id)

        # Define simulation IO
        chw_case["run_simulation"] = True
        chw_case["simulation_IO"] = {
            "idf": "../test_cases/verif_mtd_pp/idfs/{}".format(idf_f.split("/")[-1]),
            "idd": "../resources/Energy+V9_0_1.idd",
            "weather": "../weather/USA_GA_Atlanta-Hartsfield.Jackson.Intl.AP.722190_TMY3.epw",
            "output": "eplusout.csv",
            "ep_path": "C:\EnergyPlusV9-0-1\energyplus.exe",
        }
        chw_case["expected_result"] = "pass"
        chw_case["verification_class"] = "CHWReset"
        chw_case["datapoints_source"] = {
            "idf_output_variables": {
                "T_oa_db": {
                    "subject": "Environment",
                    "variable": "Site Outdoor Air Drybulb Temperature",
                    "frequency": "Detailed",
                },
                "T_chw": {
                    "subject": f"{chw_node}",
                    "variable": "System Node Setpoint Temperature",
                    "frequency": "Detailed",
                },
                "m_chw": {
                    "subject": f"{chiller_name}",
                    "variable": "Chiller Evaporator Mass Flow Rate",
                    "frequency": "Detailed",
                },
            },
            "parameters": {
                "T_oa_max": t_oa_max,
                "T_oa_min": t_oa_min,
                "T_chw_max_st": t_chw_max_st,
                "T_chw_min_st": t_chw_min_st,
            },
        }
        cases["cases"].append(chw_case)
        id += 1
    return cases, id


def hwreset(idf, idf_f, id, cases):
    # Get SP node name
    plantloops = idf.idfobjects["PlantLoop".upper()]
    hwloops = [p for p in plantloops if "heat" in p.Name.lower()]
    if len(hwloops):
        print(
            "Adding HWReset verification items for {}".format(
                idf_f.split("/")[-1].replace(".idf", "")
            )
        )

        hw_node = hwloops[0].Loop_Temperature_Setpoint_Node_Name

        # Get boiler name
        boiler_name = idf.idfobjects["Boiler:HotWater".upper()][0].Name

        # CHW reset settings
        t_oa_max = 10
        t_oa_min = -6.666667
        t_hw_max_st = 82.2
        t_hw_min_st = 79.4

        hw_case = {}
        hw_case["no"] = str(id)

        # Define simulation IO
        hw_case["run_simulation"] = True
        hw_case["simulation_IO"] = {
            "idf": "../test_cases/verif_mtd_pp/idfs/{}".format(idf_f.split("/")[-1]),
            "idd": "../resources/Energy+V9_0_1.idd",
            "weather": "../weather/USA_GA_Atlanta-Hartsfield.Jackson.Intl.AP.722190_TMY3.epw",
            "output": "eplusout.csv",
            "ep_path": "C:\EnergyPlusV9-0-1\energyplus.exe",
        }
        hw_case["expected_result"] = "pass"
        hw_case["verification_class"] = "HWReset"
        hw_case["datapoints_source"] = {
            "idf_output_variables": {
                "T_oa_db": {
                    "subject": "Environment",
                    "variable": "Site Outdoor Air Drybulb Temperature",
                    "frequency": "Detailed",
                },
                "T_hw": {
                    "subject": f"{hw_node}",
                    "variable": "System Node Setpoint Temperature",
                    "frequency": "Detailed",
                },
                "m_hw": {
                    "subject": f"{boiler_name}",
                    "variable": "Boiler Mass Flow Rate",
                    "frequency": "Detailed",
                },
            },
            "parameters": {
                "T_oa_max": t_oa_max,
                "T_oa_min": t_oa_min,
                "T_hw_max_st": t_hw_max_st,
                "T_hw_min_st": t_hw_min_st,
            },
        }
        cases["cases"].append(hw_case)
        id += 1
    return cases, id


def sat_reset(idf, idf_f, id, cases):
    # Define design cooling temperature
    # for each system
    applicable_cases = {
        "OfficeMedium": [
            ("PACU_VAV_bot", 24.0),
            ("PACU_VAV_mid", 24.0),
            ("PACU_VAV_top", 24.0),
        ],
        "OfficeLarge": [
            ("VAV_bot WITH REHEAT", 24.0),
            ("VAV_mid WITH REHEAT", 24.0),
            ("VAV_top WITH REHEAT", 24.0),
        ],
        "SchoolPrimary": [
            ("VAV_POD_1", 24.0),
            ("VAV_POD_2", 24.0),
            ("VAV_POD_3", 24.0),
            ("VAV_OTHER", 24.0),
        ],
        "SchoolSecondary": [
            ("VAV_POD_1", 24.0),
            ("VAV_POD_2", 24.0),
            ("VAV_POD_3", 24.0),
            ("VAV_OTHER", 24.0),
        ],
    }

    # Find building type in IDF file name
    bldg_type = ""
    for k in list(applicable_cases.keys()):
        if k in idf_f:
            bldg_type = k

    if bldg_type != "":
        print(
            "Adding SupplyAirTempReset verification items for {}".format(
                idf_f.split("/")[-1].replace(".idf", "")
            )
        )
        for airloop_tz_coo in applicable_cases[bldg_type]:
            # Get design cooling temp
            airloop = airloop_tz_coo[0]
            tz_coo = airloop_tz_coo[1]

            sat_case = {}
            sat_case["no"] = str(id)

            airloop = idf.getobject("AIRLOOPHVAC", airloop)
            sat_node = airloop.Supply_Side_Outlet_Node_Names

            # Define simulation IO
            sat_case["run_simulation"] = True
            sat_case["simulation_IO"] = {
                "idf": "../test_cases/verif_mtd_pp/idfs/{}".format(
                    idf_f.split("/")[-1]
                ),
                "idd": "../resources/Energy+V9_0_1.idd",
                "weather": "../weather/USA_GA_Atlanta-Hartsfield.Jackson.Intl.AP.722190_TMY3.epw",
                "output": "eplusout.csv",
                "ep_path": "C:\EnergyPlusV9-0-1\energyplus.exe",
            }
            sat_case["expected_result"] = "pass"
            sat_case["verification_class"] = "SupplyAirTempReset"
            sat_case["datapoints_source"] = {
                "idf_output_variables": {
                    "T_sa_set": {
                        "subject": f"{sat_node}",
                        "variable": "System Node Setpoint Temperature",
                        "frequency": "detailed",
                    }
                },
                "parameters": {"T_z_coo": tz_coo},
            }
            cases["cases"].append(sat_case)
            id += 1
    return cases, id


def zone_temp_ctrl(idf, idf_f, id, cases):
    print(
        "Adding ZoneTempControl verification items for {}".format(
            idf_f.split("/")[-1].replace(".idf", "")
        )
    )
    for zone in idf.idfobjects["ZONE"]:
        zone_temp_ctrl = {}
        zone_temp_ctrl["no"] = str(id)

        # Define simulation IO
        zone_temp_ctrl["run_simulation"] = True
        zone_temp_ctrl["simulation_IO"] = {
            "idf": "../test_cases/verif_mtd_pp/idfs/{}".format(idf_f.split("/")[-1]),
            "idd": "../resources/Energy+V9_0_1.idd",
            "weather": "../weather/USA_GA_Atlanta-Hartsfield.Jackson.Intl.AP.722190_TMY3.epw",
            "output": "eplusout.csv",
            "ep_path": "C:\EnergyPlusV9-0-1\energyplus.exe",
        }
        zone_temp_ctrl["expected_result"] = "pass"
        zone_temp_ctrl["verification_class"] = "ZoneTempControl"
        zone_temp_ctrl["datapoints_source"] = {
            "idf_output_variables": {
                "T_z_set_cool": {
                    "subject": f"{zone.Name}",
                    "variable": "Zone Thermostat Cooling Setpoint Temperature",
                    "frequency": "detailed",
                },
                "T_z_set_heat": {
                    "subject": f"{zone.Name}",
                    "variable": "Zone Thermostat Heating Setpoint Temperature",
                    "frequency": "detailed",
                },
            }
        }
        cases["cases"].append(zone_temp_ctrl)
        id += 1
    return cases, id


def zone_temp_ctrl_depth_htg(idf, idf_f, id, cases):
    print(
        "Adding ZoneHeatingResetDepth verification items for {}".format(
            idf_f.split("/")[-1].replace(".idf", "")
        )
    )
    for zone in idf.idfobjects["ZONE"]:
        zone_temp_ctrl_depth_htg = {}
        zone_temp_ctrl_depth_htg["no"] = str(id)

        # Define simulation IO
        zone_temp_ctrl_depth_htg["run_simulation"] = True
        zone_temp_ctrl_depth_htg["simulation_IO"] = {
            "idf": "../test_cases/verif_mtd_pp/idfs/{}".format(idf_f.split("/")[-1]),
            "idd": "../resources/Energy+V9_0_1.idd",
            "weather": "../weather/USA_GA_Atlanta-Hartsfield.Jackson.Intl.AP.722190_TMY3.epw",
            "output": "eplusout.csv",
            "ep_path": "C:\EnergyPlusV9-0-1\energyplus.exe",
        }
        zone_temp_ctrl_depth_htg["expected_result"] = "pass"
        zone_temp_ctrl_depth_htg["verification_class"] = "ZoneHeatingResetDepth"
        zone_temp_ctrl_depth_htg["datapoints_source"] = {
            "idf_output_variables": {
                "T_heat_set": {
                    "subject": f"{zone.Name}",
                    "variable": "Zone Thermostat Heating Setpoint Temperature",
                    "frequency": "detailed",
                }
            }
        }
        cases["cases"].append(zone_temp_ctrl_depth_htg)
        id += 1
    return cases, id


def zone_temp_ctrl_depth_clg(idf, idf_f, id, cases):
    print(
        "Adding ZoneCoolingResetDepth verification items for {}".format(
            idf_f.split("/")[-1].replace(".idf", "")
        )
    )
    for zone in idf.idfobjects["ZONE"]:
        zone_temp_ctrl_depth_clg = {}
        zone_temp_ctrl_depth_clg["no"] = str(id)

        # Define simulation IO
        zone_temp_ctrl_depth_clg["run_simulation"] = True
        zone_temp_ctrl_depth_clg["simulation_IO"] = {
            "idf": "../test_cases/verif_mtd_pp/idfs/{}".format(idf_f.split("/")[-1]),
            "idd": "../resources/Energy+V9_0_1.idd",
            "weather": "../weather/USA_GA_Atlanta-Hartsfield.Jackson.Intl.AP.722190_TMY3.epw",
            "output": "eplusout.csv",
            "ep_path": "C:\EnergyPlusV9-0-1\energyplus.exe",
        }
        zone_temp_ctrl_depth_clg["expected_result"] = "pass"
        zone_temp_ctrl_depth_clg["verification_class"] = "ZoneCoolingResetDepth"
        zone_temp_ctrl_depth_clg["datapoints_source"] = {
            "idf_output_variables": {
                "T_cool_set": {
                    "subject": f"{zone.Name}",
                    "variable": "Zone Thermostat Cooling Setpoint Temperature",
                    "frequency": "detailed",
                }
            }
        }
        cases["cases"].append(zone_temp_ctrl_depth_clg)
        id += 1
    return cases, id


def zone_temp_ctrl_min(idf, idf_f, id, cases):
    print(
        "Adding ZoneHeatSetpointMinimum verification items for {}".format(
            idf_f.split("/")[-1].replace(".idf", "")
        )
    )
    for zone in idf.idfobjects["ZONE"]:
        zone_temp_ctrl_min = {}
        zone_temp_ctrl_min["no"] = str(id)

        # Define simulation IO
        zone_temp_ctrl_min["run_simulation"] = True
        zone_temp_ctrl_min["simulation_IO"] = {
            "idf": "../test_cases/verif_mtd_pp/idfs/{}".format(idf_f.split("/")[-1]),
            "idd": "../resources/Energy+V9_0_1.idd",
            "weather": "../weather/USA_GA_Atlanta-Hartsfield.Jackson.Intl.AP.722190_TMY3.epw",
            "output": "eplusout.csv",
            "ep_path": "C:\EnergyPlusV9-0-1\energyplus.exe",
        }
        zone_temp_ctrl_min["expected_result"] = "pass"
        zone_temp_ctrl_min["verification_class"] = "ZoneHeatSetpointMinimum"
        zone_temp_ctrl_min["datapoints_source"] = {
            "idf_output_variables": {
                "T_heat_set": {
                    "subject": f"{zone.Name}",
                    "variable": "Zone Thermostat Heating Setpoint Temperature",
                    "frequency": "detailed",
                }
            }
        }
        cases["cases"].append(zone_temp_ctrl_min)
        id += 1
    return cases, id


def zone_temp_ctrl_max(idf, idf_f, id, cases):
    print(
        "Adding ZoneCoolingSetpointMaximum verification items for {}".format(
            idf_f.split("/")[-1].replace(".idf", "")
        )
    )
    for zone in idf.idfobjects["ZONE"]:
        zone_temp_ctrl_max = {}
        zone_temp_ctrl_max["no"] = str(id)

        # Define simulation IO
        zone_temp_ctrl_max["run_simulation"] = True
        zone_temp_ctrl_max["simulation_IO"] = {
            "idf": "../test_cases/verif_mtd_pp/idfs/{}".format(idf_f.split("/")[-1]),
            "idd": "../resources/Energy+V9_0_1.idd",
            "weather": "../weather/USA_GA_Atlanta-Hartsfield.Jackson.Intl.AP.722190_TMY3.epw",
            "output": "eplusout.csv",
            "ep_path": "C:\EnergyPlusV9-0-1\energyplus.exe",
        }
        zone_temp_ctrl_max["expected_result"] = "pass"
        zone_temp_ctrl_max["verification_class"] = "ZoneCoolingSetpointMaximum"
        zone_temp_ctrl_max["datapoints_source"] = {
            "idf_output_variables": {
                "T_cool_set": {
                    "subject": f"{zone.Name}",
                    "variable": "Zone Thermostat Cooling Setpoint Temperature",
                    "frequency": "detailed",
                }
            }
        }
        cases["cases"].append(zone_temp_ctrl_max)
        id += 1
    return cases, id


def integrated_econ(idf, idf_f, id, cases):
    # Define system OA min flow rate
    applicable_cases = {
        "OfficeMedium": {
            "2004": [
                ("PACU_VAV_bot", 1.40600),
                ("PACU_VAV_mid", 1.40600),
                ("PACU_VAV_top", 1.40600),
            ],
            "2019": [
                ("PACU_VAV_bot", 1.1950922),
                ("PACU_VAV_mid", 1.1950922),
                ("PACU_VAV_top", 1.1950922),
            ],
        },
        "OfficeLarge": {
            "2004": [
                ("VAV_bot WITH REHEAT", 2.98592),
                ("VAV_mid WITH REHEAT", 29.85923),
                ("VAV_top WITH REHEAT", 2.98592),
            ],
            "2019": [
                ("VAV_bot WITH REHEAT", 2.5380155),
                ("VAV_mid WITH REHEAT", 25.380155),
                ("VAV_top WITH REHEAT", 2.5380155),
            ],
        },
        "SchoolPrimary": {
            "2004": [
                ("VAV_POD_1", 3.81992),
                ("VAV_POD_2", 3.81992),
                ("VAV_POD_3", 3.30560),
                ("VAV_OTHER", 2.00139),
            ],
            "2019": [
                ("VAV_POD_1", 2.40512689661291),
                ("VAV_POD_2", 2.40013226038745),
                ("VAV_POD_3", 2.14260782963322),
                ("VAV_OTHER", 1.4106),
            ],
        },
        "SchoolSecondary": {
            "2004": [
                ("VAV_POD_1", 8.20595),
                ("VAV_POD_2", 8.17768),
                ("VAV_POD_3", 9.13308),
                ("VAV_OTHER", 4.25339),
            ],
            "2019": [
                ("VAV_POD_1", 5.91052411862507),
                ("VAV_POD_2", 5.9959235026983),
                ("VAV_POD_3", 6.33420151335124),
                ("VAV_OTHER", 2.6769),
            ],
        },
    }

    rep = True

    # Find building type in IDF file name
    bldg_type = ""
    for k in list(applicable_cases.keys()):
        if k in idf_f:
            bldg_type = k

    if bldg_type != "":
        # Find code version
        code_version = ""
        for y in list(applicable_cases[bldg_type].keys()):
            if y in idf_f:
                code_version = y

        for airloop_info in applicable_cases[bldg_type][code_version]:
            # Get min OA for the system
            airloop_name = airloop_info[0]
            airloop_oa = airloop_info[1]

            for oa_ctrl in idf.idfobjects["CONTROLLER:OUTDOORAIR"]:
                if airloop_name in oa_ctrl.Name:
                    # Get cooling coil name from branch
                    for brc in idf.idfobjects["BRANCH"]:
                        if airloop_name in brc.Name:
                            for i, f in enumerate(brc.fieldnames):
                                if "coil:cooling" in brc[f].lower():
                                    clg_coil = brc[brc.fieldnames[i + 1]]

                                    if rep:
                                        print(
                                            "Adding IntegratedEconomizerControl verification items for {}".format(
                                                idf_f.split("/")[-1].replace(".idf", "")
                                            )
                                        )
                                        rep = False

                                    oa_node = oa_ctrl.Actuator_Node_Name

                                    integrated_econ = {}
                                    integrated_econ["no"] = str(id)

                                    # Define simulation IO
                                    integrated_econ["run_simulation"] = True
                                    integrated_econ["simulation_IO"] = {
                                        "idf": "../test_cases/verif_mtd_pp/idfs/{}".format(
                                            idf_f.split("/")[-1]
                                        ),
                                        "idd": "../resources/Energy+V9_0_1.idd",
                                        "weather": "../weather/USA_GA_Atlanta-Hartsfield.Jackson.Intl.AP.722190_TMY3.epw",
                                        "output": "eplusout.csv",
                                        "ep_path": "C:\EnergyPlusV9-0-1\energyplus.exe",
                                    }
                                    integrated_econ["expected_result"] = "fail"
                                    integrated_econ[
                                        "verification_class"
                                    ] = "IntegratedEconomizerControl"
                                    integrated_econ["datapoints_source"] = {
                                        "idf_output_variables": {
                                            "oa_flow": {
                                                "subject": f"{oa_node}",
                                                "variable": "System Node Standard Density Volume Flow Rate",
                                                "frequency": "detailed",
                                            },
                                            "ccoil_out": {
                                                "subject": f"{clg_coil}",
                                                "variable": "Cooling Coil Total Cooling Rate",
                                                "frequency": "detailed",
                                            },
                                        },
                                        "parameters": {"oa_min_flow": airloop_oa},
                                    }
                                    cases["cases"].append(integrated_econ)
                                    id += 1
    return cases, id


def diff_enthalpy_econ(idf, idf_f, id, cases):
    # Define system OA min flow rate
    applicable_cases = {
        "OfficeMedium": {
            "2004": [
                ("PACU_VAV_bot", 1.40600),
                ("PACU_VAV_mid", 1.40600),
                ("PACU_VAV_top", 1.40600),
            ],
            "2019": [
                ("PACU_VAV_bot", 1.1950922),
                ("PACU_VAV_mid", 1.1950922),
                ("PACU_VAV_top", 1.1950922),
            ],
        },
        "OfficeLarge": {
            "2004": [
                ("VAV_bot WITH REHEAT", 2.98592),
                ("VAV_mid WITH REHEAT", 29.85923),
                ("VAV_top WITH REHEAT", 2.98592),
            ],
            "2019": [
                ("VAV_bot WITH REHEAT", 2.5380155),
                ("VAV_mid WITH REHEAT", 25.380155),
                ("VAV_top WITH REHEAT", 2.5380155),
            ],
        },
        "SchoolPrimary": {
            "2004": [
                ("VAV_POD_1", 3.81992),
                ("VAV_POD_2", 3.81992),
                ("VAV_POD_3", 3.30560),
                ("VAV_OTHER", 2.00139),
            ],
            "2019": [
                ("VAV_POD_1", 2.40512689661291),
                ("VAV_POD_2", 2.40013226038745),
                ("VAV_POD_3", 2.14260782963322),
                ("VAV_OTHER", 1.4106),
            ],
        },
        "SchoolSecondary": {
            "2004": [
                ("VAV_POD_1", 8.20595),
                ("VAV_POD_2", 8.17768),
                ("VAV_POD_3", 9.13308),
                ("VAV_OTHER", 4.25339),
            ],
            "2019": [
                ("VAV_POD_1", 5.91052411862507),
                ("VAV_POD_2", 5.9959235026983),
                ("VAV_POD_3", 6.33420151335124),
                ("VAV_OTHER", 2.6769),
            ],
        },
    }

    rep = True

    # Find building type in IDF file name
    bldg_type = ""
    for k in list(applicable_cases.keys()):
        if k in idf_f:
            bldg_type = k

    if bldg_type != "":
        # Find code version
        code_version = ""
        for y in list(applicable_cases[bldg_type].keys()):
            if y in idf_f:
                code_version = y

        for airloop_info in applicable_cases[bldg_type][code_version]:
            # Get min OA for the system
            airloop_name = airloop_info[0]
            airloop_oa = airloop_info[1]

            for oa_ctrl in idf.idfobjects["CONTROLLER:OUTDOORAIR"]:
                if airloop_name in oa_ctrl.Name:
                    if rep:
                        print(
                            "Adding EconomizerHighLimitD verification items for {}".format(
                                idf_f.split("/")[-1].replace(".idf", "")
                            )
                        )
                        rep = False

                    oa_node = oa_ctrl.Actuator_Node_Name
                    ret_node = oa_ctrl.Return_Air_Node_Name

                    diff_enthalpy_econ = {}
                    diff_enthalpy_econ["no"] = str(id)

                    # Define simulation IO
                    diff_enthalpy_econ["run_simulation"] = True
                    diff_enthalpy_econ["simulation_IO"] = {
                        "idf": "../test_cases/verif_mtd_pp/idfs/{}".format(
                            idf_f.split("/")[-1]
                        ),
                        "idd": "../resources/Energy+V9_0_1.idd",
                        "weather": "../weather/USA_GA_Atlanta-Hartsfield.Jackson.Intl.AP.722190_TMY3.epw",
                        "output": "eplusout.csv",
                        "ep_path": "C:\EnergyPlusV9-0-1\energyplus.exe",
                    }
                    diff_enthalpy_econ["expected_result"] = "fail"
                    diff_enthalpy_econ["verification_class"] = "EconomizerHighLimitD"
                    diff_enthalpy_econ["datapoints_source"] = {
                        "idf_output_variables": {
                            "oa_flow": {
                                "subject": f"{oa_node}",
                                "variable": "System Node Standard Density Volume Flow Rate",
                                "frequency": "detailed",
                            },
                            "oa_db": {
                                "subject": "Environment",
                                "variable": "Site Outdoor Air Drybulb Temperature",
                                "frequency": "detailed",
                            },
                            "oa_enth": {
                                "subject": "Environment",
                                "variable": "Site Outdoor Air Enthalpy",
                                "frequency": "detailed",
                            },
                            "ret_a_enth": {
                                "subject": f"{ret_node}",
                                "variable": "System Node Enthalpy",
                                "frequency": "detailed",
                            },
                        },
                        "parameters": {"oa_min_flow": airloop_oa, "oa_threshold": 999},
                    }
                    cases["cases"].append(diff_enthalpy_econ)
                    id += 1
    return cases, id


# Create cases "on-the-fly"
def create_cases():
    cases = {}
    cases["cases"] = []
    id = 0

    for idf_f in glob.glob("./idfs/*.idf"):
        if not "injected" in idf_f:
            idf = IDF(idf_f)

            # CHW Reset
            cases, id = chwreset(idf, idf_f, id, cases)

            # HW Reset
            cases, id = hwreset(idf, idf_f, id, cases)

            # SAT Reset
            cases, id = sat_reset(idf, idf_f, id, cases)

            # Zone temperature setpoint deadband
            cases, id = zone_temp_ctrl(idf, idf_f, id, cases)
            cases, id = zone_temp_ctrl_depth_htg(idf, idf_f, id, cases)
            cases, id = zone_temp_ctrl_depth_clg(idf, idf_f, id, cases)
            cases, id = zone_temp_ctrl_min(idf, idf_f, id, cases)
            cases, id = zone_temp_ctrl_max(idf, idf_f, id, cases)

            # Integrated economizer
            cases, id = integrated_econ(idf, idf_f, id, cases)

            # Diff enthalpy economizer with no OA DB limit
            cases, id = diff_enthalpy_econ(idf, idf_f, id, cases)

    json.dump(cases, open("./verification_cases.json", "w"), indent=4)


if __name__ == "__main__":
    create_cases()
