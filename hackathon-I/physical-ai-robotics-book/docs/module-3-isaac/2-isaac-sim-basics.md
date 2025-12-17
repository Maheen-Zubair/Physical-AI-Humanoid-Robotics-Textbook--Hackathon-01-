---
sidebar_position: 2
sidebar_label: "3.2 Isaac Sim Basics"
title: "Chapter 3.2: Isaac Sim Fundamentals"
description: "Learn the Isaac Sim interface, scene creation, and basic simulation setup"
keywords: [isaac sim, omniverse, usd, simulation, interface, scene]
---

# Isaac Sim Fundamentals

In this chapter, you will learn how to navigate the Isaac Sim interface, create scenes using USD, and set up basic simulations.

## The Isaac Sim Interface

When you launch Isaac Sim, you'll see:

```
┌────────────────────────────────────────────────────────────────────┐
│  File  Edit  Create  Physics  Replicator  Window  Help             │
├────────────────────────────────────────────────────────────────────┤
│ ┌──────────┐ ┌──────────────────────────────────────┐ ┌──────────┐│
│ │  Stage   │ │                                      │ │ Property ││
│ │  Panel   │ │           Viewport                   │ │  Panel   ││
│ │          │ │                                      │ │          ││
│ │ /World   │ │     (3D Scene View)                  │ │ Transform││
│ │  ├─Robot │ │                                      │ │ Physics  ││
│ │  └─Ground│ │                                      │ │ Material ││
│ │          │ │                                      │ │          ││
│ └──────────┘ └──────────────────────────────────────┘ └──────────┘│
│ ┌──────────────────────────────────────────────────────────────── ┐│
│ │                        Content Browser                          ││
│ │  [Assets]  [NVIDIA Assets]  [Isaac Assets]  [Project]           ││
│ └─────────────────────────────────────────────────────────────────┘│
│ ┌──────────────────────────────────────────────────────────────── ┐│
│ │  Console: Ready | FPS: 60 | Physics: Running | Play ▶ Stop ■   ││
│ └─────────────────────────────────────────────────────────────────┘│
└────────────────────────────────────────────────────────────────────┘
```

### Key Panels

| Panel | Purpose |
|-------|---------|
| **Stage** | Scene hierarchy (USD prims) |
| **Viewport** | 3D scene visualization |
| **Property** | Selected object properties |
| **Content Browser** | Asset library and files |
| **Console** | Logs and Python REPL |

### Viewport Navigation

- **Orbit**: Alt + Left Mouse
- **Pan**: Alt + Middle Mouse
- **Zoom**: Alt + Right Mouse or Scroll
- **Focus**: F key (focus on selection)
- **Frame All**: Shift + F

## Understanding USD

**USD** (Universal Scene Description) is the foundation of Isaac Sim scenes.

### USD Hierarchy

```
/World                          # Root prim
├── /World/GroundPlane          # Static ground
├── /World/Robot                # Robot model
│   ├── /World/Robot/base_link
│   ├── /World/Robot/wheel_left
│   └── /World/Robot/wheel_right
├── /World/Camera               # Camera sensor
└── /World/Light                # Scene lighting
```

### Prim Types

| Type | Description |
|------|-------------|
| **Xform** | Transform node (position, rotation, scale) |
| **Mesh** | 3D geometry |
| **Camera** | Camera sensor |
| **Light** | Light source |
| **PhysicsScene** | Physics simulation settings |
| **ArticulationRoot** | Robot base |

## Creating Your First Scene

### Step 1: Create New Stage

```python
# In the Script Editor or standalone script
from omni.isaac.kit import SimulationApp

# Launch Isaac Sim
simulation_app = SimulationApp({"headless": False})

# Now import Isaac modules
from omni.isaac.core import World
from omni.isaac.core.objects import DynamicCuboid, GroundPlane

# Create world
world = World()

# Add ground plane
world.scene.add(GroundPlane(prim_path="/World/GroundPlane", size=10))

# Add a cube
cube = world.scene.add(
    DynamicCuboid(
        prim_path="/World/Cube",
        name="my_cube",
        position=[0, 0, 1.0],
        size=[0.5, 0.5, 0.5],
        color=[1.0, 0.0, 0.0]
    )
)

# Reset world
world.reset()
```

### Step 2: Add Physics

```python
from omni.isaac.core.physics_context import PhysicsContext

# Configure physics
physics_context = PhysicsContext()
physics_context.set_gravity([0, 0, -9.81])
physics_context.set_physics_dt(1.0 / 60.0)  # 60 Hz
```

### Step 3: Run Simulation

```python
# Simulation loop
while simulation_app.is_running():
    world.step(render=True)

    # Get cube position
    position, _ = cube.get_world_pose()
    print(f"Cube position: {position}")

    # Check if cube fell below ground
    if position[2] < -1.0:
        world.reset()

simulation_app.close()
```

## Adding Robots

### Loading URDF

