---
sidebar_position: 6
sidebar_label: "3.6 Isaac ROS"
title: "Chapter 3.6: Isaac ROS for Deployment"
description: "Learn to deploy GPU-accelerated perception on real robots using Isaac ROS"
keywords: [isaac ros, deployment, gpu, perception, nvidia, jetson, real-time]
---

# Isaac ROS for Deployment

In this chapter, you will learn how to deploy GPU-accelerated perception pipelines on real robots using Isaac ROS, bridging the gap between simulation and production deployment.

## What is Isaac ROS?

**Isaac ROS** is a collection of GPU-accelerated ROS 2 packages for robotics:

```
┌─────────────────────────────────────────────────────────────┐
│                     Isaac ROS Stack                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │               ROS 2 Applications                       │  │
│  │  (Navigation, Manipulation, Perception)                │  │
│  └───────────────────────────────────────────────────────┘  │
│                           │                                  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              Isaac ROS Packages                        │  │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐     │  │
│  │  │ Visual  │ │  Depth  │ │  SLAM   │ │ Object  │     │  │
│  │  │ SLAM    │ │  Est.   │ │ (cuVSLAM)│ │ Detect  │     │  │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘     │  │
│  └───────────────────────────────────────────────────────┘  │
│                           │                                  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │            NVIDIA Acceleration Libraries               │  │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐     │  │
│  │  │ TensorRT│ │  cuDNN  │ │ VPI     │ │ NITROS  │     │  │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘     │  │
│  └───────────────────────────────────────────────────────┘  │
│                           │                                  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              NVIDIA GPU Hardware                       │  │
│  │         (Jetson, RTX, Data Center GPUs)                │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Available Packages

| Package | Function | Performance |
|---------|----------|-------------|
| **isaac_ros_visual_slam** | Visual odometry | 30+ FPS stereo |
| **isaac_ros_depth_segmentation** | Depth estimation | Real-time |
| **isaac_ros_object_detection** | YOLO, SSD detection | 100+ FPS |
| **isaac_ros_apriltag** | Fiducial detection | 100+ FPS |
| **isaac_ros_dnn_inference** | TensorRT inference | Model-dependent |
| **isaac_ros_image_pipeline** | GPU image processing | 60+ FPS |
| **isaac_ros_freespace** | Ground segmentation | Real-time |
| **isaac_ros_nvblox** | 3D reconstruction | Real-time |

## NITROS: Zero-Copy Transport

**NITROS** (NVIDIA Isaac Transport for ROS) enables zero-copy GPU data sharing:

### Traditional ROS 2 vs NITROS

```
Traditional ROS 2:
┌─────────┐    CPU Copy    ┌─────────┐    CPU Copy    ┌─────────┐
│ Node A  │ ──────────────▶│   DDS   │──────────────▶ │ Node B  │
│  (GPU)  │                │ (CPU)   │                │  (GPU)  │
└─────────┘                └─────────┘                └─────────┘
         GPU→CPU               │              CPU→GPU
                           Serialization

NITROS:
┌─────────┐   GPU Memory   ┌─────────┐
│ Node A  │ ══════════════▶│ Node B  │
│  (GPU)  │   Zero-Copy    │  (GPU)  │
└─────────┘                └─────────┘
         Shared CUDA Memory (No Copy!)
```

### Performance Comparison

| Operation | Traditional | NITROS |
|-----------|-------------|--------|
| Image (1080p) | 15ms | &lt;1ms |
| Point Cloud (100K) | 25ms | &lt;1ms |
| Latency | High | Minimal |
| CPU Usage | High | Low |

## Installation

### Prerequisites

```bash
# Install ROS 2 Humble
# (Assuming already installed from Module 1)

# Install NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
    sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt update
sudo apt install -y nvidia-container-toolkit
```

### Installing Isaac ROS

```bash
# Create workspace
mkdir -p ~/isaac_ros_ws/src
cd ~/isaac_ros_ws/src

# Clone Isaac ROS Common
git clone https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_common.git

# Clone desired packages
git clone https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_visual_slam.git
git clone https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_object_detection.git
git clone https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_apriltag.git

# Build using Docker (recommended)
cd ~/isaac_ros_ws/src/isaac_ros_common
./scripts/run_dev.sh

# Inside container, build
cd /workspaces/isaac_ros-dev
colcon build --symlink-install
source install/setup.bash
```

## Visual SLAM with cuVSLAM

### Overview

**cuVSLAM** provides GPU-accelerated visual odometry:

- Stereo or RGB-D input
- 30+ FPS on Jetson
- Loop closure detection
- Map saving/loading

### Launch Visual SLAM

```bash
# With RealSense camera
ros2 launch isaac_ros_visual_slam isaac_ros_visual_slam_realsense.launch.py

# With custom stereo camera
ros2 launch isaac_ros_visual_slam isaac_ros_visual_slam.launch.py \
    left_camera_topic:=/left/image_rect \
    right_camera_topic:=/right/image_rect \
    left_camera_info_topic:=/left/camera_info \
    right_camera_info_topic:=/right/camera_info
