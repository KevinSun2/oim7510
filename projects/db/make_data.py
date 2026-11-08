"""Generate fictional BabsonAI Labs data using only Python's built-in tools.

Run from the repository folder with: uv run python projects/db/make_data.py
Dates cover November 9, 2025 through November 8, 2026, inclusive.
Task IDs 1 and 2 deliberately name an employee outside their project's team.
"""

import csv
import random
from datetime import date, timedelta
from pathlib import Path


# A fixed seed makes the same choices every time this script runs.
random.seed(7510)
AS_OF = date(2026, 11, 8)
FIRST_DATE = date(2025, 11, 9)

# __file__ locates this script, so its output folder does not depend on where it runs.
DATA_FOLDER = Path(__file__).resolve().parent / "data"
# These options create missing folders and allow an existing data folder.
DATA_FOLDER.mkdir(parents=True, exist_ok=True)


def random_date(first_day, last_day):
    """Choose a date between the two supplied dates, including both ends."""
    number_of_days = (last_day - first_day).days
    # timedelta adds a number of days to a date.
    return first_day + timedelta(days=random.randint(0, number_of_days))


def write_csv(filename, columns, rows):
    """Write dictionaries as CSV rows, using the supplied column order."""
    # newline="" prevents extra blank lines in CSV files on Windows.
    with (DATA_FOLDER / filename).open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        # CSV writes dates as YYYY-MM-DD and None as an empty field for SQL NULL.
        writer.writerows(rows)
    print(f"{filename}: {len(rows)} rows")


# All names, email addresses, clients, and transactions below are fictional.
# example.com is used for sample email addresses instead of real contact details.
names = [
    ("Avery", "Stone"), ("Jordan", "Vale"), ("Morgan", "Reed"),
    ("Casey", "Brooks"), ("Riley", "Park"), ("Taylor", "Lane"),
    ("Alex", "Hart"), ("Sam", "Wells"), ("Jamie", "West"),
    ("Drew", "Hayes"), ("Quinn", "Lake"), ("Cameron", "Finch"),
    ("Skyler", "Dale"), ("Robin", "Field"), ("Hayden", "Ash"),
    ("Peyton", "Snow"), ("Reese", "Hill"), ("Rowan", "Fox"),
    ("Blake", "Marsh"), ("Emerson", "North"), ("Finley", "Gray"),
    ("Dakota", "Shore"), ("Sage", "Brook"), ("Charlie", "Elm"),
    ("River", "Glen"),
]
titles = ["Developer", "Data Engineer", "Analyst", "Designer", "Data Scientist"]
people = []
people_by_id = {}

# enumerate starts the employee numbers at 1 while also giving us each name.
for person_id, name in enumerate(names, start=1):
    start_date = FIRST_DATE
    if person_id <= 2:
        title = "Co-founder"
        manager_id = None
    elif person_id <= 6:
        title = "Team Lead"
        manager_id = random.choice([1, 2])
    else:
        title = random.choice(titles)
        manager_id = random.choice([3, 4, 5, 6])
        if person_id != 25:
            start_date = random_date(FIRST_DATE, FIRST_DATE + timedelta(days=100))

    person = {
        "person_id": person_id,
        "first_name": name[0],
        "last_name": name[1],
        # An f-string inserts the employee number; 02d adds a leading zero.
        "email": f"employee{person_id:02d}@example.com",
        "title": title,
        "start_date": start_date,
        "manager_id": manager_id,
    }
    people.append(person)
    people_by_id[person_id] = person


# Each item lists a project's name, client, category, budget, status, and start offset.
project_details = [
    ("Support Assistant", "Maple Demo Market", "LLM app", 12000, "active", 0),
    ("Sales Data Refresh", "Harbor Demo Goods", "data pipeline", 16000, "active", 24),
    ("Invoice Assistant", "Cedar Demo Services", "LLM app", 10000, "active", 48),
    ("Staff Knowledge Search", None, "internal tool", 18000, "active", 72),
    ("Stock Data Feed", "Pine Demo Supply", "data pipeline", 14000, "active", 96),
    ("Booking Assistant", "Willow Demo Studio", "LLM app", 12000, "active", 120),
    ("Document Search", "Birch Demo Group", "LLM app", 11000, "done", 144),
    ("Expense Dashboard", None, "internal tool", 8000, "done", 168),
    ("Delivery Data Feed", "Oak Demo Logistics", "data pipeline", 6000, "paused", 192),
    ("Menu Assistant", "Spruce Demo Cafe", "LLM app", 5000, "paused", 216),
    ("Hiring Tracker", None, "internal tool", 5000, "planned", 336),
    ("Customer Feedback Feed", "Elm Demo Retail", "data pipeline", 7000, "planned", 350),
]
projects = []

for project_id, details in enumerate(project_details, start=1):
    projects.append({
        "project_id": project_id,
        "name": details[0],
        "client_name": details[1],
        "category": details[2],
        "budget": details[3],
        "status": details[4],
        "start_date": FIRST_DATE + timedelta(days=details[5]),
    })


project_assignments = []
teams = {}
assignments_by_pair = {}
hour_choices = [2.5, 5, 7.5, 10, 12.5, 15]
roles = ["Developer", "Analyst", "Designer", "Data Engineer"]

