---
sidebar_position: 100
sidebar_label: "Software Versions"
title: "Target Software Versions"
description: "Canonical reference for all software versions used in this book"
keywords: [versions, software, ros2, gazebo, unity, isaac]
---

# Target Software Versions

This document serves as the **single source of truth** for all software versions referenced throughout this book. All code examples, installation instructions, and compatibility notes are based on these specific versions.

## Primary Software Stack

| Software | Version | Release Type | Purpose |
|----------|---------|--------------|---------|
| **Ubuntu** | 22.04 LTS | Long Term Support | Primary development OS |
| **ROS 2** | Humble Hawksbill | LTS (EOL: May 2027) | Robot middleware |
| **Python** | 3.10+ | Standard | Programming language |
| **Gazebo** | Fortress (LTS) | Long Term Support | Physics simulation |
| **Unity** | 2022 LTS | Long Term Support | 3D visualization |
| **NVIDIA Isaac Sim** | 2023.1.1+ | Latest stable | AI-powered simulation |
| **OpenAI Whisper** | Latest | Rolling | Speech recognition |

## Why These Versions?

### Ubuntu 22.04 LTS

- **Jammy Jellyfish** is the recommended platform for ROS 2 Humble
- Long-term support until April 2027
- Wide hardware and software compatibility

### ROS 2 Humble Hawksbill

- LTS release with support until May 2027
- Stable API for production robotics
- Best documentation and community support
- Default choice for new robotics projects

### Gazebo Fortress

- LTS release with long-term support
- Excellent ROS 2 integration via ros_gz
- Modern physics engines (DART, Bullet)
- Active development and bug fixes

### Unity 2022 LTS

- Long-term support version
- Stable Unity Robotics Hub integration
- Compatible with ROS-TCP-Connector
- Mature tooling and documentation

### NVIDIA Isaac Sim 2023.1.1+

- Latest stable release at time of writing
- Full Omniverse integration
- GPU-accelerated simulation
- Built-in ROS 2 bridge

## Version Compatibility Matrix

| Component | Minimum | Recommended | Maximum Tested |
|-----------|---------|-------------|----------------|
| Ubuntu | 20.04 | **22.04** | 24.04 |
| ROS 2 | Iron | **Humble** | Jazzy |
| Python | 3.8 | **3.10** | 3.12 |
| Gazebo | Garden | **Fortress** | Harmonic |
| NVIDIA Driver | 525.x | **535.x** | 545.x |
| CUDA | 11.8 | **12.1** | 12.3 |

## Checking Your Versions

Run these commands to verify your installed versions:

```bash
# Ubuntu version
lsb_release -a

# ROS 2 version
echo $ROS_DISTRO
ros2 --version

# Python version
python3 --version

# Gazebo version
gz sim --version

# NVIDIA driver version
nvidia-smi
```

## Updating This Document

This document should be updated when:

1. New LTS versions are released
2. Breaking changes occur in dependencies
3. EOL dates are reached
4. New recommended configurations are identified

Last updated: 2024
