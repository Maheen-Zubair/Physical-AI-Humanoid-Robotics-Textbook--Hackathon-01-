---
sidebar_position: 4
sidebar_label: "1.4 Services & Actions"
title: "Chapter 1.4: Services and Actions"
description: "Learn request-response patterns with services and long-running tasks with actions"
keywords: [ros2, services, actions, request, response, callback]
---

# Services and Actions

In this chapter, you will learn about two additional communication patterns: services for request-response interactions and actions for long-running tasks with feedback.

## When Topics Aren't Enough

Topics work well for continuous data streams, but some scenarios need different patterns:

| Scenario | Best Pattern |
|----------|-------------|
| Continuous sensor data | Topic (pub/sub) |
| "What is the current time?" | Service (request/response) |
| "Navigate to waypoint X" | Action (long-running with feedback) |

## Services: Request-Response

A **service** implements the request-response pattern:

1. Client sends a **request**
2. Server processes the request
3. Server sends a **response**
4. Client receives the response

```
┌──────────┐    Request     ┌──────────┐
│  Client  │ ─────────────▶ │  Server  │
│          │                │          │
│          │ ◀───────────── │          │
└──────────┘    Response    └──────────┘
```

### Service Definitions

Services use `.srv` files that define request and response structures:

```
# Example: AddTwoInts.srv
int64 a
int64 b
---
int64 sum
```

The `---` separates request fields (above) from response fields (below).

### Standard Services

ROS 2 provides standard service types:

| Service | Purpose |
|---------|---------|
| `std_srvs/srv/Empty` | Trigger with no data |
| `std_srvs/srv/SetBool` | Set a boolean value |
| `std_srvs/srv/Trigger` | Trigger and get success/message |

Explore service definitions:

```bash
ros2 interface show std_srvs/srv/SetBool
```

Output:
```
bool data # e.g. for hardware enabling / disabling
---
bool success   # indicate successful run of triggered service
string message # informational, e.g. for error messages
```

### Creating a Service Server

```python
import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts

class AdditionServer(Node):
    def __init__(self):
        super().__init__('addition_server')
        self.srv = self.create_service(
            AddTwoInts,
            'add_two_ints',
            self.add_callback)
        self.get_logger().info('Addition service ready')

    def add_callback(self, request, response):
        response.sum = request.a + request.b
        self.get_logger().info(
            f'Request: {request.a} + {request.b} = {response.sum}')
        return response

def main(args=None):
    rclpy.init(args=args)
    node = AdditionServer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
```

### Creating a Service Client

```python
import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts

class AdditionClient(Node):
    def __init__(self):
        super().__init__('addition_client')
        self.client = self.create_client(AddTwoInts, 'add_two_ints')

        # Wait for service to be available
        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for service...')

    def send_request(self, a, b):
        request = AddTwoInts.Request()
        request.a = a
        request.b = b
        future = self.client.call_async(request)
        return future

def main(args=None):
    rclpy.init(args=args)
    client = AdditionClient()

    future = client.send_request(5, 3)

    # Wait for response
    rclpy.spin_until_future_complete(client, future)

    result = future.result()
    client.get_logger().info(f'Result: {result.sum}')

    client.destroy_node()
    rclpy.shutdown()
```

### Service Command-Line Tools

```bash
# List services
ros2 service list

# Get service type
ros2 service type /add_two_ints

# Call service from command line
ros2 service call /add_two_ints example_interfaces/srv/AddTwoInts "{a: 5, b: 3}"
```

## Actions: Long-Running Tasks

**Actions** are for tasks that:
- Take a long time to complete
- Provide progress feedback
- Can be canceled

Examples:
- Navigate to a goal location
- Execute a robot arm trajectory
- Perform a complex manipulation task

### Action Structure

Actions have three parts:

1. **Goal**: What you want to achieve
2. **Feedback**: Progress updates during execution
3. **Result**: Final outcome when complete

```
┌──────────┐    Goal      ┌──────────┐
│  Client  │ ───────────▶ │  Server  │
│          │              │          │
│          │ ◀─────────── │          │ (Accepted/Rejected)
│          │              │          │
│          │ ◀─────────── │          │ (Feedback...)
│          │              │          │
│          │ ◀─────────── │          │ (Feedback...)
│          │              │          │
│          │ ◀─────────── │          │ (Result)
└──────────┘              └──────────┘
```

### Action Definition

Actions use `.action` files:

```
# Fibonacci.action
int32 order          # Goal
---
int32[] sequence     # Result
---
int32[] partial_sequence  # Feedback
```

### Action Server Example

