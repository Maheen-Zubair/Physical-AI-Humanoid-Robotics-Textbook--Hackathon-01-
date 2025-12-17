---
sidebar_position: 5
sidebar_label: "2.5 Physics"
title: "Chapter 2.5: Physics and Collision Simulation"
description: "Understand physics engines, collision detection, and realistic dynamics in robotics simulation"
keywords: [gazebo, physics, collision, dynamics, friction, contact]
---

# Physics and Collision Simulation

In this chapter, you will learn how physics engines work, how to configure collision detection, and how to tune physical parameters for realistic robot simulation.

## How Physics Engines Work

A physics engine simulates the laws of motion. At each time step, it:

1. **Detects collisions** between objects
2. **Computes contact forces** at collision points
3. **Applies constraints** (joints, limits)
4. **Integrates equations of motion** to update positions and velocities

```
┌─────────────────────────────────────────────────────────────┐
│                    Physics Update Loop                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│   │   Collision  │───▶│   Contact    │───▶│  Constraint  │ │
│   │  Detection   │    │  Resolution  │    │   Solving    │ │
│   └──────────────┘    └──────────────┘    └──────────────┘ │
│          │                                       │          │
│          ▼                                       ▼          │
│   ┌──────────────┐                       ┌──────────────┐  │
│   │   Broad      │                       │  Integration │  │
│   │   Phase      │                       │  (Motion)    │  │
│   └──────────────┘                       └──────────────┘  │
│          │                                       │          │
│          ▼                                       ▼          │
│   ┌──────────────┐                       ┌──────────────┐  │
│   │   Narrow     │                       │   Update     │  │
│   │   Phase      │                       │   State      │  │
│   └──────────────┘                       └──────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Physics Engines in Gazebo

Gazebo supports multiple physics engines:

| Engine | Strengths | Best For |
|--------|-----------|----------|
| **DART** | Accurate articulated bodies | Robot arms, humanoids |
| **Bullet** | Fast, general purpose | Mobile robots, games |
| **ODE** | Stable, well-tested | General simulation |
| **Simbody** | Biomechanics | Human body modeling |

### Selecting a Physics Engine

```xml
<physics name="my_physics" type="dart">
  <max_step_size>0.001</max_step_size>
  <real_time_factor>1.0</real_time_factor>
</physics>
```

In Gazebo Fortress+, the physics engine is selected via the gz-physics plugin:

```xml
<plugin filename="gz-sim-physics-system"
        name="gz::sim::systems::Physics">
</plugin>
```

## Configuring Physics Parameters

### Time Step

The time step determines simulation accuracy and speed:

```xml
<physics name="fast_physics" type="ignored">
  <!-- Small step = accurate but slow -->
  <max_step_size>0.001</max_step_size>

  <!-- Large step = fast but less accurate -->
  <!-- <max_step_size>0.01</max_step_size> -->
</physics>
```

### Time Step Guidelines

| Time Step | Use Case | Notes |
|-----------|----------|-------|
| 0.0001s | High-precision manipulation | Very slow |
| 0.001s | General robotics | Recommended |
| 0.005s | Mobile robots | Good balance |
| 0.01s | Quick testing | May miss collisions |

### Real-Time Factor

Control simulation speed:

```xml
<!-- Run at real-time -->
<real_time_factor>1.0</real_time_factor>

<!-- Run as fast as possible (training) -->
<real_time_factor>0</real_time_factor>

<!-- Slow motion (debugging) -->
<real_time_factor>0.5</real_time_factor>
```

### Gravity

```xml
<!-- Earth gravity (default) -->
<gravity>0 0 -9.81</gravity>

<!-- Moon gravity -->
<gravity>0 0 -1.62</gravity>

<!-- Zero-G (space simulation) -->
<gravity>0 0 0</gravity>
```

## Collision Detection

### Collision Geometry

Collision shapes should be simpler than visual geometry for performance:

```xml
<link name="complex_part">
  <!-- Detailed visual mesh -->
  <visual name="visual">
    <geometry>
      <mesh>
        <uri>model://robot/meshes/detailed_part.dae</uri>
      </mesh>
    </geometry>
  </visual>

  <!-- Simplified collision geometry -->
  <collision name="collision">
    <geometry>
      <box>
        <size>0.1 0.1 0.2</size>
      </box>
    </geometry>
  </collision>
</link>
```

### Collision Primitives

From fastest to slowest:
1. **Sphere** - Fastest
2. **Box** - Fast
3. **Cylinder** - Moderate
4. **Convex hull** - Slow
5. **Mesh** - Slowest

### Collision Categories

Use categories to filter which objects can collide:

```xml
<collision name="wheel_collision">
  <geometry>
    <cylinder radius="0.1" length="0.05"/>
  </geometry>
  <surface>
    <contact>
      <collide_bitmask>0x01</collide_bitmask>
    </contact>
  </surface>