```

### Configuration

```python
# visual_slam_params.yaml
visual_slam:
  ros__parameters:
    # Input
    enable_imu_fusion: true
    imu_frame: "imu_link"

    # Output
    enable_observations_view: true
    enable_landmarks_view: true

    # Performance
    enable_debug_mode: false
    path_max_size: 1024

    # Map
    enable_localization_n_mapping: true
    enable_slam_visualization: true
```

### Reading Odometry

```python
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry

class VslamSubscriber(Node):
    def __init__(self):
        super().__init__('vslam_subscriber')
        self.subscription = self.create_subscription(
            Odometry,
            '/visual_slam/tracking/odometry',
            self.odom_callback,
            10
        )

    def odom_callback(self, msg):
        pos = msg.pose.pose.position
        self.get_logger().info(
            f'Position: x={pos.x:.2f}, y={pos.y:.2f}, z={pos.z:.2f}'
        )

def main():
    rclpy.init()
    node = VslamSubscriber()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Object Detection with TensorRT

### Using Pre-trained Models

```bash
# Download and convert model to TensorRT
# (Example with SSD MobileNet)
ros2 run isaac_ros_dnn_inference \
    triton_to_trt_node --model_path /models/ssd_mobilenet.onnx

# Launch detection
ros2 launch isaac_ros_object_detection \
    isaac_ros_detectnet.launch.py \
    model_file_path:=/models/ssd_mobilenet.engine \
    input_image_width:=640 \
    input_image_height:=480
```

### Detection Launch File

```python
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # Image preprocessing
        Node(
            package='isaac_ros_image_proc',
            executable='resize_node',
            parameters=[{
                'output_width': 640,
                'output_height': 480,
            }],
            remappings=[
                ('image', '/camera/image_raw'),
                ('camera_info', '/camera/camera_info'),
                ('resize/image', '/image_resized'),
            ]
        ),

        # TensorRT inference
        Node(
            package='isaac_ros_tensor_rt',
            executable='tensor_rt_node',
            parameters=[{
                'model_file_path': '/models/yolov8.engine',
                'input_tensor_names': ['images'],
                'output_tensor_names': ['output0'],
                'input_binding_names': ['images'],
                'output_binding_names': ['output0'],
            }]
        ),

        # Detection decoder
        Node(
            package='isaac_ros_object_detection',
            executable='detection2d_to_detection3d_node',
            parameters=[{
                'depth_topic': '/camera/depth',
            }]
        ),
    ])
```

### Custom Model Deployment

```python
# Convert PyTorch model to ONNX
import torch

model = torch.load('custom_detector.pt')
model.eval()

dummy_input = torch.randn(1, 3, 640, 480)
torch.onnx.export(
    model,
    dummy_input,
    'custom_detector.onnx',
    input_names=['images'],
    output_names=['output'],
    dynamic_axes={
        'images': {0: 'batch'},
        'output': {0: 'batch'}
    }
)

# Convert to TensorRT (in Isaac ROS container)
# trtexec --onnx=custom_detector.onnx --saveEngine=custom_detector.engine
```

## AprilTag Detection

### GPU-Accelerated Fiducial Detection

```bash
# Launch AprilTag detector
ros2 launch isaac_ros_apriltag isaac_ros_apriltag.launch.py \
    camera_topic:=/camera/image_raw \
    camera_info_topic:=/camera/camera_info
```

### Reading Detections

```python
from isaac_ros_apriltag_interfaces.msg import AprilTagDetectionArray

class AprilTagSubscriber(Node):
    def __init__(self):
        super().__init__('apriltag_subscriber')
        self.subscription = self.create_subscription(
            AprilTagDetectionArray,
            '/tag_detections',
            self.detection_callback,
            10
        )

    def detection_callback(self, msg):
        for detection in msg.detections:
            tag_id = detection.id
            pose = detection.pose.pose.pose
            self.get_logger().info(
                f'Tag {tag_id}: pos=({pose.position.x:.2f}, '
                f'{pose.position.y:.2f}, {pose.position.z:.2f})'
            )
```

## Nvblox: 3D Reconstruction

### Real-Time Mapping

```bash
# Launch nvblox with RealSense
ros2 launch nvblox_examples_bringup realsense_example.launch.py

# View in RViz
ros2 launch nvblox_rviz_plugin nvblox_rviz.launch.py
```

### Nvblox Configuration

```yaml
# nvblox_params.yaml
nvblox_node:
  ros__parameters:
    # Voxel size (meters)
    voxel_size: 0.05

    # Update rates
    esdf_update_rate_hz: 10.0
    mesh_update_rate_hz: 5.0

    # Sensor configuration
    depth_camera_frame: "camera_depth_optical_frame"
    global_frame: "odom"

    # Integration
    max_integration_distance_m: 5.0
    truncation_distance_vox: 4.0

    # Output
    output_esdf_layer: true
    output_mesh: true
```

