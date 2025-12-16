---
sidebar_position: 7
sidebar_label: "Module 1 Quiz"
title: "Module 1: Checkpoint Quiz"
description: "Test your understanding of ROS 2 fundamentals"
keywords: [ros2, quiz, assessment, nodes, topics, services, actions, urdf]
---

# Module 1 Checkpoint Quiz

Test your understanding of ROS 2 fundamentals before moving to the next module.

---

## Instructions

- Answer all 10 questions
- Each question has one correct answer unless marked as "select all that apply"
- Review the relevant chapter if you're unsure about an answer
- Aim for at least 80% (8/10) before proceeding to Module 2

---

## Questions

### Question 1: ROS 2 Architecture

What is the underlying communication middleware used by ROS 2?

- A) TCP/IP sockets
- B) DDS (Data Distribution Service)
- C) ZeroMQ
- D) HTTP REST

<details>
<summary>Show Answer</summary>

**B) DDS (Data Distribution Service)**

ROS 2 uses DDS as its middleware, providing reliable, real-time communication with built-in discovery. This is a major architectural change from ROS 1, which used a custom protocol with a central master node.

*Reference: Chapter 1.1 - Introduction to ROS 2*
</details>

---

### Question 2: Node Fundamentals

In the following code, what is the purpose of `rclpy.spin(node)`?

```python
rclpy.init(args=args)
node = MyNode()
rclpy.spin(node)
```

- A) Creates a new thread for the node
- B) Continuously processes callbacks and incoming messages
- C) Sends the node to all other nodes in the network
- D) Initializes the node's parameters

<details>
<summary>Show Answer</summary>

**B) Continuously processes callbacks and incoming messages**

`rclpy.spin()` is the main event loop that keeps the node running and processing incoming messages, timer callbacks, and service requests. Without spinning, the node won't respond to any communication.

*Reference: Chapter 1.2 - Nodes and the Computation Graph*
</details>

---

### Question 3: Topic Communication

Which statement about ROS 2 topics is TRUE?

- A) Only one publisher can publish to a topic
- B) Subscribers must register with publishers before receiving messages
- C) Multiple publishers and subscribers can share the same topic
- D) Topics can only carry primitive data types

<details>
<summary>Show Answer</summary>

**C) Multiple publishers and subscribers can share the same topic**

Topics implement a many-to-many publish-subscribe pattern. Any number of publishers can send to a topic, and any number of subscribers can receive from it. Publishers and subscribers are decoupled - they don't need to know about each other.

*Reference: Chapter 1.3 - Topics and Publishers/Subscribers*
</details>

---

### Question 4: Message Types

What message type would you use to send velocity commands to a mobile robot?

- A) `std_msgs/msg/Float64`
- B) `geometry_msgs/msg/Twist`
- C) `nav_msgs/msg/Odometry`
- D) `sensor_msgs/msg/JointState`

<details>
<summary>Show Answer</summary>

**B) `geometry_msgs/msg/Twist`**

`geometry_msgs/msg/Twist` contains linear and angular velocity components (x, y, z for each), making it ideal for commanding robot motion. The `/cmd_vel` topic typically uses this message type.

*Reference: Chapter 1.3 - Topics and Publishers/Subscribers*
</details>

---

### Question 5: Quality of Service

When would you use a "Best Effort" QoS reliability policy instead of "Reliable"?

- A) When sending critical control commands
- B) When high-frequency sensor data loss is acceptable
- C) When guaranteed delivery is required
- D) When the network is unreliable

<details>
<summary>Show Answer</summary>

**B) When high-frequency sensor data loss is acceptable**

Best Effort QoS (like UDP) is appropriate for high-frequency sensor data where occasional packet loss is acceptable and low latency is more important than guaranteed delivery. Camera streams and LIDAR data often use Best Effort.

*Reference: Chapter 1.3 - Topics and Publishers/Subscribers*
</details>

---

### Question 6: Services vs Topics

A robot needs to query its current battery level. Which communication pattern is most appropriate?

- A) Topic - publish battery level continuously
- B) Service - request/response for current level
- C) Action - long-running battery check
- D) Parameter - store battery level

<details>
<summary>Show Answer</summary>

**B) Service - request/response for current level**

A service is ideal for quick queries where you need a single response. While continuous battery monitoring might use a topic, a one-time query is better suited to the service request-response pattern.

*Reference: Chapter 1.4 - Services and Actions*
</details>

---

### Question 7: Actions

Which of the following is NOT a component of a ROS 2 action?

- A) Goal
- B) Feedback
- C) Result
- D) Acknowledgment

<details>
<summary>Show Answer</summary>

**D) Acknowledgment**

ROS 2 actions have three components: Goal (what you want to achieve), Feedback (progress updates during execution), and Result (final outcome). While goals are accepted or rejected, "Acknowledgment" is not a formal action component.

*Reference: Chapter 1.4 - Services and Actions*
</details>

---

### Question 8: URDF Structure

In URDF, what connects two links and defines their relative motion?

- A) Connector
- B) Joint
- C) Transform
- D) Constraint

<details>
<summary>Show Answer</summary>

**B) Joint**

Joints connect links in URDF and define how they can move relative to each other. Joint types include fixed (no motion), revolute (rotation with limits), continuous (unlimited rotation), and prismatic (linear motion).

*Reference: Chapter 1.5 - Robot Description with URDF*
</details>

---

### Question 9: URDF Joint Types

A robot wheel that can rotate continuously without limits should use which joint type?

- A) `revolute`
- B) `continuous`
- C) `prismatic`
- D) `floating`

<details>
<summary>Show Answer</summary>

**B) `continuous`**

A `continuous` joint allows unlimited rotation around an axis - perfect for wheels. A `revolute` joint also rotates but has defined upper and lower limits, making it suitable for joints like elbows that have a limited range of motion.

*Reference: Chapter 1.5 - Robot Description with URDF*
</details>

---

### Question 10: RViz Visualization

In RViz, what does the "Fixed Frame" setting determine?

- A) Which robot link cannot move
- B) The reference frame for all visualization
- C) The camera position
- D) Which displays are visible

<details>
<summary>Show Answer</summary>

**B) The reference frame for all visualization**

The Fixed Frame is the reference coordinate frame for the entire RViz display. All other frames and visualizations are positioned relative to this frame. Common choices include `map` (global), `odom` (odometry-based), or `base_link` (robot-centric).

*Reference: Chapter 1.6 - Visualization with RViz*
</details>

---

## Scoring

| Score | Recommendation |
|-------|----------------|
| 10/10 | Excellent! You're ready for Module 2. |
| 8-9/10 | Good understanding. Review any missed topics briefly. |
| 6-7/10 | Review the chapters for questions you missed before continuing. |
| Below 6/10 | Re-read Module 1 chapters and redo hands-on exercises. |

---

## Key Concepts Summary

Before moving to Module 2, ensure you understand:

- [ ] ROS 2 architecture and DDS middleware
- [ ] Creating nodes with rclpy
- [ ] Publishing and subscribing to topics
- [ ] When to use services vs actions vs topics
- [ ] URDF structure: links, joints, and geometry
- [ ] Visualizing robots and data in RViz

---

**Next:** [Module 1 References](./references.md) | [Module 2: Simulation with Gazebo](../module-2-simulation/1-introduction.md)