```python
import rclpy
from rclpy.action import ActionServer
from rclpy.node import Node
from example_interfaces.action import Fibonacci

class FibonacciServer(Node):
    def __init__(self):
        super().__init__('fibonacci_server')
        self._action_server = ActionServer(
            self,
            Fibonacci,
            'fibonacci',
            self.execute_callback)
        self.get_logger().info('Fibonacci action server ready')

    def execute_callback(self, goal_handle):
        self.get_logger().info('Executing goal...')

        feedback_msg = Fibonacci.Feedback()
        feedback_msg.partial_sequence = [0, 1]

        for i in range(1, goal_handle.request.order):
            # Check if canceled
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                return Fibonacci.Result()

            # Calculate next Fibonacci number
            feedback_msg.partial_sequence.append(
                feedback_msg.partial_sequence[-1] +
                feedback_msg.partial_sequence[-2])

            # Send feedback
            goal_handle.publish_feedback(feedback_msg)
            self.get_logger().info(
                f'Feedback: {feedback_msg.partial_sequence}')

            # Simulate work
            import time
            time.sleep(0.5)

        goal_handle.succeed()
        result = Fibonacci.Result()
        result.sequence = feedback_msg.partial_sequence
        return result

def main(args=None):
    rclpy.init(args=args)
    node = FibonacciServer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
```

### Action Client Example

```python
import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from example_interfaces.action import Fibonacci

class FibonacciClient(Node):
    def __init__(self):
        super().__init__('fibonacci_client')
        self._action_client = ActionClient(
            self, Fibonacci, 'fibonacci')

    def send_goal(self, order):
        goal_msg = Fibonacci.Goal()
        goal_msg.order = order

        self._action_client.wait_for_server()
        self._send_goal_future = self._action_client.send_goal_async(
            goal_msg, feedback_callback=self.feedback_callback)
        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected')
            return

        self.get_logger().info('Goal accepted')
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def feedback_callback(self, feedback_msg):
        feedback = feedback_msg.feedback
        self.get_logger().info(
            f'Received feedback: {feedback.partial_sequence}')

    def get_result_callback(self, future):
        result = future.result().result
        self.get_logger().info(f'Result: {result.sequence}')
        rclpy.shutdown()

def main(args=None):
    rclpy.init(args=args)
    client = FibonacciClient()
    client.send_goal(10)
    rclpy.spin(client)
```

### Action Command-Line Tools

```bash
# List actions
ros2 action list

# Get action info
ros2 action info /fibonacci

# Send goal from command line
ros2 action send_goal /fibonacci example_interfaces/action/Fibonacci "{order: 5}"

# Send goal with feedback
ros2 action send_goal /fibonacci example_interfaces/action/Fibonacci "{order: 5}" --feedback
```

## Comparing Communication Patterns

| Feature | Topic | Service | Action |
|---------|-------|---------|--------|
| Pattern | Publish/Subscribe | Request/Response | Goal/Feedback/Result |
| Duration | Continuous | Instant | Long-running |
| Feedback | N/A | N/A | Yes |
| Cancelable | N/A | No | Yes |
| Use Case | Sensor data | Quick queries | Complex tasks |

### Decision Flowchart

```
Need to communicate?
        │
        ▼
Is it continuous data?
   │              │
  YES            NO
   │              │
   ▼              ▼
 TOPIC     Is it a quick operation?
              │              │
             YES            NO
              │              │
              ▼              ▼
           SERVICE       ACTION
```

## Real-World Example: Robot Control

A typical robot uses all three patterns:

```
Topics:
- /cmd_vel (velocity commands) ← continuous
- /odom (odometry) ← continuous
- /scan (LIDAR) ← continuous

Services:
- /set_mode (change robot mode) ← instant
- /get_state (query current state) ← instant

Actions:
- /navigate_to_pose (go to location) ← long-running
- /follow_path (execute trajectory) ← long-running
```

---

## Exercise: Light Switch Service

Create a service that simulates a light switch:

### Requirements

1. Service server node: `light_controller`
   - Service name: `/set_light`
   - Service type: `std_srvs/srv/SetBool`
   - When `data=True`, log "Light ON"
   - When `data=False`, log "Light OFF"
   - Return success=True and appropriate message

2. Test with command line:
```bash
ros2 service call /set_light std_srvs/srv/SetBool "{data: true}"
ros2 service call /set_light std_srvs/srv/SetBool "{data: false}"
```

### Solution

```python
import rclpy
from rclpy.node import Node
from std_srvs.srv import SetBool

class LightController(Node):
    def __init__(self):
        super().__init__('light_controller')
        self.light_on = False
        self.srv = self.create_service(
            SetBool, 'set_light', self.set_light_callback)
        self.get_logger().info('Light controller ready')

    def set_light_callback(self, request, response):
        self.light_on = request.data

        if self.light_on:
            self.get_logger().info('Light ON')
            response.message = 'Light turned ON'
        else:
            self.get_logger().info('Light OFF')
            response.message = 'Light turned OFF'

        response.success = True
        return response

def main(args=None):
    rclpy.init(args=args)
    node = LightController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
```

---

## Summary

ROS 2 provides three communication patterns:

- **Topics**: Publish-subscribe for continuous data streams
- **Services**: Request-response for quick, synchronous operations
- **Actions**: Goal-feedback-result for long-running, cancelable tasks

Choose the right pattern based on:
- Duration of the operation
- Need for feedback
- Need for cancellation
- Synchronous vs asynchronous communication

In the next chapter, you will learn how to describe robot geometry using URDF.

**Next:** [Robot Description with URDF](./5-urdf.md)
