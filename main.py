from pawpal_system import Owner, Pet, Task, Scheduler

# --- Build pets and tasks ---

buddy = Pet(name="Buddy", species="Dog")
buddy.add_task(Task(name="Morning Walk", duration=30, priority="high"))
buddy.add_task(Task(name="Feed Breakfast", duration=10, priority="high"))
buddy.add_task(Task(name="Brush Fur", duration=15, priority="medium"))

whiskers = Pet(name="Whiskers", species="Cat")
whiskers.add_task(Task(name="Clean Litter Box", duration=10, priority="high"))
whiskers.add_task(Task(name="Playtime", duration=20, priority="medium"))
whiskers.add_task(Task(name="Trim Nails", duration=10, priority="low"))

# --- Build owner ---

owner = Owner(name="Alex", time_available=90)
owner.add_pet(buddy)
owner.add_pet(whiskers)

# --- Generate and print schedule ---

schedule = Scheduler(owner=owner).create_schedule()

print(f"===== Today's Schedule for {owner.name} =====")
print(f"Available time: {int(owner.time_available)} min\n")

entries = schedule["entries"]
task_w = max(len(e["task"]) for e in entries) if entries else 10
pet_w  = max(len(e["pet"])  for e in entries) if entries else 10
dur_w  = max(len(str(int(e["duration"]))) for e in entries) if entries else 3

print("Scheduled Tasks:")
for entry in schedule["entries"]:
    print(
        f"  [{entry['priority'].upper():^6}] {entry['task']:<{task_w}} ({entry['pet']}){'':<{pet_w - len(entry['pet'])}} "
        f"{int(entry['duration']):>{dur_w}} min"
    )
print(f"\n  Total scheduled: {int(schedule['total_time_scheduled'])} / {int(schedule['time_available'])} min")

if schedule["skipped"]:
    print("\nSkipped (not enough time):")
    for s in schedule["skipped"]:
        print(f"  {s['task']} ({s['pet']}) — {int(s['duration'])} min [{s['priority']}]")
