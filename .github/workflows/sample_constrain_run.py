import constrain as cs
examples = cs.Examples()
data = examples.data("example_1")
cases = cs.api.VerificationCase(json_case_path=examples.verifications("example_1"))
cases.validate()
verif = cs.api.Verification(verifications=cases)
verif.configure(output_path = "./",
                lib_items_path = examples.library(),
                plot_option = "all-expand",
                fig_size = (10, 5),
                num_threads = 3,
                preprocessed_data = data)
verif.run()
reporting = cs.api.Reporting(verification_json= "./*_md.json",
                            result_md_name = "report_summary.md",
                            report_format = "markdown")
reporting.report_multiple_cases()