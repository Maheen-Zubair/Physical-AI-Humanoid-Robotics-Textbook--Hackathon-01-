---
sidebar_position: 3
sidebar_label: "2.3 Spawning Robots"
title: "Chapter 2.3: Spawning Robots in Simulation"
description: "Learn to spawn robot models from URDF in Gazebo and bridge to ROS 2"
keywords: [gazebo, ros2, urdf, spawn, robot, simulation, bridge]
---

# Spawning Robots in Simulation

In this chapter, you will learn how to spawn robot models in Gazebo and connect them to ROS 2 for control and monitoring.

## From URDF to Simulation

In Module 1, you learned to describe robots with URDF. Now we'll bring those descriptions to life in simulation.

### The Spawning Pipeline

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│    URDF     │───▶│   Gazebo    │───▶│   ROS 2     │
│ Description │    │  Simulation │    │   Bridge    │
└─────────────┘    └─────────────┘    └─────────────┘
       │                  │                  │
       ▼                  ▼                  ▼
   Robot model      Physics &          Topics &
   geometry         sensors            services
```

## Preparing URDF for Gazebo

Gazebo requires additional elements in your URDF for full simulation support.

### Adding Gazebo Tags

```xml
<?xml version="1.0"?>
<robot name="my_robot" xmlns:xacro="http://www.ros.org/wiki/xacro">

  <!-- Standard URDF elements -->
  <link name="base_link">
    <visual>
      <geometry><box size="0.4 0.3 0.1"/></geometry>
      <material name="blue">
        <color rgba="0.2 0.2 0.8 1"/>
      </material>
    </visual>
    <collision>
      <geometry><box size="0.4 0.3 0.1"/></geometry>
    </collision>
    <inertial>
      <mass value="5.0"/>
      <inertia ixx="0.05" ixy="0" ixz="0"
               iyy="0.05" iyz="0" izz="0.05"/>
    </inertial>
  </link>

  <!-- Gazebo-specific elements -->
  <gazebo reference="base_link">
    <material>Gazebo/Blue</material>
    <mu1>0.5</mu1>
    <mu2>0.5</mu2>
  </gazebo>

</robot>
```

### Gazebo Material Colors

```xml
<gazebo reference="link_name">
  <material>Gazebo/Red</material>
</gazebo>
```

Common Gazebo materials:
- `Gazebo/Red`, `Gazebo/Green`, `Gazebo/Blue`
- `Gazebo/White`, `Gazebo/Black`, `Gazebo/Grey`
- `Gazebo/Orange`, `Gazebo/Yellow`
- `Gazebo/Wood`, `Gazebo/Brick`

### Friction Parameters

```xml
<gazebo reference="wheel_link">
  <mu1>1.0</mu1>      <!-- Friction coefficient 1 -->
  <mu2>1.0</mu2>      <!-- Friction coefficient 2 -->
  <kp>1e6</kp>        <!-- Contact stiffness -->
  <kd>100</kd>        <!-- Contact damping -->
</gazebo>
```

## Spawning Methods

### Method 1: Include in World File

Add the robot directly to your SDF world:

```xml
<world name="robot_world">
  <!-- World setup... -->

  <!-- Include robot model -->
  <include>
    <uri>model://my_robot</uri>
    <pose>0 0 0.1 0 0 0</pose>
    <name>robot</name>
  </include>
</world>
```

### Method 2: Spawn Service

Use the Gazebo spawn service from command line:

```bash
# Spawn from URDF file
gz service -s /world/my_world/create \
  --reqtype gz.msgs.EntityFactory \
  --reptype gz.msgs.Boolean \
  --timeout 1000 \
  --req 'sdf_filename: "/path/to/robot.urdf", name: "my_robot"'
```

### Method 3: ROS 2 Spawn Node

The recommended approach for ROS 2 integration:

```python
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess
import os

def generate_launch_description():
    # Get URDF content
    urdf_file = '/path/to/robot.urdf'
    with open(urdf_file, 'r') as f:
        robot_description = f.read()

    return LaunchDescription([
        # Spawn robot in Gazebo
        Node(
            package='ros_gz_sim',
            executable='create',
            arguments=[
                '-name', 'my_robot',
                '-topic', 'robot_description',
                '-x', '0',
                '-y', '0',
                '-z', '0.1',
            ],
            output='screen',
        ),

        # Publish robot description
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_description}],
        ),
    ])
```

## The ROS-Gazebo Bridge

The bridge connects Gazebo topics to ROS 2 topics.

### Installing the Bridge

```bash
sudo apt install ros-humble-ros-gz-bridge
```

### Bridge Configuration

Create a YAML configuration file:

```yaml
# bridge_config.yaml
- topic_name: "/cmd_vel"
  ros_type_name: "geometry_msgs/msg/Twist"
  gz_type_name: "gz.msgs.Twist"
  direction: ROS_TO_GZ

