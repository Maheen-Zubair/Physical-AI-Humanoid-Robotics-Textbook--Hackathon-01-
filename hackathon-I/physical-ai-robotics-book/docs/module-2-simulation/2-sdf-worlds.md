---
sidebar_position: 2
sidebar_label: "2.2 SDF Worlds"
title: "Chapter 2.2: Building Worlds with SDF"
description: "Learn to create simulation environments using the Simulation Description Format"
keywords: [gazebo, sdf, simulation, worlds, models, xml]
---

# Building Worlds with SDF

In this chapter, you will learn how to create simulation environments using SDF (Simulation Description Format), the standard format for describing worlds and models in Gazebo.

## What is SDF?

**SDF** (Simulation Description Format) is an XML format that describes:

- **Worlds**: Complete simulation environments
- **Models**: Robots and objects
- **Lights**: Illumination sources
- **Actors**: Animated entities
- **Physics**: Simulation parameters

SDF is more powerful than URDF because it can describe entire worlds, not just robots.

### SDF vs URDF

| Feature | URDF | SDF |
|---------|------|-----|
| Describes | Single robot | Entire world |
| Multiple models | No | Yes |
| Physics settings | No | Yes |
| Lighting | No | Yes |
| Sensors | Limited | Comprehensive |
| Plugins | Limited | Full support |

## Basic World Structure

A minimal SDF world:

```xml
<?xml version="1.0" ?>
<sdf version="1.8">
    <world name="my_world">

        <!-- Physics configuration -->
        <physics name="1ms" type="ignored">
            <max_step_size>0.001</max_step_size>
            <real_time_factor>1.0</real_time_factor>
        </physics>

        <!-- Required plugins -->
        <plugin filename="gz-sim-physics-system"
                name="gz::sim::systems::Physics">
        </plugin>
        <plugin filename="gz-sim-user-commands-system"
                name="gz::sim::systems::UserCommands">
        </plugin>
        <plugin filename="gz-sim-scene-broadcaster-system"
                name="gz::sim::systems::SceneBroadcaster">
        </plugin>

        <!-- Lighting -->
        <light type="directional" name="sun">
            <cast_shadows>true</cast_shadows>
            <pose>0 0 10 0 0 0</pose>
            <diffuse>0.8 0.8 0.8 1</diffuse>
            <specular>0.2 0.2 0.2 1</specular>
            <direction>-0.5 0.1 -0.9</direction>
        </light>

        <!-- Ground plane -->
        <model name="ground_plane">
            <static>true</static>
            <link name="link">
                <collision name="collision">
                    <geometry>
                        <plane>
                            <normal>0 0 1</normal>
                        </plane>
                    </geometry>
                </collision>
                <visual name="visual">
                    <geometry>
                        <plane>
                            <normal>0 0 1</normal>
                            <size>100 100</size>
                        </plane>
                    </geometry>
                    <material>
                        <ambient>0.8 0.8 0.8 1</ambient>
                        <diffuse>0.8 0.8 0.8 1</diffuse>
                    </material>
                </visual>
            </link>
        </model>

    </world>
</sdf>
```

## Essential World Plugins

Every Gazebo world needs these system plugins:

### Physics System

Runs the physics simulation:

```xml
<plugin filename="gz-sim-physics-system"
        name="gz::sim::systems::Physics">
</plugin>
```

### User Commands

Enables spawning and moving models:

```xml
<plugin filename="gz-sim-user-commands-system"
        name="gz::sim::systems::UserCommands">
</plugin>
```

### Scene Broadcaster

Publishes scene state for visualization:

```xml
<plugin filename="gz-sim-scene-broadcaster-system"
        name="gz::sim::systems::SceneBroadcaster">
</plugin>
```

## Physics Configuration

Configure physics parameters for your simulation:

```xml
<physics name="fast_physics" type="ignored">
    <!-- Time step in seconds -->
    <max_step_size>0.001</max_step_size>

    <!-- Ratio of sim time to real time -->
    <real_time_factor>1.0</real_time_factor>

    <!-- Gravity vector (m/s^2) -->
    <gravity>0 0 -9.81</gravity>
</physics>
```

### Physics Parameters

| Parameter | Description | Typical Value |
|-----------|-------------|---------------|
| `max_step_size` | Time step (seconds) | 0.001 |
| `real_time_factor` | Speed multiplier | 1.0 |
| `gravity` | Gravity vector | 0 0 -9.81 |

### Real-Time Factor

- `1.0` = Real-time
- `0.5` = Half speed (slow motion)
- `2.0` = Double speed
- `0.0` = As fast as possible

## Creating Models

Models are the objects in your world.

### Static vs Dynamic Models

```xml
<!-- Static model: doesn't move -->
<model name="table">
    <static>true</static>
    <link name="link">
        <!-- geometry -->
    </link>
</model>

<!-- Dynamic model: affected by physics -->
<model name="ball">
    <static>false</static>  <!-- or omit; false is default -->
    <link name="link">
        <!-- geometry with inertia -->
    </link>
</model>
```

