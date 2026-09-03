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

```bash
docker-compose up --build
```

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
