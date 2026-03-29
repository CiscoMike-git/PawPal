# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
    One owner can have multiple pets and each pet can have multiple tasks that need to be performed for their care. These tasks can include walks, feeding, administering medications, grooming, or other activities. The scheduler can take these tasks for each pet, along with supplemental information, to create and display a schedule for the owner. The supplemental information could include such constraints as time availability, task priority, or owner preferences. Additionally, the scheduler should be able to explain the reasoning for its generated schedule.

- What classes did you include, and what responsibilities did you assign to each?
    Owner: handles owner information while structuring subsequent pet information (bridges scheduler to pet)
    - Name (attribute) - the name of the individual owner, likely the user
    - Time Available (attribute) - the amount of time the owner has to dedicate to completing care tasks
    - List of Pets (attribute) - a list of all pets owned by this owner
    - Set Name(String) (function) - set the Name attribute to String
    - Set Time Available(Length) (function) - set the Time Available attribute to Length
    - Add Pet(Pet) (function) - Add Pet to the List of Pets attribute
    - Remove Pet(Name) (function) - Remove pet associated with Name from List of Pets attribute
    
    Pet: handles pet information while structuring subsequent task information (bridges scheduler to task)
    - Name (attribute) - the name of the associated pet
    - Species (attribute) - the species (dog, cat, etc.) of the associated pet
    - List of Tasks (attribute) - a list of tasks which need to be performed for this pet's care
    - Set Name(String) (function) - set the Name attribute to String
    - Set Species(String) (function) - set the Species attribute to String
    - Add Task(Task) (function) - Add Task to the List of Tasks attribute
    - Remove Task(Name) (function) - Remove task associated with Name from List of Tasks attribute

    Task: handles task information
    - Name (attribute) - the name of the associated task
    - Duration (attribute) - how long it will likely take to complete this task
    - Priority (attribute) - how imperative it is for this task to be completed
    - Set Name(String) (function) - set the Name attribute to String
    - Set Duration(Length) (function) - set the Duration attribute to Length
    - Set Priority(String) (function) - set the Priority attribute to String

    Scheduler: utilizes provided information to create an optimal pet care schedule
    - Owner (attribute) - the owner that this object is assigned to create a schedule for
    - Set Owner(Owner) (function) - sets the Owner attribute to Owner
    - Create Schedule() (function) - uses the associated owner and its linked pets and tasks to produce a logical schedule for the owner, along with reasoning for that schedule

**b. Design changes**

- Did your design change during implementation?

- If yes, describe at least one change and why you made it.


---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?

- How did you decide which constraints mattered most?


**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.

- Why is that tradeoff reasonable for this scenario?


---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?

- What kinds of prompts or questions were most helpful?


**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.

- How did you evaluate or verify what the AI suggested?


---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?

- Why were these tests important?


**b. Confidence**

- How confident are you that your scheduler works correctly?

- What edge cases would you test next if you had more time?


---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?


**b. What you would improve**

- If you had another iteration, what would you improve or redesign?


**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
    