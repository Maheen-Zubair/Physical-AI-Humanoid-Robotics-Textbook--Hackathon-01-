---
sidebar_position: 1
sidebar_label: "1.1 Introduction"
title: "Chapter 1.1: Introduction to ROS 2"
description: "Learn what ROS 2 is, its history, and how it powers modern robots"
keywords: [ros2, introduction, robotics, middleware, robot operating system]
---

# Introduction to ROS 2

In this chapter, you will learn what the Robot Operating System (ROS) is, why ROS 2 was created, and how it serves as the foundation for modern robotics software development.

## What is ROS?

Despite its name, the Robot Operating System (ROS) is not actually an operating system. Instead, ROS is a **middleware framework** that provides:

- **Communication infrastructure** between software components
- **Hardware abstraction** for sensors and actuators
- **Standard message formats** for common robot data
- **Tools** for debugging, visualization, and simulation
- **Reusable libraries** for common robotics algorithms

Think of ROS as the "glue" that connects all the pieces of a robot's software together. Without ROS, you would need to write custom code to connect every sensor to every algorithm to every actuator. With ROS, each component communicates through standardized interfaces.

### The ROS Philosophy

ROS follows several key design principles:

1. **Modularity**: Software is organized into independent units called *nodes*
2. **Language neutrality**: Nodes can be written in Python, C++, or other languages
3. **Tool-based**: A rich ecosystem of command-line and GUI tools
4. **Open source**: Free to use, modify, and redistribute
5. **Community-driven**: Thousands of packages contributed by researchers and companies

## A Brief History

### ROS 1: The Original (2007-2020)

ROS was originally developed at Stanford University and later at Willow Garage starting in 2007. The first official distribution, *ROS Box Turtle*, was released in 2010.

ROS 1 revolutionized robotics research by providing:
- A common platform for sharing code
- Standard ways to describe robots (URDF)
- Powerful visualization (RViz) and simulation (Gazebo)
- An active community and package ecosystem

However, ROS 1 had limitations:
- **Single-machine focus**: Designed primarily for research robots
- **Best-effort communication**: No guarantees for message delivery
- **Security**: No built-in authentication or encryption
- **Platform support**: Linux-only official support

### ROS 2: The Next Generation (2017-Present)

ROS 2 was built from the ground up to address ROS 1's limitations while maintaining what made ROS successful. Key improvements include:

| Feature | ROS 1 | ROS 2 |
|---------|-------|-------|
| Communication | Custom (TCPROS) | DDS standard |
| Reliability | Best-effort only | Configurable QoS |
| Security | None built-in | DDS Security |
| Platforms | Linux | Linux, Windows, macOS |
| Real-time | Limited | First-class support |
| Lifecycle | None | Managed node lifecycle |

The first ROS 2 distribution, *Ardent Apalone*, was released in December 2017. The current Long Term Support (LTS) version is **Humble Hawksbill**, which this book uses.

## ROS 2 Architecture Overview

Understanding ROS 2's architecture helps you design better robot software. Here are the key components:

### The Computation Graph

ROS 2 applications form a **computation graph** of interconnected processes:

```
┌──────────┐     /camera/image     ┌──────────────┐
│  Camera  │ ──────────────────▶   │   Object     │
│  Driver  │                       │  Detector    │
└──────────┘                       └──────┬───────┘
                                          │
     /cmd_vel                  /detected_objects
        ▲                             │
        │                             ▼
┌──────────┐                   ┌──────────────┐
│  Motor   │ ◀──────────────── │   Planner    │
│  Driver  │     /cmd_vel      │              │
└──────────┘                   └──────────────┘
```

Each box is a **node** (an independent process), and each arrow is a **topic** (a named communication channel).

### DDS: The Communication Layer

ROS 2 uses the **Data Distribution Service (DDS)** standard for communication. DDS provides:

- **Discovery**: Nodes automatically find each other on the network
- **Publish-subscribe**: Decoupled, many-to-many communication
- **Quality of Service (QoS)**: Configurable reliability and latency
- **Security**: Built-in authentication and encryption

You don't need to understand DDS internals to use ROS 2, but knowing it exists helps explain ROS 2's capabilities.

### Key Concepts Preview

Here's a preview of the concepts you will learn in detail in upcoming chapters:

| Concept | Description | Chapter |
|---------|-------------|---------|
| **Node** | An independent process doing one task | 1.2 |
| **Topic** | A named channel for publishing/subscribing messages | 1.3 |
| **Service** | A request-response communication pattern | 1.4 |
| **Action** | A service for long-running tasks with feedback | 1.4 |
| **URDF** | XML format for describing robot geometry | 1.5 |
| **RViz** | 3D visualization tool for robot data | 1.6 |

## Why Use ROS 2?

### Industry Adoption

ROS 2 is used by major robotics companies and research institutions:

- **Amazon Robotics** for warehouse robots
- **NVIDIA** for Isaac Sim integration
- **Boston Dynamics** for Spot robot
- **NASA** for space exploration robots
- **Thousands of research labs** worldwide

### Career Opportunities

ROS skills are highly valued in the robotics job market. Job postings frequently require:
- ROS/ROS 2 experience
- Understanding of topics, services, and actions
- Experience with simulation (Gazebo, Isaac Sim)
- Familiarity with robot description formats (URDF)

### Community and Ecosystem

The ROS ecosystem includes:
- **Thousands of packages** for navigation, manipulation, perception
- **Active forums** at [Robotics Stack Exchange](https://robotics.stackexchange.com/)
- **Annual conferences** (ROSCon) with tutorials and talks
- **Detailed documentation** at [docs.ros.org](https://docs.ros.org/)

## Setting Up Your Mental Model

As you progress through this module, think of ROS 2 like a robot's nervous system:

- **Nodes** are like neurons - specialized cells doing specific tasks
- **Topics** are like nerve impulses - carrying signals between neurons
- **Services** are like reflexes - quick request-response patterns
- **Actions** are like complex behaviors - coordinated multi-step processes

Just as your nervous system allows different parts of your body to communicate and coordinate, ROS 2 allows different parts of a robot to work together.

---

## Exercise: Explore ROS 2

Before writing any code, let's explore ROS 2's command-line tools.

### Step 1: Verify Installation

Open a terminal and confirm ROS 2 is installed:

```bash
ros2 --version
echo $ROS_DISTRO
```

You should see the ROS 2 version and "humble" as the distribution.

### Step 2: List Available Nodes

Run the example talker node in one terminal:

```bash
ros2 run demo_nodes_cpp talker
```

In another terminal, list running nodes:

```bash
ros2 node list
```

You should see `/talker` in the output.

### Step 3: Inspect a Topic

List available topics:

```bash
ros2 topic list
```

Echo messages on the `/chatter` topic:

```bash
ros2 topic echo /chatter
```

You should see "Hello World" messages appearing.

### Step 4: Get Topic Information

Get detailed information about the topic:

```bash
ros2 topic info /chatter
ros2 interface show std_msgs/msg/String
```

### Expected Outcome

After completing this exercise, you should understand:
- How to verify ROS 2 is installed and working
- How to run example nodes
- How to list and inspect nodes and topics
- That nodes communicate by publishing and subscribing to topics

---

## Summary

ROS 2 is a middleware framework that provides the communication infrastructure for robot software. It evolved from ROS 1 to address limitations in reliability, security, and platform support. The key concepts - nodes, topics, services, and actions - form a computation graph that connects all parts of a robot's software. This standardized approach enables code reuse, community collaboration, and faster development of complex robot systems.

**Next:** [Nodes and the Computation Graph](./2-nodes.md)
