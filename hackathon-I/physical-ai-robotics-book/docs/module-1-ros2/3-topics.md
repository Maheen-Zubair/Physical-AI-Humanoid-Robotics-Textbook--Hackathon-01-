---
sidebar_position: 3
sidebar_label: "1.3 Topics"
title: "Chapter 1.3: Topics and Publishers/Subscribers"
description: "Learn the publish-subscribe pattern for ROS 2 communication using topics"
keywords: [ros2, topics, publisher, subscriber, messages, qos]
---

# Topics and Publishers/Subscribers

In this chapter, you will learn how ROS 2 nodes communicate using topics, messages, and the publish-subscribe pattern.

## What is a Topic?

A **topic** is a named communication channel that nodes use to exchange messages. Topics implement the **publish-subscribe** pattern:

- **Publishers** send messages to a topic
- **Subscribers** receive messages from a topic
- Multiple publishers can send to the same topic
- Multiple subscribers can receive from the same topic

```
┌───────────────┐          /sensor_data          ┌───────────────┐
│  Publisher A  │ ─────────────┬────────────────▶│ Subscriber 1  │
└───────────────┘              │                 └───────────────┘
                               │
┌───────────────┐              │                 ┌───────────────┐
│  Publisher B  │ ─────────────┴────────────────▶│ Subscriber 2  │
└───────────────┘                                └───────────────┘
```

### Topic Naming

Topic names follow conventions:
- Start with `/` (absolute) or without (relative to namespace)
- Use lowercase letters and underscores
- Organized hierarchically: `/robot/camera/image`

Examples:
- `/cmd_vel` - velocity commands
- `/odom` - odometry data
- `/camera/image_raw` - raw camera images
- `/scan` - LIDAR scan data

## Messages

Messages define the **structure** of data sent over topics. ROS 2 provides standard message types and allows custom definitions.

### Standard Message Types

Common message packages:

| Package | Description | Example Types |
|---------|-------------|---------------|
| `std_msgs` | Basic types | `String`, `Int32`, `Float64`, `Bool` |
| `geometry_msgs` | Geometry | `Twist`, `Pose`, `Point`, `Vector3` |
| `sensor_msgs` | Sensors | `Image`, `LaserScan`, `Imu`, `JointState` |
| `nav_msgs` | Navigation | `Odometry`, `Path`, `OccupancyGrid` |

### Exploring Messages

Use command-line tools to explore message types:

```bash
# List all available message types
ros2 interface list | grep msg

# Show message structure
ros2 interface show std_msgs/msg/String

# Show complex message
ros2 interface show geometry_msgs/msg/Twist
```

Example output for `geometry_msgs/msg/Twist`:
```
# This expresses velocity in free space broken into its linear and angular parts.

Vector3 linear
	float64 x
	float64 y
	float64 z
Vector3 angular
	float64 x
	float64 y
	float64 z
```

## Creating a Publisher

Here's how to create a node that publishes messages:

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class MinimalPublisher(Node):
    def __init__(self):
        super().__init__('minimal_publisher')

        # Create publisher: message type, topic name, queue size
        self.publisher_ = self.create_publisher(String, 'topic', 10)

        # Timer to publish periodically
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0

    def timer_callback(self):
        msg = String()
        msg.data = f'Hello World: {self.i}'
        self.publisher_.publish(msg)
        self.get_logger().info(f'Publishing: "{msg.data}"')
        self.i += 1

def main(args=None):
    rclpy.init(args=args)
    node = MinimalPublisher()
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

### Publisher Breakdown

```python
self.publisher_ = self.create_publisher(String, 'topic', 10)
```

- `String` - The message type
- `'topic'` - The topic name
- `10` - The queue size (buffer for outgoing messages)

```python
msg = String()
msg.data = f'Hello World: {self.i}'
self.publisher_.publish(msg)
```

- Create a message instance
- Fill in the fields
- Publish to the topic

## Creating a Subscriber

Here's a node that subscribes to messages:

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class MinimalSubscriber(Node):
    def __init__(self):
        super().__init__('minimal_subscriber')

        # Create subscription: type, topic, callback, queue size
        self.subscription = self.create_subscription(
            String,
            'topic',
            self.listener_callback,
            10)

    def listener_callback(self, msg):
        self.get_logger().info(f'I heard: "{msg.data}"')

def main(args=None):
    rclpy.init(args=args)
    node = MinimalSubscriber()
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

### Subscriber Breakdown

```python
self.subscription = self.create_subscription(
    String,           # Message type
    'topic',          # Topic name
    self.listener_callback,  # Callback function
    10)               # Queue size
```

The callback function receives the message as its argument:

```python
def listener_callback(self, msg):
    self.get_logger().info(f'I heard: "{msg.data}"')
```

## Quality of Service (QoS)

QoS settings control how messages are delivered. The defaults work for most cases, but some situations require specific settings.

### QoS Profiles

ROS 2 provides preset profiles:

