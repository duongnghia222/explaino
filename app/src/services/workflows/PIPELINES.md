# Explaino — Course Generation Workflow Pipelines

## Demo

https://github.com/user-attachments/assets/f094666a-1c3c-4a88-900c-be074989feb3

## Overview

Explaino uses **LangGraph** to orchestrate three distinct course generation modes. Each mode is a compiled `StateGraph` that takes a **topic** and an optional **progress callback**, and produces a structured course with lessons, quizzes, and content blocks.

All three modes share a common `BaseCourseState` (defined in `state.py`) containing `topic`, `on_progress`, `raw_data`, and `course_result`.

---

## 1. Normal Mode (`normal_graph.py`)

**Audience:** General adult learners (university-level)
**LLM Temperature:** 0.7
**Lessons:** 4–6, each with markdown content, 0–2 images, 3–5 key points, 2–3 quiz questions (4 options)

### Pipeline

```
START ──▶ plan_course ──▶ fan_out_lessons ──┬──▶ process_lesson (lesson 0)
                                            ├──▶ process_lesson (lesson 1)
                                            ├──▶ process_lesson (lesson 2)
                                            └──▶ ...
                                                      │
                                                      ▼
                                              assemble_course ──▶ END
```

### Nodes

| Node | Description |
|---|---|
| **plan_course** | Sends the topic to the LLM with a structured JSON schema (`NormalCoursePlanResponse`). Returns the full course plan in `raw_data`. |
| **fan_out_lessons** | Conditional edge that uses `Send()` to fan out each lesson to a parallel `process_lesson` instance. |
| **process_lesson** | For each lesson: generates images from `image_prompts` via `generate_images()`, builds `ContentBlock` list (text + images). Results are collected into `lesson_content_blocks`. |
| **assemble_course** | Sorts lessons by index, strips internal metadata, and produces the final `course_result`. |

### Key Characteristics

- **Parallel lesson processing** via LangGraph's `Send` mechanism
- Image generation per lesson (optional, only when prompts are provided)
- Single LLM call for the entire course plan

---

## 2. Kids Mode (`kids_graph.py`)

**Audience:** Children ages 5–10
**LLM Temperature:** 0.8
**Lessons:** 4–6, each with 3–5 short text blocks, 2–3 images, 3 key points, 2 quiz questions (3 options)

### Pipeline

```
START ──▶ plan_course ──▶ fan_out_lessons ──┬──▶ process_lesson (lesson 0)
                                            ├──▶ process_lesson (lesson 1)
                                            ├──▶ process_lesson (lesson 2)
                                            └──▶ ...
                                                      │
                                                      ▼
                                              assemble_course ──▶ END
```

### Nodes

| Node | Description |
|---|---|
| **plan_course** | Sends the topic to the LLM with a kid-friendly system prompt (`KidsCoursePlanResponse`). Uses simple words, short sentences, fun analogies, and emoji. |
| **fan_out_lessons** | Same `Send()`-based fan-out as Normal mode. |
| **process_lesson** | Generates images and **interleaves** them with text blocks (text → image → text → image → ...) to create a storybook-style layout. Remaining images are appended at the end. |
| **assemble_course** | Same as Normal mode — sorts and finalizes the course. |

### Key Characteristics

- **Storybook interleaving**: text blocks and images are alternated for a picture-book feel
- Higher temperature (0.8) for more creative output
- Simpler quiz format (3 options instead of 4)
- Image-heavy content (2–3 images per lesson vs 0–2 in Normal)

---

## 3. Advanced Mode (`advanced_graph.py`)

**Audience:** Expert-level learners
**LLM Temperature:** 0.5
**Lessons:** 4–6, with research-backed content, inline `[N]` citations, 3–5 key points, 2–3 challenging quizzes (4 options)

### Pipeline

```
START ──▶ deep_research ──▶ synthesize_course ──▶ assemble_course ──▶ END
```

### Nodes

| Node | Description |
|---|---|
| **deep_research** | Invokes the **Deep Research sub-workflow** (see below). Extracts researcher notes as `research_context` and parses all markdown URLs into a `source_index`. Truncates context at 400K chars if needed. |
| **synthesize_course** | Sends the topic + full research context to the LLM with a citation-aware prompt (`AdvancedCoursePlanResponse`). The LLM generates lessons with inline `[N]` source references. |
| **assemble_course** | Resolves `cited_sources` indices against `source_index` to build proper citation objects (with title, URL, snippet). Produces the final course. |

### Key Characteristics

- **Sequential pipeline** (no fan-out) — deep research must complete before synthesis
- No image generation — focuses on text-heavy, citation-rich content
- Lower temperature (0.5) for more factual, precise output
- Full citation tracking from source URLs to lesson content

---

### Deep Research Sub-Workflow (`deep_research/deep_researcher.py`)

The deep research system is a **multi-agent architecture** with three nested LangGraph subgraphs:

```
                        ┌──────────────────────────────────────────────┐
 START ──▶ write_research_brief ──▶ research_supervisor ──▶ END       │
                                          │                            │
                        ┌─────────────────┘                            │
                        ▼                                              │
                    supervisor ◀──────────────┐                        │
                        │                     │                        │
                        ▼                     │                        │
                  supervisor_tools ───────────┘                        │
                        │                                              │
                        │  (ConductResearch tool calls)                │
                        │                                              │
                        ├──▶ researcher_subgraph (topic A) ──┐         │
                        ├──▶ researcher_subgraph (topic B) ──┤         │
                        └──▶ researcher_subgraph (topic C) ──┘         │
                                                                       │
                        ┌──────────────────────────────────────────────┘
                        │
                        │  Each researcher_subgraph:
                        ▼
                    researcher ◀──────────────┐
                        │                     │
                        ▼                     │
                  researcher_tools ───────────┘
                        │
                        ▼
                  compress_research ──▶ END
```

#### Components

| Component | Role |
|---|---|
| **write_research_brief** | Transforms user messages into a structured `ResearchQuestion` with a focused research brief. |
| **supervisor** (loop) | Lead researcher that plans research strategy. Uses `think_tool` for reflection, `ConductResearch` to delegate tasks, and `ResearchComplete` to signal completion. Loops until max iterations or completion. |
| **supervisor_tools** | Executes supervisor tool calls. Launches researcher subgraphs **in parallel** (up to `max_concurrent_research_units`). Aggregates results back to supervisor. |
| **researcher** (loop) | Individual researcher that uses search tools (Tavily, web search) and `think_tool` to gather information on a specific sub-topic. Loops until max tool calls or `ResearchComplete`. |
| **researcher_tools** | Executes researcher tool calls in parallel. Routes back to researcher or to compression. |
| **compress_research** | Compresses all research findings into a concise summary. Has retry logic for token limit handling. |

---

## Comparison Summary

| Feature | Normal | Kids | Advanced |
|---|---|---|---|
| **Target audience** | General adult | Ages 5–10 | Expert |
| **LLM temperature** | 0.7 | 0.8 | 0.5 |
| **Deep research** | No | No | Yes (multi-agent) |
| **Image generation** | Yes (0–2/lesson) | Yes (2–3/lesson) | No |
| **Citations** | No | No | Yes (`[N]` inline) |
| **Lesson processing** | Parallel (fan-out) | Parallel (fan-out) | Sequential |
| **Content style** | Markdown blocks | Interleaved text+image storybook | Research-backed, citation-rich |
| **Quiz options** | 4 | 3 | 4 |
| **Pydantic schema** | `NormalCoursePlanResponse` | `KidsCoursePlanResponse` | `AdvancedCoursePlanResponse` |
