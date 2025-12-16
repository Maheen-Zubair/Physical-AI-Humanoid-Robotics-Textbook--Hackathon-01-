---
sidebar_position: 3
sidebar_label: "Hardware Guide"
title: "Hardware Reference Guide"
description: "Recommended hardware for Physical AI & Humanoid Robotics development"
keywords: [hardware, robotics, ai, computing, sensors, actuators]
---

# Hardware Reference Guide

This guide provides recommendations for hardware components used in Physical AI and humanoid robotics development, from simulation workstations to physical robot platforms.

## Computing Platforms

### Development Workstations

#### Minimum Requirements
- **CPU**: Intel i7-10700K or AMD Ryzen 7 3700X (8 cores, 16 threads)
- **RAM**: 32 GB DDR4
- **GPU**: NVIDIA RTX 3070 (8GB VRAM)
- **Storage**: 1 TB NVMe SSD
- **OS**: Ubuntu 22.04 LTS or Windows 10/11

#### Recommended for AI Training
- **CPU**: Intel i9-13900K or AMD Ryzen 9 7950X (16+ cores)
- **RAM**: 64-128 GB DDR4/DDR5
- **GPU**: NVIDIA RTX 4090 (24GB VRAM) or RTX 6000 Ada
- **Storage**: 2+ TB NVMe SSD (multiple drives recommended)
- **Network**: 10GbE for multi-machine setups

#### High-Performance Computing
- **GPU Cluster**: Multiple RTX 6000 Ada or H100 GPUs
- **Interconnect**: NVLink or InfiniBand for multi-GPU training
- **Cooling**: Liquid cooling for sustained performance
- **Power**: 2000W+ PSU for multi-GPU systems

### Edge Computing for Robots

#### NVIDIA Jetson Platforms
| Model | GPU | CPU | RAM | AI Performance | Use Case |
|-------|-----|-----|-----|----------------|----------|
| Jetson Nano | 128-core Maxwell | Quad-core ARM A57 | 4GB | 0.5 TOPS | Basic perception |
| Jetson TX2 | 256-core Pascal | Dual Denver 2 + Quad ARM A57 | 8GB | 1.3 TOPS | Mobile robots |
| Jetson Xavier NX | 384-core Volta | Hex-core ARM Carmel | 8GB | 21 TOPS | Manipulation |
| Jetson AGX Orin | 2048-core Ada | 12-core ARM Hercules | 32GB | 275 TOPS | Humanoid robots |

#### Alternative Edge Platforms
- **Intel Neural Compute Stick 2**: USB-based inference for prototyping
- **Google Coral TPU**: Edge TPU for TensorFlow Lite models
- **Myriad X VPU**: Intel's vision processing unit for camera processing
- **RPi 4 + Google Coral**: Low-cost edge AI development

## Robot Platforms

### Educational Robots

#### TurtleBot Series
- **TurtleBot 4**: ROS 2 compatible, Intel NUC, Realsense D435i
- **TurtleBot 3 Burger**: Low-cost differential drive, OpenManipulator
- **Use cases**: Navigation, manipulation, SLAM education

#### Clearpath Robotics Platforms
- **Jackal**: Outdoor UGV, ROS 2 support, modular sensors
- **Husky**: Heavy-duty UGV, 75kg payload, GPS/RTK support
- **CPR**: Indoor AMR, customizable for research applications

### Research-Grade Manipulators

#### Universal Robots
- **UR3/UR5/UR10**: 3kg/5kg/10kg payload, collaborative robots
- **Advantages**: Easy programming, ROS 2 support, large community
- **Limitations**: Speed limitations, payload constraints

#### Franka Emika Panda
- **Payload**: 3kg with collision detection
- **Advantages**: Torque control, precise manipulation, research-focused
- **Limitations**: Expensive, limited payload

#### KUKA LBR iiwa
- **Payload**: 7kg/14kg options, 7 DOF
- **Advantages**: High precision, torque sensing, research applications
- **Limitations**: Complex setup, high cost

### Humanoid Robot Platforms

#### Popular Humanoid Platforms
| Platform | Height | DOF | Payload | Price Range | Use Case |
|----------|--------|-----|---------|-------------|----------|
| NAO | 58cm | 25 | 0.3kg | $10k-15k | Education, research |
| Pepper | 120cm | 20 | - | $20k-25k | Social robotics |
| Romeo | 140cm | 37 | - | $100k+ | Research |
| Atlas | 180cm | 28+ | - | $2M+ | Advanced research |
| Digit | 170cm | 24 | 10kg | $200k+ | Commercial applications |

