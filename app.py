import streamlit as st
from pawpal_system import Task, Pet, Owner, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Owner")

owner_name = st.text_input("Owner name", value="")
time_available = st.number_input("Your available time today (minutes)", min_value=0, max_value=1440, value=60)

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name=owner_name, time_available=float(time_available))


st.subheader("Pets")

if st.session_state.owner.pets:
    for pet in st.session_state.owner.pets:
        st.write(f"- {pet.name} ({pet.species})")
else:
    st.info("No pets added yet.")

pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

col_add, col_rem = st.columns(2)
with col_add:
    if st.button("Add pet"):
        try:
            st.session_state.owner.add_pet(Pet(name=pet_name, species=species))
            st.rerun()
        except ValueError as e:
            st.error(str(e))
with col_rem:
    if st.button("Remove pet"):
        try:
            st.session_state.owner.remove_pet(pet_name)
            st.rerun()
        except ValueError as e:
            st.error(str(e))


st.subheader("Tasks")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

pet_names = [p.name for p in st.session_state.owner.pets]

if pet_names:
    selected_pet_name = st.selectbox("Select pet", pet_names)

    pet_tasks = [t for t in st.session_state.tasks if t.get("pet") == selected_pet_name]
    if pet_tasks:
        st.write("Current tasks:")
        st.table(pet_tasks)
    else:
        st.info("No tasks yet for this pet. Add one below.")

    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    if st.button("Add task"):
        selected_pet = next(p for p in st.session_state.owner.pets if p.name == selected_pet_name)
        
        try:
            selected_pet.add_task(Task(name=task_title, duration=float(duration), priority=priority))
            st.session_state.tasks.append(
                {"pet": selected_pet_name, "title": task_title, "duration_minutes": int(duration), "priority": priority}
            )
            st.rerun()
        except ValueError as e:
            st.error(str(e))
else:
    st.info("Add a pet first to manage tasks.")

st.divider()

st.subheader("Build Schedule")
st.caption("This button should call your scheduling logic once you implement it.")

if st.button("Generate schedule"):
    if not st.session_state.tasks:
        st.warning("Add at least one task before generating a schedule.")
    else:
        st.warning(
        "Not implemented yet. Next step: create your scheduling logic (classes/functions) and call it here."
        )
    
    st.markdown(
            """
    Suggested approach:
    1. Design your UML (draft).
    2. Create class stubs (no logic).
    3. Implement scheduling behavior.
    4. Connect your scheduler here and display results.
    """
    )