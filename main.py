from dataclasses import dataclass
from bakery import assert_equal
from drafter import *

hide_debug_information()
set_website_title("Student Assignment Tracker")
set_website_framed(False)
# Include the narrated demo when Drafter builds the public site.
add_website_file("walkthrough.html")
set_site_information(
    author="Zaheer Khan",
    description="Track assignments by course, mark them done, and check your progress.",
    sources="CISC106 course materials, Drafter documentation, and ChatGPT coding assistance.",
    planning="https://github.com/Zaheer827/W-project/blob/main/planning.md",
    links=["https://github.com/Zaheer827/W-project"]
)

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


def find_assignment(state: State, assignment_id: int) -> 'Assignment | None':
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
    # Drafter pages can contain plain text and components like buttons.
    content: list[PageContent] = [
        Header("Assignments"),
        SelectBox("status_filter", FILTERS, state.status_filter),
        Button("Apply filter", set_filter)
    ]

    shown = 0
    for assignment in state.assignments:
        status = "Completed" if assignment.completed else "Pending"
        if state.status_filter in ["All", status]:
            shown += 1
            # The button carries the ID so filtering never changes which assignment it edits.
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
    # Drafter pages can contain plain text and components like buttons.
    content: list[PageContent] = [Header(heading)]

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


def test_tracker() -> None:
    """Check the pages and state changes with a separate practice list."""
    state = State([], "", "All", 1)
    assert_equal("Welcome!" in index(state).content, True)
    assert_equal("No assignments yet." in assignment_list(state).content, True)
    assert_equal("0% complete" in progress(state).content, True)
    assert_equal(TextBox("title", "") in add_assignment(state).content, True)
    assert_equal(TextBox("student_name", "") in settings(state).content, True)
    home = save_settings(state, " Sam ")
    assert_equal(state.student_name, "Sam")
    assert_equal("Welcome, Sam!" in home.content, True)

    error = save_assignment(state, "", "Math", "", "Medium", "")
    assert_equal("Please enter a title and course." in error.content, True)
    assert_equal(state.next_id, 1)
    assert_equal(state.assignments, [])
    save_assignment(state, "Quiz", "Math", "", "Medium", "")
    save_assignment(state, "Lab", "Chem", "", "Low", "")
    assert_equal(state.next_id, 3)
    assert_equal(find_assignment(state, 1), Assignment(1, "Quiz", "Math", "", "Medium", "", False))
    assert_equal(find_assignment(state, 99), None)
    assert_equal(TextBox("title", "Lab") in edit_assignment(state, 2).content, True)
    update_assignment(state, 2, "Lab report", "Chem", "2026-12-01", "High", "Include the graph")
    assert_equal(state.assignments[1], Assignment(2, "Lab report", "Chem", "2026-12-01",
                                                  "High", "Include the graph", False))
    update_assignment(state, 2, "Oops", " ", "", "Low", "")
    assert_equal(state.assignments[1].title, "Lab report")
    toggle_complete(state, 2)
    assert_equal(state.assignments[1].completed, True)
    assert_equal("50% complete" in progress(state).content, True)
    filtered = set_filter(state, "Completed")
    assert_equal(state.status_filter, "Completed")
    assert_equal(Header("Lab report") in filtered.content, True)
    assert_equal(Header("Quiz") in filtered.content, False)
    toggle_complete(state, 2)
    assert_equal("No assignments match this filter." in assignment_list(state).content, True)
    delete_assignment(state, 1)
    assert_equal(len(state.assignments), 1)
    assert_equal(state.assignments[0].assignment_id, 2)


test_tracker()
start_server(State([], "", "All", 1))
