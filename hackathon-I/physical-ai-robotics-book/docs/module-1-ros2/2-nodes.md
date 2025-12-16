---
sidebar_position: 2
sidebar_label: "1.2 Nodes"
title: "Chapter 1.2: Nodes and the Computation Graph"
description: "Learn to create ROS 2 nodes using Python and understand the computation graph"
keywords: [ros2, nodes, rclpy, computation graph, python]
---

# Nodes and the Computation Graph

In this chapter, you will learn what ROS 2 nodes are, how they form a computation graph, and how to create your own nodes using Python (rclpy).

## What is a Node?

A **node** is the fundamental unit of computation in ROS 2. Each node is designed to perform a single, well-defined task. Examples include:

- A **camera driver node** that captures images from a camera
- An **object detection node** that processes images to find objects
- A **motor controller node** that sends commands to wheel motors
- A **path planner node** that calculates routes for navigation

### Why Use Multiple Nodes?

You might wonder why not put everything in one program. The multi-node architecture provides several benefits:

1. **Fault isolation**: If one node crashes, others keep running
2. **Reusability**: A camera driver works with any algorithm that needs images
3. **Scalability**: Distribute nodes across multiple computers
4. **Maintainability**: Smaller codebases are easier to understand and debug
5. **Language flexibility**: Each node can use the best language for its task

## The Computation Graph

When multiple nodes run and communicate, they form a **computation graph**. This graph shows:

- **Nodes** as vertices (the processes)
- **Topics** as edges (the communication channels)

```
                    ┌─────────────┐
                    │   /camera   │
                    │   driver    │
                    └──────┬──────┘
                           │ /image
                           ▼
        ┌──────────────────┴──────────────────┐
        │                                      │
        ▼                                      ▼
┌───────────────┐                      ┌───────────────┐
│   /detector   │                      │  /visualizer  │
│   (objects)   │                      │               │
└───────┬───────┘                      └───────────────┘
        │ /detections
        ▼
┌───────────────┐
│   /planner    │
└───────────────┘
```

The computation graph is **dynamic** - nodes can join and leave at any time, and the graph reconfigures automatically.

## Creating Nodes with rclpy

**rclpy** is the ROS 2 client library for Python. It provides the classes and functions needed to create nodes.

### Basic Node Structure

Every rclpy node follows this pattern:

```python
import rclpy
from rclpy.node import Node

class MyNode(Node):
    def __init__(self):
        super().__init__('my_node_name')  # Node name
        self.get_logger().info('Node started!')

def main(args=None):
    rclpy.init(args=args)           # Initialize ROS 2
    node = MyNode()                  # Create node instance
    rclpy.spin(node)                 # Process callbacks
    node.destroy_node()              # Clean up
    rclpy.shutdown()                 # Shutdown ROS 2

if __name__ == '__main__':
    main()
```

Let's break down each part:

### 1. Imports

```python
import rclpy
from rclpy.node import Node
```

- `rclpy` is the main ROS 2 Python library
- `Node` is the base class for all nodes

### 2. Node Class

```python
class MyNode(Node):
    def __init__(self):
        super().__init__('my_node_name')
```

- Your node class inherits from `Node`
- `super().__init__()` initializes the base class with a **unique node name**
- The node name appears in `ros2 node list` and logs

### 3. Initialization

```python
rclpy.init(args=args)
```

This initializes the ROS 2 communication system. It must be called before creating any nodes.

### 4. Spinning

```python
rclpy.spin(node)
```

**Spinning** means continuously checking for and processing incoming messages and timer callbacks. Without spinning, your node won't respond to anything.

### 5. Cleanup

```python
node.destroy_node()
rclpy.shutdown()
```

Proper cleanup ensures resources are released and the node unregisters from the graph.

## Node Logging

ROS 2 provides a built-in logging system with multiple severity levels:

```python
class LoggingExample(Node):
    def __init__(self):
        super().__init__('logging_example')

        # Different log levels
        self.get_logger().debug('Debug message')    # Detailed debugging
        self.get_logger().info('Info message')      # Normal operation
        self.get_logger().warn('Warning message')   # Something unexpected
        self.get_logger().error('Error message')    # Something failed
        self.get_logger().fatal('Fatal message')    # Critical failure
```

Log messages include:
- Timestamp
- Log level
- Node name
- Your message

Example output:
```
[INFO] [1699123456.789012345] [my_node]: Node started!
```

## Node Parameters

Nodes can have configurable **parameters** that modify their behavior without changing code:

```python
class ParameterNode(Node):
    def __init__(self):
        super().__init__('parameter_node')

        # Declare parameters with default values
        self.declare_parameter('robot_name', 'default_robot')
        self.declare_parameter('update_rate', 10.0)

        # Get parameter values
        robot_name = self.get_parameter('robot_name').value
        rate = self.get_parameter('update_rate').value

        self.get_logger().info(f'Robot: {robot_name}, Rate: {rate} Hz')
```

Parameters can be set from:
- Command line: `ros2 run my_pkg my_node --ros-args -p robot_name:=atlas`
- Launch files
- YAML configuration files

## Timers

Nodes often need to perform tasks periodically. **Timers** handle this:

