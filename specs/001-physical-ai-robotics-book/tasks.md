# Tasks: Physical AI & Humanoid Robotics Book

**Input**: Design documents from `/specs/001-physical-ai-robotics-book/`
**Prerequisites**: plan.md (required), spec.md (required), data-model.md, research.md, quickstart.md

**Tests**: Not applicable - this is a content creation project, not software development.

**Organization**: Tasks are grouped by user story (each module maps to one user story) to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1=Module 1, US2=Module 2, US3=Module 3, US4=Module 4)
- Include exact file paths in descriptions

## Path Conventions

- **Content files**: `docs/` at repository root (Docusaurus structure)
- **Static assets**: `static/img/` for images and diagrams
- **Config files**: Repository root for `docusaurus.config.js`, `sidebars.js`, `package.json`

---

## Phase 1: Setup (Project Scaffolding)

**Purpose**: Initialize Docusaurus project and create folder structure

- [X] T001 Initialize Docusaurus project with `npx create-docusaurus@latest physical-ai-robotics-book classic`
- [X] T002 Configure docusaurus.config.js with book metadata (title, tagline, GitHub Pages deployment)
- [X] T002a [P] Create docs/VERSION-PINNING.md documenting all target software versions (ROS 2 Humble, Gazebo Fortress, Unity 2022 LTS, Isaac Sim 2023.1.1+, Whisper latest)
- [X] T003 [P] Create docs/module-1-ros2/ directory
- [X] T004 [P] Create docs/module-2-simulation/ directory
- [X] T005 [P] Create docs/module-3-isaac/ directory
- [X] T006 [P] Create docs/module-4-vla/ directory
- [X] T007 [P] Create docs/appendices/ directory
- [X] T008 [P] Create static/img/module-1/ directory
- [X] T009 [P] Create static/img/module-2/ directory
- [X] T010 [P] Create static/img/module-3/ directory
- [X] T011 [P] Create static/img/module-4/ directory
- [X] T012 [P] Create docs/module-1-ros2/_category_.json with module metadata
- [X] T013 [P] Create docs/module-2-simulation/_category_.json with module metadata
- [X] T014 [P] Create docs/module-3-isaac/_category_.json with module metadata
- [X] T015 [P] Create docs/module-4-vla/_category_.json with module metadata
- [X] T016 [P] Create docs/appendices/_category_.json with appendices metadata
- [X] T017 Configure sidebars.js for auto-generated sidebar from folder structure
- [X] T018 Verify Docusaurus builds successfully with `npm run build`

**Checkpoint**: Project scaffolding complete - content writing can begin

---

## Phase 2: Foundational (Prefatory Content)

**Purpose**: Core content that MUST be complete before module writing begins

**Why Foundational**: Prefatory chapters establish context, prerequisites, and setup instructions that all modules reference.

**Research-Concurrent Workflow**: Use Context7 MCP to fetch current documentation before writing each chapter. Query pattern: `resolve-library-id` → `get-library-docs` with relevant topic.

- [X] T019 Write docs/intro.md - Introduction to Physical AI (~1,500 words)
- [X] T020 Write docs/prerequisites.md - Learning Outcomes & Prerequisites (~1,000 words)
- [X] T021 Write docs/setup.md - Development Environment Setup (~2,000 words)
- [X] T021a [P] Create docs/references-template.md - APA citation template for module references sections
- [X] T022 Verify prefatory content builds and navigation works

**Checkpoint**: Foundation ready - user story implementation can begin

---

## Phase 3: User Story 1 - Learn ROS 2 Fundamentals (Priority: P1) MVP

**Goal**: Students learn core ROS 2 concepts (nodes, topics, services) with hands-on Python examples

**Independent Test**: Student completes all Module 1 exercises on standard laptop with ROS 2 installed, successfully runs a multi-node communication demo

**Word Count Target**: 15,000 words (6 chapters + quiz)

### Implementation for User Story 1

