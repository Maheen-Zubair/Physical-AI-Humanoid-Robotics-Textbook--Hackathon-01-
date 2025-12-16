# Research: Physical AI & Humanoid Robotics Book

**Feature**: `001-physical-ai-robotics-book`
**Date**: 2025-12-15
**Status**: Complete

---

## 1. Docusaurus Project Structure

**Decision**: Use standard Docusaurus docs structure with category-based sidebar auto-generation

**Rationale**: Docusaurus auto-generates sidebar from folder structure, reducing maintenance overhead. Category metadata files (`_category_.json`) provide ordering control.

**Alternatives Considered**:
- Manual sidebar configuration: More control but higher maintenance burden
- Single flat docs folder: Simpler but loses module organization

**Reference Structure** (from Context7):
```
website/
├── docs/
│   ├── intro.md                    → /docs/intro
│   ├── module-1-ros2/
│   │   ├── _category_.json
│   │   ├── 1-introduction.md       → /docs/module-1-ros2/1-introduction
│   │   └── 2-nodes.md              → /docs/module-1-ros2/2-nodes
│   ├── module-2-simulation/
│   │   └── ...
│   └── appendices/
│       └── ...
├── src/pages/
├── docusaurus.config.js
├── sidebars.js
└── static/img/
```

**Key Findings**:
- Markdown front matter controls sidebar position: `sidebar_position: 2`
- Relative links work: `[link](./other-doc.md)`
- Static assets go in `/static/img/`

---

## 2. ROS 2 Code Examples (rclpy)

**Decision**: Use official ROS 2 documentation patterns for all Python examples

**Rationale**: Official examples are tested, maintained, and students can cross-reference with ROS 2 docs.

**Minimal Publisher Pattern** (from Context7):
```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class MinimalPublisher(Node):
    def __init__(self):
        super().__init__('minimal_publisher')
        self.publisher_ = self.create_publisher(String, 'topic', 10)
        timer_period = 0.5
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0

    def timer_callback(self):
        msg = String()
        msg.data = 'Hello World: %d' % self.i
        self.publisher_.publish(msg)
        self.get_logger().info('Publishing: "%s"' % msg.data)
        self.i += 1

def main(args=None):
    rclpy.init(args=args)
    minimal_publisher = MinimalPublisher()
    rclpy.spin(minimal_publisher)
    minimal_publisher.destroy_node()
    rclpy.shutdown()
```

**Minimal Subscriber Pattern**:
```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class MinimalSubscriber(Node):
    def __init__(self):
        super().__init__('minimal_subscriber')
        self.subscription = self.create_subscription(
            String, 'topic', self.listener_callback, 10)

    def listener_callback(self, msg):
        self.get_logger().info('I heard: "%s"' % msg.data)

def main(args=None):
    rclpy.init(args=args)
    minimal_subscriber = MinimalSubscriber()
    rclpy.spin(minimal_subscriber)
    minimal_subscriber.destroy_node()
    rclpy.shutdown()
```

---

## 3. Software Version Decisions

**Decision**: Target stable LTS versions for all software

| Software | Version | Rationale |
|----------|---------|-----------|
| Ubuntu | 22.04 LTS | Current LTS, ROS 2 Humble support |
| ROS 2 | Humble Hawksbill | LTS until 2027, best documented |
| Python | 3.10+ | Ships with Ubuntu 22.04 |
| Gazebo | Fortress (LTS) | Stable, ROS 2 integration proven |
| Unity | 2022 LTS | Stable for ROS-TCP-Connector |
| NVIDIA Isaac Sim | 2023.1.1+ | Latest with ROS 2 Humble support |
| OpenAI Whisper | Latest (pip) | Rapidly evolving, use latest |

**Alternatives Considered**:
- ROS 2 Iron: Newer but shorter support window
- Gazebo Garden: Newer features but less documentation

---

## 4. Chapter Writing Approach

**Decision**: Research-concurrent approach (research while writing, not all upfront)

**Rationale**:
- 80,000 words is substantial; upfront research would delay writing
- Technologies evolve; just-in-time research ensures currency
- Allows iterative refinement based on student feedback

**Writing Workflow**:
1. Read chapter spec from spec.md
2. Research specific topic using Context7 MCP + official docs
3. Write theory section (60%)
4. Write practical examples (40%)
5. Add exercise at end of chapter
6. Verify code examples execute correctly
7. Add to Docusaurus and test build

---

## 5. Citation Style

**Decision**: Use simplified in-text citations with References section per module

**Rationale**: Full APA for every claim would clutter educational content. Use:
- In-text links for quick references: `[ROS 2 docs](https://docs.ros.org/)`
- References section at module end for formal citations

**Example**:
```markdown
## References

- Open Robotics. (2024). *ROS 2 Documentation*. https://docs.ros.org/en/humble/
- NVIDIA. (2024). *Isaac Sim Documentation*. https://docs.omniverse.nvidia.com/isaacsim/
```

---

## 6. Cloud Simulation Alternatives

**Decision**: Provide cloud alternatives for all GPU-intensive modules

**Rationale**: Many students lack RTX GPUs; cloud options ensure accessibility

| Local Requirement | Cloud Alternative |
|-------------------|-------------------|
| NVIDIA GPU for Isaac | AWS/GCP GPU instances |
| High RAM for Gazebo | The Construct (ROSject) |
| RL Training | Google Colab with GPU |

**Implementation**: Each module includes "Cloud Alternative" callout box.

---

## 7. Exercise Format

**Decision**: 1 coding exercise per chapter + module quiz at end

**Exercise Template**:
```markdown
## Exercise: [Title]

**Objective**: [What student will accomplish]

**Prerequisites**: [What they should have completed]

**Steps**:
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Expected Output**: [What success looks like]

**Stretch Goal** (optional): [Advanced challenge]
```

**Quiz Format**: 5-10 multiple choice questions testing key concepts from module.

---

## 8. Resolved Technical Unknowns

| Unknown | Resolution |
|---------|------------|
| Docusaurus version | v3.x (latest stable) |
| Sidebar generation | Auto-generated from folder structure |
| Code highlighting | Prism.js (built into Docusaurus) |
| Image format | PNG/SVG for diagrams, WebP for photos |
| Deployment | GitHub Pages via `docusaurus deploy` |
| Search | Algolia DocSearch (free for open source) |

---

## Summary

All technical unknowns resolved. Ready to proceed with:
1. Data model definition
2. Project structure creation
3. Chapter writing tasks
