---
name: "NEURA Gym RWTH Aachen"
short_name: "NEURA Gym"
order: 10
type: robot
display_types: [robot]
role: "Robot Laboratory"
description: "A newly built facility where robots operate in real-world scenarios, giving the group a testbed for long-horizon autonomy beyond simulation."
specs:
  - label: "Status"
    value: "Newly built"
  - label: "Setting"
    value: "Real-world"
  - label: "Location"
    value: "Aachen"
  - label: "Use"
    value: "Long-horizon tasks"
image: "/assets/images/robots/placeholder-robot.svg"
image_alt: "/assets/images/robots/placeholder-robot-action.svg"
---

The NEURA Gym at RWTH Aachen is a newly built laboratory where robots operate in
real-world scenarios rather than curated benchmarks.

For a group working on long-horizon autonomy, that distinction matters: policies that
look robust in simulation routinely fail when contact, clutter and partial observability
arrive together. The gym exists to surface those failures early.
