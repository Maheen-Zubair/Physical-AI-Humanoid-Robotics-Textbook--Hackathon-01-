---
sidebar_position: 6
sidebar_label: "2.6 Unity"
title: "Chapter 2.6: Unity for Robotics Visualization"
description: "Learn to use Unity for high-fidelity visualization and ROS 2 integration"
keywords: [unity, robotics, visualization, ros2, simulation, ml-agents]
---

# Unity for Robotics Visualization

In this chapter, you will learn how to use Unity as a visualization and simulation platform for robotics, including ROS 2 integration and machine learning applications.

## Why Unity for Robotics?

Unity offers unique advantages for robotics applications:

| Feature | Benefit |
|---------|---------|
| **High-quality rendering** | Photorealistic visuals for demos and training |
| **Cross-platform** | Deploy to VR, AR, web, mobile |
| **ML-Agents** | Reinforcement learning integration |
| **Asset store** | Thousands of 3D models and environments |
| **ROS integration** | Unity Robotics Hub packages |
| **Industry standard** | Widely used in games and simulation |

### When to Use Unity vs Gazebo

| Use Case | Gazebo | Unity |
|----------|--------|-------|
| ROS 2 native workflow | ✓ Best | ✓ Good |
| Physics accuracy | ✓ Best | ✓ Good |
| Visual quality | Basic | ✓ Best |
| VR/AR experiences | Limited | ✓ Best |
| Machine learning | Plugin | ✓ Best |
| Real-time rendering | Basic | ✓ Best |
| Synthetic data generation | Limited | ✓ Best |

## Setting Up Unity for Robotics

### Prerequisites

