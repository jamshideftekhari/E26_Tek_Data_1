# Elective Course Registration (MVP)

Three FastAPI microservices — one per actor from the [design doc](docs/DESIGN.md)
— backed by MySQL, wired together with docker-compose.

| Service             | Port | Owns schema      |
|----------------------|------|-------------------|
| teacher-service       | 8001 | `course_db`        |
| student-service        | 8002 | `student_db`       |
| management-service    | 8003 | `management_db`    |

Each service exposes interactive API docs at `http://localhost:<port>/docs`.

## Run it

### With Docker (recommended)

```bash
docker-compose up --build
```

### Without Docker (local Python + MySQL)

Requires Python 3.11+ and a MySQL server you can reach from your machine.

**1. Create the three schemas**

```bash
mysql -u root -p < mysql-init/init.sql
```

**2. Install dependencies** — the three services share identical dependencies,
so one virtualenv is enough:

```bash
python -m venv .venv
source .venv/bin/activate        # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r teacher-service/requirements.txt \
            -r student-service/requirements.txt \
            -r management-service/requirements.txt
```

**3. Run each service in its own terminal.** `uvicorn --app-dir <service>`
puts that service's `app` package on the path without needing to `cd` into
it. Point `DATABASE_URL` at your local MySQL, and point the cross-service
URLs at `localhost` instead of the docker-compose hostnames.

```bash
# Terminal 1 — Management Service
export DATABASE_URL="mysql+pymysql://root:yourpassword@localhost:3306/management_db"
export TEACHER_SERVICE_URL="http://localhost:8001"
export STUDENT_SERVICE_URL="http://localhost:8002"
uvicorn app.main:app --app-dir management-service --port 8003 --reload
```

```bash
# Terminal 2 — Teacher Service
export DATABASE_URL="mysql+pymysql://root:yourpassword@localhost:3306/course_db"
export MANAGEMENT_SERVICE_URL="http://localhost:8003"
uvicorn app.main:app --app-dir teacher-service --port 8001 --reload
```

```bash
# Terminal 3 — Student Service
export DATABASE_URL="mysql+pymysql://root:yourpassword@localhost:3306/student_db"
export MANAGEMENT_SERVICE_URL="http://localhost:8003"
uvicorn app.main:app --app-dir student-service --port 8002 --reload
```

On Windows PowerShell, replace `export VAR="value"` with `$env:VAR="value"`.

## Demo walkthrough

```bash
# 1. Teacher adds a course
curl -X POST localhost:8001/courses -H "Content-Type: application/json" -d \
  '{"teacher_name":"Dr. Smith","code":"CS101","title":"Intro to AI","capacity":2}'

# 2. Management adds a room
curl -X POST localhost:8003/rooms -H "Content-Type: application/json" -d \
  '{"name":"Room A","capacity":2,"time_slot":"Mon 10-12"}'

# 3. Students register and submit priorities (rank 1 = highest)
curl -X POST localhost:8002/students -H "Content-Type: application/json" -d \
  '{"name":"Alice","email":"alice@example.com"}'
curl -X POST localhost:8002/students/1/priorities -H "Content-Type: application/json" -d \
  '{"priorities":[{"course_id":1,"rank":1}]}'

# 4. Management triggers the allocation
curl -X POST localhost:8003/allocation/run

# 5. Everyone checks the results
curl localhost:8001/courses/1/class-list
curl localhost:8002/students/1/schedule
curl localhost:8003/priorities-summary
```

## Notes

- No auth, no message broker, single shared MySQL instance (3 schemas) — see
  [docs/DESIGN.md](docs/DESIGN.md) §12 for the full list of MVP simplifications.
- Re-running `/allocation/run` recomputes the schedule from scratch.
