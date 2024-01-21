"""Reader module is used to read information from EP artifacts"""


from eppy.modeleditor import IDF
import pandas as pd
from fuzzywuzzy import fuzz


class EPReader:
    """Super class for classes reading EP artifacts, currently a place holder"""

    pass


class IDFReader(EPReader):
    """Reader for IDF file"""

    def __init__(self, idf_file, idd_file):
        self.idf_file = idf_file
        IDF.setiddname(idd_file)
        self.idf = IDF(self.idf_file)

    def getobjsbytype(self, objtype):
        """1st step helper: get objects by type"""
        return self.idf.idfobjects[str.upper(objtype)]

    @staticmethod
    def fieldsfilter(filters_dict, objslist):
        """2nd step helper: apply field filters on objects"""
        filteredobjs = objslist
        for fieldname, fieldvalue in filters_dict.items():
            filteredobjs = [obj for obj in filteredobjs if obj[fieldname] == fieldvalue]
        return filteredobjs

    @staticmethod
    def fieldsexcluter(excluters_dict, objslist):
        """3rd step helper: apply field exclusions on objects"""
        filteredobjs = objslist
        for fieldname, fieldvalue in excluters_dict.items():
            filteredobjs = [obj for obj in filteredobjs if obj[fieldname] != fieldvalue]
        return filteredobjs

    def getidffieldval(self, objtype, filters_dict, excluters_dict, fieldname):
        """main method to get static idf object field value

        Args:
            objtype: E.g. "Controller:OutdoorAir"
            filters_dict:
                E.g. {"Name": "PSZ-AC_1:6_OA_Controller"}
            excluters_dict:
                E.g. {"Minimum_Outdoor_Air_Flow_Rate": "Autosize"}
            fieldname:
                E.g. "Minimum_Outdoor_Air_Flow_Rate"

        Returns:
            field value of a single object, object selected by object type, field filters and exclusions
        """
        objs = self.getobjsbytype(objtype)
        filteredobjs = self.fieldsfilter(filters_dict, objs)
        excluteredobjs = self.fieldsexcluter(excluters_dict, filteredobjs)
        if len(excluteredobjs) != 1:
            print("ERROR: retrieved non-single idf obj")
            return None
        return excluteredobjs[0][fieldname]


class HTMLReader(EPReader):
    """Reader for EP simulation output html file, not implemented yet"""

    pass


class CSVReader(EPReader):
    """Reader for EP simulation output csv file"""

    def __init__(self, csv_file):
        if not csv_file is None:
            self.csv_file = csv_file
            self.df = pd.read_csv(csv_file)

    def getseries(self, cols=None):
        """get time series based on column name (string) or column names (list), cols name after processing
        cols should be "subject:variable" in idf_output_variables data points
        """

        if cols is None:
            cols = self.getcols()

        fullcols = self.getcols()
        if isinstance(cols, str):
            cols = [cols]
        pickedcols = []
        pickedcols_original_format = []
        for requestcol in cols:
            current_picks = []
            for csvcol in fullcols:
                if requestcol.upper() in csvcol.upper():
                    current_picks.append(csvcol)
            if len(current_picks) > 1:
                maxratio = None
                for i in range(len(current_picks)):
                    current_ratio = fuzz.ratio(
                        current_picks[i].upper(), requestcol.upper()
                    )
                    reset = False
                    if maxratio is None:
                        reset = True
                    else:
                        if current_ratio > maxratio:
                            reset = True
                        if current_ratio == maxratio:
                            print(
                                "ERROR: observe same fuzzywuzzy match ratio for two columns, investigation needed."
                            )
                            return None
                    if reset:
                        maxratio = current_ratio
                        picked_csvcol = current_picks[i]
            else:
                picked_csvcol = current_picks[0]

            pickedcols.append(picked_csvcol)
            pickedcols_original_format.append(requestcol)

        if len(cols) != len(pickedcols):
            print("ERROR: time series query does not match")
            return None

        if "Date/Time" in pickedcols:
            finalcols = pickedcols
            finalcols_original = pickedcols_original_format
        elif "Date/Time" in self.df.columns:
            finalcols = ["Date/Time"]
            finalcols.extend(pickedcols)
            finalcols_original = ["Date/Time"]
            finalcols_original.extend(pickedcols_original_format)
        else:
            finalcols = pickedcols
            finalcols_original = pickedcols_original_format

        pickeddf = self.df[finalcols].copy(deep=True)

        pickeddf.columns = finalcols_original

        return pickeddf

    def getcols(self):
        """get all csv output variables names, including the Date/Time column"""
        return self.df.columns.tolist()
