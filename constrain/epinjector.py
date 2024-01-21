"""Module for injecting objects into idfs"""


from io import StringIO
from constrain.datapoint import IdfOutputPoint
from typing import List
from eppy.modeleditor import IDF
import shutil


class Injector:
    """Placeholder super class"""

    pass


class IDFInjector(Injector):
    """Inject idf output variable objects to IDF files"""

    def __init__(self, idf_file_in, idd_file):
        """

        Args:
            idf_file_in: path to idf file to be injected
            idd_file: path to idd file for processing idf file with eppy
        """
        self.idf_file_in = idf_file_in
        IDF.setiddname(iddname=idd_file)
        self.appending_str = None

    def inject_idf_outputs(self, eppy_output_objs: List[IdfOutputPoint]) -> None:
        """create output variable idf objects as a string

        Args:
            eppy_output_objs: list of `IdfOutputPoint` objects to be injected into the IDF

        Returns:
            `None`. the created string to be injected is stored to `self.appending_str`

        """
        fhandle = StringIO("")
        output_idf_objs = IDF(fhandle)
        for output_obj in eppy_output_objs:
            output_idf_objs.newidfobject(
                "Output:Variable".upper(),
                Key_Value=output_obj.subject,
                Variable_Name=output_obj.variable,
                Reporting_Frequency=output_obj.frequency,
            )

        all_list = [
            str(obj) for obj in output_idf_objs.idfobjects["Output:Variable".upper()]
        ]
        self.appending_str = "\n".join(all_list)

    def save(self, idf_file_out=None):
        if idf_file_out is None:
            out_idf = self.idf_file_in
        else:
            out_idf = idf_file_out
            shutil.copyfile(self.idf_file_in, out_idf)

        with open(out_idf, "a") as f:
            f.write(
                "! ---------------injected output variables--------------------------\n"
            )
            f.write(self.appending_str)