1. **Unity Hub**: Download from [unity.com](https://unity.com)
2. **Unity 2022 LTS**: Long-term support version recommended
3. **ROS 2 Humble**: Already installed from Module 1

### Installing Unity

1. Download and install Unity Hub
2. Sign in or create a Unity account
3. Install Unity 2022.3 LTS (or newer LTS)
4. Include modules: Linux Build Support (if needed)

### Creating a Robotics Project

1. Open Unity Hub
2. Click "New Project"
3. Select "3D (URP)" template for better graphics
4. Name your project (e.g., "RoboticsVisualization")
5. Click "Create project"

## Unity Robotics Hub

The **Unity Robotics Hub** provides packages for ROS integration.

### Installing Required Packages

1. Open Window → Package Manager
2. Click + → Add package from git URL
3. Add these packages:

```
https://github.com/Unity-Technologies/ROS-TCP-Connector.git?path=/com.unity.robotics.ros-tcp-connector
```

```
https://github.com/Unity-Technologies/URDF-Importer.git?path=/com.unity.robotics.urdf-importer
```

### Package Overview

| Package | Purpose |
|---------|---------|
| **ROS-TCP-Connector** | Communicate with ROS 2 |
| **URDF-Importer** | Import robot models |
| **Visualizations** | ROS message visualization |

## ROS 2 Integration Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     ROS 2 System                         │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐                 │
│  │  Nodes  │  │ Topics  │  │Services │                 │
│  └────┬────┘  └────┬────┘  └────┬────┘                 │
│       └────────────┴────────────┘                       │
│                     │                                    │
│                     ▼                                    │
│            ┌────────────────┐                           │
│            │ ROS-TCP-Endpoint│                          │
│            │   (ROS 2 Node) │                           │
│            └───────┬────────┘                           │
└────────────────────┼────────────────────────────────────┘
                     │ TCP/IP
┌────────────────────┼────────────────────────────────────┐
│                    ▼                                     │
│            ┌────────────────┐                           │
│            │ROS-TCP-Connector│                          │
│            │ (Unity Plugin) │                           │
│            └───────┬────────┘                           │
│                    ▼                                     │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐                 │
│  │Publisher│  │Subscriber│  │ Service │                 │
│  │ Scripts │  │ Scripts  │  │ Scripts │                 │
│  └─────────┘  └─────────┘  └─────────┘                 │
│                    Unity                                 │
└─────────────────────────────────────────────────────────┘
```

### Setting Up ROS Connection

1. Install ROS-TCP-Endpoint on your ROS 2 system:

```bash
# Clone the repository
cd ~/ros2_ws/src
git clone https://github.com/Unity-Technologies/ROS-TCP-Endpoint.git -b ROS2v0.7.0

# Build
cd ~/ros2_ws
colcon build --packages-select ros_tcp_endpoint
source install/setup.bash
```

2. Run the endpoint:

```bash
ros2 run ros_tcp_endpoint default_server_endpoint --ros-args -p ROS_IP:=0.0.0.0
```

3. In Unity:
   - Go to Robotics → ROS Settings
   - Set ROS IP Address to your ROS machine IP
   - Set Port to 10000 (default)

## Importing URDF Models

### Using URDF Importer

1. Place your URDF file in the Assets folder
2. Right-click the URDF file
3. Select "Import Robot from URDF"
4. Configure import settings:
   - Axis Type: Y-up (Unity default) or Z-up (ROS convention)
   - Mesh Decomposer: VHACD for complex collisions
5. Click "Import"

### URDF Import Settings

| Setting | Description |
|---------|-------------|
| **Axis Type** | Coordinate system orientation |
| **Mesh Decomposer** | Collision mesh generation method |
| **Convex Decomposition** | Split concave meshes |

### Fixing Common Import Issues

**Materials not loading:**
```csharp
// Create a material assignment script
foreach (var renderer in GetComponentsInChildren<Renderer>())
{
    renderer.material = defaultMaterial;
}
```

**Scale issues:**
- URDF uses meters; Unity uses meters by default
- Check import scale is 1.0

## Creating a Robot Subscriber

Subscribe to ROS 2 topics to update Unity:

```csharp
using UnityEngine;
using Unity.Robotics.ROSTCPConnector;
using RosMessageTypes.Geometry;

public class RobotPoseSubscriber : MonoBehaviour
{
    public string topicName = "/robot_pose";
    public GameObject robotModel;

    void Start()
    {
        ROSConnection.GetOrCreateInstance().Subscribe<PoseMsg>(
            topicName, UpdateRobotPose);
    }

    void UpdateRobotPose(PoseMsg poseMsg)
    {
        // Convert ROS pose to Unity
        Vector3 position = new Vector3(
            (float)poseMsg.position.x,
            (float)poseMsg.position.z,  // Y-up conversion
            (float)poseMsg.position.y
        );

        Quaternion rotation = new Quaternion(
            (float)poseMsg.orientation.x,
            (float)poseMsg.orientation.z,
            (float)poseMsg.orientation.y,
            (float)-poseMsg.orientation.w
        );

        robotModel.transform.position = position;
        robotModel.transform.rotation = rotation;
    }
}
```

## Creating a Publisher

Publish data from Unity to ROS 2:

```csharp
using UnityEngine;
using Unity.Robotics.ROSTCPConnector;
using RosMessageTypes.Geometry;

public class VelocityPublisher : MonoBehaviour
{
    public string topicName = "/cmd_vel";
    public float linearSpeed = 0.5f;
    public float angularSpeed = 1.0f;

    private ROSConnection ros;

    void Start()
    {
        ros = ROSConnection.GetOrCreateInstance();
        ros.RegisterPublisher<TwistMsg>(topicName);
    }

    void Update()
    {
        TwistMsg twist = new TwistMsg();

        // Read keyboard input
        float linear = Input.GetAxis("Vertical") * linearSpeed;
        float angular = -Input.GetAxis("Horizontal") * angularSpeed;

        twist.linear.x = linear;
        twist.angular.z = angular;

        ros.Publish(topicName, twist);
    }
}
```

## Visualizing Sensor Data

### Displaying LIDAR Scans

```csharp
using UnityEngine;
using Unity.Robotics.ROSTCPConnector;
using RosMessageTypes.Sensor;

public class LaserScanVisualizer : MonoBehaviour
{
    public string topicName = "/scan";
    public Material laserMaterial;
    public float pointSize = 0.02f;

    private GameObject[] points;
    private int maxPoints = 360;

    void Start()
    {
        // Create point objects
        points = new GameObject[maxPoints];
        for (int i = 0; i < maxPoints; i++)
        {
            points[i] = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            points[i].transform.localScale = Vector3.one * pointSize;
            points[i].GetComponent<Renderer>().material = laserMaterial;
            points[i].transform.parent = transform;
        }

        ROSConnection.GetOrCreateInstance().Subscribe<LaserScanMsg>(
            topicName, UpdateLaserScan);
    }

    void UpdateLaserScan(LaserScanMsg scan)
    {
        float angle = scan.angle_min;

        for (int i = 0; i < scan.ranges.Length && i < maxPoints; i++)
        {
            float range = scan.ranges[i];

            if (range > scan.range_min && range < scan.range_max)
            {
                float x = range * Mathf.Cos(angle);
                float z = range * Mathf.Sin(angle);

                points[i].transform.localPosition = new Vector3(x, 0, z);
                points[i].SetActive(true);
            }
            else
            {
                points[i].SetActive(false);
            }

            angle += scan.angle_increment;
        }
    }
}
```

### Displaying Camera Images

```csharp
using UnityEngine;
using UnityEngine.UI;
using Unity.Robotics.ROSTCPConnector;
using RosMessageTypes.Sensor;

public class CameraImageDisplay : MonoBehaviour
{
    public string topicName = "/camera/image_raw";
    public RawImage displayImage;

    private Texture2D texture;

    void Start()
    {
        ROSConnection.GetOrCreateInstance().Subscribe<ImageMsg>(
            topicName, UpdateImage);
    }

    void UpdateImage(ImageMsg imageMsg)
    {
        if (texture == null ||
            texture.width != (int)imageMsg.width ||
            texture.height != (int)imageMsg.height)
        {
            texture = new Texture2D(
                (int)imageMsg.width,
                (int)imageMsg.height,
                TextureFormat.RGB24, false);
            displayImage.texture = texture;
        }

        texture.LoadRawTextureData(imageMsg.data);
        texture.Apply();
    }
}
```

## Joint State Visualization

Animate robot joints based on ROS 2 joint states:

```csharp
using UnityEngine;
using Unity.Robotics.ROSTCPConnector;
using RosMessageTypes.Sensor;
using System.Collections.Generic;

public class JointStateSubscriber : MonoBehaviour
{
    public string topicName = "/joint_states";

    private Dictionary<string, ArticulationBody> joints =
        new Dictionary<string, ArticulationBody>();

    void Start()
    {
        // Find all articulation bodies
        foreach (var joint in GetComponentsInChildren<ArticulationBody>())
        {
            joints[joint.name] = joint;
        }

        ROSConnection.GetOrCreateInstance().Subscribe<JointStateMsg>(
            topicName, UpdateJoints);
    }

    void UpdateJoints(JointStateMsg msg)
    {
        for (int i = 0; i < msg.name.Length; i++)
        {
            string jointName = msg.name[i];
            float position = (float)msg.position[i];

            if (joints.TryGetValue(jointName, out ArticulationBody joint))
            {
                var drive = joint.xDrive;
                drive.target = position * Mathf.Rad2Deg;
                joint.xDrive = drive;
            }
        }
    }
}
```

## Building Custom Environments

### Creating a Warehouse Scene

1. **Floor**: Create a plane, scale to 50×50
2. **Walls**: Use cubes, position around perimeter
3. **Lighting**: Add directional light for sun
4. **Shelves**: Import or create shelf models
5. **Props**: Add boxes, pallets, etc.

### Adding NavMesh for Navigation

1. Select floor and obstacles
2. Mark as "Navigation Static"
3. Window → AI → Navigation
4. Click "Bake"
5. Robot can now use Unity's NavMesh

## ML-Agents Integration

Train robots using reinforcement learning:

### Installing ML-Agents

```bash
# Python package
pip install mlagents

# Unity package (via Package Manager)
# Add: com.unity.ml-agents
```

### Creating a Training Environment

```csharp
using Unity.MLAgents;
using Unity.MLAgents.Sensors;
using Unity.MLAgents.Actuators;

public class RobotAgent : Agent
{
    public Transform target;
    public ArticulationBody robotBase;

    public override void OnEpisodeBegin()
    {
        // Reset robot and target positions
        transform.localPosition = Vector3.zero;
        target.localPosition = new Vector3(
            Random.Range(-4f, 4f), 0,
            Random.Range(-4f, 4f));
    }

    public override void CollectObservations(VectorSensor sensor)
    {
        // Robot position and velocity
        sensor.AddObservation(transform.localPosition);
        sensor.AddObservation(robotBase.velocity);

        // Target position
        sensor.AddObservation(target.localPosition);
    }

    public override void OnActionReceived(ActionBuffers actions)
    {
        // Apply actions to robot
        float moveX = actions.ContinuousActions[0];
        float moveZ = actions.ContinuousActions[1];

        robotBase.AddForce(new Vector3(moveX, 0, moveZ) * 10f);

        // Calculate reward
        float distance = Vector3.Distance(
            transform.localPosition, target.localPosition);

        if (distance < 0.5f)
        {
            SetReward(1.0f);
            EndEpisode();
        }
        else
        {
            SetReward(-0.001f);  // Small negative reward per step
        }
    }
}
```

## Coordinate System Conversion

Unity and ROS use different coordinate systems:

| Axis | ROS | Unity |
|------|-----|-------|
| Forward | X+ | Z+ |
| Left | Y+ | X- |
| Up | Z+ | Y+ |

### Conversion Functions

```csharp
public static class CoordinateConverter
{
    // ROS to Unity position
    public static Vector3 RosToUnity(Vector3 rosPos)
    {
        return new Vector3(-rosPos.y, rosPos.z, rosPos.x);
    }

    // Unity to ROS position
    public static Vector3 UnityToRos(Vector3 unityPos)
    {
        return new Vector3(unityPos.z, -unityPos.x, unityPos.y);
    }

    // ROS to Unity rotation
    public static Quaternion RosToUnity(Quaternion rosRot)
    {
        return new Quaternion(-rosRot.y, rosRot.z, rosRot.x, -rosRot.w);
    }
}
```

---

## Exercise: Create a Visualization Dashboard

Build a Unity application that visualizes robot data from ROS 2.

### Requirements

1. Import your robot URDF into Unity
2. Subscribe to:
   - `/joint_states` - animate robot model
   - `/scan` - display LIDAR points
   - `/camera/image_raw` - show camera feed
3. Add UI elements:
   - Robot status panel
   - Sensor data readouts
   - Camera view window

### Expected Outcome

- Robot model animates based on joint states
- LIDAR points visualized around robot
- Camera feed displayed in UI
- Clean, professional visualization

---

## Summary

Unity provides powerful capabilities for robotics:

- **High-quality visualization** for demonstrations
- **ROS 2 integration** via ROS-TCP-Connector
- **URDF import** for robot models
- **ML-Agents** for reinforcement learning
- **Cross-platform** deployment options

Key skills learned:
- Setting up Unity Robotics Hub
- Importing URDF models
- Creating ROS 2 publishers and subscribers
- Visualizing sensor data
- Building custom environments

This completes Module 2 on simulation. You now have the skills to:
- Build simulation worlds in Gazebo
- Spawn and control robots
- Simulate sensors realistically
- Use Unity for visualization

**Next:** [Module 2 Quiz](./quiz)