for project in projects:
    project_id = project["project_id"]
    if project_id == 1:
        team = [1, 3, 6, 9, 12]
    elif project_id == 2:
        team = [1, 4, 7, 10, 13]
    elif project_id == 3:
        team = [1, 5, 8, 11, 14]
    elif project_id >= 11:
        team = [2, 23, 24]
    else:
        # sample chooses five different employees, without repeating a person.
        team = random.sample(range(1, 23), 5)
    teams[project_id] = team

    for person_id in team:
        person = people_by_id[person_id]
        # max selects the later date so nobody joins before being hired.
        earliest_join = max(project["start_date"], person["start_date"])
        joined_date = random_date(earliest_join, earliest_join + timedelta(days=7))
        weekly_hours = random.choice(hour_choices)
        role = random.choice(roles)
        if person_id == 1 and project_id <= 3:
            weekly_hours = 18
            role = "Project Lead"
        if person_id == 1 and project_id == 1:
            joined_date = FIRST_DATE

        assignment = {
            "person_id": person_id,
            "project_id": project_id,
            "role": role,
            "weekly_hours": weekly_hours,
            "joined_date": joined_date,
        }
        project_assignments.append(assignment)
        # A tuple lets us look up one particular employee-and-project pairing.
        assignments_by_pair[(person_id, project_id)] = assignment


task_counts = [48, 42, 37, 35, 32, 28, 24, 22, 18, 14]
task_descriptions = [
    "Confirm requirements", "Prepare sample inputs", "Check data quality",
    "Build a prototype", "Review output accuracy", "Test an edge case",
    "Write user instructions", "Review client feedback", "Measure response time",
]
tasks = []
task_id = 0

# The two planned projects intentionally have no tasks or expenses yet.
for project in projects:
    project_id = project["project_id"]
    if project_id <= 10:
        for task_number in range(1, task_counts[project_id - 1] + 1):
            task_id += 1
            assigned_person_id = random.choice(teams[project_id])
            # Some unfinished tasks are deliberately unassigned, which is allowed.
            if project["status"] != "done" and random.randint(1, 10) == 1:
                assigned_person_id = None
            if task_id <= 2:
                assigned_person_id = 1

            earliest_created = project["start_date"]
            if assigned_person_id is not None:
                assignment = assignments_by_pair[(assigned_person_id, project_id)]
                earliest_created = max(earliest_created, assignment["joined_date"])

            latest_created = AS_OF
            if project["status"] in ["done", "paused"]:
                latest_created = AS_OF - timedelta(days=30)
            created_date = random_date(earliest_created, latest_created)
            if task_id == 1:
                created_date = FIRST_DATE
            due_date = created_date + timedelta(days=random.randint(7, 28))

            assigned_date = None
            completed_date = None
            if assigned_person_id is not None:
                # min prevents an assignment or completion from falling after AS_OF.
                assigned_date = min(created_date + timedelta(days=random.randint(0, 2)), AS_OF)
                if project["status"] == "done" or random.randint(1, 100) <= 65:
                    completed_date = min(assigned_date + timedelta(days=random.randint(1, 18)), AS_OF)

            # Employee 25 exists and was hired on FIRST_DATE but belongs to no project.
            # Changing these two assignees breaks only the project-membership rule.
            if task_id <= 2:
                assigned_person_id = 25

            tasks.append({
                "task_id": task_id,
                "project_id": project_id,
                "description": f"{random.choice(task_descriptions)} (task {task_number})",
                "created_date": created_date,
                "assigned_person_id": assigned_person_id,
                "assigned_date": assigned_date,
                "due_date": due_date,
                "completed_date": completed_date,
            })


expense_counts = [30, 26, 24, 22, 20, 18, 14, 12, 8, 6]
# Repeating categories makes cloud and software charges more common than travel.
expense_categories = [
    "GPU cloud", "GPU cloud", "GPU cloud", "software", "software", "software",
    "data labeling", "data labeling", "travel",
]
expense_ranges = {
    "GPU cloud": (10000, 250000),
    "software": (2000, 60000),
    "data labeling": (10000, 120000),
    "travel": (5000, 80000),
}
expense_notes = {
    "GPU cloud": "Model development and testing compute",
    "software": "Project software subscription",
    "data labeling": "Review and label training examples",
    "travel": "Travel for a project meeting",
}
expenses = []
expense_id = 0

for project in projects:
    project_id = project["project_id"]
    if project_id <= 10:
        for expense_number in range(1, expense_counts[project_id - 1] + 1):
            expense_id += 1
            category = random.choice(expense_categories)
            low_cents, high_cents = expense_ranges[category]
            cents = random.randint(low_cents, high_cents)
            latest_expense = AS_OF
            if project["status"] in ["done", "paused"]:
                latest_expense = AS_OF - timedelta(days=30)
            expense_date = random_date(project["start_date"], latest_expense)
            if expense_id == 1:
                expense_date = FIRST_DATE
            if project_id == 6 and expense_number == expense_counts[5]:
                expense_date = AS_OF

            expenses.append({
                "expense_id": expense_id,
                "project_id": project_id,
                "expense_date": expense_date,
                # .2f writes dollars with exactly two digits after the decimal point.
                "amount": f"{cents / 100:.2f}",
                "category": category,
                "note": expense_notes[category],
            })


print(f"Data period: {FIRST_DATE} through {AS_OF}")
# list(dictionary) supplies its column names in the order they were defined above.
write_csv("people.csv", list(people[0]), people)
write_csv("projects.csv", list(projects[0]), projects)
write_csv("project_assignments.csv", list(project_assignments[0]), project_assignments)
write_csv("tasks.csv", list(tasks[0]), tasks)
write_csv("expenses.csv", list(expenses[0]), expenses)
print("Intentional project-membership violations: task IDs 1 and 2, project 1, employee 25.")
print("Projects with no expenses: 11 and 12 (both planned).")
print("Employee 25 has no project assignments.")
print("Employee 1 commits at least 54 hours per week across active projects.")
print("Existing source rows skipped or converted: 0; all data was generated.")