- topic_name: "/odom"
  ros_type_name: "nav_msgs/msg/Odometry"
  gz_type_name: "gz.msgs.Odometry"
  direction: GZ_TO_ROS

- topic_name: "/scan"
  ros_type_name: "sensor_msgs/msg/LaserScan"
  gz_type_name: "gz.msgs.LaserScan"
  direction: GZ_TO_ROS

- topic_name: "/camera/image_raw"
  ros_type_name: "sensor_msgs/msg/Image"
  gz_type_name: "gz.msgs.Image"
  direction: GZ_TO_ROS
```

### Running the Bridge

```bash
# Run with config file
ros2 run ros_gz_bridge parameter_bridge \
  --ros-args -p config_file:=/path/to/bridge_config.yaml

# Or specify topics directly
ros2 run ros_gz_bridge parameter_bridge \
  /cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist
```

### Bridge Direction Syntax

```
/topic@ros_type@gz_type           # Bidirectional
/topic@ros_type@>gz_type          # ROS to Gazebo
/topic@ros_type@<gz_type          # Gazebo to ROS
```

## Complete Launch File

Here's a complete launch file that:
1. Starts Gazebo with a world
2. Spawns a robot
3. Runs the ROS-Gazebo bridge
4. Starts robot state publisher

```python
import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    # Package paths
    pkg_my_robot = get_package_share_directory('my_robot_description')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')

    # Files
    urdf_file = os.path.join(pkg_my_robot, 'urdf', 'robot.urdf')
    world_file = os.path.join(pkg_my_robot, 'worlds', 'test_world.sdf')

    # Read URDF
    with open(urdf_file, 'r') as f:
        robot_description = f.read()

    return LaunchDescription([
        # Launch Gazebo
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
            ),
            launch_arguments={'gz_args': world_file}.items(),
        ),

        # Robot State Publisher
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{'robot_description': robot_description}],
        ),

        # Spawn robot
        Node(
            package='ros_gz_sim',
            executable='create',
            name='spawn_robot',
            arguments=[
                '-name', 'my_robot',
                '-topic', 'robot_description',
                '-x', '0.0',
                '-y', '0.0',
                '-z', '0.1',
            ],
            output='screen',
        ),

        # ROS-Gazebo Bridge
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            name='ros_gz_bridge',
            arguments=[
                '/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
                '/odom@nav_msgs/msg/Odometry@gz.msgs.Odometry',
                '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            ],
            output='screen',
        ),
    ])
```

## Adding Sensors to Your Robot

### LIDAR Sensor

Add a LIDAR sensor to your URDF:

```xml
<!-- LIDAR link -->
<link name="lidar_link">
  <visual>
    <geometry><cylinder radius="0.05" length="0.04"/></geometry>
  </visual>
  <collision>
    <geometry><cylinder radius="0.05" length="0.04"/></geometry>
  </collision>
  <inertial>
    <mass value="0.1"/>
    <inertia ixx="0.001" ixy="0" ixz="0"
             iyy="0.001" iyz="0" izz="0.001"/>
  </inertial>
</link>

<joint name="lidar_joint" type="fixed">
  <parent link="base_link"/>
  <child link="lidar_link"/>
  <origin xyz="0.1 0 0.1" rpy="0 0 0"/>
</joint>

<!-- Gazebo LIDAR plugin -->
<gazebo reference="lidar_link">
  <sensor name="lidar" type="gpu_lidar">
    <pose>0 0 0 0 0 0</pose>
    <topic>scan</topic>
    <update_rate>10</update_rate>
    <lidar>
      <scan>
        <horizontal>
          <samples>360</samples>
          <resolution>1</resolution>
          <min_angle>-3.14159</min_angle>
          <max_angle>3.14159</max_angle>
        </horizontal>
      </scan>
      <range>
        <min>0.1</min>
        <max>10.0</max>
        <resolution>0.01</resolution>
      </range>
    </lidar>
    <always_on>true</always_on>
    <visualize>true</visualize>
  </sensor>
</gazebo>
```

### Camera Sensor

```xml
<!-- Camera link -->
<link name="camera_link">
  <visual>
    <geometry><box size="0.02 0.05 0.05"/></geometry>
  </visual>
  <collision>
    <geometry><box size="0.02 0.05 0.05"/></geometry>
  </collision>
  <inertial>
    <mass value="0.05"/>
    <inertia ixx="0.0001" ixy="0" ixz="0"
             iyy="0.0001" iyz="0" izz="0.0001"/>
  </inertial>
</link>