- [ ] T023 [P] [US1] Write docs/module-1-ros2/1-introduction.md - Introduction to ROS 2 (~2,000 words)
- [ ] T024 [P] [US1] Write docs/module-1-ros2/2-nodes.md - Nodes and the Computation Graph (~2,500 words)
- [ ] T025 [P] [US1] Write docs/module-1-ros2/3-topics.md - Topics and Publishers/Subscribers (~3,000 words)
- [ ] T026 [P] [US1] Write docs/module-1-ros2/4-services.md - Services and Actions (~2,500 words)
- [ ] T027 [P] [US1] Write docs/module-1-ros2/5-urdf.md - Robot Description with URDF (~3,000 words)
- [ ] T028 [P] [US1] Write docs/module-1-ros2/6-rviz.md - Visualization with RViz (~2,000 words)
- [ ] T029 [US1] Write docs/module-1-ros2/quiz.md - Module 1 Checkpoint Quiz (5-10 questions)
- [ ] T029a [US1] Write docs/module-1-ros2/references.md - Module 1 References (APA format citations for ROS 2 docs)
- [ ] T030 [US1] Verify all Module 1 code examples execute correctly on ROS 2 Humble
- [ ] T031 [US1] Verify Module 1 word count within target range (13,500-16,500 words)
- [ ] T032 [US1] Verify Module 1 builds without errors

**Checkpoint**: User Story 1 complete - student can learn ROS 2 fundamentals independently

---

## Phase 4: User Story 2 - Simulate Robots in Virtual Environments (Priority: P2)

**Goal**: Students test robots in Gazebo and Unity virtual environments with physics simulation

**Independent Test**: Student launches simulated robot in Gazebo, commands it to move, observes sensor data flow back to ROS 2

**Word Count Target**: 16,000 words (6 chapters + quiz)

**Dependency**: Requires understanding of ROS 2 from User Story 1 (but can be written in parallel)

### Implementation for User Story 2

- [ ] T033 [P] [US2] Write docs/module-2-simulation/1-intro-simulation.md - Introduction to Robot Simulation (~1,500 words)
- [ ] T034 [P] [US2] Write docs/module-2-simulation/2-gazebo-basics.md - Gazebo Basics (~3,000 words)
- [ ] T035 [P] [US2] Write docs/module-2-simulation/3-robot-simulation.md - Robot Simulation in Gazebo (~3,500 words)
- [ ] T036 [P] [US2] Write docs/module-2-simulation/4-sensors.md - Sensors in Simulation (~3,000 words)
- [ ] T037 [P] [US2] Write docs/module-2-simulation/5-unity.md - Unity for Robot Visualization (~2,500 words)
- [ ] T038 [P] [US2] Write docs/module-2-simulation/6-environments.md - Building Custom Environments (~2,500 words)
- [ ] T039 [US2] Write docs/module-2-simulation/quiz.md - Module 2 Checkpoint Quiz (5-10 questions)
- [ ] T039a [US2] Write docs/module-2-simulation/references.md - Module 2 References (APA format citations for Gazebo/Unity docs)
- [ ] T040 [US2] Verify all Module 2 code examples execute correctly on Gazebo Fortress
- [ ] T041 [US2] Verify Module 2 word count within target range (14,400-17,600 words)
- [ ] T042 [US2] Verify Module 2 builds without errors

**Checkpoint**: User Story 2 complete - student can simulate robots independently

---

## Phase 5: User Story 3 - Implement AI-Powered Navigation (Priority: P3)

**Goal**: Students implement SLAM, path planning, and reinforcement learning using NVIDIA Isaac

**Independent Test**: Student runs VSLAM demo in Isaac Sim, observes robot build a map while navigating

**Word Count Target**: 18,000 words (6 chapters + quiz)

**Dependency**: Requires simulation understanding from User Story 2 (but can be written in parallel)

### Implementation for User Story 3