#### DIY Humanoid Options
- **InMoov**: Open-source 3D printable humanoid
- **Poppy**: Open-source research humanoid
- **Robobo**: Educational humanoid with smartphone brain

## Sensors

### Vision Sensors

#### RGB-D Cameras
| Model | Resolution | FPS | Depth Tech | Price | Notes |
|-------|------------|-----|------------|-------|-------|
| Intel Realsense D435 | 1280×720 | 30 | Stereo | $150 | Popular for robotics |
| Realsense D435i | 1280×720 | 30 | Stereo + IMU | $200 | Includes IMU |
| Realsense D455 | 2560×1440 | 90 | Stereo | $400 | Higher resolution |
| Azure Kinect | 2048×1536 | 30 | ToF | $400 | Time-of-flight |
| Orbbec Astra Pro | 1280×720 | 30 | Stereo | $100 | Budget option |

#### High-End Vision Systems
- **FLIR Blackfly**: Industrial cameras with global shutter
- **Basler ace**: High-speed cameras for dynamic applications
- **Point Grey Grasshopper**: Professional machine vision

### LIDAR Sensors

#### 2D LIDAR
| Model | Range | Accuracy | Price | Use |
|-------|-------|----------|-------|-----|
| Hokuyo URG-04LX | 4m | ±30mm | $1000 | Indoor navigation |
| Sick TIM551 | 10m | ±20mm | $1500 | Industrial |
| Slamtec RPLIDAR A3 | 25m | ±30mm | $400 | Budget option |
| YDLIDAR X4 | 10m | ±20mm | $150 | Hobby projects |

#### 3D LIDAR
- **Velodyne VLP-16**: 100m range, 0.1° resolution, $8000
- **Ouster OS1**: Solid-state, 120m range, $8000
- **Hesai PandarQT**: 240m range, automotive-grade, $1500

### Inertial Measurement Units (IMU)

#### IMU Options
| Model | Accel | Gyro | Mag | Price | Notes |
|-------|-------|------|-----|-------|-------|
| Bosch BNO055 | ±16g | ±2000°/s | 3D | $25 | Integrated sensor fusion |
| ADIS16470 | ±1800g | ±2000°/s | 3D | $300 | High-performance |
| MTi-3 | ±16g | ±2000°/s | 3D | $2000 | Industrial grade |
| Pixhawk IMU | ±16g | ±2000°/s | 3D | $100 | Drone/robot flight controller |

### Tactile Sensors

#### Force/Torque Sensors
- **ATI F/T Sensors**: High-precision, various ranges, $5000+
- **Robotiq FT300**: Collaborative robot compatible, $2000
- **OnRobot FG10-150**: Gripper-integrated force sensing, $1500

#### Tactile Skin
- **BioTac**: Biomimetic tactile sensing, $5000/sensor
- **GelSight**: Optical tactile sensing, research grade
- **Barrett Tactile Sensors**: Integrated with Barrett hands

## Actuators and Motors

### Servo Motors

#### Hobby-Grade Servos
| Type | Torque | Speed | Feedback | Price | Use |
|------|--------|-------|----------|-------|-----|
| MG996R | 10kg·cm | 0.14s/60° | Position only | $15 | Low-cost robots |
| Dynamixel AX-12 | 1.5kg·cm | 0.17s/60° | Position, load, temp | $100 | Educational |
| Dynamixel XL430 | 1.1kg·cm | 0.14s/60° | Position, velocity, load | $80 | Modern servos |

#### High-Performance Servos
- **Dynamixel X-Series**: Position, velocity, current control
- **Herkulex**: CAN bus communication, high resolution
- **Futaba**: High-torque options for larger robots

### Brushless DC Motors

#### Motor Controllers
- **ODrive**: Dual motor controller, position/velocity/current control
- **SimpleFOC**: Open-source BLDC control library
- **RoboClaw**: Dual motor controller with encoder feedback

#### Motor Specifications
- **KV Rating**: RPM per volt (high KV = fast, low torque)
- **Continuous Current**: Determines sustained torque output
- **Encoder Resolution**: Position feedback accuracy

## End-Effectors

