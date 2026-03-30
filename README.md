# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Smarter Scheduling

PawPal+ uses several algorithms and data-driven heuristics to build the best possible daily plan:

### Knapsack Task Selection
The scheduler treats your available time as a capacity budget and uses a **0/1 knapsack dynamic programming algorithm** to select the highest-value combination of tasks that fits. Each task is assigned a numeric value based on its priority (high = 100, medium = 10, low = 1), multiplied by an urgency factor that grows the more overdue a recurring task is.

### Slot Preferences
Tasks can specify a preferred time of day — `morning`, `afternoon`, or `evening`. Tasks scheduled in their preferred slot receive a small value bonus, nudging the optimizer to honor owner and pet preferences when time permits.

### Dependency Ordering
Tasks can declare dependencies on other tasks (e.g., "give medication after feeding"). The scheduler uses **topological sort** to ensure dependencies always run first, and skips a task entirely if its dependency was not selected.

### Time-Window Packing
Owners define one or more availability windows (e.g., 9:00–11:30, 17:00–19:00). Selected tasks are packed sequentially into those windows, with each task's start time assigned immediately after the previous task ends.

### Conflict Detection
After scheduling, `detect_conflicts()` scans for any tasks whose time ranges overlap and surfaces them so the user can resolve them.

### Recurring Task Tracking
Tasks can recur on a `daily`, `weekly`, or `monthly` frequency. When `complete_task()` is called, the current task is marked done and a new task representing the next occurrence is automatically created and added to the pet's task list.

### Filtering and Sorting
The schedule can be queried after generation. `filter_tasks()` narrows results by completion status or pet name, and `sort_by_time()` returns tasks ordered by their assigned start time — useful for displaying the plan chronologically in the UI.

### Explanations
Every generated schedule includes a human-readable explanation for each included task (why it was prioritized) and each skipped task (whether it was dropped due to time, a missing dependency, or already being complete).

## Testing PawPal+
- Test Command: python -m pytest
- Confidence Level: 5 Stars

### Description

The suite contains **83 tests** across 10 categories:

- **Task properties & validation** — name, duration, priority, frequency, preferred slot, dependencies, last-done timestamp, `mark_complete`, urgency multiplier, and scheduling value
- **Pet management** — name and species setters, adding and removing tasks, duplicate task prevention
- **Owner management** — name validation, adding and removing time windows (including format and ordering checks), available-minutes calculation, and adding and removing pets
- **Scheduler initialization** — `set_owner` assignment
- **Scheduling algorithm** — knapsack optimizer correctness, per-pet task grouping, slot-preference bonuses, overdue-task urgency prioritization, completion ratio, and edge cases (zero time budget, task exceeding window size)
- **Dependency resolution** — topological ordering, dangling dependency handling, and cycle detection with graceful fallback
- **Task recurrence** — `complete_task` for daily, weekly, and monthly frequencies; field inheritance; timestamp accuracy; name-suffix parsing; error paths for unknown pets, unknown tasks, and already-completed tasks
- **Conflict detection** — same-start, overlapping, cross-pet, strict adjacency, three-way overlap, untimed-task exclusion, and no-owner edge cases
- **Filter tasks** — filtering by completion status, by pet name, combined filters, and error paths
- **Sort by time** — chronological ordering, untimed tasks appended last, insertion-order preservation, cross-pet merging, and no-owner error

## Features

- **0/1 Knapsack Scheduling** — selects the highest-value subset of tasks that fits within available time using dynamic programming
- **Weighted Priority Scoring** — assigns each task a numeric value (high=100, medium=10, low=1) multiplied by an urgency factor that grows proportionally as recurring tasks fall overdue
- **Slot-Preference Bonuses** — tasks specifying a preferred time of day (morning/afternoon/evening) receive a small value bonus, nudging the optimizer to honor preferences when time permits
- **Topological Dependency Ordering** — uses Kahn's algorithm with a min-heap to reorder tasks so dependencies always execute first; detects cycles and falls back to the original order
- **Interval Merging & Subtraction** — owner availability windows are maintained as a list of non-overlapping intervals; adding a window merges overlaps, removing one performs interval subtraction (including splits)
- **First-Fit Time-Window Packing** — sequentially assigns concrete start times by packing selected tasks into availability windows in priority order; tasks that don't fit any window are demoted to skipped
- **Conflict Detection** — after scheduling, performs pairwise interval overlap checks across all timed tasks and surfaces any collisions as warnings
- **Recurring Task Generation** — when a recurring task (daily/weekly/monthly) is completed, automatically clones it with a unique incremental name suffix and resets the last-done timestamp
- **Multi-Criteria Filtering & Sorting** — `filter_tasks()` narrows results by completion status and/or pet name; `sort_by_time()` returns chronologically ordered tasks with untimed tasks appended last
- **Human-Readable Explanations** — every generated schedule includes a narrative explanation covering available time, why tasks were selected or skipped, dependency notes, and slot preference matches

## Demo
<a href="Images\Built Schedule.png" target="_blank"><img src='Images\Built Schedule.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>.

## Weighted Prioritization
Agent Mode assisted me in creating the weighted prioritization by suggesting potential weights and weighted algorithms to utilize in achieving this functionality. While I was not aware of the knapsack selection algorithm, I was familiar with topological sort and heaps. Therefore, after having the AI explain the knapsack selection algorithm to me, I felt comfortable with implementing it in adherence to the AI's suggestions. The AI also assisted in refactoring the surrounding code to utilize this new algorithm rather than the old implementation.