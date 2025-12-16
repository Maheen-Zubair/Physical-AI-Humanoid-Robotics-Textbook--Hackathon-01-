# Data Model: Physical AI & Humanoid Robotics Book

**Feature**: `001-physical-ai-robotics-book`
**Date**: 2025-12-15

---

## Entity Overview

This book is a content project, not a software application. The "data model" describes the content structure and relationships.

```
Book
├── Prefatory Section (3 chapters)
├── Module 1: ROS 2 (6 chapters)
├── Module 2: Simulation (6 chapters)
├── Module 3: Isaac AI (6 chapters)
├── Module 4: VLA (6 chapters)
├── Closing Section (5 chapters)
└── Assets (images, code samples)
```

---

## Entity Definitions

### Book

The top-level container for all content.

| Attribute | Type | Description |
|-----------|------|-------------|
| title | string | "Physical AI & Humanoid Robotics" |
| version | semver | Book version (e.g., "1.0.0") |
| target_words | integer | ~80,000 |
| target_audience | string | "Beginner to intermediate" |
| deploy_target | string | "GitHub Pages" |

---

### Module

A major thematic section containing multiple chapters.

| Attribute | Type | Description |
|-----------|------|-------------|
| id | string | "module-1-ros2", "module-2-simulation", etc. |
| title | string | "The Robotic Nervous System (ROS 2)" |
| order | integer | 1-4 (display order) |
| chapters | Chapter[] | List of chapters in this module |
| word_count | integer | Estimated total words |
| prerequisites | string[] | Required prior knowledge |
| learning_outcomes | string[] | What students will learn |
| checkpoint_quiz | Quiz | End-of-module assessment |

**Modules**:
1. `module-1-ros2` - The Robotic Nervous System (15,000 words)
2. `module-2-simulation` - The Digital Twin (16,000 words)
3. `module-3-isaac` - The AI-Robot Brain (18,000 words)
4. `module-4-vla` - Vision-Language-Action (17,500 words)

---

### Chapter

A single document teaching one focused concept.

| Attribute | Type | Description |
|-----------|------|-------------|
| id | string | "1-1-introduction-ros2" |
| title | string | "Introduction to ROS 2" |
| module_id | string | Parent module reference |
| order | integer | Position within module |
| word_count | integer | Estimated words (2,000-4,000) |
| key_topics | string[] | Main concepts covered |
| exercise | Exercise | Hands-on activity |
| code_examples | CodeExample[] | Executable snippets |

**Front Matter Schema** (Docusaurus):
```yaml
---
sidebar_position: 1
sidebar_label: "Introduction to ROS 2"
title: "Chapter 1.1: Introduction to ROS 2"
description: "Learn what ROS 2 is and why it matters for robotics"
keywords: [ros2, robotics, middleware]
---
```

---

### Exercise

A hands-on activity at the end of each chapter.

| Attribute | Type | Description |
|-----------|------|-------------|
| id | string | "ex-1-1-hello-ros" |
| title | string | "Create Your First ROS 2 Node" |
| objective | string | What student will accomplish |
| prerequisites | string[] | Required completions |
| steps | string[] | Ordered instructions |
| expected_output | string | Success criteria |
| stretch_goal | string? | Optional advanced challenge |
| estimated_time | integer | Minutes to complete |

---

### CodeExample

An executable code snippet within a chapter.

| Attribute | Type | Description |
|-----------|------|-------------|
| id | string | "code-1-2-publisher" |
| language | string | "python", "bash", "xml", etc. |
| filename | string | "minimal_publisher.py" |
| code | string | The actual code |
| explanation | string | Line-by-line commentary |
| tested_on | string | "Ubuntu 22.04, ROS 2 Humble" |
| runnable | boolean | Can be executed as-is |

---

### Quiz

End-of-module checkpoint assessment.

| Attribute | Type | Description |
|-----------|------|-------------|
| id | string | "quiz-module-1" |
| module_id | string | Parent module reference |
| questions | Question[] | 5-10 questions |
| passing_score | integer | 85% (per SC-006) |

---

### Question

A single quiz question.

| Attribute | Type | Description |
|-----------|------|-------------|
| id | string | "q-1-1" |
| text | string | Question text |
| type | enum | "multiple_choice", "true_false" |
| options | string[] | Answer choices |
| correct_answer | string | Correct option |
| explanation | string | Why this is correct |

---

## File Structure (Docusaurus)

```
docs/
├── intro.md                           # Book introduction
├── prerequisites.md                   # Learning prerequisites
├── setup.md                           # Development environment setup
│
├── module-1-ros2/
│   ├── _category_.json               # Module metadata
│   ├── 1-introduction.md             # Chapter 1.1
│   ├── 2-nodes.md                    # Chapter 1.2
│   ├── 3-topics.md                   # Chapter 1.3
│   ├── 4-services.md                 # Chapter 1.4
│   ├── 5-urdf.md                     # Chapter 1.5
│   ├── 6-rviz.md                     # Chapter 1.6
│   └── quiz.md                       # Module 1 checkpoint quiz
│
├── module-2-simulation/
│   ├── _category_.json
│   ├── 1-intro-simulation.md
│   ├── 2-gazebo-basics.md
│   ├── 3-robot-simulation.md
│   ├── 4-sensors.md
│   ├── 5-unity.md
│   ├── 6-environments.md
│   └── quiz.md
│
├── module-3-isaac/
│   ├── _category_.json
│   ├── 1-intro-isaac.md
│   ├── 2-isaac-sim.md
│   ├── 3-vslam.md
│   ├── 4-navigation.md
│   ├── 5-rl-intro.md
│   ├── 6-rl-control.md
│   └── quiz.md
│
├── module-4-vla/
│   ├── _category_.json
│   ├── 1-intro-vla.md
│   ├── 2-whisper.md
│   ├── 3-nlu.md
│   ├── 4-planning.md
│   ├── 5-integration.md
│   ├── 6-capstone.md
│   └── quiz.md
│
├── conclusion.md                      # Summary and next steps
│
└── appendices/
    ├── _category_.json
    ├── hardware.md                    # Hardware reference guide
    ├── installation.md                # Software installation
    ├── troubleshooting.md            # Common issues
    └── glossary.md                   # Technical terms
```

---

## Category Metadata Schema

Each module folder contains `_category_.json`:

```json
{
  "label": "Module 1: The Robotic Nervous System (ROS 2)",
  "position": 1,
  "collapsible": true,
  "collapsed": false,
  "link": {
    "type": "generated-index",
    "description": "Learn the foundations of ROS 2 - the middleware that powers modern robots."
  }
}
```

---

## Relationships

```
Book (1) ──────────── (N) Module
Module (1) ─────────── (N) Chapter
Module (1) ─────────── (1) Quiz
Chapter (1) ────────── (N) CodeExample
Chapter (1) ────────── (1) Exercise
Quiz (1) ───────────── (N) Question
```

---

## Validation Rules

1. **Every chapter must have**:
   - Exactly 1 exercise
   - At least 1 code example
   - Word count between 1,500-4,000

2. **Every module must have**:
   - 5-10 quiz questions
   - Prerequisites listed
   - Learning outcomes defined

3. **Every code example must be**:
   - Syntactically correct
   - Tested on specified platform
   - Self-contained (runnable as-is)

4. **Navigation**:
   - All internal links must resolve
   - No orphan pages (unreachable from sidebar)
   - Consistent heading hierarchy (H1 → H2 → H3)
