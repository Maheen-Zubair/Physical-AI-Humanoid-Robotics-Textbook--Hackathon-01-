---
sidebar_position: 5
sidebar_label: "1.5 URDF"
title: "Chapter 1.5: Robot Description with URDF"
description: "Learn to describe robot geometry using the Unified Robot Description Format"
keywords: [ros2, urdf, robot description, links, joints, xml]
---

# Robot Description with URDF

In this chapter, you will learn how to describe a robot's physical structure using URDF (Unified Robot Description Format).

## What is URDF?

**URDF** is an XML format that describes:

- **Links**: Rigid bodies (robot parts)
- **Joints**: Connections between links
- **Visual geometry**: How the robot looks
- **Collision geometry**: Shapes used for collision detection
- **Inertial properties**: Mass and moments of inertia

URDF is used by:
- RViz for visualization
- Gazebo for simulation
- Motion planning algorithms
- Robot state publishers

## URDF Structure

A basic URDF file looks like this:

```xml
<?xml version="1.0"?>
<robot name="my_robot">
  <!-- Links define rigid bodies -->
  <link name="base_link">
    <!-- Visual, collision, and inertial properties -->
  </link>

  <link name="wheel">
    <!-- Visual, collision, and inertial properties -->
  </link>

  <!-- Joints connect links -->
  <joint name="base_to_wheel" type="continuous">
    <parent link="base_link"/>
    <child link="wheel"/>
    <!-- Joint properties -->
  </joint>
</robot>
```

## Links

A **link** represents a single rigid body. It has three main components:

### Visual Properties

Define how the link looks in visualization tools:

```xml
<link name="base_link">
  <visual>
    <geometry>
      <box size="0.5 0.3 0.1"/>  <!-- Width, depth, height in meters -->
    </geometry>
    <origin xyz="0 0 0.05" rpy="0 0 0"/>  <!-- Position and rotation -->
    <material name="blue">
      <color rgba="0 0 0.8 1"/>  <!-- Red, green, blue, alpha -->
    </material>
  </visual>
</link>
```

### Collision Properties

Define the shape used for collision detection (often simplified):

```xml
<link name="base_link">
  <collision>
    <geometry>
      <box size="0.5 0.3 0.1"/>
    </geometry>
    <origin xyz="0 0 0.05" rpy="0 0 0"/>
  </collision>
</link>
```

### Inertial Properties

Define mass and moments of inertia for physics simulation:

```xml
<link name="base_link">
  <inertial>
    <mass value="10.0"/>  <!-- kg -->
    <origin xyz="0 0 0.05" rpy="0 0 0"/>
    <inertia ixx="0.1" ixy="0" ixz="0"
             iyy="0.1" iyz="0" izz="0.1"/>
  </inertial>
</link>
```

### Geometry Types

URDF supports several geometry primitives:

```xml
<!-- Box: width, depth, height -->
<box size="1.0 0.5 0.25"/>

<!-- Cylinder: radius, length -->
<cylinder radius="0.1" length="0.5"/>

<!-- Sphere: radius -->
<sphere radius="0.2"/>

<!-- Mesh: external 3D model -->
<mesh filename="package://my_robot/meshes/body.stl" scale="1.0 1.0 1.0"/>
```

## Joints

A **joint** connects two links and defines their relative motion.

### Joint Types

| Type | Description | DOF |
|------|-------------|-----|
| `fixed` | No motion allowed | 0 |
| `revolute` | Rotation with limits | 1 |
| `continuous` | Rotation without limits | 1 |
| `prismatic` | Linear sliding | 1 |
| `floating` | Free motion in 6DOF | 6 |
| `planar` | Motion in a plane | 3 |

### Joint Properties

```xml
<joint name="wheel_joint" type="continuous">
  <parent link="base_link"/>
  <child link="wheel"/>
  <origin xyz="0.2 0 0" rpy="0 1.5708 0"/>  <!-- Position and orientation -->
  <axis xyz="0 0 1"/>  <!-- Rotation axis -->
</joint>
```

For `revolute` and `prismatic` joints, add limits:

```xml
<joint name="arm_joint" type="revolute">
  <parent link="body"/>
  <child link="arm"/>
  <origin xyz="0 0 0.5" rpy="0 0 0"/>
  <axis xyz="0 1 0"/>
  <limit lower="-1.57" upper="1.57"    <!-- Radians -->
         effort="100" velocity="1.0"/>  <!-- Max torque/force, max velocity -->
</joint>
```

## Building a Simple Robot

Let's create a simple two-wheeled robot step by step.

### Step 1: Define the Base

```xml
<?xml version="1.0"?>
<robot name="simple_robot">

  <!-- Base link -->
  <link name="base_link">
    <visual>
      <geometry>
        <box size="0.4 0.3 0.1"/>
      </geometry>
      <material name="blue">
        <color rgba="0.2 0.2 0.8 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <box size="0.4 0.3 0.1"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="5.0"/>
      <inertia ixx="0.05" ixy="0" ixz="0"
               iyy="0.05" iyz="0" izz="0.05"/>
    </inertial>
  </link>
```

### Step 2: Add Wheels

