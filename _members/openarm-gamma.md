---
name: "OpenArm Gamma"
short_name: "Gamma"
order: 12
type: robot
display_types: [robot]
role: "Bimanual Manipulator"
description: "Open-source bimanual arm with backdrivable joints."
specs:
  - label: "Unit"
    value: "Gamma"
  - label: "Version"
    value: "v1.1"
  - label: "Configuration"
    value: "Bimanual"
  - label: "Joints"
    value: "Backdrivable"
  - label: "Source"
    value: "Open"
links:
  - label: "openarm.dev"
    url: "https://openarm.dev"
image: "/assets/images/robots/openarm.svg"
image_alt: "/assets/images/robots/openarm-action.svg"
---

Kept free for teleoperation and data collection.

OpenArm is an open-source bimanual robot arm from [Enactic](https://openarm.dev), built
for physical AI research and deployment in contact-rich environments. CAD, firmware,
control code and simulation tooling are all openly available.

Compliant, backdrivable joints make it safe for human-adjacent operation and well suited
to teleoperation with bilateral force feedback — which in turn makes it a practical source
of demonstration data for imitation learning.

*Exact DOF, payload and reach are still to be confirmed: the figures published on the
vendor's landing page were placeholders at the time of writing.*
