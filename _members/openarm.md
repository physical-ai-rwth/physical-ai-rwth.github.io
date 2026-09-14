---
name: "OpenArm"
short_name: "OpenArm"
order: 10
type: robot
display_types: [robot]
role: "Bimanual Manipulator — 3 units"
description: "Open-source bimanual arms built for physical AI research in contact-rich settings. Compliant, backdrivable joints make them safe to work alongside and well suited to learning from physical interaction."
specs:
  - label: "Units"
    value: "3"
  - label: "Configuration"
    value: "Bimanual"
  - label: "Joints"
    value: "Backdrivable"
  - label: "Bus"
    value: "CAN-FD"
  - label: "Source"
    value: "Open"
links:
  - label: "openarm.dev"
    url: "https://openarm.dev"
image: "/assets/images/robots/placeholder-robot.svg"
image_alt: "/assets/images/robots/placeholder-robot-action.svg"
---

OpenArm is an open-source bimanual robot arm from [Enactic](https://openarm.dev), built
for physical AI research and deployment in contact-rich environments. CAD, firmware,
control code and simulation tooling are all openly available.

Compliant, backdrivable joints make the arms safe for human-adjacent operation and
well suited to teleoperation with bilateral force feedback — which in turn makes them a
practical source of demonstration data for imitation learning.

*Exact DOF, payload and reach figures are still to be confirmed — the values published
on the vendor's landing page were placeholders at the time of writing.*