```python
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

# Reliable delivery (like TCP)
reliable_qos = QoSProfile(
    reliability=ReliabilityPolicy.RELIABLE,
    history=HistoryPolicy.KEEP_LAST,
    depth=10
)

# Best-effort delivery (like UDP)
sensor_qos = QoSProfile(
    reliability=ReliabilityPolicy.BEST_EFFORT,
    history=HistoryPolicy.KEEP_LAST,
    depth=5
)
```

### When to Use Each

| Profile | Use Case |
|---------|----------|
| **Reliable** | Commands, configuration, state changes |
| **Best Effort** | High-frequency sensor data, video streams |

### Sensor Data QoS

For sensor data, use the sensor data QoS profile:

```python
from rclpy.qos import qos_profile_sensor_data

self.subscription = self.create_subscription(
    Image,
    '/camera/image_raw',
    self.image_callback,
    qos_profile_sensor_data)
```

## Publishing Complex Messages

Let's publish robot velocity commands using `geometry_msgs/Twist`:

```python
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class VelocityPublisher(Node):
    def __init__(self):
        super().__init__('velocity_publisher')
        self.publisher_ = self.create_publisher(Twist, 'cmd_vel', 10)
        self.timer = self.create_timer(0.1, self.timer_callback)

    def timer_callback(self):
        msg = Twist()
        msg.linear.x = 0.5   # Forward velocity (m/s)
        msg.linear.y = 0.0
        msg.linear.z = 0.0
        msg.angular.x = 0.0
        msg.angular.y = 0.0
        msg.angular.z = 0.1  # Rotation (rad/s)
        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = VelocityPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
```

## Command-Line Tools for Topics

### List Topics

```bash
ros2 topic list
```

### Echo Messages

```bash
ros2 topic echo /topic
```

### Get Topic Info

```bash
ros2 topic info /topic
```

Shows:
- Message type
- Publisher count
- Subscriber count

### Check Message Rate

```bash
ros2 topic hz /topic
```

Shows publishing frequency.

### Publish from Command Line

```bash
# Publish a String
ros2 topic pub /topic std_msgs/msg/String "{data: 'Hello'}"

# Publish once
ros2 topic pub --once /topic std_msgs/msg/String "{data: 'Hello'}"

# Publish at rate
ros2 topic pub --rate 10 /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.5}}"
```

## A Complete Example: Temperature Monitor

Let's create a system with a temperature sensor publisher and a monitor subscriber.

### Temperature Publisher

```python
# temperature_publisher.py
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64
import random

class TemperaturePublisher(Node):
    def __init__(self):
        super().__init__('temperature_sensor')
        self.publisher_ = self.create_publisher(Float64, 'temperature', 10)
        self.timer = self.create_timer(1.0, self.publish_temperature)
        self.base_temp = 25.0

    def publish_temperature(self):
        msg = Float64()
        # Simulate temperature with some noise
        msg.data = self.base_temp + random.uniform(-2.0, 2.0)
        self.publisher_.publish(msg)
        self.get_logger().info(f'Temperature: {msg.data:.1f}°C')

def main(args=None):
    rclpy.init(args=args)
    node = TemperaturePublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
```

### Temperature Monitor

```python
# temperature_monitor.py
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64

class TemperatureMonitor(Node):
    def __init__(self):
        super().__init__('temperature_monitor')
        self.subscription = self.create_subscription(
            Float64,
            'temperature',
            self.temperature_callback,
            10)
        self.threshold = 27.0

    def temperature_callback(self, msg):
        temp = msg.data
        if temp > self.threshold:
            self.get_logger().warn(f'HIGH TEMP: {temp:.1f}°C')
        else:
            self.get_logger().info(f'Normal: {temp:.1f}°C')

def main(args=None):
    rclpy.init(args=args)
    node = TemperatureMonitor()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
```

Run both nodes in separate terminals to see them communicate.

---

## Exercise: Number Relay

Create a publisher-subscriber system where:
1. A publisher sends random numbers (1-100)
2. A subscriber receives them and logs whether each is even or odd

### Requirements

1. Publisher node: `number_generator`
   - Publishes to topic `/random_number`
   - Message type: `std_msgs/msg/Int32`
   - Publishes every 0.5 seconds

2. Subscriber node: `number_checker`
   - Subscribes to `/random_number`
   - Logs "EVEN: X" or "ODD: X" for each number

### Expected Output

Terminal 1 (Publisher):
```
[INFO] [number_generator]: Publishing: 42
[INFO] [number_generator]: Publishing: 17
```

Terminal 2 (Subscriber):
```
[INFO] [number_checker]: EVEN: 42
[INFO] [number_checker]: ODD: 17
```

---

## Summary

Topics are the primary communication mechanism in ROS 2:

- Publishers send messages to named topics
- Subscribers receive messages from topics
- Messages define the data structure
- QoS settings control delivery guarantees
- Multiple publishers and subscribers can share a topic

The publish-subscribe pattern enables:
- Decoupled communication (publishers don't know about subscribers)
- Many-to-many data distribution
- Flexible system architecture

In the next chapter, you will learn about services and actions for request-response and long-running task patterns.

**Next:** [Services and Actions](./4-services.md)
