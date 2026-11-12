# Project AI conversations

## Planning
The following is the conversation as recorded in the supplied design document.

User: hey i'm working on my cisc106 final project design sheet. i want to make a student assignment tracker where you can add homework, mark stuff done, filter by status, and see a progress bar. can u help me brainstorm what state attributes and routes i'll need for drafter?
Assistant: That’s a great idea for a project! To make a Student Assignment Tracker work in Drafter, you’ll want a main State dataclass to keep track of site-wide data, and a second dataclass (like Assignment) for individual task details.
Here’s a solid way to set up your State:
assignments: a list[Assignment] to store all tasks
student_name: str for personalizing the header
status_filter: str (e.g., "All", "Pending", "Completed")
next_id: int to auto-assign unique IDs
For routes, you could set up: index, assignment_list, add_assignment, save_assignment, edit_assignment, update_assignment, toggle_complete, delete_assignment, set_filter, progress, settings, and save_settings.
User: bet, that works. i put together a tech debt assignment earlier using lists of objects—here's the file:
[User attached Tech Debt worksheet]
can u check if my state setup matches how i handled dataclasses in tech debt, and if those 12 routes cover all 5 of my pages (home, list, add, edit, progress/settings)?
Assistant: Looking at your Tech Debt file, your setup using Student objects with embedded Course lists maps directly to a State holding a list of Assignment objects.
Your 12 routes cover all 5 pages completely:
Home: index
Assignments: assignment_list, set_filter, toggle_complete, delete_assignment
Add Assignment: add_assignment, save_assignment
Edit Assignment: edit_assignment, update_assignment
Progress & Settings: progress, settings, save_settings
Your logic for input validation, list filtering, and checking for empty lists before calculating progress percentages also fits the requirements well.
User: cool thanks. i typed up all my answers for the design doc planning questions and the implementation table, but it sounds too weird can u make it sound more professional without breaking the table?
Assistant: Sure thing! Here is your text formatted neatly so you can copy and paste it directly into the original table boxes without messing up the template structure.
(ChatGPT reformatted the user's drafted answers into clean text blocks to fit the template layout, leaving the original assignment questions and table structure intact.)

## Development and deployment
This is a reconstruction from the available messages. Code is included below where it was supplied. The uploaded design and two deployment screenshots were also discussed.

**User:** take this in:

**Assistant:** Got it. I’ll use this as the plan for your CISC106 Drafter assignment tracker. You’ve planned six pages and 12 routes. Each assignment keeps a unique ID so editing, completing, or deleting it still targets the right one when the list is filtered.

**User:** r u sure u read everything

**Assistant:** Yeah, I read the whole pasted file, including the planning answers, site diagram instructions, requirements table, LLM conversation, and final `.docx` submission instructions for Canvas.

I said **six pages** because your table lists Home, Assignments, Add Assignment, Edit Assignment, Progress, and Settings. The pasted conversation says five because it groups Progress and Settings together.

The pasted text includes the `State` fields and route parameters. I didn’t see the mock-up image itself or the separate Canvas requirements it references.

**User:** ok now look at my screen and see what I can add to this code or just write the code for this assignment

**Assistant:** Your GitHub editor has the “Hello World!” starter. I wrote a complete replacement for the assignment tracker in your design sheet.

It includes all six pages and 12 routes. You can add, edit, delete, complete, and reopen assignments, filter them by status, view your progress, and save your name. I tested all 12 route functions locally, including the blank-title check and editing a completed assignment. I haven’t tested the full website in a browser or checked the separate Canvas rubric.

To use it, replace the starter code in your open GitHub editor with the contents of `main.py`, then click **Commit changes**. Your design sheet also asks you to include the full LLM conversation, so keep this exchange for that section.

**User:** bro just write cod in chat

**Assistant:**

```python
from dataclasses import dataclass
from bakery import assert_equal
from drafter import *

hide_debug_information()
set_website_title("Student Assignment Tracker")
set_website_framed(False)

PRIORITIES = ["Low", "Medium", "High"]
FILTERS = ["All", "Pending", "Completed"]


@dataclass
class Assignment:
    assignment_id: int
    title: str
    course: str
    due_date: str
    priority: str
    notes: str
    completed: bool


@dataclass
class State:
    assignments: list[Assignment]
    student_name: str
    status_filter: str
    next_id: int


def find_assignment(state: State, assignment_id: int):
    for assignment in state.assignments:
        if assignment.assignment_id == assignment_id:
            return assignment
    return None


@route
def index(state: State) -> Page:
    greeting = "Welcome!"
    if state.student_name:
        greeting = f"Welcome, {state.student_name}!"

    return Page(state, [
        Header("Student Assignment Tracker"),
        greeting,
        Button("View assignments", assignment_list),
        Button("Add assignment", add_assignment),
        Button("Progress", progress),
        Button("Settings", settings)
    ])


@route
def assignment_list(state: State) -> Page:
    content = [
        Header("Assignments"),
        SelectBox("status_filter", FILTERS, state.status_filter),
        Button("Apply filter", set_filter)
    ]

    shown = 0
    for assignment in state.assignments:
        status = "Completed" if assignment.completed else "Pending"
        if state.status_filter in ["All", status]:
            shown += 1
            target = Argument("assignment_id", assignment.assignment_id)
            action = "Reopen" if assignment.completed else "Complete"
            content.extend([
                Header(assignment.title),
                assignment.course,
                "Due: " + (assignment.due_date or "No deadline"),
                "Priority: " + assignment.priority,
                status,
                Button("Edit", edit_assignment, target),
                Button(action, toggle_complete, target)
            ])

    if not state.assignments:
        content.append("No assignments yet.")
    elif shown == 0:
        content.append("No assignments match this filter.")

    content.extend([
        Button("Add assignment", add_assignment),
        Button("Home", index)
    ])
    return Page(state, content)


@route
def set_filter(state: State, status_filter: str) -> Page:
    if status_filter in FILTERS:
        state.status_filter = status_filter
    return assignment_list(state)


def assignment_form(state: State, draft: Assignment,
                    editing: bool, error: str = "") -> Page:
    heading = "Edit Assignment" if editing else "Add Assignment"
    content = [Header(heading)]

    if error:
        content.append(error)

    content.extend([
        "Title", TextBox("title", draft.title),
        "Course", TextBox("course", draft.course),
        "Due date (YYYY-MM-DD)", TextBox("due_date", draft.due_date),
        "Priority", SelectBox("priority", PRIORITIES, draft.priority),
        "Notes", TextArea("notes", draft.notes)
    ])

    if editing:
        target = Argument("assignment_id", draft.assignment_id)
        content.append(Button("Save changes", update_assignment, target))
        content.append(Button("Delete", delete_assignment, target))
    else:
        content.append(Button("Save", save_assignment))

    content.append(Button("Cancel", assignment_list))
    return Page(state, content)


@route
def add_assignment(state: State) -> Page:
    draft = Assignment(state.next_id, "", "", "", "Medium", "", False)
    return assignment_form(state, draft, False)


@route
def save_assignment(state: State, title: str, course: str,
                    due_date: str, priority: str, notes: str) -> Page:
    draft = Assignment(
        state.next_id, title.strip(), course.strip(), due_date.strip(),
        priority, notes.strip(), False
    )

    if not draft.title or not draft.course:
        return assignment_form(state, draft, False, "Please enter a title and course.")

    state.assignments.append(draft)
    state.next_id += 1
    return assignment_list(state)


@route
def edit_assignment(state: State, assignment_id: int) -> Page:
    assignment = find_assignment(state, assignment_id)
    if assignment is None:
        return assignment_list(state)
    return assignment_form(state, assignment, True)


@route
def update_assignment(state: State, assignment_id: int, title: str,
                      course: str, due_date: str, priority: str, notes: str) -> Page:
    assignment = find_assignment(state, assignment_id)
    if assignment is None:
        return assignment_list(state)

    if not title.strip() or not course.strip():
        draft = Assignment(
            assignment_id, title, course, due_date, priority, notes,
            assignment.completed
        )
        return assignment_form(state, draft, True, "Please enter a title and course.")

    assignment.title = title.strip()
    assignment.course = course.strip()
    assignment.due_date = due_date.strip()
    assignment.priority = priority
    assignment.notes = notes.strip()
    return assignment_list(state)


@route
def toggle_complete(state: State, assignment_id: int) -> Page:
    assignment = find_assignment(state, assignment_id)
    if assignment is not None:
        assignment.completed = not assignment.completed
    return assignment_list(state)


@route
def delete_assignment(state: State, assignment_id: int) -> Page:
    assignment = find_assignment(state, assignment_id)
    if assignment is not None:
        state.assignments.remove(assignment)
    return assignment_list(state)


@route
def progress(state: State) -> Page:
    total = len(state.assignments)
    completed = 0
    for assignment in state.assignments:
        if assignment.completed:
            completed += 1

    percent = 0
    if total > 0:
        percent = round(100 * completed / total)

    bars = round(percent / 10)
    return Page(state, [
        Header("Progress"),
        f"Total: {total}",
        f"Completed: {completed}",
        f"Pending: {total - completed}",
        f"{percent}% complete",
        "■" * bars + "□" * (10 - bars),
        Button("Home", index)
    ])


@route
def settings(state: State) -> Page:
    return Page(state, [
        Header("Settings"),
        "Your name",
        TextBox("student_name", state.student_name),
        Button("Save name", save_settings),
        Button("Home", index)
    ])


@route
def save_settings(state: State, student_name: str) -> Page:
    state.student_name = student_name.strip()
    return index(state)


sample = Assignment(4, "Lab report", "CHEM133", "", "High", "", False)
example_state = State([sample], "", "All", 5)
assert_equal(find_assignment(example_state, 4), sample)
assert_equal(find_assignment(example_state, 1), None)

start_server(State([], "", "All", 1))

```

**User:** bro i think we need docstring in each function make it so it looks like I wrote the doctring

**Assistant:** Yeah, I’d add one to each of the 14 functions, including `find_assignment` and `assignment_form`. Here are short docstrings in the same order as your code. Paste each triple-quoted line right under its `def` line, indented four spaces. The comments show which function each one goes in.

- `find_assignment` — """Find the assignment with the given ID, or return None if it's missing."""
- `index` — """Welcome the student and show the buttons on the home page."""
- `assignment_list` — """Show the assignments that match the current filter."""
- `set_filter` — """Save the selected filter and show the updated list."""
- `assignment_form` — """Build the form for adding or editing an assignment."""
- `add_assignment` — """Open a blank form for a new assignment."""
- `save_assignment` — """Add the assignment if the student entered a title and course."""
- `edit_assignment` — """Open the form with the assignment's current details filled in."""
- `update_assignment` — """Save edits to an assignment if its title and course are filled in."""
- `toggle_complete` — """Mark a pending assignment complete or reopen a completed one."""
- `delete_assignment` — """Remove the assignment with the given ID from the list."""
- `progress` — """Count completed assignments and show the student's overall progress."""
- `settings` — """Show the settings page where the student can change their name."""
- `save_settings` — """Save the student's name and return to the home page."""

**User:** just write it with the code

**Assistant:**

```python
from dataclasses import dataclass
from bakery import assert_equal
from drafter import *

hide_debug_information()
set_website_title("Student Assignment Tracker")
set_website_framed(False)

PRIORITIES = ["Low", "Medium", "High"]
FILTERS = ["All", "Pending", "Completed"]


@dataclass
class Assignment:
    assignment_id: int
    title: str
    course: str
    due_date: str
    priority: str
    notes: str
    completed: bool


@dataclass
class State:
    assignments: list[Assignment]
    student_name: str
    status_filter: str
    next_id: int


def find_assignment(state: State, assignment_id: int):
    """Find the assignment with the given ID, or return None if it's missing."""
    for assignment in state.assignments:
        if assignment.assignment_id == assignment_id:
            return assignment
    return None


@route
def index(state: State) -> Page:
    """Welcome the student and show the buttons on the home page."""
    greeting = "Welcome!"
    if state.student_name:
        greeting = f"Welcome, {state.student_name}!"

    return Page(state, [
        Header("Student Assignment Tracker"),
        greeting,
        Button("View assignments", assignment_list),
        Button("Add assignment", add_assignment),
        Button("Progress", progress),
        Button("Settings", settings)
    ])


@route
def assignment_list(state: State) -> Page:
    """Show the assignments that match the current filter."""
    content = [
        Header("Assignments"),
        SelectBox("status_filter", FILTERS, state.status_filter),
        Button("Apply filter", set_filter)
    ]

    shown = 0
    for assignment in state.assignments:
        status = "Completed" if assignment.completed else "Pending"
        if state.status_filter in ["All", status]:
            shown += 1
            target = Argument("assignment_id", assignment.assignment_id)
            action = "Reopen" if assignment.completed else "Complete"
            content.extend([
                Header(assignment.title),
                assignment.course,
                "Due: " + (assignment.due_date or "No deadline"),
                "Priority: " + assignment.priority,
                status,
                Button("Edit", edit_assignment, target),
                Button(action, toggle_complete, target)
            ])

    if not state.assignments:
        content.append("No assignments yet.")
    elif shown == 0:
        content.append("No assignments match this filter.")

    content.extend([
        Button("Add assignment", add_assignment),
        Button("Home", index)
    ])
    return Page(state, content)


@route
def set_filter(state: State, status_filter: str) -> Page:
    """Save the selected filter and show the updated list."""
    if status_filter in FILTERS:
        state.status_filter = status_filter
    return assignment_list(state)


def assignment_form(state: State, draft: Assignment,
                    editing: bool, error: str = "") -> Page:
    """Build the form for adding or editing an assignment."""
    heading = "Edit Assignment" if editing else "Add Assignment"
    content = [Header(heading)]

    if error:
        content.append(error)

    content.extend([
        "Title", TextBox("title", draft.title),
        "Course", TextBox("course", draft.course),
        "Due date (YYYY-MM-DD)", TextBox("due_date", draft.due_date),
        "Priority", SelectBox("priority", PRIORITIES, draft.priority),
        "Notes", TextArea("notes", draft.notes)
    ])

    if editing:
        target = Argument("assignment_id", draft.assignment_id)
        content.append(Button("Save changes", update_assignment, target))
        content.append(Button("Delete", delete_assignment, target))
    else:
        content.append(Button("Save", save_assignment))

    content.append(Button("Cancel", assignment_list))
    return Page(state, content)


@route
def add_assignment(state: State) -> Page:
    """Open a blank form for a new assignment."""
    draft = Assignment(state.next_id, "", "", "", "Medium", "", False)
    return assignment_form(state, draft, False)


@route
def save_assignment(state: State, title: str, course: str,
                    due_date: str, priority: str, notes: str) -> Page:
    """Add the assignment if the student entered a title and course."""
    draft = Assignment(
        state.next_id, title.strip(), course.strip(), due_date.strip(),
        priority, notes.strip(), False
    )

    if not draft.title or not draft.course:
        return assignment_form(state, draft, False, "Please enter a title and course.")

    state.assignments.append(draft)
    state.next_id += 1
    return assignment_list(state)


@route
def edit_assignment(state: State, assignment_id: int) -> Page:
    """Open the form with the assignment's current details filled in."""
    assignment = find_assignment(state, assignment_id)
    if assignment is None:
        return assignment_list(state)
    return assignment_form(state, assignment, True)


@route
def update_assignment(state: State, assignment_id: int, title: str,
                      course: str, due_date: str, priority: str, notes: str) -> Page:
    """Save edits to an assignment if its title and course are filled in."""
    assignment = find_assignment(state, assignment_id)
    if assignment is None:
        return assignment_list(state)

    if not title.strip() or not course.strip():
        draft = Assignment(
            assignment_id, title, course, due_date, priority, notes,
            assignment.completed
        )
        return assignment_form(state, draft, True, "Please enter a title and course.")

    assignment.title = title.strip()
    assignment.course = course.strip()
    assignment.due_date = due_date.strip()
    assignment.priority = priority
    assignment.notes = notes.strip()
    return assignment_list(state)


@route
def toggle_complete(state: State, assignment_id: int) -> Page:
    """Mark a pending assignment complete or reopen a completed one."""
    assignment = find_assignment(state, assignment_id)
    if assignment is not None:
        assignment.completed = not assignment.completed
    return assignment_list(state)


@route
def delete_assignment(state: State, assignment_id: int) -> Page:
    """Remove the assignment with the given ID from the list."""
    assignment = find_assignment(state, assignment_id)
    if assignment is not None:
        state.assignments.remove(assignment)
    return assignment_list(state)


@route
def progress(state: State) -> Page:
    """Count completed assignments and show the student's overall progress."""
    total = len(state.assignments)
    completed = 0
    for assignment in state.assignments:
        if assignment.completed:
            completed += 1

    percent = 0
    if total > 0:
        percent = round(100 * completed / total)

    bars = round(percent / 10)
    return Page(state, [
        Header("Progress"),
        f"Total: {total}",
        f"Completed: {completed}",
        f"Pending: {total - completed}",
        f"{percent}% complete",
        "■" * bars + "□" * (10 - bars),
        Button("Home", index)
    ])


@route
def settings(state: State) -> Page:
    """Show the settings page where the student can change their name."""
    return Page(state, [
        Header("Settings"),
        "Your name",
        TextBox("student_name", state.student_name),
        Button("Save name", save_settings),
        Button("Home", index)
    ])


@route
def save_settings(state: State, student_name: str) -> Page:
    """Save the student's name and return to the home page."""
    state.student_name = student_name.strip()
    return index(state)


sample = Assignment(4, "Lab report", "CHEM133", "", "High", "", False)
example_state = State([sample], "", "All", 5)
assert_equal(find_assignment(example_state, 4), sample)
assert_equal(find_assignment(example_state, 1), None)

start_server(State([], "", "All", 1))

```

**User:** what is this tab saying

**Assistant:** GitHub is asking if you’re ready to save your updated `main.py`. Copilot suggested the message **“Transform website into Student Assignment Tracker,”** and **“Commit directly to the main branch”** is selected.

You can leave both as they are and click **Commit changes** at the bottom to save your code to GitHub.

**User:** so I am supposed to sub mit a link of my working public wesite where do I get that from

**Assistant:** Your public website link should be **https://zaheer827.github.io/W-project/**. Open it and try adding an assignment. If that works, **paste that link into Canvas**. I can see your code was committed, but I couldn’t verify that the site is live.

If the link shows **404** or still says **Hello World**, publish your latest code:

1. Open Settings → Pages and set Source to GitHub Actions.
2. Open Actions, select the deploy workflow on the left, and click Run workflow. Confirm with the green button.
3. Once the run has a green checkmark, open it. Its summary contains the live website link to test and submit.

**User:** this is where it brought me [GitHub Pages settings screenshot]

**Assistant:** You’re in the right place. **GitHub Actions** is already selected. Click **View workflow runs** near the bottom of your screenshot, below the two **Configure** buttons.

1. In the left sidebar, select the workflow with Deploy in its name.
2. Click Run workflow, leave the branch on main, and confirm with the green Run workflow button.
3. When the run shows a green checkmark, open it and click the website link. Once your Student Assignment Tracker loads, copy that URL into Canvas.

**User:** why does it say this [GitHub Actions annotations screenshot]

**Assistant:** Both **build** and **deploy** have green checks, so GitHub marked both jobs successful. The red **“exit code 1”** means one command reported a failure. The screenshot doesn’t show which command failed. The yellow **“Drafter site information missing”** warning is separate. It means the About page is missing your name and project description.

**Try your live Student Assignment Tracker.** Add a sample assignment, mark it complete, and check that Progress shows **100%**. If that works, submit that link. If the site is blank or shows an error, click **build** on the left and expand the step containing **exit code 1**. The lines immediately above it should tell us what went wrong.

**User:** bro take over do it and these are the requirements do it and make sure all reqs are met and it looks like I wrote the code [CISC106 final project specifications pasted]

**Assistant work on this request:** Added site information, annotated the assignment lookup and page content, replaced global test data with local test data, and wrote unit tests for each route. Tested the deployed tracker in a browser. Prepared the repository planning page, AI-use record, and a walkthrough of the deployed app with synthesized narration.
