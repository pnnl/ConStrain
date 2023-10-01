# <span style="color:orange">_Con_</span>trol <span style="color:orange">_Strain_</span>er (<span style="color:orange">_ConStrain_</span>): A Data-driven Control Verification Framework (formally known as <span style="color:orange">_ANIMATE_</span>)

<!-- # ANIMATE: a dAtadriveN buildIng perforMance verificATion framEwork -->

Unit tests status: ![Tests](https://github.com/pnnl/ConStrain/actions/workflows/unit_tests.yml/badge.svg)

# Background and Motivation

Advances in building control have shown significant potential for improving building energy performance and decarbonization. Studies show that designs utilizing optimized controls that are properly tuned could cut commercial building energy consumption by approximately 29% - equivalent to 4-5 Quads, or 4-5% of the energy consumed in the United States. Driven by the significant control-related energy-saving potential, commercial building energy codes (such as ASHRAE 90.1) have progressed with many control-related addenda. For example, from the publication of 90.1-2004 to 90.1-2016 (four code cycles), 30% of the new requirements are related to building control (with most of them focused on HVAC system control).

However, one of the challenges to realizing those savings is the correct implementation of such advanced control strategies and regularly verifying their actual operational performance. A field study found that only 50% of systems observed have their control system correctly configured to meet the energy codes requirement, and control-related compliance verification is typically not included in the commissioning (Cx) scope. The current control verification is often manually conducted, which is time-consuming, ad-hoc, incomplete, and error-prone.

# What is _ConStrain_?

ConStrain is a data-driven knowledge-integrated framework that automatically verifies that controls function as intended. The figure below shows an overview of ConStrain and how it can be used. ConStrain was born out of the need of automating the verification of time-series data describing the behavior of building components, especially the control functions.

ConStrain is designed around three key features: building control knowledge integration, analytics, and automation. The framework includes three major components: a control verification algorithm library (rule-based, procedure-based, and AI-based), an automated preparation process and verification case generation, a standardized performance evaluation and reporting process.

While the development of ConStrain was motivated by use cases with building energy modeling (BEM), it is now evolved for more application scenarios towards real building control verification.

![Overview of ConStrain](constrain_overview.png)

# Who shall be interested in this framework?

- Cx agent – reduce effort and cost, while increasing rigor.
- Building operator – implement Continuous Commissioning (CCx) to avoid performance drift.
- Authority having jurisdiction (AHJ) – achieve better compliance rates for control provisions in code.
- Mechanical engineer/energy modeler – ensure that chosen systems and their controls will comply with code.
- Energy code/control guideline developer – identify ambiguity in code languages.
- BEM software developer – identify control related issues in simulation engine.

# Current Version of _ConStrain_?

The current version of ConStrain includes the framework implementation, a preliminary development and implementation of the verification library (based on ASHRAE 90.1-2016 control related requirement), and the test cases of verification algorithms using prototype building models. The current list of implemented verification algorithms includes supply air temperature control, economizer high limit, integrated economizer control, zone temperature control (dead band), zone temperature control (setback), hot water temperature reset, chilled water temperature reset, etc.

A newly released API helps users to use ConStrain more easily. An API workflow demo is provided at `demo/api_demo` and `test/api/test_workflow.py`

See the Publications section for more information and example of uses of the framework.

## Get Started

- Demos are located in `demo/`
- Visit [API documentation page](https://pnnl.github.io/ConStrain/) to learn about how to use the ConStrain API.
- Visit [Guideline 36 Verification Items List](./design/g36_lib_contents.md) to learn more about the ASHRAE Guideline 36 related verification in ConStrain verification library.
- Visit [Local Loop Verification Items List](./design/local_loop_verification_items_list.md) to learn more about local loop performance verification library.
- Visit [Brick Integration Doc](./design/brick_integration_doc.md) to learn more about the beta version of brick schema integration API.

<!-- ## Note

- Currently the master branch is setup to run simulation and verification batches in parralel on PNNL's PIC platform. Updates are expected to properly expose setup options for different environments and use cases.

## Key files in the repository

| File                                         | Description                                                                          |
| -------------------------------------------- | ------------------------------------------------------------------------------------ |
| src/library.py                               | verification library                                                                 |
| src/run_sim_for_cases.py                     | idf file instrumenter and runner                                                     |
| src/run_verification_case.py                 | batch verification cases runner                                                      |
| src/summarize_md.py                          | batch verification cases results report generator                                    |
| src/verification_cases_split.py              | split instantiated verification cases by idf with batch size limit                   |
| schema/library.json                          | verification library meta data                                                       |
| schema/library_verification_cases.json       | library verification test cases input file (outdated)                                |
| other files in src/                          | verification framework implementation                                                |
| test_cases/                                  | verification test cases input and related files                                      |
| test_cases/verif_mtd_pp/create_test_cases.py | verification case instantiator                                                       |
| demo/verification_approach_demo              | 3 different verification methods demo outputs                                        |
| demo/library_item_demo                       | verification cases demo run in Ipython Notebook with associated case definition json | -->

## Publications

- Chen Y., M. Wetter, X. Lei, J. Lerond, P.K. Anand, Y. Jung, P. Ehrlich, and D.L. Vrabie. 2023. "Control Performance Verification – The Hidden Opportunity of Ensuring High Performance of Building Control System." In Building Simulation 2023 Conference
- Lei X., J. Lerond, Y. Jung, and Y. Chen. 2023. "Development of an Application Programming Interface for a Building Systems Control Performance Verification Framework." In 2023 ASHRAE Annual Conference
- [Chen Y., J. Lerond, X. Lei, and M.I. Rosenberg. 2021. "A Knowledge-based Framework for Building Energy Model Performance Verification." In Building Simulation 2021 Conference](https://publications.ibpsa.org/conference/paper/?id=bs2021_30725)

## Referencing

If you wish to cite ConStrain in academic work please use: Lei, X., Lerond, J., Jung, Y. J., & Chen, Y. (2023). ConStrain (Version 0.3.0) [Computer software]. https://github.com/github/ConStrain

<!-- Pending DOI for new ConStrain -->
