---
title: 'pd-parser: A tool for Matching Photodiode Deflection Events to Time-Stamped Events'
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

``pd-parser`` uses mne [@Agramfort2013] to read in an electrophysiology data file with a channel that recorded photodiode events, or takes two channels and does a bipolar rereference, and matches that with time-stamped events (from stimulus timing or button presses for instance) stored in a tab-separated value (tsv) file. Candidate photodiode events are identified based on matching a square-wave template. The best alignment of behavior events relative to photodiode deflection events is then found while accounting for any drift between computer clocks of separate recording devices. Events are excluded where when the difference between the photodiode event and the time-stamped event are greater then a specified threshold. This could be because the monitor's display was hung up or the computer paused task execution to compute background tasks or many other reasons. Events that are timed relative to the event that was timed via the photodiode can then be added. This might be needed because there is only one photodiode channel and multiple events or if the large signal from the photodiode is observed to affect neighboring channels on the amplifier. Finally, the raw data and events data can be saved in brain imagaing data structure (BIDS) format, which allows the behavioral events to be stored in a standardized format without modifying the underlying raw electrophysiology file.

# Statement of need 

As far as we know, there have been no software packages dealing with photodidode and time-stamped event synchronization, despite there being widespread use of photodiodes for task timing. Photodiodes sense luminance and thus can be used for high-precision timing so they provide a powerful method to synchronize recording systems. For example, synchronizing behavioral tasks displayed on a laptop to electrophysiological recordings. While many specially designed research systems are setup to handle triggers to link recordings from separate machines directly, other recording systems, especially clinical systems, lack this capability. In these cases, use of a photodiode offers a robust and reliable method for synchronization. We developed this software package to address our need for intracranial recordings acquired in the epilepsy monitoring unit. Here electrophysiology was acquired using a clinical system and a behavioral task was performed using a laptop brought to the patients bedside. A photodiode placed on the monitor of the laptop was used to detect task-related luminance changes. The photdiode recordings were then digitized by the same clinical recording system which was  used for the electrophysiology recordings.  Due to variablility in refresh rates for monitors, the use of photodiodes is especially helpful for research where precision timing of the display is critical, for example vision or psychophysics research. This software package addresses photodiode synchronization in a comprehensive way so that photodiode parsing can be done by flexibly changing key parameters avoiding writing entirely new scripts. This reduces redundancy, inefficiency and potential for errors.

``pd_parser`` handles complex photodiode parsing for all setups, making it a one-size-fits-all tool for research using photodiode synchronization. Ideal photodiode signals would not require a complex algorithm, but in actual experimental setups, photodiode signals are often more complex. This is especially true in clinical environments where elements of the clinical environment may be outside of experimenter control. Often the baseline value of photodiode may change over time, the plateaus of photodiode events trend back toward baseline and overshoot after event cessation and artifacts contaminate the photodiode signal due to factors. In clincal settings especially, artifacts in the photodiode channel are likely to be caused by movement of the photodiode device, changes in the room lighting, hospital equipment or any number of other issues. This package has robust photodiode event-determination and photodiode-time-stamp alignment algorithms that are validated with both real and simulated photodiode data. The parameters to parse a photodiode channel can be unique to the particular setup (how long the photodiode is on, what the inter-event interval is and what the amplitude of the on period compared to the baseline is), which can be found with an interactive GUI if the default parameters don't work. ``pd-parser`` can accommodate if a researcher choses to synchronize a multi-step task based on one time-stamped event with all other events relative to that event, and it can also handle multiple photodiode-synchronized events parsed seperately, in case a researcher chooses to have trigger the photodiode for each event in a multi-step task. Unpublished, existing algorithms are generally written for specific projects and lack flexibility, leading to the creation of redundant algorithms that, due to this redundancy, are vulnerable to coding errors. Not only does pd-parser offer this flexibility but it also serves a forum where new issues can be identified and addressed by the ``pd-parser`` community. `pd-parser` deals with common issues, and it is a forum where issues can be raised and addressed for situations not yet encountered by the ``pd-parser`` community can be addressed so that they can be fixed once for all groups. Finally, ``pd-parser`` integrates with BIDS [@Gorgolewski2016; @Niso2018; @Pernet2019 @Holdgraf2019] using ``mne-bids ``[@Appelhoff2019] to store the extracted event data in a standardized data structure improving the reproducibility of the project using photodiode data. The well-tested instructions, Application Programming Interface (API) and Command Line Interface (CLI) of `pd-parser` make it easy to use and encourage both careful photodiode synchronization and adoption of the BIDS community standard. Without careful consideration of the early, low-level steps, such as photodiode synchronization, potential errors could be carried forward in subsequent, more complex analyses, causing incorrect conclusions.

# Acknowledgements

We acknowledge support from the Renée James Seed grant to Accelerate Scientific Research from University of Oregon.

# References