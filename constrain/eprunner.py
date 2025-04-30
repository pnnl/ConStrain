"""Module for running energyplus simulations to generate output files"""

import subprocess
import shutil
from pathlib import Path


class EPRunner:
    """Energyplus runner"""

    def __init__(
        self,
        idf_path,
        weather_path,
        idd_path=r"C:\EnergyPlusV9-0-1\Energy+.idd",
        ep_path=r"C:\EnergyPlusV9-0-1\energyplus.exe",
        output_path=None,
        output_prefix=None,
    ):
        """

        Args:
            idf_path: path to the idf file
            weather_path: path to the weather epw file
            idd_path: idd file path, default to windows ep 9.0.1 folder idd file path
            ep_path: energyplus path, defatul to windows ep 9.0.1 folder energyplus.exe path
            output_path: output directory, default to None, which set to a new folder at the location of the idf file,
                with folder name being the idf file name
            output_prefix: output files prefix as a string, default to None, which does not add any prefix
        """
        self.idf_path = idf_path
        self.weather_path = weather_path
        self.idd_path = idd_path
        self.ep_path = ep_path
        self.output_prefix = output_prefix
        # by default, use the case name as the output folder
        if output_path is None:
            if ".idf" in idf_path.lower():
                self.output_path = idf_path[:-4]
            elif ".epjson" in idf_path.lower():
                self.output_path = idf_path[:-7]
            else:
                self.output_path = idf_path
        self.process_run = None

    def run_simulation(self):
        """run simulation with setup obtained in the constructor

        Returns:
            precess run object, which contains all stdout/stderr, will be saved by the save_log method

        """

        # copy weather file to the simulation output folder to allow simulations in parallel
        Path(self.output_path).mkdir(parents=True, exist_ok=True)
        shutil.copyfile(
            self.weather_path,
            "".join(self.output_path, "/", self.weather_path.split("/")[-1]),
        )  # weather_path should perhaps be renamed
        self.weather_path = self.output_path + "/" + self.weather_path.split("/")[-1]

        command = [
            self.ep_path,
            "--weather",
            self.weather_path,
            "--output-directory",
            self.output_path,
            "--idd",
            self.idd_path,
            "--expandobjects",
            "-r",  # use to do read vars
        ]

        if self.output_prefix is not None:
            command.extend(["--output-prefix", self.output_prefix])

        command.append(self.idf_path)

        self.process_run = subprocess.run(command, shell=True, capture_output=True)

        return self.process_run

    def save_log(self, log_path=None):
        """save running log for manual inspection

        Args:
            log_path: path to save the log
        """
        if log_path is None:
            log_path = f"{self.output_path}/run_log.log"
        with open(log_path, "wt") as logfile:
            logfile.write(str(self.process_run))
        shutil.copyfile(self.idf_path, self.output_path + "/in.idf")
