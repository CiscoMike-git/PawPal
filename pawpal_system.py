from dataclasses import dataclass, field
from typing import List


@dataclass
class Task:
    name: str = ""
    duration: float = 1.0
    priority: str = "low"
    completed: bool = False

    def mark_complete(self) -> None:
        self.completed = True

    def set_name(self, name: str) -> None:
        self.name = name

    def set_duration(self, length: float) -> None:
        self.duration = max(1.0, min(240.0, length))

    def set_priority(self, priority: str) -> None:
        if priority not in ("low", "medium", "high"):
            raise ValueError(f"Priority must be 'low', 'medium', or 'high', got '{priority}'.")
        self.priority = priority


@dataclass
class Pet:
    name: str = ""
    species: str = ""
    tasks: List[Task] = field(default_factory=list)

    def set_name(self, name: str) -> None:
        self.name = name

    def set_species(self, species: str) -> None:
        self.species = species

    def add_task(self, task: Task) -> None:
        if any(t.name == task.name for t in self.tasks):
            raise ValueError(f"Task '{task.name}' already exists for this pet.")
        self.tasks.append(task)

    def remove_task(self, name: str) -> None:
        if not any(t.name == name for t in self.tasks):
            raise ValueError(f"Task '{name}' not found for this pet.")
        self.tasks = [t for t in self.tasks if t.name != name]


@dataclass
class Owner:
    name: str = ""
    time_available: float = 0.0
    pets: List[Pet] = field(default_factory=list)

    def set_name(self, name: str) -> None:
        self.name = name

    def set_time_available(self, length: float) -> None:
        if length < 0.0:
            raise ValueError(f"Time available must be >= 0.0, got {length}.")
        self.time_available = length

    def add_pet(self, pet: Pet) -> None:
        if any(p.name == pet.name for p in self.pets):
            raise ValueError(f"Pet '{pet.name}' already exists for this owner.")
        self.pets.append(pet)

    def remove_pet(self, name: str) -> None:
        if not any(p.name == name for p in self.pets):
            raise ValueError(f"Pet '{name}' not found for this owner.")
        self.pets = [p for p in self.pets if p.name != name]


class Scheduler:
    def __init__(self, owner: "Owner | None" = None):
        self.owner = owner

    def set_owner(self, owner: Owner) -> None:
        self.owner = owner

    def create_schedule(self) -> dict:
        if self.owner is None:
            raise ValueError("Cannot create schedule: no owner assigned.")

        PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}
        owner = self.owner

        if not owner.pets:
            return {
                "entries": [], "skipped": [],
                "total_time_scheduled": 0.0, "time_available": owner.time_available,
                "explanation": f"{owner.name} has no pets registered. Add a pet and its tasks first.",
            }

        all_pairs = [(pet, task) for pet in owner.pets for task in pet.tasks if not task.completed]
        completed_pairs = [(pet, task) for pet in owner.pets for task in pet.tasks if task.completed]

        if not all_pairs and not completed_pairs:
            pet_names = ", ".join(p.name for p in owner.pets)
            return {
                "entries": [], "skipped": [], "completed": [],
                "total_time_scheduled": 0.0, "time_available": owner.time_available,
                "explanation": f"{owner.name} has pets ({pet_names}) but none have tasks. Add tasks first.",
            }

        if not all_pairs:
            return {
                "entries": [], "skipped": [],
                "completed": [
                    {"pet": pet.name, "task": task.name, "duration": task.duration, "priority": task.priority}
                    for pet, task in completed_pairs
                ],
                "total_time_scheduled": 0.0, "time_available": owner.time_available,
                "explanation": f"All tasks for {owner.name}'s pets are already completed.",
            }

        all_pairs.sort(key=lambda pair: (PRIORITY_RANK[pair[1].priority], pair[1].duration))

        entries, skipped = [], []
        time_used, position, budget_exhausted = 0.0, 1, False

        for pet, task in all_pairs:
            if time_used + task.duration <= owner.time_available:
                entries.append({
                    "order": position, "pet": pet.name, "task": task.name,
                    "duration": task.duration, "priority": task.priority,
                })
                time_used += task.duration
                position += 1
            else:
                budget_exhausted = True
                skipped.append({
                    "pet": pet.name, "task": task.name,
                    "duration": task.duration, "priority": task.priority,
                    "reason": "time budget exhausted",
                })

        lines = [f"{owner.name} has {owner.time_available:.0f} minutes available today."]
        if not entries:
            lines.append("No tasks could be scheduled.")
            if owner.time_available == 0:
                lines.append("The time budget is 0 minutes — increase 'time available' to schedule tasks.")
            elif budget_exhausted:
                s = skipped[0]
                lines.append(
                    f"Even the shortest task ('{s['task']}' for {s['pet']}, {s['duration']:.0f} min) "
                    "exceeds the available time."
                )
        else:
            word = "task" if len(entries) == 1 else "tasks"
            lines.append(
                f"{len(entries)} {word} scheduled, using {time_used:.0f} of {owner.time_available:.0f} minutes."
            )
            lines.append(
                "Tasks were ordered by priority (high first, then medium, then low). "
                "Within the same priority, shorter tasks were placed first to maximise the number of tasks completed."
            )
        if skipped:
            word = "task was" if len(skipped) == 1 else "tasks were"
            names = ", ".join(
                "'{task}' ({pet}, {duration:.0f} min, {priority} priority)".format(**s)
                for s in skipped
            )
            lines.append(f"{len(skipped)} {word} excluded because the time budget was reached: {names}.")

        return {
            "entries": entries, "skipped": skipped,
            "completed": [
                {"pet": pet.name, "task": task.name, "duration": task.duration, "priority": task.priority}
                for pet, task in completed_pairs
            ],
            "total_time_scheduled": time_used, "time_available": owner.time_available,
            "explanation": " ".join(lines),
        }
