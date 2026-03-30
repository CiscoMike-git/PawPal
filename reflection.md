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
    My design changed significantly from what I first envisioned during the UML design process to when it was implemented. Initially, I designed this system to be a basic scheduler of the day's tasks, only taking in a few parameters and then outputting a reasonable schedule. This schedule, however, was formatted as a list of sequential activities to perform, not a comprehensive schedule with specified times to do the activity. As I got through phase 3 and 4 of the project, I discovered that I probably misunderstood the objective of this project's application due to how my implementation and the project's instructions heavily differed from, and actually countered, each other. This required me to heavily depend on AI to attempt to 180 from my initial architecture and conform with CodePath's requirements.

- If yes, describe at least one change and why you made it.
    An example of the aforementioned changes was including a completion status to the Task class. My design figured that an owner only needed to know their list of activities for the day, not actively maintain it. Due to this, I did not include any completion validation within my initial framework. After coming across Phase 2 - Step 3 in the project instructions, I refactored my code to include such to conform with CodePath's expectations.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
    After heavy revision, my scheduler considers an array of constraints including available time, task duration, task priority, last task completion date vs required frequency, any task dependencies, and time-of-day preferences. The priority constraint for my algorithm is time; without the requisite amount, a task cannot, and will not, be scheduled. Following this are the weights of a task, such as task priority and last task completion date vs required frequency. These factors will decide which task should be prioritized for placement. Finally, task dependencies outline a required sequence for a set of tasks preventing tasks logically subsequent to another from being placed ahead of that task. In essence, time budget decides feasibility, priority & urgency decides value, and dependency order decides sequencing.

- How did you decide which constraints mattered most?
    I determined that the ultimate make or break of a task would be if it could be put into the schedule, because no matter how imperative a task was, if the time wasn't there, it was a hapless endeavor. Therefore, I deduced that time should take priority followed by the value of a task which would be determined based on urgency and given priority. This is not to say that a shorter task will automatically win over a higher value, my algorithm will attempt to balance between the two, creating an optimal schedule with both being considered. By programming the algorithm in this way, the resultant schedule is neither greedy nor slim.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
    My scheduler trades off readability for complexity, having extensive features and complex scheduling capabilities that make the codebase long and unwieldy. Such complexity includes features like time blocks and sequencing, both commonly utilized aspects of scheduling. However, the copious functionality has also increased my codebase by several hundred lines of code and has made many lines difficult to read to facilitate modularity.
- Why is that tradeoff reasonable for this scenario?
    This tradeoff is reasonable because it provides the target audience with an application especially suited to their needs at the expense of the programmer's ease. This prospect is a naturally expected aspect of software programming, when complexity increases, it is likely that the codebase will also increase to back that complexity up. Therefore, being as the additional functionality is viable, reasonably expected, and likely commonly utilized, it is a fair tradeoff for the scenario.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
    - Design Brainstorming
    - Spellcheck/Grammatical Adherence
    - Debugging
    - Unit Test Creation
    - Refactoring Code
    - Explaining/Simplifying Concepts
    - Sanity Checks
    - Optimization
- What kinds of prompts or questions were most helpful?
    I found that the most helpful prompts were ones where I knew exactly what I wanted and was therefore able to articulate it to the AI. During the instances where I didn't exactly know, and the prompt was therefore poorly worded, the AI commonly would need additional prompting to rectify a few select undesirable additions. Additionally, detailed, concise prompts tended to do better than long or basic prompts with extremely long or multi-stepped prompts tending to cause the AI to stall.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
    During my initial system design, the AI decided that the quantifications of duration and time available should be strings rather than numerics. As these attributes were measuring a value (time), I felt these should be floats instead. Therefore, I corrected the AI and it swiftly rectified its error without subsequent relapse. Eventually, the time available attribute was changed to a list of string tuples, causing us both to be wrong with our initial plan in the end.
- How did you evaluate or verify what the AI suggested?
    Before I allowed the AI to make any edits to my codebase, I would review its suggestions and provide additional prompting when needed. I would not allow these edits to go through until I was completely satisfied with its answers, being knowledgeable about its underlying objective and what it was about to attempt to do. Additionally, I would review any edits made after the fact to ensure congruence between the suggestions and actual edits. 

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
    I attempted to test as many behaviors as possible, including basic class operations, algorithmic logic, and helper functions. The basic class operations included things like setters and list modifiers and attempted to ensure that the dataclasses would properly handle and store parsed data. The algorithmic logic testers tested how the task justification and sorting performed and whether or not they would unexpectedly fail. Finally, the helper function testing confirmed that individual helper functions, primarily in the Scheduler class, operated in an expected manner without erroneous data being moved between steps.
- Why were these tests important?
    These tests ensured that the underlying pawpal system logic, of which everything else is based off of, functioned properly. Without these tests there would be no easy way to appropriately identify, and rectify, logical errors without combing through the codebase. Additionally, these tests ensure that the user won't be able to break the logic once the application allows them to input data.

**b. Confidence**

- How confident are you that your scheduler works correctly?
    While I am confident in the scheduler's operations, based both on testing and observations, there were several points in the project where I had to rely especially heavily on and deeply trust the AI to progress through the project. These instances have given me a slight hesitation in trusting it completely, at least until I have the time to go step by step through the codebase and deeply review it after all changes are finalized. That being said, I have yet to run into any logical or looming errors which would validate my apprehension. Therefore, I would rate my overall confidence as a 4/5 and my confidence based on current testing and observations at 5/5.
- What edge cases would you test next if you had more time?
    As of this time I have not thought of another edge case that I would like to test. I attempted to make my testing suite quite thorough and in doing so have exhausted my and the AI's thoughts on this matter.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
    I'm most satisfied with the dynamic complexity that my application has, even if it was a stumble to get there. From where I started, and my initial scope, I feel that this application has evolved into a legitimate pet care scheduler and could feasibly be utilized as such. That fact alone makes completing this project feel quite rewarding.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
    I would like to spend more time becoming intimately familiar with the codebase as in certain locations, I am not as familiar with the code as I should be. Once I become absolutely familiar, I would like to redesign the system from the ground up. This is because I 180'd from my initial design and therefore believe there is likely leftover erroneous/redundant code in the codebase that I would like to remove or refactor.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
    I learned that AI can create complicated systems with very little prompting, but those systems are unlikely to match your needs. When working with AI, you need to already know what you want to be able to appropriately steer the AI toward your objectives. Additionally, one should become familiar with the project in its entirety before beginning to avoid extensively redesigning the system multiple times, potentially confusing yourself.