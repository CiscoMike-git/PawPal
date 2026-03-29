from dataclasses import dataclass, field
from typing import List


@dataclass
class Task:
    name: str = ""
    duration: float = 0.0
    priority: str = ""

    def set_name(self, name: str) -> None:
        self.name = name

    def set_duration(self, length: float) -> None:
        self.duration = length

    def set_priority(self, priority: str) -> None:
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
        self.tasks.append(task)

    def remove_task(self, name: str) -> None:
        self.tasks = [t for t in self.tasks if t.name != name]


@dataclass
class Owner:
    name: str = ""
    time_available: float = 0.0
    pets: List[Pet] = field(default_factory=list)

    def set_name(self, name: str) -> None:
        self.name = name

    def set_time_available(self, length: float) -> None:
        self.time_available = length

    def add_pet(self, pet: Pet) -> None:
        self.pets.append(pet)

    def remove_pet(self, name: str) -> None:
        self.pets = [p for p in self.pets if p.name != name]


class Scheduler:
    def __init__(self, owner: "Owner | None" = None):
        self.owner = owner

    def set_owner(self, owner: Owner) -> None:
        self.owner = owner

    def create_schedule(self) -> None:
        pass
