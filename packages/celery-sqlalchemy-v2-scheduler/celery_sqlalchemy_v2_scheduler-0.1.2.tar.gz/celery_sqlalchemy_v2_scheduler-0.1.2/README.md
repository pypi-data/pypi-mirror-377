# Celery SQLAlchemy V2 Scheduler

A Celery Beat scheduler that stores the schedule in a database via SQLAlchemy.

This scheduler allows you to store periodic task schedules in a database, enabling you to add, edit, and remove tasks dynamically without restarting the Celery beat service.

[![PyPI version](https://img.shields.io/pypi/v/celery-sqlalchemy-v2-scheduler.svg)](https://pypi.python.org/pypi/celery-sqlalchemy-v2-scheduler)
[![Build Status](https://img.shields.io/travis/your-repo/celery-sqlalchemy-v2-scheduler.svg)](https://travis-ci.org/your-repo/celery-sqlalchemy-v2-scheduler)

---

## Features

*   **Dynamic Schedule Management**: Add, edit, and disable tasks on the fly by manipulating the database.
*   **SQLAlchemy Backend**: Works with any database supported by SQLAlchemy (e.g., PostgreSQL, MySQL, SQLite).
*   **Full-Featured Schedules**: Natively supports `interval`, `crontab`, and `solar` schedules.
*   **Timezone-Aware Crontabs**: Define cron jobs that run in specific timezones.
*   **Declarative Setup**: Define an initial schedule directly in your Celery configuration, which will be synchronized to the database on startup.

## Installation

Install the package from PyPI:

```bash
pip install celery-sqlalchemy-v2-scheduler
```

## Setup

To use this scheduler, you need to set the beat_scheduler and beat_dburi in your Celery application configuration. The scheduler will automatically create the necessary tables in your database when it first starts.

```python
# in your_app/celery.py

from celery import Celery
from celery.schedules import crontab

app = Celery('your_app')

# Configure the scheduler
app.conf.beat_scheduler = 'celery_sqlalchemy_v2_scheduler.schedulers.DatabaseScheduler'

# The database URI for the scheduler.
# This can be any database supported by SQLAlchemy.
app.conf.beat_dburi = 'sqlite:///schedule.db'

# (Optional) Define a static schedule in your config.
# These tasks will be added to the database when the scheduler starts.
# This is useful for defining a default set of tasks.
app.conf.beat_schedule = {
    'cleanup-every-morning': {
        'task': 'your_app.tasks.backend_cleanup',
        'schedule': crontab(hour=4, minute=0),
    },
    'add-every-30-seconds': {
        'task': 'your_app.tasks.add',
        'schedule': 30.0,
        'args': (16, 16)
    },
}

# Load task modules
app.autodiscover_tasks(['your_app.tasks'])
```

## Usage

### Running Celery Beat

Start the beat service. If you have configured the scheduler in your Celery app as shown above, you don't need to specify it on the command line.

```bash
celery -A your_app beat -l info
```

The scheduler will connect to the database specified in beat_dburi and create the necessary tables if they don't exist.

### Managing Tasks Programmatically

You can add, modify, or delete tasks by directly interacting with the SQLAlchemy models. This is the primary benefit of using a database-backed scheduler.

Here's an example of how to add a new periodic task that runs every 10 seconds.

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from celery.schedules import schedule

from celery_sqlalchemy_v2_scheduler.session import SessionManager
from celery_sqlalchemy_v2_scheduler.models import PeriodicTask, IntervalSchedule

# 1. Setup the database session
db_uri = 'sqlite:///schedule.db'
session_manager = SessionManager()
engine, Session = session_manager.create_session(db_uri)
session = Session()

# 2. Create an interval schedule
# The scheduler will look for an existing schedule with the same properties
# or create a new one if it doesn't exist.
interval = IntervalSchedule.from_schedule(session, schedule(run_every=10.0))
session.flush() # Ensure the interval gets an ID

# 3. Create the periodic task
task = PeriodicTask(
    name='My Programmatic Task',
    task='your_app.tasks.some_task',
    interval=interval,
    args='[1, 2]',
    kwargs='{"foo": "bar"}',
    enabled=True
)

session.add(task)
session.commit()

print(f"Task '{task.name}' with id {task.id} created.")

session.close()
```

### Disabling a Task

To disable a task, simply query it and set its enabled flag to False. The beat service will automatically detect the change and stop scheduling the task.

```python
# ... (session setup from previous example) ...

task_to_disable = session.query(PeriodicTask).filter_by(name='My Programmatic Task').first()

if task_to_disable:
    task_to_disable.enabled = False
    session.commit()
    print(f"Task '{task_to_disable.name}' has been disabled.")

session.close()
```

## Database Models

The scheduler uses the following core models:

*   `PeriodicTask`: The main model representing a single periodic task. It holds the task name, arguments, execution options, and a foreign key to one of the schedule types.
*   `IntervalSchedule`: Stores interval-based schedules (e.g., "run every 30 seconds").
*   `CrontabSchedule`: Stores cron-style schedules (e.g., "run every day at 5 AM"). This model is timezone-aware.
*   `SolarSchedule`: Stores schedules based on solar events like sunrise, sunset, dawn, and dusk for a given geographic location.
*   `PeriodicTaskChanged`: A helper table used internally to efficiently detect when the schedule has been updated, prompting the scheduler to reload its tasks.