```python
from omni.isaac.core.utils.extensions import enable_extension
enable_extension("omni.isaac.urdf")

from omni.isaac.urdf import _urdf
from omni.isaac.core.articulations import Articulation

# Import URDF configuration
urdf_interface = _urdf.acquire_urdf_interface()
import_config = _urdf.ImportConfig()
import_config.merge_fixed_joints = False
import_config.fix_base = False
import_config.make_default_prim = True

# Import the URDF
result = urdf_interface.parse_urdf(
    "/path/to/robot.urdf",
    import_config
)

# Create robot prim
robot_prim_path = urdf_interface.import_robot(
    "/path/to/robot.urdf",
    "/World/Robot",
    import_config,
    ""
)

# Wrap as Articulation
robot = Articulation(prim_path="/World/Robot")
world.scene.add(robot)
world.reset()
```

### Using Isaac Assets

```python
from omni.isaac.core.utils.nucleus import get_assets_root_path

# Get Isaac Sim assets path
assets_root = get_assets_root_path()

# Load a pre-built robot
robot_usd_path = assets_root + "/Isaac/Robots/Franka/franka.usd"

from omni.isaac.core.utils.stage import add_reference_to_stage

add_reference_to_stage(robot_usd_path, "/World/Franka")
```

## Working with Robots

### Robot Articulation

```python
from omni.isaac.core.articulations import Articulation

# Create articulation wrapper
robot = Articulation(prim_path="/World/Robot")
world.scene.add(robot)
world.reset()

# Get joint information
num_joints = robot.num_dof
joint_names = robot.dof_names
print(f"Robot has {num_joints} joints: {joint_names}")

# Get current joint positions
joint_positions = robot.get_joint_positions()
print(f"Joint positions: {joint_positions}")
```

### Controlling Joints

```python
import numpy as np

# Set joint positions directly
target_positions = np.array([0.0, -0.5, 0.0, -1.5, 0.0, 1.0, 0.5])
robot.set_joint_positions(target_positions)

# Apply joint velocities
target_velocities = np.array([0.1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
robot.set_joint_velocities(target_velocities)

# Apply joint efforts (torques/forces)
efforts = np.array([10.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
robot.set_joint_efforts(efforts)
```

### Position Control

```python
from omni.isaac.core.controllers import ArticulationController

# Create controller
controller = ArticulationController()
robot.set_joint_positions(controller.forward(
    target_positions=target_positions,
    current_positions=robot.get_joint_positions()
))
```

## Adding Sensors

### Camera Sensor

```python
from omni.isaac.sensor import Camera
import numpy as np

# Create camera
camera = Camera(
    prim_path="/World/Camera",
    position=np.array([3.0, 0.0, 1.0]),
    resolution=(640, 480),
    frequency=30
)

world.scene.add(camera)
world.reset()
camera.initialize()

# Get camera data
for i in range(100):
    world.step(render=True)

    # RGB image
    rgb = camera.get_rgba()[:, :, :3]

    # Depth image
    depth = camera.get_depth()

    # Point cloud
    points = camera.get_pointcloud()
```

### LIDAR Sensor

```python
from omni.isaac.range_sensor import _range_sensor
from pxr import Gf

# Create LIDAR
lidar_path = "/World/Robot/Lidar"
result, lidar = omni.kit.commands.execute(
    "RangeSensorCreateLidar",
    path=lidar_path,
    parent=None,
    min_range=0.1,
    max_range=100.0,
    draw_points=True,
    draw_lines=False,
    horizontal_fov=360.0,
    vertical_fov=30.0,
    horizontal_resolution=0.4,
    vertical_resolution=4.0,
    rotation_rate=0.0,
    high_lod=False,
    yaw_offset=0.0,
    enable_semantics=False
)

# Get LIDAR data
lidar_interface = _range_sensor.acquire_lidar_sensor_interface()
depth_data = lidar_interface.get_linear_depth_data(lidar_path)
```

### IMU Sensor

```python
from omni.isaac.sensor import IMUSensor

# Create IMU
imu = IMUSensor(
    prim_path="/World/Robot/base_link/Imu",
    name="imu",
    frequency=100,
    translation=np.array([0, 0, 0])
)

world.scene.add(imu)
world.reset()

# Get IMU data
for i in range(100):
    world.step(render=True)

    frame = imu.get_current_frame()
    linear_acceleration = frame["lin_acc"]
    angular_velocity = frame["ang_vel"]
    orientation = frame["orientation"]
```

## Physics Configuration

### Physics Scene Settings

```python
from pxr import UsdPhysics, PhysxSchema

# Get or create physics scene
stage = omni.usd.get_context().get_stage()
physics_scene = UsdPhysics.Scene.Define(stage, "/World/PhysicsScene")

# Set gravity
physics_scene.CreateGravityDirectionAttr().Set((0, 0, -1))
physics_scene.CreateGravityMagnitudeAttr().Set(9.81)

# Configure PhysX settings
physx_scene = PhysxSchema.PhysxSceneAPI.Apply(physics_scene.GetPrim())
physx_scene.CreateTimeStepsPerSecondAttr().Set(60)
physx_scene.CreateEnableCCDAttr().Set(True)  # Continuous collision detection
physx_scene.CreateEnableGPUDynamicsAttr().Set(True)  # GPU physics
```

