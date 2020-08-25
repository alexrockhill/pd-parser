---
title: 'pd-parser: A tool for Matching Photodiode Events with Behavior'
tags:
  - Python
  - neuroscience
  - electrophysiology
  - psychology
  - behavior
authors:
  - name: Alexander P. Rockhill, 
    orcid: 0000-0003-3868-7453
    affiliation: 1
  - name: Nicole C. Swann
    orcid: 0000-0003-2463-5134
    affiliation: 1
affiliations:
 - name: University of Oregon, Department of Human Physiology
   index: 1
date: 25 August 2020
bibliography: paper.bib
---

# Summary

`pd-parser` takes an electrophysiology data file with one (common reference) or two (bipolar reference) channels that recorded photodiode events and matches that with time-stamped behavior stored in a tab-separated value (tsv) file. Candidate photodiode events are found based on having a square-wave shape, then these events are aligned to the behavior events (accounting for the timing of the photodiode drifting away from the behavior), and then events are excluded where the monitor hung up or the photodiode was different compared to the behavior for any reason. Events that are timed relative to the photodiode can then be added (this method might be a good idea as the large signal from the photodiode has been observed to affect neighboring channels on the amplifier). Finally, the data can be saved to BIDS format, copying over the raw data as is and unconverted (unless it's an unsupported file type by BIDS) and supplying the necessary support files to determine behavior, events and all the other necessary information to analyze the data.

# Statement of need 

Many research groups quickly write a processing script to find events from photodiode data without peer-reviewed validation. This software package addresses photodiode synchronization in a comprehensive way so that photodiode parsing can be done by changing parameters and not by writing an entirely new script. Synchonizing photodiode events with computer-recorded timing of behavior is an incredibly common task in research, where this synchronization is used to ensure correct timing of signal varying over time with regards to a task displayed on a monitor. If the photodiode signal were a flat signal with a perfect square-wave for every event, no complex algorithm would be needed, but unfortunately real photodiode signal is a bit more complex; the baseline value of photodiode changes over time, the plateaus of photodiode events tend to trend back toward baseline and overshoot after event cessation and artifacts contaminate the photodiode signal because of movement of the device, changes in the room lighting or a myriad of other issues which are especially difficult to control in clinical settings. This package has robust event-determination and alignment algorithms that are validated with both real and simulated photodiode data, and the parameters parse a photodiode channel unique to the particular setup can be found with an interactive GUI if the default parameters don't work. Whether a researcher chose to synchronize a multi-step task with several photodiode events on the same channel (different channels works as well), or they synchronized based on one behavioral event with all other events relative to that event, the `pd-parser` software package can accomodate and parse the events. Bespoke algorithms written by many different labs waste time in dealing with one particular of these situations, and then when they are passed on to another group, that group has to modify the script to deal with their own research situation. `pd-parser` deals with common major issues, and it is a forum where issues can be raised for situations not yet encountered by the `pd-parser` community can be addressed so that they can be fixed once for all groups. Finally, `pd-parser` integrates with the Brain Imaging Data Structure (BIDS) to store the extracted event data in a standardized data structure improving the reproducibility of the project using photodiode data. The well-tested instructions, Application Programming Interface (API) and Command Line Interface (CLI) of `pd-parser` make it easy to use and encourage both careful photodiode synchronization and adoption of the BIDS community standard. Without careful consideration of the early, low-level steps, such as photodiode synchronization, complex analyses will be completely misplaced.

# Acknowledgements

We acknowledge support from the Renée James Seed grant.

# References