### Grippers

#### Parallel Jaw Grippers
| Model | Stroke | Force | Control | Price |
|-------|--------|-------|---------|-------|
| Robotiq 2F-85 | 85mm | 235N | ROS 2 | $3500 |
| Robotiq 2F-140 | 140mm | 60N | ROS 2 | $3500 |
| OnRobot RG2 | 70mm | 60N | ROS 2 | $2000 |
| SRT SimpleGripper | 50mm | 20N | ROS 2 | $800 |

#### Specialized Grippers
- **Adaptive Grippers**: Accommodate various object shapes
- **Suction Cups**: For flat objects, lightweight
- **Three-Finger Hands**: Multi-dexterity, complex manipulation
- **Underactuated Hands**: Mechanical adaptation to object shape

## Communication Hardware

### Network Infrastructure

#### Ethernet for Robotics
- **CAT6/CAT6a**: Standard for robot networks
- **Industrial Ethernet**: Ruggedized for factory environments
- **PoE**: Power over Ethernet for cameras and sensors

#### Wireless Communication
- **WiFi 6**: For high-bandwidth data transmission
- **5G**: Low-latency control, emerging technology
- **Bluetooth**: Short-range sensor communication
- **Zigbee**: Mesh networking for sensor networks

### Fieldbus Systems
- **CAN Bus**: Standard automotive/industrial communication
- **EtherCAT**: Real-time industrial Ethernet
- **PROFINET**: Industrial automation protocol

## Power Systems

### Battery Technologies

#### Lithium-based Batteries
| Type | Voltage | Energy Density | Cycle Life | Use Case |
|------|---------|----------------|------------|----------|
| Li-ion | 3.7V | 250 Wh/kg | 500-1000 | General robotics |
| LiFePO4 | 3.2V | 180 Wh/kg | 2000+ | Safety-critical |
| LiPo | 3.7V | 265 Wh/kg | 300-500 | High-power applications |

#### Power Management
- **Voltage Regulators**: Step-down for sensitive electronics
- **Power Distribution**: Fused distribution boards
- **Battery Management Systems**: Protection and monitoring

## Safety Hardware

### Emergency Systems
- **Emergency Stop Buttons**: Red mushroom switches, category 0
- **Safety Light Curtains**: Perimeter protection
- **Pressure Mats**: Area monitoring
- **Safety PLCs**: Monitored safety systems

### Collision Detection
- **Force/Torque Sensors**: Collision detection in end-effectors
- **Proximity Sensors**: Prevent collisions with environment
- **Torque Limiting**: Intrinsic collision safety in joints

## Tools and Accessories

### Mechanical Assembly
- **Aluminum Extrusions**: 80/20, Misumi, Bosch Rexroth
- **Linear Guides**: For precise linear motion
- **Timing Belts**: For power transmission
- **Bearings**: For smooth rotational motion

### Electronics Tools
- **Multimeter**: Essential for debugging
- **Oscilloscope**: Signal analysis
- **Logic Analyzer**: Digital signal debugging
- **Soldering Station**: Electronics assembly

### Mechanical Tools
- **Calipers**: Precision measurement
- **Levels**: Ensuring proper alignment
- **Torque Wrenches**: Proper fastener torque
- **3D Printer**: Rapid prototyping

## Integration Considerations

### Mounting and Integration
- **Standard Mounting Patterns**: Use industry standards when possible
- **Cable Management**: Prevent entanglement and wear
- **EMI/RFI Shielding**: Protect sensitive electronics
- **Thermal Management**: Cooling for high-power components

### Environmental Protection
- **IP Ratings**: Protection from dust and water
- **Temperature Range**: Operational limits
- **Shock/Vibration**: Mounting for dynamic environments
- **EMC Compliance**: Electromagnetic compatibility

## Budget Considerations

### Cost-Effective Approaches
- **Used Equipment**: Academic surplus, manufacturer returns
- **DIY Solutions**: 3D printing, open-source hardware
- **Educational Discounts**: Many manufacturers offer academic pricing
- **Phased Purchases**: Start with minimum viable setup

### Total Cost of Ownership
- **Initial Purchase**: Hardware costs
- **Maintenance**: Replacement parts, calibration
- **Training**: Learning curves for complex systems
- **Upgrades**: Technology refresh cycles

---

**Next:** [Installation Appendix](./installation.md)
