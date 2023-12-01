"""Module implementing data structures of datapoints"""


class Datapoint:
    """Data point super class, mostly a placeholder for now

    Attributes:
        name: name of the point used in json file as datapoint keys and in assertions
        valuetype: "Scalor" or "TimeSeries", does not impact the computation for now
        value: place to hold corresponding data when acquired from simulation i/o

    """

    def __init__(self, pointname, valuetype):
        """

        Args:
            pointname: name of the point used in json file as datapoint keys and in assertions
            valuetype: "Scalor" or "TimeSeries", does not impact the computation for now
        """
        self.name = pointname
        self.valuetype = valuetype
        self.value = None


class DevSettingPoint(Datapoint):
    """Datapoint subclass to represent item execution settings.

    This point type reads scalor values from json input directly.
    """

    def __init__(self, pointname, pointvalue):
        """

        Args:
            pointname: name of the point used in json file as datapoint keys and in assertions
            pointvalue: the numeric scalor value of the dev_setting point
        """
        super().__init__(pointname, "Scalor")
        self.value = pointvalue


class IdfInfoPoint(Datapoint):
    """Datapoint subclass to represent an IDF information point.

    This point type reads data from static IDF input file.
    """

    def __init__(self, pointname, pointdict):
        """

        Args:
            pointname: name of the point used in json file as datapoint keys and in assertions
            pointdict: sub fields of the IDF information point source in the Json file. containing keys: "filters"
                (must contain a sub key of "idf_object_type"), "exclusions", "field". Example below:
                "OA_min_sys": {
                        "filters": {
                            "idf_object_type": "Controller:OutdoorAir",
                            "Name": "PSZ-AC_1:6_OA_Controller"
                        },
                        "exclusions": {
                            "Minimum_Outdoor_Air_Flow_Rate": "Autosize"
                        },
                        "field": "Minimum_Outdoor_Air_Flow_Rate"
                    }
        """
        super().__init__(pointname, "Scalor")
        self.filters = pointdict["filters"]
        if "exclusions" in pointdict.keys():
            self.exclusions = pointdict["exclusions"]
        else:
            self.exclusions = {}
        self.field = pointdict["field"]


class IdfOutputPoint(Datapoint):
    """Datapoint subclass to represent an IDF output variable

    This point type reads data from injected EP Output:Variable objects in the simulation results csv file.

    Attributes:
        outputobj: string used for creating a hash to determine object uniqueness
        variable_name: string used for retrieving data later
    """

    def __init__(self, pointname, pointdict):
        """

        Args:
            pointname: name of the point used in json file as datapoint keys and in assertions
            pointdict: sub fields of the IDF output point source in the Json file. containing keys: "subject",
                "variable" and "frequency". Example below:
                "OA_timestep": {
                        "subject": "PSZ-AC_1:6_OAInlet Node",
                        "variable": "System Node Standard Density Volume Flow Rate",
                        "frequency": "timestep"
                    }
        """
        super().__init__(pointname, "TimeSeries")
        if isinstance(pointdict, dict):
            self.subject = pointdict["subject"]
            self.variable = pointdict["variable"]
            self.frequency = pointdict["frequency"]
            self.outputobj = (
                f"Output:Variable,{self.subject},{self.variable},{self.frequency};"
            )
            self.variable_name = f"{self.subject}:{self.variable}"
        elif isinstance(pointdict, str):
            self.outputobj = "Override, manually provided full variable string, should have NO injection!"
            self.variable_name = pointdict
        else:
            print("output variable setup in the case json file has errors!")

    def __hash__(self):
        """only designed to be used for picking unique output variables"""
        return self.outputobj.__hash__()

    def __eq__(self, other):
        return self.outputobj.strip().lower() == other.outputobj.strip().lower()
