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
date: 4 April 2024
bibliography: paper.bib
---

# Summary

The Control Strainer, or `ConStrain`, is a python-based framework that can be used by energy modelers, building engineers, and researchers to conduct consistent and automated verification of building system controls using either timeseries generated from whole-building energy simulations or from actual building automation system trend data. `ConStrain` is made of three distinct parts: a control verification algorithm library, an automated preparation process and verification case generation, and a standardized performance evaluation and reporting process. At its roots, `ConStrain`'s verification library was developed with the verification of control related building energy code requirements in mind, but it is built such that its library is expandable and can cover any type of customized control verifications.

# Statement of need

Advances in building control have shown significant potential for improving building energy performance and decarbonization. Studies show that designs utilizing optimized controls that are properly tuned could cut commercial building energy consumption by approximately 29% - equivalent to 4-5 Quads, or 4-5% of the energy consumed in the United States [@impa_ctrl]. Driven by the significant control-related energy-saving potential, commercial building energy codes (such as ASHRAE 90.1 [@90.1]) have progressed with many control-related addenda. For example, from the publication of 90.1-2004 to 90.1-2016 (four code cycles), 30% of the new requirements are related to building control (with most of them focused on HVAC system control) [@impl_ctrl].

However, one of the challenges to realizing those savings is the correct implementation of such advanced control strategies and regularly verifying their actual operational performance. A field study found that only 50% of systems observed have their control system correctly configured to meet the energy codes requirement, and control-related compliance verification is typically not included in the commissioning scope. Current control verification is often conducted manually, which is time-consuming, ad-hoc, incomplete, and error-prone.

`ConStrain` can be used as a standalone tool and can also be integrated into existing workflows. `ConStrain` has been successfully integrated as part of the continuous integration software development process of whole-building energy simulation-based software tool (e.g., Washington State's Total System Performance Ratio Analysis Tool [@tspr]) to make sure that software code contributions as well as simulation software updates doesn't affect the simulated performance of building system controls. Moreover, a set of `OpenStudio` [@os] measures have also been developed to provide enable energy modelers using this platform to have access to perform verification on their models with close to no setup.

# Acknowledgements

ConStrain was developed at the Pacific Northwest National Laboratory and was funded under contract with the U.S. Department of Energy (DOE). It is actively being developed as an open-source project.

# References