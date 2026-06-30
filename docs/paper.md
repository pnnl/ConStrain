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
  - name: Fan Feng[^1]
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

[^1]: Fan Feng contributed to this work while affiliated with Pacific Northwest National Laboratory (PNNL). He is no longer affiliated with PNNL at the time of publication.

# Summary

The Control Strainer, or `ConStrain`, is a Python-based framework that can be used by energy modelers, building engineers, and researchers to conduct consistent and automated verification of building system controls using either timeseries data generated from whole-building energy simulations or from actual building automation system (BAS) trend data. `ConStrain` is made of two distinct components: an expandable control verification algorithms library, and a consistent performance evaluation and reporting workflow framework. At its roots, `ConStrain`'s verification library was developed with the verification of control related building energy code requirements in mind, but it is built such that its library is expandable and can cover user-customized control verifications.

# Statement of need

Advances in building control have shown significant potential for reducing the cost of utility bills and improving building energy performance. Studies show that designs utilizing optimized controls that are properly tuned could cut commercial building energy consumption by approximately 29% — equivalent to 4-5 Quads, or 4-5% of the energy consumed in the United States [@impa_ctrl]. However, one of the challenges to realizing those savings is the correct implementation of such advanced control strategies and regularly verifying their actual operational performance [@lei2021]. A field study found that only 50% of systems observed have their control system correctly configured, and control-related compliance verification is typically not currently included in the commissioning scope.

`ConStrain` focuses on formalizing and automating verification of HVAC controls by analyzing sensor and actuator data streams from building control systems [@bs2021_30725].

`ConStrain` is an open-source library and a Python application programming interface (API) for analyzing building automation system (BAS) data streams for adherence to an operational specification, which can correspond to the building and building owner's needs [@lei2023ashrae]. Note that this API, in its current form, provides a software interface for other Python programs, not a web REST API service.

`ConStrain` is also incorporating semantic modeling capabilities to enable automated configuration and deployment of verification [@bs2023_1660].

`ConStrain` can be used as a standalone tool and can also be integrated into established workflows of third-party tools and practices. For instance, `ConStrain` has been successfully integrated as part of the continuous integration software development process of whole-building energy simulation-based software tool (e.g., Washington State's Total System Performance Ratio Analysis Tool [@tspr]) to make sure that software code contributions as well as simulation software updates do not have unexpected impacts on the simulated performance of building system controls. Moreover, a set of `OpenStudio` [@os] measures [@osm] have also been developed to enable building energy modelers using `OpenStudio` to have access to perform verification on their models with minimal configurations required.

Currently, `ConStrain` requires each verification case to provide inputs in the same units as the expected data points defined for its verification item. Automatic unit conversion is not in the core workflow of `ConStrain`, so inputs shall be converted to the required units before being passed to `ConStrain`.

## Comparison with existing tools and industry practices

In current industry practices, HVAC control verification is often conducted manually by commissioning agents or facilities teams, or through proprietary trend data analytics solutions integrated into BAS. These tools, while valuable for fault detection and system monitoring, are generally vendor-specific, offer limited transparency, and are not purpose-built to ensure that control strategies intended to deliver energy savings are functioning as intended in actual operation.

`ConStrain` distinguishes itself by offering:

- A growing library of modular, reusable control logic verification tests
- A flexible and local API for custom verification logic and report generation
- Integration with semantic models [@brick] to enable automated verification case setup
- Compatibility with both simulated and real BAS data sources
- Seamless use in simulation and CI pipelines (e.g., OpenStudio [@os], TSPR [@tspr])

These capabilities enable `ConStrain` to bridge the gap between simulation-based design intent and real-world implementation, supporting code compliance, model-based commissioning, and continuous performance verification.

# Acknowledgements

`ConStrain` is developed at the Pacific Northwest National Laboratory and is funded by the U.S. Department of Energy (DOE) under Contract DE-AC05-76RL01830. It is actively being developed as an open-source project.

# References
