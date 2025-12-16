---
sidebar_position: 6
sidebar_label: "1.6 RViz"
title: "Chapter 1.6: Visualization with RViz"
description: "Learn to visualize robot data, models, and sensor information using RViz"
keywords: [ros2, rviz, visualization, debugging, displays, tf]
---

# Visualization with RViz

In this chapter, you will learn how to use RViz2, the 3D visualization tool for ROS 2, to visualize robot models, sensor data, and debug your applications.

## What is RViz?

**RViz** (Robot Visualization) is a 3D visualization tool that displays:

- Robot models from URDF
- Sensor data (cameras, LIDAR, point clouds)
- Coordinate frames (TF)
- Paths and trajectories
- Custom markers and shapes
- Interactive elements

RViz is essential for:
- Debugging robot behavior
- Understanding spatial relationships
- Monitoring sensor data
- Developing navigation and manipulation

## Launching RViz

Start RViz with:

```bash
ros2 run rviz2 rviz2
```

Or use the shortcut:

```bash
rviz2
```

You'll see the main RViz window:

```
┌─────────────────────────────────────────────────────────────┐
│  File  Edit  Panels  Help                                    │
├───────────────┬─────────────────────────────────────────────┤
│               │                                              │
│   Displays    │              3D View                         │
│   Panel       │                                              │
│               │                                              │
│  ┌─────────┐  │                                              │
│  │ Add     │  │              (empty on start)                │
│  │ Remove  │  │                                              │
│  └─────────┘  │                                              │
│               │                                              │
├───────────────┴─────────────────────────────────────────────┤
│                        Status Bar                            │
└─────────────────────────────────────────────────────────────┘
```

## Core Concepts

### Fixed Frame

The **Fixed Frame** is the reference frame for all visualization. Common choices:

- `map` - For navigation (global reference)
- `odom` - For odometry-based visualization
- `base_link` - Robot-centric view

Set it in the "Global Options" section of the Displays panel.

### Displays

**Displays** are visualization plugins. Each display type shows specific data:

| Display | Data Source | Use Case |
|---------|-------------|----------|
| RobotModel | URDF | Show robot structure |
| TF | Transform tree | Show coordinate frames |
| LaserScan | sensor_msgs/LaserScan | LIDAR data |
| PointCloud2 | sensor_msgs/PointCloud2 | 3D point data |
| Image | sensor_msgs/Image | Camera feed |
| Path | nav_msgs/Path | Planned paths |
| Marker | visualization_msgs/Marker | Custom shapes |

### Adding Displays

1. Click "Add" in the Displays panel
2. Choose the display type
3. Configure the topic and options

## Visualizing a Robot Model

### Step 1: Launch Required Nodes

You need:
- `robot_state_publisher` - Publishes robot model and transforms
- `joint_state_publisher_gui` - Publishes joint positions (for testing)

```bash
# Terminal 1: Robot state publisher
ros2 run robot_state_publisher robot_state_publisher \
  --ros-args -p robot_description:="$(cat robot.urdf)"

# Terminal 2: Joint state publisher GUI
ros2 run joint_state_publisher_gui joint_state_publisher_gui

# Terminal 3: RViz
rviz2
```

### Step 2: Configure RViz

1. Set Fixed Frame to `base_link`
2. Add > RobotModel
3. Set "Description Topic" to `/robot_description`

The robot model should appear in the 3D view.

### Step 3: Add TF Display

1. Add > TF
2. Enable "Show Names" to see frame labels
3. Adjust "Marker Scale" for visibility

## Transform Tree (TF)

TF is ROS's transform library. It tracks:

- Position and orientation of every coordinate frame
- Parent-child relationships
- Time-stamped transforms

View the TF tree:

```bash
ros2 run tf2_tools view_frames
```

This generates a PDF showing the transform hierarchy.

In RViz, the TF display shows:
- Frame axes (RGB = XYZ)
- Frame names
- Parent-child connections

## Visualizing Sensor Data

### LIDAR (LaserScan)

1. Add > LaserScan
2. Set topic to your LIDAR topic (e.g., `/scan`)
3. Configure appearance:
   - Size: Point size
   - Color Transformer: How to color points
   - Style: Points, lines, or squares

### Camera Images

1. Add > Image
2. Set topic to image topic (e.g., `/camera/image_raw`)
3. A small window shows the camera feed

### Point Clouds

1. Add > PointCloud2
2. Set topic to your point cloud topic
3. Configure:
   - Style: Points, squares, spheres
   - Size: Point/shape size
   - Color Transformer: Flat, intensity, axis, etc.

## Custom Markers

You can publish custom markers from your nodes:

```python
import rclpy
from rclpy.node import Node
from visualization_msgs.msg import Marker

class MarkerPublisher(Node):
    def __init__(self):
        super().__init__('marker_publisher')
        self.publisher = self.create_publisher(Marker, 'visualization_marker', 10)
        self.timer = self.create_timer(0.1, self.publish_marker)

    def publish_marker(self):
        marker = Marker()
        marker.header.frame_id = 'base_link'
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.ns = 'my_markers'
        marker.id = 0
        marker.type = Marker.SPHERE
        marker.action = Marker.ADD

        # Position
        marker.pose.position.x = 1.0
        marker.pose.position.y = 0.0
        marker.pose.position.z = 0.5
        marker.pose.orientation.w = 1.0

        # Scale
        marker.scale.x = 0.2
        marker.scale.y = 0.2
        marker.scale.z = 0.2

        # Color (RGBA)
        marker.color.r = 1.0
        marker.color.g = 0.0
        marker.color.b = 0.0
        marker.color.a = 1.0

        self.publisher.publish(marker)

def main(args=None):
    rclpy.init(args=args)
    node = MarkerPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
```

### Marker Types

| Type | Description |
|------|-------------|
| `ARROW` | 3D arrow |
| `CUBE` | Box |
| `SPHERE` | Ball |
| `CYLINDER` | Cylinder |
| `LINE_STRIP` | Connected lines |
| `LINE_LIST` | Separate line segments |
| `CUBE_LIST` | Multiple cubes |
| `SPHERE_LIST` | Multiple spheres |
| `POINTS` | Point cloud |
| `TEXT_VIEW_FACING` | 3D text |
| `MESH_RESOURCE` | 3D mesh file |

## Navigation Controls

### Mouse Controls

- **Left click + drag**: Rotate view
- **Middle click + drag**: Pan view
- **Scroll wheel**: Zoom
- **Shift + left click**: Move focal point

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `F` | Focus on selection |
| `Ctrl+S` | Save configuration |
| `Ctrl+O` | Open configuration |

### View Types

Change the view type in the "Views" panel:

- **Orbit**: Rotate around focal point
- **FPS**: First-person shooter style
- **TopDownOrtho**: Top-down orthographic
- **XYOrbit**: Orbit with locked Z-axis

## Saving and Loading Configurations

Save your RViz setup for reuse:

1. File > Save Config As
2. Choose location and name (`.rviz` extension)

Load a configuration:

1. File > Open Config
2. Or from command line: `rviz2 -d my_config.rviz`

### Configuration in Launch Files

Include RViz configuration in launch files:

```python
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    pkg_path = get_package_share_directory('my_robot')
    rviz_config = os.path.join(pkg_path, 'rviz', 'robot.rviz')

    return LaunchDescription([
        Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-d', rviz_config]
        ),
    ])
```

## Debugging with RViz

### Common Issues and Solutions

**Problem**: Robot model not visible
- Check Fixed Frame matches a frame in TF
- Verify `/robot_description` topic is published
- Check RobotModel display is enabled

**Problem**: TF frames missing
- Ensure robot_state_publisher is running
- Check joint_state_publisher is publishing
- Look for TF warnings in terminal

**Problem**: Sensor data not showing
- Verify topic name is correct
- Check message type matches display type
- Ensure sensor is publishing data

### Using Echo to Debug

```bash
# Check if topic exists
ros2 topic list

# Verify data is flowing
ros2 topic hz /scan

# View actual messages
ros2 topic echo /scan --once
```

## Interactive Markers

For advanced applications, use interactive markers that respond to user input:

```python
from interactive_markers import InteractiveMarkerServer
from visualization_msgs.msg import InteractiveMarker, InteractiveMarkerControl
```

Interactive markers allow:
- Dragging objects in 3D
- User input for robot control
- Interactive path planning

---

## Exercise: Visualize and Debug

Create a complete visualization setup for your robot.

### Requirements

1. Launch robot_state_publisher with your URDF
2. Launch joint_state_publisher_gui
3. Configure RViz with:
   - RobotModel display
   - TF display showing all frames
   - Grid display for reference
4. Save the configuration to a `.rviz` file
5. Create a launch file that starts everything

### Expected Outcome

- Robot model visible in RViz
- Joint sliders control the model
- TF frames visible at each joint
- Configuration saved for reuse

### Launch File Template

```python
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    pkg = get_package_share_directory('my_robot_description')

    urdf_file = os.path.join(pkg, 'urdf', 'robot.urdf')
    with open(urdf_file, 'r') as f:
        robot_desc = f.read()

    rviz_config = os.path.join(pkg, 'rviz', 'display.rviz')

    return LaunchDescription([
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_desc}]
        ),
        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-d', rviz_config]
        ),
    ])
```

---

## Summary

RViz is essential for robotics development:

- **Visualize robot models** from URDF
- **Monitor sensor data** in real-time
- **Debug coordinate frames** with TF display
- **Create custom visualizations** with markers
- **Save configurations** for reproducibility

Key skills learned:
- Adding and configuring displays
- Understanding the transform tree
- Publishing custom markers
- Debugging visualization issues

This completes Module 1. You now have the foundation to:
- Create ROS 2 nodes
- Communicate using topics, services, and actions
- Describe robots with URDF
- Visualize everything in RViz

**Next:** [Module 1 Quiz](./quiz.md)
