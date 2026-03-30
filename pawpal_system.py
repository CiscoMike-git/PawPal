from dataclasses import dataclass, field
from datetime import datetime
from heapq import heapify, heappop, heappush
from typing import List, Optional, Tuple


PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}
PRIORITY_VALUE = {"high": 100, "medium": 10, "low": 1}
FREQUENCY_DAYS = {"daily": 1, "weekly": 7, "monthly": 30}
VALID_SLOTS = ("morning", "afternoon", "evening")
VALID_FREQUENCIES = ("daily", "weekly", "monthly")


@dataclass
class Task:
    name: str = ""
    duration: int = 1
    priority: str = "low"
    completed: bool = False
    depends_on: Optional[str] = None
    frequency: Optional[str] = None
    last_done: Optional[datetime] = None
    preferred_slot: Optional[str] = None
    time: Optional[str] = None  # "HH:MM" format

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def set_name(self, name: str) -> None:
        """Set the task name, raising ValueError if empty or whitespace."""
        if not name.strip():
            raise ValueError("Task name must not be empty or whitespace.")
        self.name = name

    def set_duration(self, length: int) -> None:
        """Set the task duration in minutes, raising ValueError if not between 1 and 240."""
        if not (1 <= length <= 240):
            raise ValueError(f"Duration must be between 1 and 240 minutes, got {length}.")
        self.duration = length

    def set_priority(self, priority: str) -> None:
        """Set the task priority to 'low', 'medium', or 'high'."""
        if priority not in ("low", "medium", "high"):
            raise ValueError(f"Priority must be 'low', 'medium', or 'high', got '{priority}'.")
        self.priority = priority

    def set_depends_on(self, task_name: Optional[str]) -> None:
        """Set the name of a task this task must come after in the schedule, or None to clear."""
        self.depends_on = task_name

    def set_frequency(self, frequency: Optional[str]) -> None:
        """Set recurrence frequency: 'daily', 'weekly', 'monthly', or None."""
        if frequency is not None and frequency not in VALID_FREQUENCIES:
            raise ValueError(
                f"Frequency must be one of {VALID_FREQUENCIES} or None, got '{frequency}'."
            )
        self.frequency = frequency

    def set_last_done(self, when: Optional[datetime]) -> None:
        """Record when this task was last completed to enable urgency scoring."""
        self.last_done = when

    def set_preferred_slot(self, slot: Optional[str]) -> None:
        """Set a preferred time-of-day slot: 'morning', 'afternoon', 'evening', or None."""
        if slot is not None and slot not in VALID_SLOTS:
            raise ValueError(
                f"Slot must be one of {VALID_SLOTS} or None, got '{slot}'."
            )
        self.preferred_slot = slot

    def urgency_multiplier(self) -> float:
        """Return how overdue a recurring task is as a multiplier (0.0 if on schedule or no frequency)."""
        if self.frequency is None or self.last_done is None:
            return 0.0
        days_since = (datetime.now() - self.last_done).days
        period = FREQUENCY_DAYS[self.frequency]
        return max(0.0, days_since / period - 1.0)

    def scheduling_value(self, current_slot: Optional[str] = None) -> float:
        """Compute a scheduling value based on priority, urgency, and slot match."""
        base = PRIORITY_VALUE[self.priority]
        slot_bonus = 0.5 if (current_slot and self.preferred_slot == current_slot) else 0.0
        return base * (1.0 + self.urgency_multiplier()) + slot_bonus


@dataclass
class Pet:
    name: str = ""
    species: str = ""
    tasks: List[Task] = field(default_factory=list)

    def set_name(self, name: str) -> None:
        """Set the pet's name, raising ValueError if empty or whitespace."""
        if not name.strip():
            raise ValueError("Pet name must not be empty or whitespace.")
        self.name = name

    def set_species(self, species: str) -> None:
        """Set the pet's species."""
        self.species = species

    def add_task(self, task: Task) -> None:
        """Add a task to this pet, raising ValueError if a task with the same name already exists."""
        if any(t.name == task.name for t in self.tasks):
            raise ValueError(f"Task '{task.name}' already exists for this pet.")
        self.tasks.append(task)

    def remove_task(self, name: str) -> None:
        """Remove a task by name, raising ValueError if it does not exist."""
        if not any(t.name == name for t in self.tasks):
            raise ValueError(f"Task '{name}' not found for this pet.")
        self.tasks = [t for t in self.tasks if t.name != name]


