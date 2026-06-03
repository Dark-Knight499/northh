# North v1

## Vision

North is a personal thinking workspace.

North is designed for people who generate many ideas, explore many domains, work on multiple projects, and learn through reflection and discussion.

North is not a productivity application.

North is not a task manager.

North is not a note-taking application.

North is a workspace for capturing, refining, organizing, and revisiting thoughts.

The primary goal of North is reducing friction between having an idea and preserving that idea.

---

# Problem

Ideas are generated continuously.

Examples:

* startup ideas
* project ideas
* learning insights
* observations
* arguments
* frameworks
* questions

These ideas often become fragmented across:

* memory
* chats
* notes
* temporary files
* conversations

As a result:

* ideas get lost
* ideas are difficult to revisit
* ideas are difficult to refine
* ideas become disconnected

---

# Philosophy

Capture First.

Organize Later.

The cost of losing an idea is higher than the cost of storing an unorganized idea.

North should encourage idea capture before categorization.

---

# Core User

A curious builder.

Someone who:

* learns through discussion
* learns through exploration
* generates many ideas
* works on multiple projects
* studies multiple domains
* values thinking and reflection

---

# Core Concepts

## Ideas

Raw thoughts.

Examples:

* observations
* arguments
* startup concepts
* random questions
* frameworks

Ideas are lightweight and fast to create.

Ideas are timestamped and preserved.

---

## Projects

Structured explorations.

Examples:

* Axiom
* Portfolio
* Reminder Agent
* North

Projects provide a place for ongoing development of an idea.

Projects contain:

* thoughts
* features
* architecture
* experiments
* notes

---

## Domains

Long-term learning spaces.

Examples:

* Data
* Systems
* AI
* Mathematics
* Networking
* Cloud

Domains contain:

* resources
* notes
* references
* learning material
* reflections

Domains represent areas of exploration rather than projects.

---

## Journal

Personal reflection.

Used for:

* daily thoughts
* observations
* lessons
* emotional reflections

The journal is intended to capture the evolution of thinking over time.

---

# User Experience Principles

Minimal Friction.

Minimal Configuration.

Minimal Cognitive Load.

The system should feel faster than manually creating files.

The system should encourage thinking rather than management.

---

# User Workflow

Idea Appears
↓
Capture
↓
Store
↓
Revisit
↓
Refine
↓
Connect

---

Project Idea Appears
↓
Open Project
↓
Capture Thought
↓
Continue Exploration

---

Learning Insight Appears
↓
Store in Domain
↓
Revisit Later

---

# Functional Requirements

The user must be able to:

* capture ideas
* create project entries
* create domain entries
* create journal entries
* browse existing content
* search existing content
* revisit previous thoughts

---

# Optional Future Capabilities

Speech-to-Text

Text-to-Speech

AI Refinement

AI Summarization

Semantic Search

Idea Linking

Knowledge Graphs

Thought Connections

These are enhancements and not part of the core product.

---

# Non Goals

North is not:

* a task manager
* a habit tracker
* a calendar
* a kanban board
* a productivity dashboard
* a project management system
* a social platform

North should avoid becoming a general productivity application.

---

# Success Criteria

A user can capture a thought in seconds.

A user can find a previous thought quickly.

Ideas are preserved rather than lost.

Projects accumulate knowledge over time.

Domains accumulate learning over time.

North becomes a trusted workspace for exploration and thinking.

---

# Guiding Principle

North should feel like a place to think.

Not a place to manage thinking.


# Workspace Philosophy

North is fundamentally a workspace.

The workspace is the product.

The CLI is an interface.

The TUI is an interface.

Future GUIs are interfaces.

The knowledge stored inside the workspace is the primary asset.

All interfaces should be replaceable without affecting the underlying knowledge.

If every tool inside North disappeared tomorrow, the workspace should remain fully usable through folders and markdown files.

---

# Workspace First Design

North is built around a folder-based knowledge structure.

Knowledge is stored as files.

Knowledge is not stored inside an application.

Knowledge is not locked inside a database.

Knowledge remains accessible through standard filesystem tools.

The user should always own and control their knowledge.

---

# Workspace Structure

The North Workspace contains four primary areas.

Ideas

Projects

Domains

Journal

These areas exist independently of any interface.

The CLI simply provides a faster way to interact with them.

---

# Interface Philosophy

North should never require a CLI.

North should never require a TUI.

North should never require AI.

North should never require Speech-to-Text.

These tools exist to improve the experience.

They are not the foundation.

The foundation is:

Folders
+
Markdown Files
+
User Knowledge

---

# Long-Term Goal

The goal of North is not to build software.

The goal of North is to create a durable personal knowledge workspace.

A workspace where:

* ideas accumulate
* projects evolve
* learning compounds
* reflections persist

over years.

The software layer should serve the workspace.

The workspace should never serve the software.

---

# Design Rule

Knowledge must outlive the implementation.

The workspace should remain valuable even if North itself is deleted.
