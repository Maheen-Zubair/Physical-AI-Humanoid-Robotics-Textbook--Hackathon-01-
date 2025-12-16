---
sidebar_position: 4
sidebar_label: "2.4 Sensors"
title: "Chapter 2.4: Simulating Robot Sensors"
description: "Learn to add and configure realistic sensor simulations including cameras, LIDAR, and IMU"
keywords: [gazebo, sensors, lidar, camera, imu, simulation, noise]
---

# Simulating Robot Sensors

In this chapter, you will learn how to simulate various robot sensors in Gazebo, including cameras, LIDAR, IMU, and contact sensors, with realistic noise models.

## Why Simulate Sensors?

Real robots perceive the world through sensors. Simulating sensors accurately is crucial for:

- **Algorithm development**: Test perception algorithms before deployment
- **Noise handling**: Design filters for realistic sensor noise
- **Sensor fusion**: Combine multiple sensor modalities
- **Edge cases**: Test scenarios that are hard to create physically

## Sensor Types in Gazebo

Gazebo supports a wide variety of sensors:

| Sensor Type | Description | Output |
|-------------|-------------|--------|
| Camera | RGB images | sensor_msgs/Image |
| Depth Camera | RGB + depth | sensor_msgs/Image, PointCloud2 |
| LIDAR | Laser range finder | sensor_msgs/LaserScan |
| 3D LIDAR | Point cloud scanner | sensor_msgs/PointCloud2 |
| IMU | Orientation & acceleration | sensor_msgs/Imu |
| Contact | Collision detection | gazebo_msgs/ContactsState |
| GPS | Global position | sensor_msgs/NavSatFix |
| Magnetometer | Magnetic field | sensor_msgs/MagneticField |

## Camera Sensors

### Basic RGB Camera

```xml
<gazebo reference="camera_link">
  <sensor name="camera" type="camera">
    <always_on>true</always_on>
    <update_rate>30</update_rate>
    <topic>camera/image_raw</topic>

    <camera>
      <!-- Field of view in radians -->
      <horizontal_fov>1.047</horizontal_fov>

      <!-- Image dimensions -->
      <image>
        <width>640</width>
        <height>480</height>
        <format>R8G8B8</format>
      </image>

      <!-- Clipping planes -->
      <clip>
        <near>0.1</near>
        <far>100</far>
      </clip>

      <!-- Lens distortion (optional) -->
      <distortion>
        <k1>0.0</k1>
        <k2>0.0</k2>
        <k3>0.0</k3>
        <p1>0.0</p1>
        <p2>0.0</p2>
        <center>0.5 0.5</center>
      </distortion>
    </camera>
  </sensor>
</gazebo>
```

### Depth Camera (RGBD)

```xml
<gazebo reference="depth_camera_link">
  <sensor name="depth_camera" type="depth_camera">
    <always_on>true</always_on>
    <update_rate>15</update_rate>
    <topic>depth_camera</topic>

    <camera>
      <horizontal_fov>1.047</horizontal_fov>
      <image>
        <width>640</width>
        <height>480</height>
        <format>R8G8B8</format>
      </image>
      <clip>
        <near>0.1</near>
        <far>10.0</far>
      </clip>
    </camera>
  </sensor>
</gazebo>
```

### Camera Noise

Add realistic noise to camera images:

```xml
<camera>
  <!-- ... other settings ... -->
  <noise>
    <type>gaussian</type>
    <mean>0.0</mean>
    <stddev>0.007</stddev>
  </noise>
</camera>
```

## LIDAR Sensors

### 2D LIDAR (Laser Scanner)

```xml
<gazebo reference="lidar_link">
  <sensor name="lidar" type="gpu_lidar">
    <always_on>true</always_on>
    <update_rate>10</update_rate>
    <topic>scan</topic>
    <visualize>true</visualize>

    <lidar>
      <scan>
        <horizontal>
          <!-- Number of rays -->
          <samples>360</samples>
          <!-- Angular resolution -->
          <resolution>1</resolution>
          <!-- Field of view -->
          <min_angle>-3.14159</min_angle>
          <max_angle>3.14159</max_angle>
        </horizontal>
      </scan>
      <range>
        <!-- Range limits in meters -->
        <min>0.12</min>
        <max>10.0</max>
        <!-- Distance resolution -->
        <resolution>0.01</resolution>
      </range>
      <noise>
        <type>gaussian</type>
        <mean>0.0</mean>
        <stddev>0.01</stddev>
      </noise>
    </lidar>
  </sensor>
</gazebo>
```