```python
class TimerNode(Node):
    def __init__(self):
        super().__init__('timer_node')
        self.counter = 0

        # Create timer: period in seconds, callback function
        self.timer = self.create_timer(1.0, self.timer_callback)

    def timer_callback(self):
        self.counter += 1
        self.get_logger().info(f'Timer fired: {self.counter}')
```

The timer callback runs at the specified rate (here, once per second) as long as the node is spinning.

## Node Lifecycle

ROS 2 supports **managed lifecycle nodes** for more control over node states:

```
┌─────────────┐     configure()     ┌─────────────┐
│ Unconfigured│ ─────────────────▶  │ Inactive    │
└─────────────┘                     └──────┬──────┘
       ▲                                   │
       │ cleanup()                         │ activate()
       │                                   ▼
┌──────┴──────┐                     ┌─────────────┐
│   Finalized │ ◀───────────────── │   Active    │
└─────────────┘     deactivate()    └─────────────┘
                    + cleanup()
```

Lifecycle nodes are useful for:
- Ensuring proper initialization order
- Managing resources (like hardware connections)
- Graceful shutdown and recovery

For now, we'll use basic nodes. Lifecycle nodes are covered in advanced topics.

## Creating a ROS 2 Package

Nodes live inside **packages**. Let's create a package for our examples:

### Step 1: Create the Package

```bash
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_python my_robot_pkg
```

This creates:
```
my_robot_pkg/
├── my_robot_pkg/
│   └── __init__.py
├── package.xml
├── setup.cfg
├── setup.py
└── resource/
    └── my_robot_pkg
```

### Step 2: Add Dependencies

Edit `package.xml` to add dependencies:

```xml
<exec_depend>rclpy</exec_depend>
<exec_depend>std_msgs</exec_depend>
```

### Step 3: Create Node File

Create `my_robot_pkg/my_first_node.py`:

```python
import rclpy
from rclpy.node import Node

class MyFirstNode(Node):
    def __init__(self):
        super().__init__('my_first_node')
        self.counter = 0
        self.timer = self.create_timer(0.5, self.timer_callback)
        self.get_logger().info('My first node has started!')

    def timer_callback(self):
        self.counter += 1
        self.get_logger().info(f'Hello ROS 2! Count: {self.counter}')

def main(args=None):
    rclpy.init(args=args)
    node = MyFirstNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Step 4: Register the Entry Point

Edit `setup.py`:

```python
entry_points={
    'console_scripts': [
        'my_first_node = my_robot_pkg.my_first_node:main',
    ],
},
```

### Step 5: Build and Run

```bash
cd ~/ros2_ws
colcon build --packages-select my_robot_pkg
source install/setup.bash
ros2 run my_robot_pkg my_first_node
```

## Command-Line Tools for Nodes

ROS 2 provides tools to inspect running nodes:

### List Nodes

```bash
ros2 node list
```

Output:
```
/my_first_node
```

### Get Node Info

```bash
ros2 node info /my_first_node
```

Shows:
- Subscribers
- Publishers
- Service servers
- Service clients
- Action servers
- Action clients

### List Parameters

```bash
ros2 param list /my_first_node
```

### Get/Set Parameters

```bash
ros2 param get /my_first_node robot_name
ros2 param set /my_first_node update_rate 20.0
```

---

## Exercise: Create a Counter Node

Create a node that counts up and logs every second.

### Requirements

1. Create a new Python file `counter_node.py` in your package
2. The node should:
   - Be named `counter_node`
   - Have a parameter `start_value` (default: 0)
   - Count up every second
   - Log the current count

### Solution Template

```python
import rclpy
from rclpy.node import Node

class CounterNode(Node):
    def __init__(self):
        super().__init__('counter_node')

        # Declare parameter
        self.declare_parameter('start_value', 0)

        # Initialize counter from parameter
        self.counter = self.get_parameter('start_value').value

        # Create timer (1 second interval)
        self.timer = self.create_timer(1.0, self.timer_callback)

        self.get_logger().info(f'Counter starting at {self.counter}')

    def timer_callback(self):
        self.get_logger().info(f'Count: {self.counter}')
        self.counter += 1

def main(args=None):
    rclpy.init(args=args)
    node = CounterNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Test Your Node

```bash
# Build
colcon build --packages-select my_robot_pkg
source install/setup.bash

# Run with default start value
ros2 run my_robot_pkg counter_node

# Run with custom start value
ros2 run my_robot_pkg counter_node --ros-args -p start_value:=100
```

### Expected Outcome

- Node logs increasing numbers every second
- Starting value can be customized via parameter
- Node appears in `ros2 node list`

---

## Summary

Nodes are the building blocks of ROS 2 applications. Each node performs a specific task and communicates with others to form a computation graph. Using rclpy, you can create Python nodes that:

- Initialize with `rclpy.init()` and spin with `rclpy.spin()`
- Log messages at different severity levels
- Use parameters for configuration
- Execute periodic tasks with timers
- Live inside packages for organization and distribution

In the next chapter, you will learn how nodes communicate using topics and the publish-subscribe pattern.

**Next:** [Topics and Publishers/Subscribers](./3-topics.md)