</collision>
```

## Friction

Friction determines how objects slide against each other.

### Coulomb Friction Model

```xml
<collision name="collision">
  <geometry>
    <box><size>1 1 1</size></box>
  </geometry>
  <surface>
    <friction>
      <ode>
        <!-- Friction coefficients -->
        <mu>0.8</mu>    <!-- Primary direction -->
        <mu2>0.8</mu2>  <!-- Secondary direction -->
        <slip1>0.0</slip1>
        <slip2>0.0</slip2>
      </ode>
    </friction>
  </surface>
</collision>
```

### Friction Coefficients

| Material Pair | μ (mu) |
|---------------|--------|
| Rubber on concrete | 0.8 - 1.0 |
| Rubber on wood | 0.7 - 0.8 |
| Steel on steel | 0.4 - 0.6 |
| Ice on ice | 0.03 - 0.05 |
| Teflon on Teflon | 0.04 |

### Wheel Friction

For mobile robot wheels:

```xml
<gazebo reference="wheel_link">
  <mu1>1.0</mu1>
  <mu2>1.0</mu2>
  <kp>1000000.0</kp>
  <kd>100.0</kd>
  <minDepth>0.001</minDepth>
  <maxVel>1.0</maxVel>
</gazebo>
```

## Contact Properties

Fine-tune how objects interact at contact points.

### Contact Parameters

```xml
<surface>
  <contact>
    <!-- Baumgarte stabilization coefficient -->
    <ode>
      <kp>1e6</kp>      <!-- Contact stiffness -->
      <kd>100</kd>      <!-- Contact damping -->
      <min_depth>0.001</min_depth>  <!-- Penetration before contact -->
      <max_vel>1.0</max_vel>  <!-- Max correcting velocity -->
    </ode>
  </contact>
</surface>
```

### Soft Contact (Deformable)

For objects that should "sink" slightly:

```xml
<surface>
  <contact>
    <ode>
      <soft_cfm>0.001</soft_cfm>  <!-- Constraint force mixing -->
      <soft_erp>0.2</soft_erp>    <!-- Error reduction parameter -->
      <kp>10000</kp>              <!-- Lower stiffness -->
      <kd>100</kd>
    </ode>
  </contact>
</surface>
```

### Bouncy Objects

For elastic collisions:

```xml
<surface>
  <bounce>
    <restitution_coefficient>0.8</restitution_coefficient>
    <threshold>0.01</threshold>
  </bounce>
</surface>
```

## Joint Dynamics

### Joint Friction

```xml
<joint name="arm_joint" type="revolute">
  <parent link="base"/>
  <child link="arm"/>
  <axis xyz="0 1 0"/>
  <dynamics>
    <damping>0.1</damping>      <!-- Viscous friction (velocity-dependent) -->
    <friction>0.05</friction>   <!-- Coulomb friction (constant) -->
  </dynamics>
</joint>
```

### Joint Limits

```xml
<joint name="arm_joint" type="revolute">
  <axis xyz="0 1 0"/>
  <limit>
    <lower>-1.57</lower>        <!-- Min position (rad) -->
    <upper>1.57</upper>         <!-- Max position (rad) -->
    <effort>100</effort>        <!-- Max torque (N·m) -->
    <velocity>2.0</velocity>    <!-- Max velocity (rad/s) -->
  </limit>
</joint>
```

## Inertia Configuration

Correct inertia is crucial for realistic dynamics.

### Calculating Inertia

For a box with dimensions (w, d, h) and mass m:

```
Ixx = (1/12) * m * (d² + h²)
Iyy = (1/12) * m * (w² + h²)
Izz = (1/12) * m * (w² + d²)
```

### URDF Inertia Block

```xml
<link name="box_link">
  <inertial>
    <mass value="5.0"/>
    <origin xyz="0 0 0" rpy="0 0 0"/>
    <inertia
      ixx="0.0417"  <!-- (1/12)*5*(0.3² + 0.1²) -->
      ixy="0.0"
      ixz="0.0"
      iyy="0.0708"  <!-- (1/12)*5*(0.4² + 0.1²) -->
      iyz="0.0"
      izz="0.0625"  <!-- (1/12)*5*(0.4² + 0.3²) -->
    />
  </inertial>
