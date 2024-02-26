import pytest
import openstudio
import pathlib
import sys
from ..measure import GenerateConStrainReport
import logging

LOGGER = logging.getLogger(__name__)


class TestGenerateConStrainReport:
    def test_number_of_arguments_and_argument_names(self):
        """
        Test that the arguments are what we expect
        """
        # create an instance of the measure
        measure = GenerateConStrainReport()

        # make an empty model
        model = openstudio.model.Model()

        # get arguments and test that they are expecting a failure
        # because the model doesn't have a chiller
        # Create dummy chiller object

        # get arguments and test that they are what we are expecting
        arguments = measure.arguments(model)
        assert arguments.size() == 1
        assert arguments[0].name() == "workflow_path"

    def test_good_argument_values(self):
        """
        Test running the measure with appropriate arguments, and that the
        measure runs fine and with expected results
        """

        measure = GenerateConStrainReport()

        osw = openstudio.openstudioutilitiesfiletypes.WorkflowJSON()
        runner = openstudio.measure.OSRunner(osw)

        model = openstudio.model.exampleModel()
        sql_path = openstudio.path("eplusout.db")
        sql_file = openstudio.SqlFile("eplusout.db")
        model.setSqlFile(sql_file)
        print(model.sqlFile().get().path())
        # Create dummy chiller object

        arguments = measure.arguments(model)
        argument_map = openstudio.measure.convertOSArgumentVectorToMap(arguments)

        args_dict = {}
        args_dict["workflow_path"] = "test_files/G36_demo_workflow.json"

        for arg in arguments:
            temp_arg_var = arg.clone()
            if arg.name() in args_dict:
                temp_arg_var.setValue(args_dict[arg.name()])
                # if arg.name() != "chiller_name":
                assert temp_arg_var.setValue(args_dict[arg.name()])
                argument_map[arg.name()] = temp_arg_var

        # Run measure
        measure.run(model, runner, argument_map)
        result = runner.result()
        assert result.value().valueName() == "Success"

        # Save model
        output_file_path = str(
            pathlib.Path(__file__).parent.absolute() / "output" / "test_output.osm"
        )
        model.save(output_file_path, True)


if __name__ == "__main__":
    pytest.main()