- [ ] T043 [P] [US3] Write docs/module-3-isaac/1-intro-isaac.md - Introduction to NVIDIA Isaac (~2,000 words)
- [ ] T044 [P] [US3] Write docs/module-3-isaac/2-isaac-sim.md - Isaac Sim Setup and Basics (~3,000 words)
- [ ] T045 [P] [US3] Write docs/module-3-isaac/3-vslam.md - Visual SLAM (VSLAM) (~3,500 words)
- [ ] T046 [P] [US3] Write docs/module-3-isaac/4-navigation.md - Path Planning and Navigation (~3,500 words)
- [ ] T047 [P] [US3] Write docs/module-3-isaac/5-rl-intro.md - Introduction to Reinforcement Learning (~3,000 words)
- [ ] T048 [P] [US3] Write docs/module-3-isaac/6-rl-control.md - RL for Robot Control (~3,000 words)
- [ ] T049 [US3] Write docs/module-3-isaac/quiz.md - Module 3 Checkpoint Quiz (5-10 questions)
- [ ] T049a [US3] Write docs/module-3-isaac/references.md - Module 3 References (APA format citations for NVIDIA Isaac docs)
- [ ] T050 [US3] Verify all Module 3 code examples execute correctly on Isaac Sim 2023.1.1+
- [ ] T051 [US3] Verify Module 3 word count within target range (16,200-19,800 words)
- [ ] T052 [US3] Verify Module 3 builds without errors

**Checkpoint**: User Story 3 complete - student can implement AI navigation independently

---

## Phase 6: User Story 4 - Build Vision-Language-Action Systems (Priority: P4)

**Goal**: Students integrate speech recognition with cognitive planning for voice-commanded robots

**Independent Test**: Student demonstrates voice-commanded action where robot hears "pick up the red block" and executes in simulation

**Word Count Target**: 17,500 words (6 chapters + quiz)

**Dependency**: Requires all previous modules (capstone integrates everything)

### Implementation for User Story 4

- [ ] T053 [P] [US4] Write docs/module-4-vla/1-intro-vla.md - Introduction to VLA Systems (~2,000 words)
- [ ] T054 [P] [US4] Write docs/module-4-vla/2-whisper.md - Speech Recognition with Whisper (~3,000 words)
- [ ] T055 [P] [US4] Write docs/module-4-vla/3-nlu.md - Natural Language Understanding (~2,500 words)
- [ ] T056 [P] [US4] Write docs/module-4-vla/4-planning.md - Cognitive Action Planning (~3,000 words)
- [ ] T057 [P] [US4] Write docs/module-4-vla/5-integration.md - VLA Pipeline Integration (~3,000 words)
- [ ] T058 [US4] Write docs/module-4-vla/6-capstone.md - Capstone: Autonomous Humanoid (~4,000 words)
- [ ] T059 [US4] Write docs/module-4-vla/quiz.md - Module 4 Checkpoint Quiz (5-10 questions)
- [ ] T059a [US4] Write docs/module-4-vla/references.md - Module 4 References (APA format citations for Whisper/VLA docs)
- [ ] T060 [US4] Verify all Module 4 code examples execute correctly
- [ ] T061 [US4] Verify Module 4 word count within target range (15,750-19,250 words)
- [ ] T062 [US4] Verify Module 4 builds without errors

**Checkpoint**: User Story 4 complete - student can build VLA systems independently

---

## Phase 7: Closing Content

**Purpose**: Summary, appendices, and reference materials

- [X] T063 Write docs/conclusion.md - Conclusion and Next Steps (~1,500 words)
- [ ] T064 [P] Write docs/appendices/hardware.md - Hardware Reference Guide (~2,000 words)
- [ ] T065 [P] Write docs/appendices/installation.md - Software Installation Appendix (~2,500 words)
- [X] T066 [P] Write docs/appendices/troubleshooting.md - Troubleshooting Guide (~2,000 words)
- [X] T067 [P] Write docs/appendices/glossary.md - Glossary (~1,000 words)
- [ ] T068 Verify closing content builds without errors

**Checkpoint**: All content complete

---

## Phase 8: Quality Assurance & Polish

**Purpose**: Final validation and deployment preparation

### Content Validation

