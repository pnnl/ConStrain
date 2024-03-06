import openstudio
from constrain.api.workflow import Workflow
import typing
import csv
import os


class GenerateConStrainReport(openstudio.measure.ReportingMeasure):
    def name(self):
        """
        Return the human readable name.
        Measure name should be the title case of the class name.
        """
        return "Generate ConStrain report"

    def description(self):
        """
        Human readable description
        """
        return "Generate ConStrain report"

    def modeler_description(self):
        """
        Human readable description of the modeling approach
        """
        return "Generate ConStrain report."

    def arguments(self):
        """
        Define arguments
        """
        args = openstudio.measure.OSArgumentVector()
        workflow_path = openstudio.measure.OSArgument.makeStringArgument(
            "workflow_path", True
        )
        args.append(workflow_path)

        return args

    def run(
        self,
        runner: openstudio.measure.OSRunner,
        user_arguments: openstudio.measure.OSArgumentMap,
    ):
        """
        Define what happens when the measure is run
        """
        super().run(runner, user_arguments)

        if not (runner.validateUserArguments(self.arguments(), user_arguments)):
            return False

        # Get arguments
        workflow_path = runner.getStringArgumentValue("workflow_path", user_arguments)

        runner.registerInitialCondition("Init")
        workflow = Workflow(workflow_path)
        workflow.run_workflow(verbose=True)

        runner.registerFinalCondition("Done.")
        return True


GenerateConStrainReport().registerWithApplication()
