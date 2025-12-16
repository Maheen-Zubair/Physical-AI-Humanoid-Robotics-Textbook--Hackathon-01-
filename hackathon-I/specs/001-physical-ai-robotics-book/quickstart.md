# Quickstart: Physical AI & Humanoid Robotics Book

**Feature**: `001-physical-ai-robotics-book`
**Date**: 2025-12-15

This guide helps writers quickly get started with contributing to the book.

---

## Prerequisites

- Node.js 18+ installed
- Git installed
- Basic Markdown knowledge
- (Optional) ROS 2 Humble for testing code examples

---

## 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/[org]/physical-ai-robotics-book.git
cd physical-ai-robotics-book

# Install dependencies
npm install

# Start development server
npm run start
```

The book will be available at `http://localhost:3000`

---

## 2. Project Structure

```
physical-ai-robotics-book/
├── docs/                    # All book content (Markdown)
│   ├── intro.md
│   ├── module-1-ros2/
│   ├── module-2-simulation/
│   ├── module-3-isaac/
│   ├── module-4-vla/
│   └── appendices/
├── static/                  # Images, diagrams, assets
│   └── img/
├── src/                     # Custom React components (if needed)
├── docusaurus.config.js     # Site configuration
├── sidebars.js              # Sidebar configuration
└── specs/                   # Specifications (this folder)
```

---

## 3. Writing a Chapter

### Step 1: Create the file

```bash
# Example: Create Chapter 1.2
touch docs/module-1-ros2/2-nodes.md
```

### Step 2: Add front matter

```markdown
---
sidebar_position: 2
sidebar_label: "Nodes and the Computation Graph"
title: "Chapter 1.2: Nodes and the Computation Graph"
description: "Learn how ROS 2 nodes work and how they communicate"
keywords: [ros2, nodes, rclpy, computation graph]
---

# Nodes and the Computation Graph

Your content here...
```

### Step 3: Follow the chapter template

Each chapter should include:

1. **Introduction** (~200 words)
   - What this chapter covers
   - Why it matters
   - Prerequisites

2. **Theory Section** (~60% of content)
   - Concept explanation
   - Diagrams where helpful
   - Define terms on first use

3. **Practical Section** (~40% of content)
   - Code examples
   - Step-by-step instructions
   - Expected outputs

4. **Exercise** (end of chapter)
   - Clear objective
   - Numbered steps
   - Expected outcome

5. **Summary** (~100 words)
   - Key takeaways
   - Link to next chapter

---

## 4. Code Example Format

Use fenced code blocks with language specification:

````markdown
```python title="minimal_publisher.py"
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class MinimalPublisher(Node):
    def __init__(self):
        super().__init__('minimal_publisher')
        # ... rest of code
```
````

**Requirements**:
- Include `title` for filename
- Add comments explaining key lines
- Test before committing
- Must be runnable as-is

---

## 5. Adding Images

1. Place images in `static/img/module-X/`
2. Reference using absolute paths:

```markdown
![ROS 2 Node Graph](/img/module-1/node-graph.png)
```

**Image Guidelines**:
- PNG for diagrams, WebP for photos
- Max width: 800px
- Include alt text for accessibility

---

## 6. Exercise Template

```markdown
## Exercise: [Title]

**Objective**: [What student will accomplish]

**Prerequisites**: Complete Chapter X.X

**Estimated Time**: 20 minutes

### Steps

1. [First step with clear instruction]
   ```bash
   # Command to run
   ```

2. [Second step]

3. [Third step]

### Expected Output

```
[What the student should see]
```

### Stretch Goal (Optional)

[Advanced challenge for motivated students]
```

---

## 7. Quiz Format

Create `quiz.md` at the end of each module:

```markdown
---
sidebar_position: 99
sidebar_label: "Module Quiz"
---

# Module 1 Checkpoint Quiz

Test your understanding of ROS 2 fundamentals.

## Question 1

What is the primary function of a ROS 2 node?

- [ ] A) Store data permanently
- [x] B) Execute a single, modular piece of functionality
- [ ] C) Connect to the internet
- [ ] D) Render graphics

<details>
<summary>Explanation</summary>

A ROS 2 node is designed to be a modular unit of computation...
</details>
```

---

## 8. Building for Production

```bash
# Build static site
npm run build

# Test production build locally
npm run serve

# Deploy to GitHub Pages
npm run deploy
```

---

## 9. Quality Checklist

Before submitting a chapter:

- [ ] Front matter complete (position, label, title, description)
- [ ] All code examples tested and working
- [ ] Images have alt text
- [ ] Technical terms defined on first use
- [ ] Exercise included at end
- [ ] No broken internal links
- [ ] Spell check passed
- [ ] Word count within target range

---

## 10. Getting Help

- **Spec questions**: Check `specs/001-physical-ai-robotics-book/spec.md`
- **Style questions**: Check `.specify/memory/constitution.md`
- **Technical issues**: Create GitHub issue

---

## Commands Reference

| Command | Description |
|---------|-------------|
| `npm run start` | Start dev server |
| `npm run build` | Build for production |
| `npm run serve` | Preview production build |
| `npm run deploy` | Deploy to GitHub Pages |
| `npm run clear` | Clear build cache |