- [ ] T069 Verify all internal links resolve correctly
- [ ] T070 Verify total word count within target (~80,000 words, +/- 10%)
- [ ] T071 Run spell check on all markdown files
- [ ] T072 Verify all frontmatter is complete (position, label, title, description, keywords)
- [ ] T073 Verify each chapter has exactly 1 exercise
- [ ] T074 Verify each module quiz has 5-10 questions

### Cross-Module Consistency Checks

- [ ] T074a Verify terminology consistency across all modules (e.g., "node" vs "Node", "ROS 2" vs "ROS2") and technical terms defined on first use
- [ ] T074b Verify code style consistency (variable naming, comment style, import ordering)
- [ ] T074c Verify all software version references match VERSION-PINNING.md
- [ ] T074d Verify all references sections follow APA format from references-template.md
- [ ] T074e Verify all technical claims are verifiable against official documentation (FR-007)
- [ ] T074f Verify second-person instructional tone consistency across all chapters (FR-010)

### Deployment

- [ ] T075 Test full Docusaurus build with `npm run build`
- [ ] T076 Deploy to GitHub Pages and verify live site
- [ ] T077 Run quickstart.md validation (contributor can follow guide)

**Checkpoint**: Book ready for publication

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (different writers)
  - Or sequentially in priority order (P1 → P2 → P3 → P4)
- **Closing (Phase 7)**: Can start after User Story 1, references all modules
- **Polish (Phase 8)**: Depends on all content being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational - References US1 concepts but independently writable
- **User Story 3 (P3)**: Can start after Foundational - References US2 concepts but independently writable
- **User Story 4 (P4)**: Can start after Foundational - Capstone requires all previous, but chapters 1-5 independently writable

### Within Each User Story

- All chapter tasks marked [P] can run in parallel (different files)
- Quiz task depends on all chapters being written
- Verification tasks depend on all content being complete

### Parallel Opportunities

- All Setup tasks T003-T016 marked [P] can run in parallel
- All chapter writing tasks within each module marked [P] can run in parallel
- All appendix tasks T064-T067 marked [P] can run in parallel
- Different user stories can be worked on in parallel by different writers

---

## Parallel Example: User Story 1

