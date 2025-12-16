---
sidebar_position: 99
sidebar_label: "Citation Template"
title: "References Template"
description: "APA citation format template for module references sections"
keywords: [references, citations, apa, template]
---

# References Template

This document provides the standard format for citing sources in this book. Each module contains a `references.md` file following this template.

## Citation Format

This book uses **APA 7th Edition** format for citations. References are collected at the module level rather than per-chapter to reduce repetition.

## In-Text Citations

When referencing official documentation within chapter text, use inline markdown links:

```markdown
According to the [ROS 2 documentation](https://docs.ros.org/en/humble/), nodes are
the fundamental building blocks of robot applications.
```

This keeps the content readable while providing direct access to sources.

## Module References Section Format

Each module's `references.md` should follow this structure:

```markdown
---
sidebar_position: 99
sidebar_label: "References"
title: "Module X References"
description: "Sources and citations for Module X content"
---

# Module X References

## Official Documentation

- Author/Organization. (Year). *Title of documentation*. URL

## Academic Papers

- Author, A. A., & Author, B. B. (Year). Title of article. *Journal Name*,
  Volume(Issue), pages. https://doi.org/xxxxx

## Books

- Author, A. A. (Year). *Title of book* (Edition). Publisher.

## Software and Tools

- Organization. (Year). *Software name* (Version X.X) [Computer software]. URL
```

## Example References (Module 1)

Here is an example of how Module 1 references should be formatted:

```markdown
# Module 1 References

## Official Documentation

- Open Robotics. (2024). *ROS 2 Documentation: Humble Hawksbill*.
  https://docs.ros.org/en/humble/

- Open Robotics. (2024). *rclpy API Reference*.
  https://docs.ros2.org/latest/api/rclpy/

- Open Robotics. (2024). *URDF Specification*.
  https://wiki.ros.org/urdf/XML

## Academic Papers

- Macenski, S., Foote, T., Gerkey, B., Lalancette, C., & Woodall, W. (2022).
  Robot Operating System 2: Design, architecture, and uses in the wild.
  *Science Robotics*, 7(66), eabm6074.
  https://doi.org/10.1126/scirobotics.abm6074

## Books

- Koubaa, A. (Ed.). (2023). *Robot Operating System (ROS): The Complete
  Reference* (Volume 7). Springer.

## Software and Tools

- Open Robotics. (2024). *ROS 2 Humble Hawksbill* (Version 2024.01)
  [Computer software]. https://docs.ros.org/en/humble/
```

## Common Sources by Module

### Module 1: ROS 2

| Source | Type | URL |
|--------|------|-----|
| ROS 2 Humble Docs | Official | https://docs.ros.org/en/humble/ |
| rclpy API | API Ref | https://docs.ros2.org/latest/api/rclpy/ |
| URDF Spec | Spec | https://wiki.ros.org/urdf/XML |
| TF2 Docs | Official | https://docs.ros.org/en/humble/Concepts/About-Tf2.html |

### Module 2: Simulation

| Source | Type | URL |
|--------|------|-----|
| Gazebo Fortress Docs | Official | https://gazebosim.org/docs/fortress |
| ros_gz Bridge | Official | https://github.com/gazebosim/ros_gz |
| Unity Robotics Hub | Official | https://github.com/Unity-Technologies/Unity-Robotics-Hub |
| SDF Specification | Spec | http://sdformat.org/spec |

### Module 3: NVIDIA Isaac

| Source | Type | URL |
|--------|------|-----|
| Isaac Sim Docs | Official | https://docs.omniverse.nvidia.com/isaacsim/ |
| Isaac ROS | Official | https://nvidia-isaac-ros.github.io/ |
| Omniverse | Official | https://docs.omniverse.nvidia.com/ |

### Module 4: VLA

| Source | Type | URL |
|--------|------|-----|
| OpenAI Whisper | Official | https://github.com/openai/whisper |
| Whisper Paper | Paper | https://arxiv.org/abs/2212.04356 |

## Verification Requirements

Per FR-007, all technical claims must be verifiable against official documentation. When writing chapters:

1. **Cite the source** for any specific technical claim
2. **Include version numbers** when behavior is version-specific
3. **Link to official docs** rather than third-party tutorials
4. **Update citations** if documentation URLs change

## Notes for Contributors

- Always verify URLs are accessible before submitting
- Use archived links (web.archive.org) for potentially unstable URLs
- Prefer official documentation over blog posts or tutorials
- Include access dates for frequently updated sources
