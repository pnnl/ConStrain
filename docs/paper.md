---
title: 'Control Strainer (ConStrain): a data-driven control verification framework'
tags:
  - python
  - energy
  - building
  - control
  - simulation
  - hvac
authors:
  - name: Xuechen Lei
    orcid: 0000-0003-3310-9750
    affiliation: 1
  - name: Jérémy Lerond
    orcid: 0000-0002-1630-6886
    affiliation: 1
  - name: Yun Joon Jung
    orcid: 0000-0003-1311-8932
    affiliation: 1
  - name: Julian Slane-Holloway
    orcid: 0009-0008-9572-9123
    affiliation: 1
  - name: Fan Feng
    orcid: 0000-0002-6230-0063
    affiliation: 1
  - name: Yan Chen
    orcid: 0000-0002-2988-9136
    affiliation: 1

affiliations:
 - name: Pacific Northwest National Laboratory, Richland, WA, USA
   index: 1
date: 28 May 2024

bibliography: paper.bib
---

# Summary

The Control Strainer (ConStrain) is a Python-based, open-source framework that enables commissioning agents, controls engineers, building automation specialists, facility managers, and energy modelers to conduct consistent and automated verification of building system controls. It utilizes real-time Building Automation System (BAS) trend data or time-series data generated from whole-building energy system simulations (e.g., EnergyPlus [@energyplus], Spawn-of-EnergyPlus [@spawn], Modelica [@modelica]).

At its roots, `ConStrain`'s verification library was developed to check for compliance with control-related requirements in building energy codes—such as scheduling, economizer logic, demand-controlled ventilation, or equipment staging. These requirements specify how Heating, Ventilation, and Air Conditioning (HVAC) systems should behave to ensure energy efficiency. ConStrain formalizes and automates the control verification process, which involves checking time-series sensor and actuator data to determine whether actual system operation aligns with those intended control sequences. Meanwhile, the verification library is implemented in a way such that it is expandable and can cover user-customized control verifications.

# Statement of need

Robust HVAC control is a “no regrets” strategy for building decarbonization, reducing energy use, enabling flexibility and resilience, and supporting the transition to electrified heating, all with low embodied carbon. The Buildings Technology Office (BTO) of the United States Department of Energy’s blueprint has a goal of “more than 50% of all homes and businesses have automated control platforms that reduce energy waste and enable flexibility“ [@bto_blueprint].

Advances in building control have shown significant potential for improving building energy performance and decarbonization. Studies show that designs utilizing optimized controls that are properly tuned could cut commercial building energy consumption by approximately 29% - equivalent to 4–5 quadrillion BTUs (“Quads”), or about 4–5% of total U.S. energy consumption [@impa_ctrl]. Driven by the significant control-related energy-saving potential, commercial building energy codes and standards (such as American Society of Heating, Refrigerating and Air-Conditioning Engineers (ASHRAE) 90.1 [@90.1]) have progressed with many control-related addenda. For example, over the course of four successive ASHRAE 90.1 code cycles—from the 2004 edition to the 2016 edition — approximately 30% of the new requirements are related to building control (with most of them focused on HVAC system control) [@impl_ctrl]. This trend reflects the increasing importance of automated control in achieving code-mandated energy performance.

However, one of the challenges to realizing those savings is the correct implementation of such advanced control strategies and regularly verifying their actual operational performance. A field study found that only 50% of systems observed have their control system correctly configured to meet the energy codes requirement [@impl_ctrl], and control-related compliance verification is typically not included in the commissioning scope.

Current control verification is often conducted manually, which is time-consuming, ad-hoc, incomplete, and error-prone. To address this, `ConStrain` focuses on formalizing and automating verification of HVAC controls by analyzing sensor and actuator data streams from building control systems. `ConStrain` is an executable control verification knowledge base and application programming interface (API) for analyzing BAS data streams for adherence to an operational specification, which can correspond to building energy code (e.g., ASHRAE 90.1) or to a high-performance building control guideline (e.g., ASHRAE Guideline 36 [@g36]). `ConStrain` is also incorporating semantic modeling [@brick] capabilities to enable automated configuration and deployment of verification.

`ConStrain` can be used as a standalone tool and can also be integrated into established workflows of third-party tools. For instance, `ConStrain` has been successfully integrated as part of the continuous integration software development process of whole-building energy simulation-based software tool (e.g., Washington State's Total System Performance Ratio Analysis Tool [@tspr]) to make sure that software code contributions as well as simulation software updates do not have unexpected impacts on the simulated performance of building system controls. Moreover, a set of `OpenStudio` [@os] measures [@osm] have also been developed to enable building energy modelers using `OpenStudio` to perform verification on their models with minimal configurations required.


### Comparison with existing tools and industry practices

In current industry practices, HVAC control verification is often conducted manually by commissioning agents or facilities teams, or through proprietary trend data analytics solutions integrated into BAS. These tools, while valuable for fault detection and system monitoring, are generally vendor-specific, offer limited transparency, and are not purpose-built to ensure that control strategies intended to deliver energy savings, such as those specified in energy codes or design standards, are functioning as intended in actual operation. 

To our knowledge, ConStrain is the only open-source software framework focused specifically on automated control verification aligned with building energy code and advanced building control guidelines (e.g., ASHRAE 90.1, Guideline 36). It distinguishes itself by offering:

- A growing library of modular, reusable control logic verification tests
- A flexible API for custom verification logic and report generation
- Integration with semantic models [@brick] to enable automated verification case setup
- Compatibility with both simulated and real BAS data sources
- Seamless use in simulation and CI pipelines (e.g., OpenStudio [@os], TSPR [@tspr])

These capabilities enable ConStrain to bridge the gap between simulation-based design intent and real-world implementation, supporting code compliance, model-based commissioning, and continuous performance verification.


# Acknowledgements

ConStrain was developed at the Pacific Northwest National Laboratory and was funded under contract with the U.S. Department of Energy (DOE). It is actively being developed as an open-source project.

# References