### 3D LIDAR (Point Cloud)

```xml
<gazebo reference="lidar_3d_link">
  <sensor name="lidar_3d" type="gpu_lidar">
    <always_on>true</always_on>
    <update_rate>10</update_rate>
    <topic>points</topic>
    <visualize>true</visualize>

    <lidar>
      <scan>
        <horizontal>
          <samples>1800</samples>
          <resolution>1</resolution>
          <min_angle>-3.14159</min_angle>
          <max_angle>3.14159</max_angle>
        </horizontal>
        <vertical>
          <samples>16</samples>
          <resolution>1</resolution>
          <min_angle>-0.2618</min_angle>
          <max_angle>0.2618</max_angle>
        </vertical>
      </scan>
      <range>
        <min>0.5</min>
        <max>100.0</max>
        <resolution>0.01</resolution>
      </range>
      <noise>
        <type>gaussian</type>
        <mean>0.0</mean>
        <stddev>0.02</stddev>
      </noise>
    </lidar>
  </sensor>
</gazebo>
```

### Common LIDAR Configurations

| Model | Samples | Vertical | Range | Update Rate |
|-------|---------|----------|-------|-------------|
| SICK TiM | 270 | 1 | 10m | 15 Hz |
| Hokuyo UTM | 1080 | 1 | 30m | 25 Hz |
| Velodyne VLP-16 | 1800 | 16 | 100m | 10 Hz |
| Ouster OS1-64 | 2048 | 64 | 120m | 10 Hz |

## IMU Sensors

### Basic IMU

```xml
<gazebo reference="imu_link">
  <sensor name="imu" type="imu">
    <always_on>true</always_on>
    <update_rate>100</update_rate>
    <topic>imu/data</topic>

    <imu>
      <angular_velocity>
        <x>
          <noise type="gaussian">
            <mean>0</mean>
            <stddev>0.0003</stddev>
          </noise>
        </x>
        <y>
          <noise type="gaussian">
            <mean>0</mean>
            <stddev>0.0003</stddev>
          </noise>
        </y>
        <z>
          <noise type="gaussian">
            <mean>0</mean>
            <stddev>0.0003</stddev>
          </noise>
        </z>
      </angular_velocity>

      <linear_acceleration>
        <x>
          <noise type="gaussian">
            <mean>0</mean>
            <stddev>0.017</stddev>
          </noise>
        </x>
        <y>
          <noise type="gaussian">
            <mean>0</mean>
            <stddev>0.017</stddev>
          </noise>
        </y>
        <z>
          <noise type="gaussian">
            <mean>0</mean>
            <stddev>0.017</stddev>
          </noise>
        </z>
      </linear_acceleration>
    </imu>
  </sensor>
</gazebo>
```

### IMU with Bias

Real IMUs have slowly drifting biases:

```xml
<angular_velocity>
  <x>
    <noise type="gaussian">
      <mean>0</mean>
      <stddev>0.0003</stddev>
      <bias_mean>0.0001</bias_mean>
      <bias_stddev>0.00001</bias_stddev>
    </noise>
  </x>
  <!-- ... y and z ... -->
</angular_velocity>
```

## Contact Sensors

Detect collisions with other objects:

```xml
<gazebo reference="gripper_finger_link">
  <sensor name="contact_sensor" type="contact">
    <always_on>true</always_on>
    <update_rate>100</update_rate>
    <topic>gripper/contact</topic>

    <contact>
      <collision>gripper_finger_link_collision</collision>
    </contact>
  </sensor>
</gazebo>
```

## GPS Sensors

```xml
<gazebo reference="gps_link">
  <sensor name="gps" type="gps">
    <always_on>true</always_on>
    <update_rate>10</update_rate>
    <topic>gps/fix</topic>

    <gps>
      <position_sensing>
        <horizontal>
          <noise type="gaussian">
            <mean>0</mean>
            <stddev>2.0</stddev>
          </noise>
        </horizontal>
        <vertical>
          <noise type="gaussian">
            <mean>0</mean>
            <stddev>3.0</stddev>
          </noise>
        </vertical>
      </position_sensing>
    </gps>
  </sensor>
</gazebo>
```