### Material Properties

```python
from pxr import UsdShade, Sdf

# Create physics material
material_path = "/World/Materials/RubberMaterial"
material = UsdShade.Material.Define(stage, material_path)

# Add physics material API
physics_material = UsdPhysics.MaterialAPI.Apply(material.GetPrim())
physics_material.CreateStaticFrictionAttr().Set(0.8)
physics_material.CreateDynamicFrictionAttr().Set(0.6)
physics_material.CreateRestitutionAttr().Set(0.3)

# Apply to collision geometry
collision_prim = stage.GetPrimAtPath("/World/Robot/wheel/collision")
binding = UsdShade.MaterialBindingAPI(collision_prim)
binding.Bind(material, UsdShade.Tokens.weakerThanDescendants, "physics")
```

## Saving and Loading Scenes

### Save as USD

```python
# Save current stage
stage = omni.usd.get_context().get_stage()
stage.Export("/path/to/my_scene.usd")

# Or save with flattened references
stage.Flatten().Export("/path/to/my_scene_flat.usd")
```

### Load USD Scene

```python
from omni.isaac.core.utils.stage import open_stage

# Open existing USD file
open_stage("/path/to/my_scene.usd")

# Or add as reference to current stage
from omni.isaac.core.utils.stage import add_reference_to_stage
add_reference_to_stage("/path/to/robot.usd", "/World/Robot")
```

## Standalone Scripts

### Complete Standalone Example

```python
"""
standalone_example.py
Run with: ~/.local/share/ov/pkg/isaac_sim-*/python.sh standalone_example.py
"""

from omni.isaac.kit import SimulationApp

# Configuration
config = {
    "headless": False,
    "width": 1280,
    "height": 720,
}

# Create simulation app (must be first)
simulation_app = SimulationApp(config)

# Now import Isaac modules
from omni.isaac.core import World
from omni.isaac.core.objects import DynamicCuboid, GroundPlane
from omni.isaac.core.utils.nucleus import get_assets_root_path
import numpy as np

def main():
    # Create world
    world = World(stage_units_in_meters=1.0)

    # Add ground
    world.scene.add(GroundPlane(
        prim_path="/World/GroundPlane",
        size=10,
        color=np.array([0.5, 0.5, 0.5])
    ))

    # Add falling cubes
    for i in range(5):
        world.scene.add(DynamicCuboid(
            prim_path=f"/World/Cube_{i}",
            name=f"cube_{i}",
            position=np.array([i * 0.5 - 1.0, 0, 2.0 + i * 0.5]),
            size=np.array([0.3, 0.3, 0.3]),
            color=np.array([np.random.rand(), np.random.rand(), np.random.rand()])
        ))

    # Reset world to initialize physics
    world.reset()

    # Simulation loop
    step_count = 0
    while simulation_app.is_running():
        world.step(render=True)
        step_count += 1

        if step_count % 100 == 0:
            print(f"Step: {step_count}")

        # Reset after 500 steps
        if step_count >= 500:
            world.reset()
            step_count = 0

    # Cleanup
    simulation_app.close()

if __name__ == "__main__":
    main()
```

---

## Exercise: Create a Robot Scene

Build a complete Isaac Sim scene with a robot and sensors.

### Requirements

1. Create a new USD stage
2. Add a ground plane
3. Load a robot (Franka or URDF)
4. Add a camera sensor
5. Run simulation and print joint positions

### Expected Outcome

- Robot appears in the scene
- Camera captures images
- Physics simulation runs smoothly
- Joint positions update each step

### Starter Code

```python
from omni.isaac.kit import SimulationApp
simulation_app = SimulationApp({"headless": False})

from omni.isaac.core import World
from omni.isaac.core.objects import GroundPlane
# Add your code here...

world = World()
world.scene.add(GroundPlane(prim_path="/World/Ground", size=10))

# TODO: Add robot
# TODO: Add camera
# TODO: Run simulation loop

simulation_app.close()
```

---

## Summary

Isaac Sim fundamentals include:

- **Interface navigation**: Stage, viewport, properties panels
- **USD scene management**: Hierarchical scene representation
- **Robot loading**: URDF import and Isaac assets
- **Sensor simulation**: Cameras, LIDAR, IMU
- **Physics configuration**: Materials, collision, dynamics

Key skills learned:
- Creating and saving USD scenes
- Adding and controlling robots
- Configuring sensors
- Writing standalone Python scripts

In the next chapter, you will learn about domain randomization for robust training.

**Next:** [Domain Randomization](./3-domain-randomization.md)