```bash
# Launch all chapter writing tasks in parallel:
Task: "Write docs/module-1-ros2/1-introduction.md - Introduction to ROS 2"
Task: "Write docs/module-1-ros2/2-nodes.md - Nodes and the Computation Graph"
Task: "Write docs/module-1-ros2/3-topics.md - Topics and Publishers/Subscribers"
Task: "Write docs/module-1-ros2/4-services.md - Services and Actions"
Task: "Write docs/module-1-ros2/5-urdf.md - Robot Description with URDF"
Task: "Write docs/module-1-ros2/6-rviz.md - Visualization with RViz"

# Then after all chapters complete:
Task: "Write docs/module-1-ros2/quiz.md - Module 1 Checkpoint Quiz"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (Prefatory Content)
3. Complete Phase 3: User Story 1 (Module 1 - ROS 2)
4. **STOP and VALIDATE**: Student can learn ROS 2 fundamentals
5. Deploy to GitHub Pages - MVP is live!

### Incremental Delivery

1. Setup + Foundational → Project ready
2. Add User Story 1 → Deploy (MVP: ROS 2 Fundamentals)
3. Add User Story 2 → Deploy (Simulation added)
4. Add User Story 3 → Deploy (AI Navigation added)
5. Add User Story 4 → Deploy (VLA + Capstone complete)
6. Add Closing + Polish → Full book published

### Parallel Team Strategy

With multiple writers:

1. Writer A: User Story 1 (Module 1 - ROS 2)
2. Writer B: User Story 2 (Module 2 - Simulation)
3. Writer C: User Story 3 (Module 3 - Isaac AI)
4. Writer D: User Story 4 (Module 4 - VLA)
5. All complete → Merge and run QA phase

---

## Summary

| Phase | Tasks | Parallel Tasks | User Story |
|-------|-------|----------------|------------|
| Phase 1: Setup | T001-T018 + T002a | 15 | - |
| Phase 2: Foundational | T019-T022 + T021a | 1 | - |
| Phase 3: US1 - ROS 2 | T023-T032 + T029a | 6 | US1 (P1) |
| Phase 4: US2 - Simulation | T033-T042 + T039a | 6 | US2 (P2) |
| Phase 5: US3 - Isaac AI | T043-T052 + T049a | 6 | US3 (P3) |
| Phase 6: US4 - VLA | T053-T062 + T059a | 6 | US4 (P4) |
| Phase 7: Closing | T063-T068 | 4 | - |
| Phase 8: QA | T069-T077 + T074a-f | 0 | - |
| **TOTAL** | **89 tasks** | **44 parallel** | **4 stories** |

---

## Notes

- [P] tasks = different files, no dependencies - can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story (module) should be independently completable and testable
- Word count targets include 10% tolerance
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All code examples must be tested on specified platform versions

---

## Task Coverage Summary

### Requirements Alignment

| Requirement | Coverage | Tasks |
|-------------|----------|-------|
| Module 1: ROS 2 | ✅ Complete | T023-T032, T029a |
| Module 2: Gazebo & Unity | ✅ Complete | T033-T042, T039a |
| Module 3: NVIDIA Isaac | ✅ Complete | T043-T052, T049a |
| Module 4: Vision-Language-Action | ✅ Complete | T053-T062, T059a |
| Docusaurus Setup | ✅ Complete | T001-T018 |
| GitHub Pages Deployment | ✅ Complete | T076 |

### Gap Analysis (Added Tasks)

| Gap Identified | Resolution | Task(s) Added |
|----------------|------------|---------------|
| Version pinning documentation | Created VERSION-PINNING.md | T002a |
| APA citation template | Created references-template.md | T021a |
| Module references sections | Added references.md per module | T029a, T039a, T049a, T059a |
| Terminology consistency | Cross-module consistency check + term definitions | T074a |
| Code style consistency | Cross-module style check | T074b |
| Version reference validation | Check against VERSION-PINNING.md | T074c |
| APA format validation | Check against references-template.md | T074d |
| Technical claims verification | Verify against official docs (FR-007) | T074e |
| Tone consistency | Second-person instructional tone (FR-010) | T074f |

### Research-Concurrent Workflow

Each chapter writing task should follow this workflow:

1. **Before writing**: Use Context7 MCP to fetch current documentation
   - `resolve-library-id` for the relevant library (ros2, gazebo, isaac-sim, etc.)
   - `get-library-docs` with topic matching chapter content
2. **During writing**: Reference official docs for accuracy
3. **After writing**: Add APA citations to module references.md

### Coverage Metrics

| Metric | Count | Notes |
|--------|-------|-------|
| Total Tasks | 87 | +10 from original 77 |
| Parallelizable Tasks | 44 | 50.6% of all tasks |
| Chapter Writing Tasks | 24 | 6 chapters × 4 modules |
| Quiz Tasks | 4 | 1 per module |
| References Tasks | 4 | 1 per module (new) |
| QA Tasks | 13 | Including 4 new consistency checks |

### Spec-to-Task Traceability

| Spec Requirement | Mapped Tasks |
|------------------|--------------|
| FR-001: Prefatory chapters | T019-T022 |
| FR-002: 4 core modules | Phase 3-6 |
| FR-003: Theory + exercises + quiz | All chapter tasks + quiz tasks |
| FR-004: Closing chapters | T063-T068 |
| FR-005: Docusaurus Markdown | All writing tasks |
| FR-006: Tested code examples | T030, T040, T050, T060 |
| FR-011-FR-014: Module 1 ROS 2 | T023-T032 |
| FR-015-FR-018: Module 2 Simulation | T033-T042 |
| FR-019-FR-022: Module 3 Isaac | T043-T052 |
| FR-023-FR-026: Module 4 VLA | T053-T062 |

### Quality Gates

Each module must pass these checks before completion:

1. ✅ All chapters written with frontmatter
2. ✅ Quiz created (5-10 questions)
3. ✅ References section with APA citations
4. ✅ Code examples tested on target versions
5. ✅ Word count within 10% of target
6. ✅ Docusaurus build succeeds