## Sensor Plugins

Enable sensor systems in your world file:

```xml
<world name="sensor_world">
  <!-- Camera system -->
  <plugin filename="gz-sim-sensors-system"
          name="gz::sim::systems::Sensors">
    <render_engine>ogre2</render_engine>
  </plugin>

  <!-- IMU system -->
  <plugin filename="gz-sim-imu-system"
          name="gz::sim::systems::Imu">
  </plugin>

  <!-- Contact system -->
  <plugin filename="gz-sim-contact-system"
          name="gz::sim::systems::Contact">
  </plugin>

  <!-- ... rest of world ... -->
</world>
```

## Bridging Sensors to ROS 2

### Bridge Configuration for Sensors

```yaml
# sensor_bridge.yaml
- topic_name: "/scan"
  ros_type_name: "sensor_msgs/msg/LaserScan"
  gz_type_name: "gz.msgs.LaserScan"
  direction: GZ_TO_ROS

- topic_name: "/camera/image_raw"
  ros_type_name: "sensor_msgs/msg/Image"
  gz_type_name: "gz.msgs.Image"
  direction: GZ_TO_ROS

- topic_name: "/camera/camera_info"
  ros_type_name: "sensor_msgs/msg/CameraInfo"
  gz_type_name: "gz.msgs.CameraInfo"
  direction: GZ_TO_ROS

- topic_name: "/depth_camera/points"
  ros_type_name: "sensor_msgs/msg/PointCloud2"
  gz_type_name: "gz.msgs.PointCloudPacked"
  direction: GZ_TO_ROS

- topic_name: "/imu/data"
  ros_type_name: "sensor_msgs/msg/Imu"
  gz_type_name: "gz.msgs.IMU"
  direction: GZ_TO_ROS
```

### Launch with Sensor Bridge

```python
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # Sensor bridge
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            arguments=[
                '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
                '/camera/image_raw@sensor_msgs/msg/Image[gz.msgs.Image',
                '/imu/data@sensor_msgs/msg/Imu[gz.msgs.IMU',
            ],
            output='screen',
        ),

        # Image bridge (for high-bandwidth camera)
        Node(
            package='ros_gz_image',
            executable='image_bridge',
            arguments=['camera/image_raw'],
            output='screen',
        ),
    ])
```

## Visualizing Sensor Data

### In RViz

```bash
# Launch RViz
rviz2
```

Add displays for:
- **LaserScan**: Topic `/scan`
- **Image**: Topic `/camera/image_raw`
- **PointCloud2**: Topic `/depth_camera/points`
- **Imu**: Topic `/imu/data`

### Checking Data Flow

```bash
# Check topic frequency
ros2 topic hz /scan
ros2 topic hz /camera/image_raw
ros2 topic hz /imu/data

# View raw data
ros2 topic echo /scan --once
ros2 topic echo /imu/data --once
```

## Sensor Noise Models

### Gaussian Noise

Most common noise model:

```xml
<noise type="gaussian">
  <mean>0.0</mean>
  <stddev>0.01</stddev>
</noise>
```

### Noise with Drift (Bias)

For IMU bias drift:

```xml
<noise type="gaussian">
  <mean>0.0</mean>
  <stddev>0.01</stddev>
  <bias_mean>0.001</bias_mean>
  <bias_stddev>0.0001</bias_stddev>
  <dynamic_bias_stddev>0.00001</dynamic_bias_stddev>
  <dynamic_bias_correlation_time>300</dynamic_bias_correlation_time>
</noise>
```

### Realistic Noise Parameters

| Sensor | Noise Parameter | Typical Value |
|--------|-----------------|---------------|
| LIDAR range | stddev | 0.01 - 0.02 m |
| Camera | stddev | 0.005 - 0.01 |
| IMU gyro | stddev | 0.0003 rad/s |
| IMU accel | stddev | 0.017 m/s² |
| GPS horizontal | stddev | 1.0 - 5.0 m |

## Multi-Sensor Robot Example

Here's a complete robot with multiple sensors:

```xml
<?xml version="1.0"?>
<robot name="sensor_robot" xmlns:xacro="http://www.ros.org/wiki/xacro">

  <!-- Base link -->
  <link name="base_link">
    <visual><geometry><box size="0.4 0.3 0.15"/></geometry></visual>
    <collision><geometry><box size="0.4 0.3 0.15"/></geometry></collision>
    <inertial>
      <mass value="10.0"/>
      <inertia ixx="0.1" iyy="0.1" izz="0.1" ixy="0" ixz="0" iyz="0"/>
    </inertial>
  </link>

  <!-- LIDAR mount -->
  <link name="lidar_link">
    <visual><geometry><cylinder radius="0.03" length="0.04"/></geometry></visual>
    <collision><geometry><cylinder radius="0.03" length="0.04"/></geometry></collision>
    <inertial><mass value="0.1"/>
      <inertia ixx="0.001" iyy="0.001" izz="0.001" ixy="0" ixz="0" iyz="0"/>
    </inertial>
  </link>

  <joint name="lidar_joint" type="fixed">
    <parent link="base_link"/>
    <child link="lidar_link"/>
    <origin xyz="0.1 0 0.1" rpy="0 0 0"/>
  </joint>

  <!-- Camera mount -->
  <link name="camera_link">
    <visual><geometry><box size="0.02 0.05 0.03"/></geometry></visual>
    <collision><geometry><box size="0.02 0.05 0.03"/></geometry></collision>
    <inertial><mass value="0.05"/>
      <inertia ixx="0.0001" iyy="0.0001" izz="0.0001" ixy="0" ixz="0" iyz="0"/>
    </inertial>
  </link>

  <joint name="camera_joint" type="fixed">
    <parent link="base_link"/>
    <child link="camera_link"/>
    <origin xyz="0.2 0 0.05" rpy="0 0.1 0"/>
  </joint>

  <!-- IMU (inside base, no separate link needed) -->

  <!-- Gazebo sensors -->
  <gazebo reference="lidar_link">
    <sensor name="lidar" type="gpu_lidar">
      <topic>scan</topic>
      <update_rate>10</update_rate>
      <always_on>true</always_on>
      <visualize>true</visualize>
      <lidar>
        <scan>
          <horizontal>
            <samples>360</samples>
            <min_angle>-3.14159</min_angle>
            <max_angle>3.14159</max_angle>
          </horizontal>
        </scan>
        <range><min>0.1</min><max>10.0</max></range>
        <noise type="gaussian"><stddev>0.01</stddev></noise>
      </lidar>
    </sensor>
  </gazebo>

  <gazebo reference="camera_link">
    <sensor name="camera" type="camera">
      <topic>camera/image_raw</topic>
      <update_rate>30</update_rate>
      <always_on>true</always_on>
      <camera>
        <horizontal_fov>1.047</horizontal_fov>
        <image><width>640</width><height>480</height></image>
        <clip><near>0.1</near><far>50</far></clip>
      </camera>
    </sensor>
  </gazebo>

  <gazebo reference="base_link">
    <sensor name="imu" type="imu">
      <topic>imu/data</topic>
      <update_rate>100</update_rate>
      <always_on>true</always_on>
    </sensor>
  </gazebo>

</robot>
```

---

## Exercise: Create a Sensor Suite

Build a robot with a complete sensor package.

### Requirements

1. Add to a differential drive robot:
   - 2D LIDAR (360°, 10Hz, 10m range)
   - RGB camera (640×480, 30Hz)
   - IMU (100Hz with noise)
2. Configure the ROS-Gazebo bridge for all sensors
3. Visualize all sensor data in RViz

### Expected Outcome

- LIDAR scan visible in RViz
- Camera feed in image display
- IMU data on `/imu/data` topic
- All sensors updating at specified rates

### Verification

```bash
# Check all sensor topics exist
ros2 topic list | grep -E "scan|camera|imu"

# Verify update rates
ros2 topic hz /scan
ros2 topic hz /camera/image_raw
ros2 topic hz /imu/data
```

---

## Summary

Simulating sensors realistically is essential for robotics development:

- **Cameras**: RGB, depth, with configurable resolution and FOV
- **LIDAR**: 2D scanners and 3D point clouds
- **IMU**: Angular velocity and linear acceleration
- **Noise models**: Gaussian noise with optional bias drift

Key skills learned:
- Configuring various sensor types in Gazebo
- Adding realistic noise to sensor measurements
- Bridging sensor topics to ROS 2
- Visualizing sensor data

In the next chapter, you will learn about physics and collision simulation.

**Next:** [Physics and Collisions](./5-physics)