### Link Geometry

Links contain visual and collision geometry:

```xml
<link name="box_link">
    <!-- What it looks like -->
    <visual name="visual">
        <geometry>
            <box>
                <size>1.0 0.5 0.25</size>
            </box>
        </geometry>
        <material>
            <ambient>0.2 0.5 0.8 1</ambient>
            <diffuse>0.2 0.5 0.8 1</diffuse>
        </material>
    </visual>

    <!-- Physics collision shape -->
    <collision name="collision">
        <geometry>
            <box>
                <size>1.0 0.5 0.25</size>
            </box>
        </geometry>
    </collision>

    <!-- Mass and inertia for dynamics -->
    <inertial>
        <mass>5.0</mass>
        <inertia>
            <ixx>0.1</ixx>
            <iyy>0.2</iyy>
            <izz>0.15</izz>
        </inertia>
    </inertial>
</link>
```

### Geometry Primitives

```xml
<!-- Box: width × depth × height -->
<box><size>1.0 0.5 0.25</size></box>

<!-- Cylinder: radius and length -->
<cylinder>
    <radius>0.1</radius>
    <length>0.5</length>
</cylinder>

<!-- Sphere: radius -->
<sphere><radius>0.2</radius></sphere>

<!-- Mesh: external 3D model -->
<mesh>
    <uri>model://my_robot/meshes/body.dae</uri>
    <scale>1 1 1</scale>
</mesh>
```

## Positioning Objects

Use the `<pose>` element to position objects:

```xml
<pose>x y z roll pitch yaw</pose>
```

- **x, y, z**: Position in meters
- **roll, pitch, yaw**: Rotation in radians

### Examples

```xml
<!-- 2 meters forward, 1 meter up -->
<pose>2 0 1 0 0 0</pose>

<!-- Rotated 90° around Z axis -->
<pose>0 0 0 0 0 1.5708</pose>

<!-- Tilted 45° forward -->
<pose>0 0 0.5 0 0.785 0</pose>
```

### Relative Poses

Position relative to another frame:

```xml
<pose relative_to="base_link">0.5 0 0.2 0 0 0</pose>
```

## Lighting

Good lighting is essential for camera sensors and visualization.

### Directional Light (Sun)

```xml
<light type="directional" name="sun">
    <cast_shadows>true</cast_shadows>
    <pose>0 0 10 0 0 0</pose>
    <diffuse>0.8 0.8 0.8 1</diffuse>
    <specular>0.2 0.2 0.2 1</specular>
    <attenuation>
        <range>1000</range>
        <constant>0.9</constant>
        <linear>0.01</linear>
        <quadratic>0.001</quadratic>
    </attenuation>
    <direction>-0.5 0.1 -0.9</direction>
</light>
```

### Point Light

```xml
<light type="point" name="lamp">
    <pose>0 0 3 0 0 0</pose>
    <diffuse>1 1 0.9 1</diffuse>
    <specular>0.1 0.1 0.1 1</specular>
    <attenuation>
        <range>20</range>
        <constant>0.5</constant>
        <linear>0.01</linear>
        <quadratic>0.001</quadratic>
    </attenuation>
</light>
```

### Spot Light

```xml
<light type="spot" name="spotlight">
    <pose>0 0 5 0 0 0</pose>
    <diffuse>1 1 1 1</diffuse>
    <specular>0.1 0.1 0.1 1</specular>
    <direction>0 0 -1</direction>
    <spot>
        <inner_angle>0.3</inner_angle>
        <outer_angle>0.5</outer_angle>
        <falloff>1.0</falloff>
    </spot>
</light>
```

## Including Models

Include models from files or Fuel:

### From Local File

```xml
<include>
    <uri>model://my_robot</uri>
    <pose>0 0 0 0 0 0</pose>
    <name>robot_1</name>
</include>
```

### From Gazebo Fuel

```xml
<include>
    <uri>https://fuel.gazebosim.org/1.0/OpenRobotics/models/Coke Can</uri>
    <pose>1 0 0.5 0 0 0</pose>
</include>
```

## Building a Complete World

Let's create a warehouse environment:

```xml
<?xml version="1.0" ?>
<sdf version="1.8">
    <world name="warehouse">

        <!-- Physics -->
        <physics name="1ms" type="ignored">
            <max_step_size>0.001</max_step_size>
            <real_time_factor>1.0</real_time_factor>
        </physics>

        <!-- Plugins -->
        <plugin filename="gz-sim-physics-system"
                name="gz::sim::systems::Physics"/>
        <plugin filename="gz-sim-user-commands-system"
                name="gz::sim::systems::UserCommands"/>
        <plugin filename="gz-sim-scene-broadcaster-system"
                name="gz::sim::systems::SceneBroadcaster"/>

        <!-- Lighting -->
        <light type="directional" name="sun">
            <cast_shadows>true</cast_shadows>
            <pose>0 0 10 0 0 0</pose>
            <diffuse>0.8 0.8 0.8 1</diffuse>
            <specular>0.2 0.2 0.2 1</specular>
            <direction>-0.5 0.1 -0.9</direction>
        </light>

        <!-- Floor -->
        <model name="floor">
            <static>true</static>
            <link name="link">
                <collision name="collision">
                    <geometry>
                        <plane><normal>0 0 1</normal></plane>
                    </geometry>
                </collision>
                <visual name="visual">
                    <geometry>
                        <plane>
                            <normal>0 0 1</normal>
                            <size>20 20</size>
                        </plane>
                    </geometry>
                    <material>
                        <ambient>0.5 0.5 0.5 1</ambient>
                        <diffuse>0.5 0.5 0.5 1</diffuse>
                    </material>
                </visual>
            </link>
        </model>

        <!-- Wall 1 -->
        <model name="wall_north">
            <static>true</static>
            <pose>0 10 1.5 0 0 0</pose>
            <link name="link">
                <collision name="collision">
                    <geometry>
                        <box><size>20 0.2 3</size></box>
                    </geometry>
                </collision>
                <visual name="visual">
                    <geometry>
                        <box><size>20 0.2 3</size></box>
                    </geometry>
                    <material>
                        <ambient>0.7 0.7 0.7 1</ambient>
                    </material>
                </visual>
            </link>
        </model>

        <!-- Wall 2 -->
        <model name="wall_south">
            <static>true</static>
            <pose>0 -10 1.5 0 0 0</pose>
            <link name="link">
                <collision name="collision">
                    <geometry>
                        <box><size>20 0.2 3</size></box>
                    </geometry>
                </collision>
                <visual name="visual">
                    <geometry>
                        <box><size>20 0.2 3</size></box>
                    </geometry>
                    <material>
                        <ambient>0.7 0.7 0.7 1</ambient>
                    </material>
                </visual>
            </link>
        </model>

        <!-- Shelving unit -->
        <model name="shelf_1">
            <static>true</static>
            <pose>5 0 1 0 0 0</pose>
            <link name="link">
                <collision name="collision">
                    <geometry>
                        <box><size>0.5 3 2</size></box>
                    </geometry>
                </collision>
                <visual name="visual">
                    <geometry>
                        <box><size>0.5 3 2</size></box>
                    </geometry>
                    <material>
                        <ambient>0.6 0.4 0.2 1</ambient>
                        <diffuse>0.6 0.4 0.2 1</diffuse>
                    </material>
                </visual>
            </link>
        </model>

        <!-- Box on floor -->
        <model name="cardboard_box">
            <pose>2 2 0.25 0 0 0.3</pose>
            <link name="link">
                <collision name="collision">
                    <geometry>
                        <box><size>0.4 0.4 0.5</size></box>
                    </geometry>
                </collision>
                <visual name="visual">
                    <geometry>
                        <box><size>0.4 0.4 0.5</size></box>
                    </geometry>
                    <material>
                        <ambient>0.7 0.5 0.3 1</ambient>
                        <diffuse>0.7 0.5 0.3 1</diffuse>
                    </material>
                </visual>
                <inertial>
                    <mass>2.0</mass>
                    <inertia>
                        <ixx>0.05</ixx>
                        <iyy>0.05</iyy>
                        <izz>0.03</izz>
                    </inertia>
                </inertial>
            </link>
        </model>

    </world>
</sdf>
```

## Launching Your World

### Command Line

```bash
# Launch the world
gz sim warehouse.sdf

# With verbose output
gz sim -v 4 warehouse.sdf

# Headless (no GUI)
gz sim -s warehouse.sdf
```

### From ROS 2 Launch File

```python
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')

    world_file = os.path.join(
        get_package_share_directory('my_robot_sim'),
        'worlds', 'warehouse.sdf')

    return LaunchDescription([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
            ),
            launch_arguments={'gz_args': world_file}.items(),
        ),
    ])
```

---

## Exercise: Create a Test Environment

Create an SDF world for robot navigation testing.

### Requirements

1. Create a file `navigation_test.sdf`
2. Include:
   - Ground plane (10m × 10m)
   - Four walls forming a boundary
   - Three obstacles (boxes) at different positions
   - Appropriate lighting
3. Save and launch in Gazebo

### Expected Outcome

- World loads without errors
- All objects are visible
- Obstacles are correctly positioned
- Physics simulation runs when started

### Verification Commands

```bash
# Launch your world
gz sim navigation_test.sdf

# Check for errors
gz sim -v 4 navigation_test.sdf
```

---

## Summary

SDF is the standard format for Gazebo simulation worlds:

- **World structure**: Physics, plugins, lights, models
- **Models**: Collections of links with geometry
- **Poses**: Position and orientation in 3D space
- **Lighting**: Directional, point, and spot lights
- **Includes**: Reference external models

Key skills learned:
- Creating basic SDF world files
- Configuring physics parameters
- Adding static and dynamic models
- Positioning objects with poses
- Setting up lighting

In the next chapter, you will learn to spawn robots in your simulation world and integrate with ROS 2.

**Next:** [Spawning Robots](./3-spawning-robots.md)