@dataclass
class Owner:
    name: str = ""
    time_available: List[Tuple[str, str]] = field(default_factory=list)  # list of (start "HH:MM", end "HH:MM") windows
    pets: List[Pet] = field(default_factory=list)

    @property
    def time_available_minutes(self) -> float:
        """Return the total available time across all windows in minutes."""
        def _to_min(t: str) -> int:
            h, m = map(int, t.split(":"))
            return h * 60 + m
        return float(sum(max(0, _to_min(end) - _to_min(start)) for start, end in self.time_available))

    def set_name(self, name: str) -> None:
        """Set the owner's name, raising ValueError if empty or whitespace."""
        if not name.strip():
            raise ValueError("Owner name must not be empty or whitespace.")
        self.name = name

    @staticmethod
    def _validate_window(start: str, end: str) -> None:
        for label, t in (("start", start), ("end", end)):
            parts = t.split(":")
            if len(parts) != 2 or not all(p.isdigit() for p in parts):
                raise ValueError(f"{label} time must be in HH:MM format, got '{t}'.")
        if start >= end:
            raise ValueError(f"Start time '{start}' must be before end time '{end}'.")

    def add_time_window(self, start: str, end: str) -> None:
        """Append a (start, end) availability window, raising ValueError on invalid input."""
        self._validate_window(start, end)
        self.time_available.append((start, end))

    def remove_time_window(self, start: str, end: str) -> None:
        """Remove an existing (start, end) window, raising ValueError if not found."""
        try:
            self.time_available.remove((start, end))
        except ValueError:
            raise ValueError(f"Time window '{start}'–'{end}' not found.")

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner, raising ValueError if a pet with the same name already exists."""
        if any(p.name == pet.name for p in self.pets):
            raise ValueError(f"Pet '{pet.name}' already exists for this owner.")
        self.pets.append(pet)

    def remove_pet(self, name: str) -> None:
        """Remove a pet by name, raising ValueError if it does not exist."""
        if not any(p.name == name for p in self.pets):
            raise ValueError(f"Pet '{name}' not found for this owner.")
        self.pets = [p for p in self.pets if p.name != name]


class Scheduler:
    def __init__(self, owner: "Owner | None" = None):
        """Initialise the scheduler, optionally binding it to an owner."""
        self.owner = owner

    @staticmethod
    def _knapsack_select(pairs: list, capacity: float, current_slot: Optional[str] = None) -> list:
        """Return the subset of (pet, task) pairs that maximises total value within capacity."""
        n = len(pairs)
        if n == 0 or capacity <= 0:
            return []
        cap = int(capacity)
        weights = [max(1, p[1].duration) for p in pairs]
        values = [p[1].scheduling_value(current_slot) for p in pairs]

        # Standard 0/1 knapsack DP — O(n * cap) time and space
        dp = [[0.0] * (cap + 1) for _ in range(n + 1)]
        for i in range(1, n + 1):
            w, v = weights[i - 1], values[i - 1]
            for j in range(cap + 1):
                dp[i][j] = dp[i - 1][j]
                if j >= w and dp[i - 1][j - w] + v > dp[i][j]:
                    dp[i][j] = dp[i - 1][j - w] + v

        selected, j = [], cap
        for i in range(n, 0, -1):
            if dp[i][j] != dp[i - 1][j]:
                selected.append(pairs[i - 1])
                j -= weights[i - 1]
        return selected

    @staticmethod
    def _topo_sort(ordered_pairs: list) -> list:
        """Stable topological sort: reorder pairs to satisfy Task.depends_on constraints."""
        name_to_idx = {task.name: i for i, (_, task) in enumerate(ordered_pairs)}
        n = len(ordered_pairs)
        in_degree = [0] * n
        edges = [[] for _ in range(n)]

        for i, (_, task) in enumerate(ordered_pairs):
            if task.depends_on and task.depends_on in name_to_idx:
                parent = name_to_idx[task.depends_on]
                edges[parent].append(i)
                in_degree[i] += 1

        available = [i for i in range(n) if in_degree[i] == 0]
        heapify(available)
        result = []
        while available:
            i = heappop(available)
            result.append(ordered_pairs[i])
            for j in edges[i]:
                in_degree[j] -= 1
                if in_degree[j] == 0:
                    heappush(available, j)

        # Fall back to original order if a dependency cycle is detected
        return result if len(result) == n else ordered_pairs

    @staticmethod
    def _assign_start_times(selected: list, time_available: List[Tuple[str, str]]) -> None:
        """Pack selected tasks sequentially into the owner's time windows, writing task.time for each.

        Tasks are never split across non-consecutive windows: a task is only placed when
        cursor + duration <= win_end, guaranteeing it fits entirely within a single window.
        If no remaining window can fit a task it is assigned time = None.
        """
        def to_min(t: str) -> int:
            h, m = map(int, t.split(":"))
            return h * 60 + m

        def to_hhmm(minutes: int) -> str:
            return f"{minutes // 60:02d}:{minutes % 60:02d}"

        # Sort windows chronologically so we fill them in order
        windows = sorted((to_min(s), to_min(e)) for s, e in time_available)
        if not windows:
            for _, task in selected:
                task.time = None
            return

        window_idx = 0
        cursor = windows[0][0]

        for _, task in selected:
            duration = max(1, task.duration)
            assigned = None
            # Advance through windows until we find one where the full task fits
            while window_idx < len(windows):
                win_start, win_end = windows[window_idx]
                # Move cursor to at least the start of this window
                cursor = max(cursor, win_start)
                if cursor + duration <= win_end:
                    # Task fits entirely within this window — place it
                    assigned = to_hhmm(cursor)
                    cursor += duration
                    break
                else:
                    # Task does not fit; advance to the next window
                    window_idx += 1
                    if window_idx < len(windows):
                        cursor = windows[window_idx][0]
            task.time = assigned

    @staticmethod
    def _build_explanation(
        owner: "Owner",
        entries: list,
        skipped: list,
        time_used: float,
        completion_ratio: float,
        current_slot: Optional[str],
        selected: list,
    ) -> str:
        """Build a human-readable explanation of the scheduling result."""
        total_min = owner.time_available_minutes
        windows_str = ", ".join(f"{s}–{e}" for s, e in owner.time_available) or "none"
        lines = [f"{owner.name} has {total_min:.0f} minutes available today ({windows_str})."]
        if not entries:
            lines.append("No tasks could be scheduled.")
            if total_min == 0:
                lines.append(
                    "The time budget is 0 minutes — add availability windows to schedule tasks."
                )
            elif skipped:
                s = min(skipped, key=lambda x: x["duration"])
                lines.append(
                    f"Even the shortest task ('{s['task']}' for {s['pet']}, {s['duration']} min) "
                    "exceeds the available time."
                )
        else:
            word = "task" if len(entries) == 1 else "tasks"
            lines.append(
                f"{len(entries)} {word} scheduled ({completion_ratio:.0%} of incomplete tasks), "
                f"using {time_used:.0f} of {total_min:.0f} minutes."
            )
            lines.append(
                "Tasks were selected to maximise priority-weighted value within the time budget. "
                "Within the same priority, tasks are grouped by pet to reduce context-switching."
            )
            if any(t.depends_on for _, t in selected):
                lines.append(
                    "Dependency ordering was applied where tasks specify a 'depends_on' constraint."
                )
            if current_slot:
                lines.append(f"Tasks matching the '{current_slot}' time slot were preferred.")

        if skipped:
            word = "task was" if len(skipped) == 1 else "tasks were"
            names = ", ".join(
                "'{task}' ({pet}, {duration} min, {priority} priority)".format(**s)
                for s in skipped
            )
            lines.append(
                f"{len(skipped)} {word} excluded because the time budget was reached: {names}."
            )
        return " ".join(lines)

    def set_owner(self, owner: Owner) -> None:
        """Assign an owner to this scheduler."""
        self.owner = owner

    def filter_tasks(
        self,
        completed: Optional[bool] = None,
        pet_name: Optional[str] = None,
    ) -> List[Task]:
        """Return tasks filtered by completion status and/or pet name.

        Args:
            completed: If True, return only completed tasks. If False, return only
                       incomplete tasks. If None, completion status is not filtered.
            pet_name:  If provided, return only tasks belonging to the named pet.
                       Raises ValueError if no pet with that name exists.
        """
        if self.owner is None:
            raise ValueError("Cannot filter tasks: no owner assigned.")
        if pet_name is not None and not any(p.name == pet_name for p in self.owner.pets):
            raise ValueError(f"Pet '{pet_name}' not found.")

        tasks = [
            task
            for pet in self.owner.pets
            for task in pet.tasks
            if (pet_name is None or pet.name == pet_name)
            and (completed is None or task.completed == completed)
        ]
        return tasks

    def sort_by_time(self) -> List[Task]:
        """Return all tasks across all pets sorted by their time attribute.

        Tasks with a time value come first in chronological order.
        Tasks with no time set are appended at the end in their original order.
        """
        if self.owner is None:
            raise ValueError("Cannot sort tasks: no owner assigned.")
        all_tasks = [task for pet in self.owner.pets for task in pet.tasks]
        timed = sorted((t for t in all_tasks if t.time is not None), key=lambda t: t.time)
        untimed = [t for t in all_tasks if t.time is None]
        return timed + untimed

    def detect_conflicts(self) -> List[str]:
        """Return warning strings for any tasks whose time windows overlap.

        Only tasks with an explicit ``time`` value ("HH:MM") are considered.
        Tasks without a time are ignored. Never raises; always returns a list
        (empty when there are no conflicts).
        """
        timed: List[tuple] = []
        if self.owner:
            for pet in self.owner.pets:
                for task in pet.tasks:
                    if task.time:
                        timed.append((pet.name, task))

        warnings: List[str] = []
        for i in range(len(timed)):
            for j in range(i + 1, len(timed)):
                pet_a, task_a = timed[i]
                pet_b, task_b = timed[j]
                try:
                    h_a, m_a = map(int, task_a.time.split(":"))
                    h_b, m_b = map(int, task_b.time.split(":"))
                except (ValueError, AttributeError):
                    continue
                start_a = h_a * 60 + m_a
                start_b = h_b * 60 + m_b
                end_a = start_a + task_a.duration
                end_b = start_b + task_b.duration
                if start_a < end_b and start_b < end_a:
                    warnings.append(
                        f"Conflict: '{task_a.name}' ({pet_a}) at {task_a.time} "
                        f"overlaps with '{task_b.name}' ({pet_b}) at {task_b.time}."
                    )
        return warnings

    def complete_task(self, pet_name: str, task_name: str) -> Optional[Task]:
        """Mark a task complete and create the next occurrence for daily/weekly/monthly tasks.

        Returns the newly created Task if frequency is 'daily', 'weekly', or 'monthly', else None.
        Raises ValueError if the pet or task is not found, or the task is already completed.
        """
        if self.owner is None:
            raise ValueError("Cannot complete task: no owner assigned.")

        pet = next((p for p in self.owner.pets if p.name == pet_name), None)
        if pet is None:
            raise ValueError(f"Pet '{pet_name}' not found.")

        task = next((t for t in pet.tasks if t.name == task_name), None)
        if task is None:
            raise ValueError(f"Task '{task_name}' not found for pet '{pet_name}'.")

        if task.completed:
            raise ValueError(f"Task '{task_name}' is already completed.")

        task.mark_complete()

        if task.frequency not in ("daily", "weekly", "monthly"):
            return None

        # Build a unique name for the next occurrence (e.g. "Walk #2", "Walk #3", ...)
        # Strip any existing " #N" suffix to get the canonical base name.
        existing_names = {t.name for t in pet.tasks}
        parts = task_name.rsplit(" #", 1)
        base = parts[0] if len(parts) == 2 and parts[1].isdigit() else task_name
        counter = 2
        candidate = f"{base} #{counter}"
        while candidate in existing_names:
            counter += 1
            candidate = f"{base} #{counter}"

        next_task = Task(
            name=candidate,
            duration=task.duration,
            priority=task.priority,
            completed=False,
            depends_on=task.depends_on,
            frequency=task.frequency,
            last_done=datetime.now(),
            preferred_slot=task.preferred_slot,
            time=task.time,
        )
        pet.add_task(next_task)
        return next_task

    def create_schedule(self, current_slot: Optional[str] = None) -> dict: # schould overwrite the old one (and any time data)
        """Build and return a prioritised schedule of pet tasks within the owner's available time.

        Uses a 0/1 knapsack algorithm to select the highest-value tasks that fit within the
        time budget. Value is derived from priority, urgency (how overdue a recurring task is),
        and whether the task matches the optional current_slot. Selected tasks are then grouped
        by pet (to minimise owner context-switching) and reordered to satisfy any depends_on
        constraints.

        Args:
            current_slot: Optional time-of-day hint ('morning', 'afternoon', 'evening').
                          Tasks whose preferred_slot matches receive a scheduling bonus.
        """
        if self.owner is None:
            raise ValueError("Cannot create schedule: no owner assigned.")
        if current_slot is not None and current_slot not in VALID_SLOTS:
            raise ValueError(f"current_slot must be one of {VALID_SLOTS} or None.")

        owner = self.owner

        if not owner.pets:
            return {
                "entries": [], "skipped": [],
                "total_time_scheduled": 0.0, "time_available": owner.time_available_minutes,
                "completion_ratio": 1.0,
                "explanation": f"{owner.name} has no pets registered. Add a pet and its tasks first.",
            }

        all_pairs = [(pet, task) for pet in owner.pets for task in pet.tasks if not task.completed]
        completed_pairs = [(pet, task) for pet in owner.pets for task in pet.tasks if task.completed]

        if not all_pairs and not completed_pairs:
            pet_names = ", ".join(p.name for p in owner.pets)
            return {
                "entries": [], "skipped": [], "completed": [],
                "total_time_scheduled": 0.0, "time_available": owner.time_available_minutes,
                "completion_ratio": 1.0,
                "explanation": f"{owner.name} has pets ({pet_names}) but none have tasks. Add tasks first.",
            }

        if not all_pairs:
            return {
                "entries": [], "skipped": [],
                "completed": [
                    {
                        "pet": pet.name, "task": task.name,
                        "duration": task.duration, "priority": task.priority,
                        "time": task.time, "preferred_slot": task.preferred_slot,
                        "frequency": task.frequency, "depends_on": task.depends_on,
                    }
                    for pet, task in completed_pairs
                ],
                "total_time_scheduled": 0.0, "time_available": owner.time_available_minutes,
                "completion_ratio": 1.0,
                "explanation": f"All tasks for {owner.name}'s pets are already completed.",
            }

        # Knapsack selects the best-value subset that fits within the time budget
        selected = self._knapsack_select(all_pairs, owner.time_available_minutes, current_slot)
        selected_names = {task.name for _, task in selected}
        skipped = [
            {
                "pet": pet.name, "task": task.name,
                "duration": task.duration, "priority": task.priority,
                "time": task.time, "preferred_slot": task.preferred_slot,
                "frequency": task.frequency, "depends_on": task.depends_on,
                "reason": "time budget exhausted",
            }
            for pet, task in all_pairs if task.name not in selected_names
        ]

        # Sort selected tasks: priority → pet grouping (reduces context-switching) → duration
        selected.sort(key=lambda p: (PRIORITY_RANK[p[1].priority], p[0].name, p[1].duration))

        # Reorder to satisfy depends_on constraints while preserving the priority/pet sort
        selected = self._topo_sort(selected)

        # Assign a concrete start time to each task by packing them into the owner's windows.
        # Any task that could not be placed within a window gets task.time = None.
        self._assign_start_times(selected, owner.time_available)

        # The knapsack used total minutes as capacity, unaware of window-boundary dead space.
        # Demote any task that _assign_start_times could not place to skipped so that entries
        # only contains tasks with a confirmed start time.
        unplaceable = [(pet, task) for pet, task in selected if task.time is None]
        if unplaceable:
            unplaceable_names = {task.name for _, task in unplaceable}
            selected = [(pet, task) for pet, task in selected if task.name not in unplaceable_names]
            skipped.extend(
                {
                    "pet": pet.name, "task": task.name,
                    "duration": task.duration, "priority": task.priority,
                    "time": None, "preferred_slot": task.preferred_slot,
                    "frequency": task.frequency, "depends_on": task.depends_on,
                    "reason": "window gap too small to place after earlier tasks",
                }
                for pet, task in unplaceable
            )

        entries = [
            {
                "order": i, "pet": pet.name, "task": task.name,
                "duration": task.duration, "priority": task.priority,
                "time": task.time, "preferred_slot": task.preferred_slot,
                "frequency": task.frequency, "depends_on": task.depends_on,
            }
            for i, (pet, task) in enumerate(selected, 1)
        ]
        time_used = sum(task.duration for _, task in selected)

        total_incomplete = len(all_pairs)
        completion_ratio = len(entries) / total_incomplete if total_incomplete > 0 else 1.0

        return {
            "entries": entries,
            "skipped": skipped,
            "completed": [
                {
                    "pet": pet.name, "task": task.name,
                    "duration": task.duration, "priority": task.priority,
                    "time": task.time, "preferred_slot": task.preferred_slot,
                    "frequency": task.frequency, "depends_on": task.depends_on,
                }
                for pet, task in completed_pairs
            ],
            "total_time_scheduled": time_used,
            "time_available": owner.time_available_minutes,
            "completion_ratio": completion_ratio,
            "explanation": self._build_explanation(
                owner, entries, skipped, time_used, completion_ratio, current_slot, selected
            ),
            "conflicts": self.detect_conflicts(),
        }
