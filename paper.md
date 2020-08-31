---
title: 'pd-parser: A tool for Matching Photodiode Deflections with Time-Stamp Events'
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

`pd-parser` takes an electrophysiology data file with one or two channels (common reference re-referenced to bipolar) that recorded photodiode events and matches that with time-stamped events (from stimulus timing or button presses for instance) stored in a tab-separated value (tsv) file. Candidate photodiode events are found based on having a square-wave shape, then these events are aligned to the behavior events (accounting for the timing of the photodiode drifting away from the behavior), and then events are excluded where when the difference between the photodiode and time-stamped event are greater then a specified threshold. This could be because the monitor's display was hung up or the computer paused task execution to compute background tasks or many other reasons. Events that are timed relative to the event that was timed via the photodiode can then be added. This might be needed because there is only one photodiode channel and multiple events or if the large signal from the photodiode is observed to affect neighboring channels on the amplifier. Finally, the data can be saved in brain imagaing data structure (BIDS) format, copying over the raw data as is (conversion only happens if the electrophysiology data file is of a type unsupported by BIDS) and supplying the necessary support files to determine behavior, events and all the other necessary information to analyze the data (such as channel locations, date, etc.).

# Statement of need 

As far as we know, there have been no software packages dealing with photodidode and time-stamped event synchronization, despite there being widespread use of photodiodes for task timing. Synchonizing photodiode events with computer-recorded timing of behavior is an incredibly common need in research, where this synchronization is used to ensure correct timing of signal varying over time with respect to a task displayed on a computer monitor. For any setup where the recording equipment cannot handle event triggers, photodiode timing may be the only option for synchronization. This is often the case for intracranial recordings in many epilespy monitoring units, and other clincal recording situations, where a channel can be used for recording the photodiode instead of electrophysiology signal. For research dealing with precision timing of the display on a monitor, such as research in vision, using a photodiode is essential for timing of the greatest possible accuracy. Psychophysical tasks are another large area of research where a photodiode is often used when precise timing is needed. This software package addresses photodiode synchronization in a comprehensive way so that photodiode parsing can be done by flexibly changing key parameters avoidy writing entirely new scripts. Many research groups write their own processing script to find events from photodiode data, creating redundancy, inefficiency and a considerable potential for errors.

`pd_parser` handles complex photodiode parsing for the vast majority of existing and conceivable setups, making it a one-size-fits-all tool for research using photodiode synchronization. If the photodiode signal were a flat signal with a perfect square-wave for every event, no complex algorithm would be needed, but, unfortunately, in actual experimental setups, photodiode signal is usually a bit more complex; the baseline value of photodiode changes over time, the plateaus of photodiode events tend to trend back toward baseline and overshoot after event cessation and artifacts contaminate the photodiode signal due to factors such as movement of the device, changes in the room lighting or a myriad of other issues. These factors are especially difficult to control in clinical settings. This package has robust photodiode event-determination and photodiode-time-stamp alignment algorithms that are validated with both real and simulated photodiode data. The parameters to parse a photodiode channel can be unique to the particular setup (how long the photodiode is on, what the inter-event interval is and what the ampltidude compared to the baseline is), and these parameters can't be found until you've recognized a photodiode event but a photodiode event can't be positively identified with assurance without the parameters. Thus, since it is prohibitively computationally intensive to try all combinations of these parameters for full automation, these key parameters can be found with an interactive GUI if the default parameters don't work. Whether a researcher chose to synchronize a multi-step task with several photodiode events on the same channel or different channels works as well, or they synchronized based on one behavioral event with all other events relative to that event, the `pd-parser` software package can accomodate and parse the events. Unpublished, existing algorithms are generally written for specific projects and lack flexibility, leading to the creation of redundant algorithms that, due to this redundancy, are vulnerable to coding errors. Not only does pd-parser offer this flexibility but it also serves a forum where new issues can be identified and addressed by the `pd-parser` community. `pd-parser` deals with common major issues, and it is a forum where issues can be raised for situations not yet encountered by the `pd-parser` community can be addressed so that they can be fixed once for all groups. Finally, `pd-parser` integrates with BIDS to store the extracted event data in a standardized data structure improving the reproducibility of the project using photodiode data. The well-tested instructions, Application Programming Interface (API) and Command Line Interface (CLI) of `pd-parser` make it easy to use and encourage both careful photodiode synchronization and adoption of the BIDS community standard. Without careful consideration of the early, low-level steps, such as photodiode synchronization, potential errors could be carried forward in subsequent, more complex analyses, causing incorrect conclusions.

# Acknowledgements

We acknowledge support from the Renée James Seed grant.

# References