<joint name="camera_joint" type="fixed">
  <parent link="base_link"/>
  <child link="camera_link"/>
  <origin xyz="0.2 0 0.1" rpy="0 0 0"/>
</joint>

<!-- Gazebo camera plugin -->
<gazebo reference="camera_link">
  <sensor name="camera" type="camera">
    <pose>0 0 0 0 0 0</pose>
    <topic>camera/image_raw</topic>
    <update_rate>30</update_rate>
    <camera>
      <horizontal_fov>1.047</horizontal_fov>
      <image>
        <width>640</width>
        <height>480</height>
        <format>R8G8B8</format>
      </image>
      <clip>
        <near>0.1</near>
        <far>100</far>
      </clip>
    </camera>
    <always_on>true</always_on>
    <visualize>true</visualize>
  </sensor>
</gazebo>
```

### IMU Sensor

```xml
<gazebo reference="base_link">
  <sensor name="imu" type="imu">
    <topic>imu</topic>
    <update_rate>100</update_rate>
    <always_on>true</always_on>
    <imu>
      <angular_velocity>
        <x><noise type="gaussian">
          <mean>0</mean><stddev>0.001</stddev>
        </noise></x>
        <y><noise type="gaussian">
          <mean>0</mean><stddev>0.001</stddev>
        </noise></y>
        <z><noise type="gaussian">
          <mean>0</mean><stddev>0.001</stddev>
        </noise></z>
      </angular_velocity>
      <linear_acceleration>
        <x><noise type="gaussian">
          <mean>0</mean><stddev>0.01</stddev>
        </noise></x>
        <y><noise type="gaussian">
          <mean>0</mean><stddev>0.01</stddev>
        </noise></y>
        <z><noise type="gaussian">
          <mean>0</mean><stddev>0.01</stddev>
        </noise></z>
      </linear_acceleration>
    </imu>
  </sensor>
</gazebo>
```

## Differential Drive Plugin

For wheeled robots, add the differential drive plugin:

```xml
<gazebo>
  <plugin filename="gz-sim-diff-drive-system"
          name="gz::sim::systems::DiffDrive">
    <left_joint>left_wheel_joint</left_joint>
    <right_joint>right_wheel_joint</right_joint>
    <wheel_separation>0.35</wheel_separation>
    <wheel_radius>0.1</wheel_radius>
    <max_linear_acceleration>1.0</max_linear_acceleration>
    <max_angular_acceleration>2.0</max_angular_acceleration>
    <topic>cmd_vel</topic>
    <odom_topic>odom</odom_topic>
    <frame_id>odom</frame_id>
    <child_frame_id>base_link</child_frame_id>
    <odom_publish_frequency>50</odom_publish_frequency>
  </plugin>
</gazebo>
```

## Testing Your Robot

### Verify Spawning

```bash
# List models in simulation
gz model --list

# Get model info
gz model -m my_robot --info
```

### Check ROS 2 Topics

```bash
# List all topics
ros2 topic list

# Check if data is flowing
ros2 topic hz /scan
ros2 topic echo /odom --once
```

### Send Velocity Commands

```bash
# Move forward
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.5}, angular: {z: 0.0}}"

# Rotate
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.0}, angular: {z: 0.5}}"
```

---

## Exercise: Spawn and Control a Robot

Create a complete simulation setup for a differential drive robot.

### Requirements

1. Create a URDF with:
   - Base link (box)
   - Two drive wheels
   - One caster wheel
   - LIDAR sensor
2. Create a world file with obstacles
3. Write a launch file that spawns the robot
4. Configure the ROS-Gazebo bridge
5. Control the robot using `ros2 topic pub`

### Expected Outcome

- Robot spawns in the world
- Robot responds to velocity commands
- LIDAR data is visible in RViz
- Robot avoids obstacles when controlled manually

### Verification

```bash
# Launch simulation
ros2 launch my_robot_sim simulation.launch.py

# In another terminal, check topics
ros2 topic list

# Send movement command
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.2}, angular: {z: 0.1}}" -r 10
```

---

## Summary

Spawning robots in Gazebo involves:

- **Preparing URDF**: Adding Gazebo-specific tags
- **Spawning methods**: World include, service, or ROS 2 node
- **ROS-Gazebo bridge**: Connecting simulation to ROS 2
- **Sensors**: LIDAR, camera, IMU configuration
- **Control plugins**: Differential drive, joint controllers

Key skills learned:
- Enhancing URDF for Gazebo compatibility
- Writing launch files for simulation
- Configuring the ROS-Gazebo bridge
- Adding sensors to simulated robots
- Controlling robots via ROS 2 topics

In the next chapter, you will learn about simulating sensors in detail.

**Next:** [Sensor Simulation](./4-sensors)
