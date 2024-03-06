import openstudio
import constrain
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

    def arguments(self, model: openstudio.model.Model):
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
        model: openstudio.model.Model,
        runner: openstudio.measure.OSRunner,
        user_arguments: openstudio.measure.OSArgumentMap,
    ):
        """
        Define what happens when the measure is run
        """
        super().run(runner, user_arguments)

        if not (runner.validateUserArguments(self.arguments(model), user_arguments)):
            return False

        # Get arguments
        reporting_frequency = "Hourly"
        workflow_path = runner.getStringArgumentValue("workflow_path", user_arguments)

        runner.registerInitialCondition("Init")

        sql_file = model.sqlFile().get()
        print(sql_file.supportedVersion())

        ann_env_pd = None
        for env_pd in sql_file.availableEnvPeriods():
            print(env_pd)
            env_type = sql_file.environmentType(env_pd)
            if env_type.is_initialized() and isinstance(
                env_type.get(), openstudio.EnvironmentType.new("WeatherRunPeriod")
            ):
                ann_env_pd = env_pd
                break

        if reporting_frequency != "All":
            headers = [f"{reporting_frequency}"]
            output_timeseries = {}

            print(ann_env_pd, reporting_frequency)
            variable_names = sql_file.availableVariableNames(
                ann_env_pd, reporting_frequency
            )
            for variable_name in variable_names:
                print(
                    "****************************", f"Variable Name = {variable_name}"
                )
                key_values = sql_file.availableKeyValues(
                    ann_env_pd, reporting_frequency, str(variable_name)
                )
                if not key_values:
                    runner.registerError(
                        f"Timeseries for {variable_name} did not have any key values. No timeseries available."
                    )

                for key_value in key_values:
                    print(f"Key = {key_value}")
                    timeseries = sql_file.timeSeries(
                        ann_env_pd,
                        reporting_frequency,
                        str(variable_name),
                        str(key_value),
                    )
                    if timeseries:
                        timeseries = timeseries.get()
                        units = timeseries.units()
                        headers.append(
                            f"{str(key_value)}:{str(variable_name)}[{units}]"
                        )
                        output_timeseries[headers[-1]] = timeseries
                    else:
                        runner.registerWarning(
                            f"Timeseries for {str(key_value)} {str(variable_name)} is empty."
                        )

            if not output_timeseries:
                print(
                    f"No output variables found at reporting frequency = {reporting_frequency}"
                )
            else:
                csv_array = [headers]

                date_times = output_timeseries[
                    list(output_timeseries.keys())[0]
                ].dateTimes()

                values = {}
                for key in output_timeseries.keys():
                    values[key] = output_timeseries[key].values()

                num_times = len(date_times) - 1
                for i in range(num_times):
                    date_time = date_times[i]
                    row = []
                    row.append(date_time)
                    for key in headers[1:]:
                        value = values[key][i]
                        row.append(value)
                    csv_array.append(row)

                reporting_frequency = "your_frequency_here"  # Replace "your_frequency_here" with the actual frequency
                file_name = f"./report_variables_{reporting_frequency.replace(' ', '')}.csv"  # Constructing the file name

                with open(file_name, "w", newline="") as file:
                    writer = csv.writer(file)
                    for elem in csv_array:
                        writer.writerow(elem)

                runner.registerInfo(
                    f"Output file written to {os.path.abspath(file_name)}"
                )
        else:
            reporting_frequencies = ["Hourly", "Zone Timestep", "HVAC System Timestep"]

            for reporting_frequency in reporting_frequencies:
                print("***********************************************")
                print("Reporting Frequency =", reporting_frequency)

                headers = [reporting_frequency]
                output_timeseries = {}

                variable_names = sql_file.availableVariableNames(
                    ann_env_pd, reporting_frequency
                )
                for variable_name in variable_names:
                    print("****************************")
                    print("Variable Name =", variable_name)
                    key_values = sql_file.availableKeyValues(
                        ann_env_pd, reporting_frequency, str(variable_name)
                    )
                    if len(key_values) == 0:
                        runner.registerError(
                            f"Timeseries for {variable_name} did not have any key values. No timeseries available."
                        )

                    for key_value in key_values:
                        print("Key =", key_value)
                        timeseries = sql_file.timeSeries(
                            ann_env_pd,
                            reporting_frequency,
                            str(variable_name),
                            str(key_value),
                        )
                        if timeseries:
                            units = timeseries.units()
                            headers.append(f"{key_value}:{variable_name}[{units}]")
                            output_timeseries[headers[-1]] = timeseries
                        else:
                            runner.registerWarning(
                                f"Timeseries for {key_value} {variable_name} is empty."
                            )

                if not output_timeseries:
                    print(
                        f"No output variables found at reporting frequency = {reporting_frequency}"
                    )
                    continue

                csv_array = [headers]
                date_times = output_timeseries[
                    list(output_timeseries.keys())[0]
                ].dateTimes()
                values = {
                    key: output_timeseries[key].values()
                    for key in output_timeseries.keys()
                }

                for i, date_time in enumerate(date_times):
                    row = [date_time]
                    for key in headers[1:]:
                        value = values[key][i]
                        row.append(value)
                    csv_array.append(row)

                file_name = (
                    f"./report_variables_{reporting_frequency.replace(' ', '')}.csv"
                )
                with open(file_name, "w", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerows(csv_array)

                print("Output file written to", os.path.abspath(file_name))

        sql_file.close()
        runner.registerFinalCondition("Done.")
        return True


GenerateConStrainReport().registerWithApplication()
