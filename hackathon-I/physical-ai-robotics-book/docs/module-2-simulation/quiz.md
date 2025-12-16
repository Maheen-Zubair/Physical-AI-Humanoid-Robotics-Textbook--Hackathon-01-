---
sidebar_position: 7
sidebar_label: "Module 2 Quiz"
title: "Module 2: Checkpoint Quiz"
description: "Test your understanding of robot simulation fundamentals"
keywords: [gazebo, simulation, physics, sdf, sensors, quiz]
---

# Module 2 Checkpoint Quiz

Test your understanding of robot simulation before moving to the next module.

---

## Instructions

- Answer all 10 questions
- Each question has one correct answer
- Review the relevant chapter if you're unsure about an answer
- Aim for at least 80% (8/10) before proceeding to Module 3

---

## Questions

### Question 1: Simulation Benefits

What is the primary advantage of using simulation for robotics development?

- A) Simulations are always more accurate than real-world testing
- B) Safe, fast, and cost-effective testing without risking hardware
- C) Simulations require no setup or configuration
- D) Simulated robots are easier to manufacture

<details>
<summary>Show Answer</summary>

**B) Safe, fast, and cost-effective testing without risking hardware**

Simulation allows testing dangerous maneuvers, running thousands of tests quickly, and avoiding wear on expensive hardware. While simulations have limitations (sim-to-real gap), their safety and speed benefits are the primary advantages.

*Reference: Chapter 2.1 - Introduction to Robot Simulation*
</details>

---

### Question 2: SDF vs URDF

What can SDF describe that URDF cannot?

- A) Robot links and joints
- B) Visual geometry
- C) Complete simulation worlds with multiple models
- D) Collision geometry

<details>
<summary>Show Answer</summary>

**C) Complete simulation worlds with multiple models**

SDF (Simulation Description Format) can describe entire worlds including physics settings, lighting, multiple robots, and environment objects. URDF is limited to describing a single robot model.

*Reference: Chapter 2.2 - Building Worlds with SDF*
</details>

---

### Question 3: Physics Time Step

What happens when you decrease the physics time step (e.g., from 0.01s to 0.001s)?

- A) Simulation becomes faster but less accurate
- B) Simulation becomes slower but more accurate
- C) No change in accuracy or speed
- D) Physics engine is disabled

<details>
<summary>Show Answer</summary>

**B) Simulation becomes slower but more accurate**

A smaller time step means more calculations per second of simulated time, resulting in more accurate physics at the cost of computational speed. This is important for precise contact simulation.

*Reference: Chapter 2.1 - Introduction to Robot Simulation*
</details>

---

### Question 4: Essential Gazebo Plugins

Which plugin is required for Gazebo to run physics simulation?

- A) SceneBroadcaster
- B) UserCommands
- C) Physics
- D) Sensors

<details>
<summary>Show Answer</summary>

**C) Physics**

The Physics system plugin (`gz-sim-physics-system`) is essential for running the physics simulation. Without it, objects won't move or interact. SceneBroadcaster is for visualization, UserCommands for spawning models.

*Reference: Chapter 2.2 - Building Worlds with SDF*
</details>

---

### Question 5: ROS-Gazebo Bridge

What is the purpose of the ROS-Gazebo bridge?

- A) To convert URDF files to SDF format
- B) To connect Gazebo topics to ROS 2 topics for communication
- C) To improve physics simulation accuracy
- D) To render Gazebo graphics on remote displays

<details>
<summary>Show Answer</summary>

**B) To connect Gazebo topics to ROS 2 topics for communication**

The ros_gz_bridge package converts messages between Gazebo transport and ROS 2, allowing ROS 2 nodes to send commands to and receive data from the simulation.

*Reference: Chapter 2.3 - Spawning Robots*
</details>

---

### Question 6: Sensor Noise

Why should you add noise to simulated sensors?

- A) To make the simulation run faster
- B) To prepare algorithms for realistic sensor imperfections
- C) To test if the simulation crashes
- D) Noise is required by Gazebo

<details>
<summary>Show Answer</summary>

**B) To prepare algorithms for realistic sensor imperfections**

Real sensors have noise, drift, and inaccuracies. Adding noise to simulated sensors helps develop algorithms that are robust to these imperfections, improving sim-to-real transfer.

*Reference: Chapter 2.4 - Simulating Robot Sensors*
</details>

---

### Question 7: Collision Geometry

Why should collision geometry be simpler than visual geometry?

- A) Simple geometry looks better in visualization
- B) Gazebo cannot handle complex collision shapes
- C) Simpler collision shapes are faster to compute
- D) Visual geometry must always match collision geometry

<details>
<summary>Show Answer</summary>

**C) Simpler collision shapes are faster to compute**

Collision detection with complex meshes is computationally expensive. Using simplified primitives (boxes, cylinders, spheres) for collision while keeping detailed visual meshes provides good visual quality with fast physics performance.

*Reference: Chapter 2.5 - Physics and Collisions*
</details>

---

### Question 8: Friction Coefficients

A mobile robot's wheels are slipping on a simulated floor. What should you adjust?

- A) Decrease the friction coefficient (mu)
- B) Increase the friction coefficient (mu)
- C) Increase the time step
- D) Remove the collision geometry

<details>
<summary>Show Answer</summary>

**B) Increase the friction coefficient (mu)**

Higher friction coefficients (mu1, mu2) provide more grip between surfaces. Typical rubber-on-concrete friction is 0.8-1.0. Increasing these values will reduce wheel slippage.

*Reference: Chapter 2.5 - Physics and Collisions*
</details>

---

### Question 9: Unity ROS Integration

What package enables Unity to communicate with ROS 2?

- A) Unity Physics
- B) ROS-TCP-Connector
- C) URDF-Importer
- D) ML-Agents

<details>
<summary>Show Answer</summary>

**B) ROS-TCP-Connector**

The ROS-TCP-Connector package from Unity Robotics Hub enables Unity to communicate with ROS 2 through a TCP/IP connection to the ROS-TCP-Endpoint node.

*Reference: Chapter 2.6 - Unity for Robotics*
</details>

---

### Question 10: Coordinate Systems

When converting between ROS and Unity coordinate systems, which axis represents "up"?

- A) X in both ROS and Unity
- B) Y in ROS, Z in Unity
- C) Z in ROS, Y in Unity
- D) Y in both ROS and Unity

<details>
<summary>Show Answer</summary>

**C) Z in ROS, Y in Unity**

ROS uses Z-up (right-handed), while Unity uses Y-up (left-handed). This requires coordinate conversion when transferring positions and orientations between the two systems.

*Reference: Chapter 2.6 - Unity for Robotics*
</details>

---

## Scoring

| Score | Recommendation |
|-------|----------------|
| 10/10 | Excellent! You're ready for Module 3. |
| 8-9/10 | Good understanding. Review any missed topics briefly. |
| 6-7/10 | Review the chapters for questions you missed before continuing. |
| Below 6/10 | Re-read Module 2 chapters and redo hands-on exercises. |

---

## Key Concepts Summary

Before moving to Module 3, ensure you understand:

- [ ] Benefits and limitations of simulation
- [ ] SDF world file structure
- [ ] Spawning robots and bridging to ROS 2
- [ ] Configuring sensors (LIDAR, camera, IMU)
- [ ] Physics parameters and friction tuning
- [ ] Unity-ROS integration basics

---

**Next:** [Module 2 References](./references.md) | [Module 3: NVIDIA Isaac for AI](../module-3-isaac/1-introduction.md)