## Jetson Deployment

### Optimizing for Jetson

| Jetson Model | Capabilities |
|--------------|--------------|
| Orin Nano | Basic perception |
| Orin NX | Full Isaac ROS |
| AGX Orin | Multi-sensor, complex AI |

### Performance Tuning

```bash
# Set maximum performance mode
sudo nvpmodel -m 0
sudo jetson_clocks

# Monitor performance
tegrastats
```

### Memory Management

```python
# Reduce memory usage
parameters=[{
    # Use smaller batch sizes
    'batch_size': 1,

    # Limit image resolution
    'input_image_width': 320,
    'input_image_height': 240,

    # Reduce model precision (FP16)
    'precision': 'fp16',
}]
```

## Complete Robot Integration

### Launch File for Mobile Robot

```python
from launch import LaunchDescription
from launch_ros.actions import Node, ComposableNodeContainer
from launch_ros.descriptions import ComposableNode

def generate_launch_description():
    return LaunchDescription([
        # Camera driver
        Node(
            package='realsense2_camera',
            executable='realsense2_camera_node',
            parameters=[{
                'enable_depth': True,
                'enable_color': True,
                'depth_module.profile': '640x480x30',
                'rgb_camera.profile': '640x480x30',
            }]
        ),

        # Isaac ROS NITROS container
        ComposableNodeContainer(
            name='isaac_ros_container',
            namespace='',
            package='rclcpp_components',
            executable='component_container_mt',
            composable_node_descriptions=[
                # Visual SLAM
                ComposableNode(
                    package='isaac_ros_visual_slam',
                    plugin='nvidia::isaac_ros::visual_slam::VisualSlamNode',
                    parameters=[{
                        'enable_imu_fusion': True,
                    }],
                    remappings=[
                        ('stereo_camera/left/image', '/camera/infra1/image_rect_raw'),
                        ('stereo_camera/right/image', '/camera/infra2/image_rect_raw'),
                    ]
                ),

                # Object detection
                ComposableNode(
                    package='isaac_ros_tensor_rt',
                    plugin='nvidia::isaac_ros::dnn_inference::TensorRTNode',
                    parameters=[{
                        'model_file_path': '/models/yolov8.engine',
                    }],
                    remappings=[
                        ('image', '/camera/color/image_raw'),
                    ]
                ),
            ],
        ),

        # Navigation stack
        Node(
            package='nav2_bringup',
            executable='bringup_launch.py',
            parameters=[{
                'use_sim_time': False,
            }]
        ),
    ])
```

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Complete Robot System                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Sensors:                  Isaac ROS:            Output:     │
│  ┌─────────┐              ┌─────────┐          ┌─────────┐  │
│  │ Stereo  │────NITROS───▶│ Visual  │─────────▶│ Odometry│  │
│  │ Camera  │              │ SLAM    │          └─────────┘  │
│  └─────────┘              └─────────┘                        │
│                                                              │
│  ┌─────────┐              ┌─────────┐          ┌─────────┐  │
│  │  RGB    │────NITROS───▶│ Object  │─────────▶│Detections│ │
│  │ Camera  │              │Detection│          └─────────┘  │
│  └─────────┘              └─────────┘                        │
│                                                              │
│  ┌─────────┐              ┌─────────┐          ┌─────────┐  │
│  │ Depth   │────NITROS───▶│ Nvblox  │─────────▶│  3D Map │  │
│  │ Camera  │              │         │          └─────────┘  │
│  └─────────┘              └─────────┘                        │
│                                                              │
│  All ──────────────────▶  Nav2 Stack  ──────▶  Motion      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Exercise: Deploy Object Detection

Deploy a GPU-accelerated object detector on a robot.

### Requirements

1. Set up Isaac ROS Docker environment
2. Convert a YOLO model to TensorRT
3. Create a launch file for detection pipeline
4. Integrate with ROS 2 camera topic
5. Visualize detections in RViz

### Expected Outcome

- Object detection running at 30+ FPS
- Bounding boxes published on ROS 2 topic
- Minimal CPU usage (GPU doing the work)
- RViz showing detected objects

### Verification

```bash
# Check detection rate
ros2 topic hz /detections

# Check GPU usage
nvidia-smi

# View detections
ros2 topic echo /detections --once
```

---

## Summary

Isaac ROS enables high-performance deployment:

- **NITROS**: Zero-copy GPU data sharing
- **cuVSLAM**: GPU-accelerated visual odometry
- **TensorRT**: Optimized neural network inference
- **Nvblox**: Real-time 3D reconstruction

Key deployment considerations:
- Use NITROS for GPU-to-GPU data flow
- Convert models to TensorRT for speed
- Tune for target hardware (Jetson vs desktop)
- Monitor GPU memory and utilization

This completes Module 3 on NVIDIA Isaac. You now have skills for:
- Setting up Isaac Sim
- Training with Isaac Lab
- Generating synthetic data
- Deploying with Isaac ROS

**Next:** [Module 3 Quiz](./quiz)