</link>
```

### Common Inertia Formulas

| Shape | Ixx | Iyy | Izz |
|-------|-----|-----|-----|
| Solid box (w×d×h) | m(d²+h²)/12 | m(w²+h²)/12 | m(w²+d²)/12 |
| Solid cylinder (r, h) | m(3r²+h²)/12 | m(3r²+h²)/12 | mr²/2 |
| Solid sphere (r) | 2mr²/5 | 2mr²/5 | 2mr²/5 |

## Debugging Physics Issues

### Common Problems

**1. Objects fall through the ground**
- Increase contact stiffness (`kp`)
- Decrease time step
- Check collision geometry exists

**2. Robot vibrates or jitters**
- Reduce damping
- Check inertia values
- Increase time step slightly

**3. Wheels slip**
- Increase friction coefficients
- Add more collision contacts

**4. Joints explode**
- Check inertia values aren't too small
- Add joint damping
- Verify limits are set

### Visualization Tools

```bash
# View collision geometry
gz model -m robot_name --collision

# Check physics state
gz physics --info

# Monitor frame rate
gz stats
```

### ROS 2 Diagnostics

```bash
# Check TF tree for issues
ros2 run tf2_tools view_frames

# Monitor joint states
ros2 topic echo /joint_states
```

## Performance Optimization

### Tips for Faster Simulation

1. **Simplify collision geometry**
   - Use primitives over meshes
   - Reduce vertex count

2. **Increase time step** (if accuracy permits)
   - 0.001s → 0.005s can double speed

3. **Reduce update rates**
   - Sensors: 10Hz instead of 30Hz
   - Publishing: Only what's needed

4. **Disable unused features**
   - Turn off shadows
   - Disable visualization in headless mode

### Headless Simulation

Run without GUI for maximum speed:

```bash
# Server only (no GUI)
gz sim -s world.sdf

# With ROS 2 bridge
gz sim -s world.sdf &
ros2 run ros_gz_bridge parameter_bridge ...
```

## Example: Tuned Mobile Robot

```xml
<?xml version="1.0"?>
<robot name="tuned_robot">

  <link name="base_link">
    <visual>
      <geometry><box size="0.4 0.3 0.1"/></geometry>
    </visual>
    <collision>
      <geometry><box size="0.4 0.3 0.1"/></geometry>
    </collision>
    <inertial>
      <mass value="5.0"/>
      <inertia ixx="0.0479" ixy="0" ixz="0"
               iyy="0.0708" iyz="0" izz="0.1042"/>
    </inertial>
  </link>

  <link name="wheel_left">
    <visual>
      <geometry><cylinder radius="0.1" length="0.05"/></geometry>
    </visual>
    <collision>
      <geometry><cylinder radius="0.1" length="0.05"/></geometry>
    </collision>
    <inertial>
      <mass value="0.5"/>
      <inertia ixx="0.0014" ixy="0" ixz="0"
               iyy="0.0014" iyz="0" izz="0.0025"/>
    </inertial>
  </link>

  <joint name="wheel_left_joint" type="continuous">
    <parent link="base_link"/>
    <child link="wheel_left"/>
    <origin xyz="0 0.175 0" rpy="-1.5708 0 0"/>
    <axis xyz="0 0 1"/>
    <dynamics damping="0.01" friction="0.005"/>
  </joint>

  <!-- Gazebo physics tuning -->
  <gazebo reference="wheel_left">
    <mu1>1.0</mu1>
    <mu2>0.8</mu2>
    <kp>1000000</kp>
    <kd>100</kd>
    <minDepth>0.001</minDepth>
  </gazebo>

  <gazebo reference="base_link">
    <mu1>0.2</mu1>
    <mu2>0.2</mu2>
  </gazebo>

</robot>
```

---

## Exercise: Tune Physics Parameters

Optimize physics parameters for a specific scenario.

### Requirements

1. Create a ramp world (incline of 15°)
2. Spawn a wheeled robot at the top
3. Tune friction so the robot:
   - Stays still when motors are off
   - Can climb when motors are on
4. Adjust time step to balance accuracy and speed

### Expected Outcome

- Robot doesn't slide down when stationary
- Robot can drive up the ramp
- Simulation runs at real-time or faster

### Parameters to Adjust

```xml
<!-- Try different values -->
<mu1>0.5 to 1.5</mu1>
<max_step_size>0.001 to 0.01</max_step_size>
<kp>100000 to 10000000</kp>
```

---

## Summary

Understanding physics simulation is key to realistic robotics:

- **Physics engines**: DART, Bullet, ODE each have strengths
- **Time step**: Balances accuracy and speed
- **Collision**: Use simple primitives when possible
- **Friction**: Critical for wheeled robots
- **Inertia**: Must be realistic for stable simulation

Key skills learned:
- Configuring physics engine parameters
- Setting up collision geometry
- Tuning friction coefficients
- Debugging physics issues
- Optimizing simulation performance

In the next chapter, you will learn about Unity as an alternative simulation platform for visualization and machine learning.

**Next:** [Unity for Robotics](./6-unity.md)
