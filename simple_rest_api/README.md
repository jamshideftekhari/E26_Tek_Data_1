# Elective Course Registration — Simple REST API (MVC Monolith)

A single Flask app using Controller → Service → Model layering against one
shared MySQL database, accessed with `mysql-connector-python` (no ORM). No
containers — see [DESIGN.md](DESIGN.md) for the full design and how this
compares to the [microservices version](../docs/DESIGN.md) at the repo root.

## Setup

**1. Create the database and tables**

```bash
mysql -u root -p < schema.sql
```

**2. Install dependencies**

```bash
python -m venv .venv
source .venv/bin/activate        # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**3. Configure the DB connection** (defaults shown; only needed if yours differ)

```bash
export DB_HOST=localhost
export DB_PORT=3306
export DB_USER=root
export DB_PASSWORD=root
export DB_NAME=elective_registration
```

On Windows PowerShell, use `$env:DB_HOST="localhost"` etc.

**4. Run it**

```bash
python app.py
```

The app listens on `http://localhost:5000`.

## Demo walkthrough

```bash
# 1. Teacher adds a course
curl -X POST localhost:5000/teacher/courses -H "Content-Type: application/json" -d \
  '{"teacher_name":"Dr. Smith","code":"CS101","title":"Intro to AI","capacity":2}'

# 2. Management adds a room
curl -X POST localhost:5000/management/rooms -H "Content-Type: application/json" -d \
  '{"name":"Room A","capacity":2,"time_slot":"Mon 10-12"}'

# 3. Students register and submit priorities (rank 1 = highest)
curl -X POST localhost:5000/student/students -H "Content-Type: application/json" -d \
  '{"name":"Alice","email":"alice@example.com"}'
curl -X POST localhost:5000/student/students/1/priorities -H "Content-Type: application/json" -d \
  '{"priorities":[{"course_id":1,"rank":1}]}'

# 4. Management triggers the allocation
curl -X POST localhost:5000/management/allocation/run

# 5. Everyone checks the results
curl localhost:5000/teacher/courses/1/class-list
curl localhost:5000/student/students/1/schedule
curl localhost:5000/management/priorities-summary
```

## Notes

- No auth, no ORM, no migrations tool — see [DESIGN.md](DESIGN.md) §7 for the
  full list of simplifications.
- The connection pool is created eagerly at import time, so `python app.py`
  will fail fast with a clear error if MySQL isn't reachable or `schema.sql`
  hasn't been applied yet.
- Re-running `/management/allocation/run` recomputes the schedule from scratch.