```xml
  <!-- Left wheel -->
  <link name="left_wheel">
    <visual>
      <geometry>
        <cylinder radius="0.1" length="0.05"/>
      </geometry>
      <material name="black">
        <color rgba="0.1 0.1 0.1 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <cylinder radius="0.1" length="0.05"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="0.5"/>
      <inertia ixx="0.001" ixy="0" ixz="0"
               iyy="0.001" iyz="0" izz="0.001"/>
    </inertial>
  </link>

  <!-- Right wheel (same structure) -->
  <link name="right_wheel">
    <visual>
      <geometry>
        <cylinder radius="0.1" length="0.05"/>
      </geometry>
      <material name="black">
        <color rgba="0.1 0.1 0.1 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <cylinder radius="0.1" length="0.05"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="0.5"/>
      <inertia ixx="0.001" ixy="0" ixz="0"
               iyy="0.001" iyz="0" izz="0.001"/>
    </inertial>
  </link>
```

### Step 3: Connect with Joints

```xml
  <!-- Left wheel joint -->
  <joint name="left_wheel_joint" type="continuous">
    <parent link="base_link"/>
    <child link="left_wheel"/>
    <origin xyz="0 0.175 0" rpy="-1.5708 0 0"/>
    <axis xyz="0 0 1"/>
  </joint>

  <!-- Right wheel joint -->
  <joint name="right_wheel_joint" type="continuous">
    <parent link="base_link"/>
    <child link="right_wheel"/>
    <origin xyz="0 -0.175 0" rpy="-1.5708 0 0"/>
    <axis xyz="0 0 1"/>
  </joint>

</robot>
```

## Coordinate Frames

Understanding coordinate frames is essential:

- **Origin**: Each link has an origin at its joint connection point
- **Axes**: X (forward), Y (left), Z (up) - ROS convention
- **rpy**: Roll, pitch, yaw in radians

```
       Z (up)
       │
       │
       └───── Y (left)
      /
     /
    X (forward)
```

The `origin` element positions a child relative to its parent:

```xml
<origin xyz="x y z" rpy="roll pitch yaw"/>
```

## Robot State Publisher

The **robot_state_publisher** node:
- Reads URDF
- Subscribes to joint states
- Publishes coordinate frame transforms (TF)

Launch it with:

```bash
ros2 run robot_state_publisher robot_state_publisher --ros-args -p robot_description:="$(cat robot.urdf)"
```

Or in a launch file:

```python
from launch import LaunchDescription
from launch_ros.actions import Node
import os

def generate_launch_description():
    urdf_file = os.path.join(
        get_package_share_directory('my_robot'),
        'urdf', 'robot.urdf')

    with open(urdf_file, 'r') as f:
        robot_description = f.read()

    return LaunchDescription([
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_description}]
        ),
    ])
```

## Joint State Publisher

For testing without a real robot, use **joint_state_publisher_gui**:

```bash
ros2 run joint_state_publisher_gui joint_state_publisher_gui
```

This provides sliders to manually set joint positions.

## URDF in a Package

Organize your robot description in a package:

```
my_robot_description/
├── package.xml
├── setup.py
├── urdf/
│   └── robot.urdf
├── meshes/
│   └── body.stl
└── launch/
    └── display.launch.py
```

### Display Launch File

```python
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import Command
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    pkg_path = get_package_share_directory('my_robot_description')
    urdf_file = os.path.join(pkg_path, 'urdf', 'robot.urdf')

    with open(urdf_file, 'r') as f:
        robot_description = f.read()

    return LaunchDescription([
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_description}]
        ),
        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-d', os.path.join(pkg_path, 'rviz', 'display.rviz')]
        ),
    ])
```

## URDF Validation

Check your URDF for errors:

```bash
# Install check_urdf tool
sudo apt install liburdfdom-tools

# Check URDF
check_urdf robot.urdf

# Visualize link tree
urdf_to_graphiz robot.urdf
```

---

## Exercise: Add a Caster Wheel

Extend the simple robot with a caster wheel at the back.

### Requirements

1. Add a `caster_link` (sphere, radius 0.05m)
2. Connect to `base_link` with a `fixed` joint
3. Position at the back of the robot
4. Verify in RViz

### Solution

```xml
<!-- Caster wheel -->
<link name="caster_wheel">
  <visual>
    <geometry>
      <sphere radius="0.05"/>
    </geometry>
    <material name="gray">
      <color rgba="0.5 0.5 0.5 1"/>
    </material>
  </visual>
  <collision>
    <geometry>
      <sphere radius="0.05"/>
    </geometry>
  </collision>
  <inertial>
    <mass value="0.2"/>
    <inertia ixx="0.0001" ixy="0" ixz="0"
             iyy="0.0001" iyz="0" izz="0.0001"/>
  </inertial>
</link>

<joint name="caster_joint" type="fixed">
  <parent link="base_link"/>
  <child link="caster_wheel"/>
  <origin xyz="-0.15 0 -0.05" rpy="0 0 0"/>
</joint>
```

---

## Summary

URDF describes robot structure using:

- **Links**: Rigid bodies with visual, collision, and inertial properties
- **Joints**: Connections with specified motion types
- **Geometry**: Boxes, cylinders, spheres, and meshes
- **Origins**: Position and orientation in 3D space

Key tools for working with URDF:
- `robot_state_publisher`: Publishes transforms
- `joint_state_publisher_gui`: Test joint positions
- `check_urdf`: Validate URDF syntax
- RViz: Visualize the robot model

In the next chapter, you will learn to visualize your robot and sensor data in RViz.

**Next:** [Visualization with RViz](./6-rviz.md)
