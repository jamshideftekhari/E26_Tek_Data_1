# Elective Course Registration — Design Document (MVP)

## 1. Purpose & Scope

A minimal demo of an elective course registration system, decomposed into three
independently deployable services — one per external actor from the context
diagram — that collaborate over REST to allocate students to elective courses.

This document covers:

- Recap of the Level 0 context diagram
- Level 1 data flow diagram (process decomposition)
- Service & API boundaries
- Cross-service interaction (allocation sequence)
- Data model per service
- Deployment architecture (docker-compose)
- MVP simplifications and next steps

## 2. Actors (from context diagram)

| Actor      | Provides                         | Receives                        |
|------------|-----------------------------------|----------------------------------|
| Teacher    | course description                 | class list, course schedule     |
| Student    | course priority                    | schedule                        |
| Management | room availability                  | course schedule, course priority |

## 3. Context Diagram (Level 0) — recap

```mermaid
flowchart LR
    Teacher[Teacher]
    Student[Student]
    Management[Management]
    P0((elective registration))

    Teacher -->|course description| P0
    P0 -->|class list| Teacher
    P0 -->|course schedule| Teacher

    Student -->|course priority| P0
    P0 -->|schedule| Student

    Management -->|room availability| P0
    P0 -->|course schedule| Management
    P0 -->|course priority| Management
```

## 4. Service Decomposition Overview

The single "elective registration" process is split **by actor** into three
services, plus one internal process (the allocation engine) that lives inside
the Management Service because Management is the actor that triggers it and
consumes its output for oversight.

| # | Process                              | Owning service     |
|---|---------------------------------------|---------------------|
| 1.0 | Manage Course Catalog                | Teacher Service      |
| 2.0 | Manage Student Priorities             | Student Service      |
| 3.0 | Manage Rooms & Oversight               | Management Service   |
| 4.0 | Allocate Schedule (matching engine)    | Management Service (internal) |

## 5. Level 1 Data Flow Diagram

### 5.1 Data stores

| Store | Contents                           | Owned by            |
|-------|-------------------------------------|----------------------|
| D1    | Courses (catalog)                   | Teacher Service DB   |
| D2    | Priorities (student course rankings)| Student Service DB   |
| D3    | Rooms (availability/capacity)       | Management Service DB|
| D4    | Schedule (allocation results)       | Management Service DB|

### 5.2 Diagram

```mermaid
flowchart LR
    Teacher[Teacher]
    Student[Student]
    Management[Management]

    P1((1.0 Manage<br/>Course Catalog))
    P2((2.0 Manage Student<br/>Priorities))
    P3((3.0 Manage Rooms<br/>&amp; Oversight))
    P4((4.0 Allocate<br/>Schedule))

    D1[(D1 Courses)]
    D2[(D2 Priorities)]
    D3[(D3 Rooms)]
    D4[(D4 Schedule)]

    Teacher -->|course description| P1
    P1 -->|write| D1
    P1 -->|class list| Teacher
    P1 -->|course schedule| Teacher

    Student -->|course priority| P2
    P2 -->|write| D2
    P2 -->|schedule| Student

    Management -->|room availability| P3
    P3 -->|write| D3
    P3 -->|course schedule| Management
    P3 -->|course priority| Management

    Management -->|run allocation| P4
    D1 -.->|GET /courses via REST| P4
    D2 -.->|GET /priorities via REST| P4
    D3 -->|local read| P4
    P4 -->|local write| D4

    D4 -.->|GET /schedule/course/:id via REST| P1
    D4 -.->|GET /schedule/student/:id via REST| P2
    D4 -->|local read| P3
```

Dashed arrows (`-.->`) cross a service boundary and are implemented as REST
calls; solid arrows within the same service are local DB reads/writes.

### 5.3 Data flow descriptions

| # | Flow                          | From → To                        | Mechanism |
|---|--------------------------------|-----------------------------------|-----------|
| 1 | course description              | Teacher → 1.0                     | REST (external) |
| 2 | class list                      | 1.0 → Teacher                     | REST (external) |
| 3 | course schedule                 | 1.0 → Teacher                     | REST (external) |
| 4 | course priority                 | Student → 2.0                     | REST (external) |
| 5 | schedule                        | 2.0 → Student                     | REST (external) |
| 6 | room availability               | Management → 3.0                  | REST (external) |
| 7 | course schedule (report)        | 3.0 → Management                  | REST (external) |
| 8 | course priority (report)        | 3.0 → Management                  | REST (external) |
| 9 | run allocation                  | Management → 4.0                  | REST (external, triggers internal job) |
| 10 | courses (read)                 | D1 → 4.0                          | REST, Management Service → Teacher Service |
| 11 | priorities (read)               | D2 → 4.0                          | REST, Management Service → Student Service |
| 12 | rooms (read)                    | D3 → 4.0                          | local DB read |
| 13 | schedule (write)                | 4.0 → D4                          | local DB write |
| 14 | schedule detail (read)          | D4 → 1.0                          | REST, Teacher Service → Management Service |
| 15 | schedule detail (read)          | D4 → 2.0                          | REST, Student Service → Management Service |

## 6. Service & API Design

Each service is a small FastAPI app with automatic OpenAPI docs at `/docs`,
which doubles as the actor-facing UI for this MVP (no separate frontend).

### 6.1 Teacher Service (port 8001, schema `course_db`)

| Method | Path                          | Purpose |
|--------|--------------------------------|---------|
| POST   | `/courses`                     | Submit a course description |
| GET    | `/courses`                     | List all courses (also used by Management Service) |
| GET    | `/courses/{id}/class-list`     | Class list — calls Management `GET /schedule/course/{id}` |
| GET    | `/courses/{id}/schedule`       | Course schedule — calls Management `GET /schedule/course/{id}` |

### 6.2 Student Service (port 8002, schema `student_db`)

| Method | Path                              | Purpose |
|--------|-------------------------------------|---------|
| POST   | `/students`                        | Register a student |
| POST   | `/students/{id}/priorities`        | Submit ranked course priorities |
| GET    | `/priorities`                      | List all priorities (used by Management Service) |
| GET    | `/students/{id}/schedule`          | Assigned schedule — calls Management `GET /schedule/student/{id}` |

### 6.3 Management Service (port 8003, schema `management_db`)

| Method | Path                          | Purpose |
|--------|--------------------------------|---------|
| POST   | `/rooms`                        | Submit room availability |
| GET    | `/rooms`                        | List rooms |
| POST   | `/allocation/run`               | Trigger the allocation engine (4.0) |
| GET    | `/schedule`                     | Full schedule (management oversight view) |
| GET    | `/schedule/course/{id}`         | Schedule detail for one course (called by Teacher Service) |
| GET    | `/schedule/student/{id}`        | Schedule detail for one student (called by Student Service) |
| GET    | `/priorities-summary`           | Aggregated demand per course vs. capacity (management report) |

## 7. Cross-Service Interaction — Allocation Sequence

```mermaid
sequenceDiagram
    participant Mgmt as Management (actor)
    participant MS as Management Service
    participant TS as Teacher Service
    participant SS as Student Service

    Mgmt->>MS: POST /allocation/run
    MS->>TS: GET /courses
    TS-->>MS: courses[]
    MS->>SS: GET /priorities
    SS-->>MS: priorities[]
    MS->>MS: read rooms (local DB)
    MS->>MS: run allocation algorithm
    MS->>MS: write schedule (local DB)
    MS-->>Mgmt: 200 OK { summary }

    Note over TS,MS: Later, on demand
    TS->>MS: GET /schedule/course/{id}
    MS-->>TS: schedule detail

    SS->>MS: GET /schedule/student/{id}
    MS-->>SS: schedule detail
```

## 8. Data Model (per service)

**Teacher Service — `course_db`**
```
courses(id, teacher_name, code, title, description, capacity)
```

**Student Service — `student_db`**
```
students(id, name, email)
priorities(id, student_id, course_id, rank)
```

**Management Service — `management_db`**
```
rooms(id, name, capacity, time_slot)
schedule(id, course_id, room_id, time_slot)
allocations(id, schedule_id, student_id)
```

## 9. Entity-Relationship Diagram

All tables live in one MySQL instance but are split across three schemas
(one per service). Relationships **within** a schema are real foreign keys;
relationships **across** schemas (dashed in the diagram below, dotted-style
labels) are logical references only — validated at the application layer via
REST calls, not enforced by the database. This keeps each service's schema
independently owned, so the shared instance could be split into three
physical databases later without changing any table.

```mermaid
erDiagram
    COURSES ||--o{ PRIORITIES : "ranked in (logical, via REST)"
    COURSES ||--o{ SCHEDULE : "allocated to (logical, via REST)"
    STUDENTS ||--o{ PRIORITIES : "submits"
    STUDENTS ||--o{ ALLOCATIONS : "assigned to (logical, via REST)"
    ROOMS ||--o{ SCHEDULE : "hosts"
    SCHEDULE ||--o{ ALLOCATIONS : "contains"

    COURSES {
        int id PK
        string teacher_name
        string code
        string title
        string description
        int capacity
    }

    STUDENTS {
        int id PK
        string name
        string email
    }

    PRIORITIES {
        int id PK
        int student_id FK
        int course_id "logical FK -> COURSES.id (course_db)"
        int rank
    }

    ROOMS {
        int id PK
        string name
        int capacity
        string time_slot
    }

    SCHEDULE {
        int id PK
        int course_id "logical FK -> COURSES.id (course_db)"
        int room_id FK
        string time_slot
    }

    ALLOCATIONS {
        int id PK
        int schedule_id FK
        int student_id "logical FK -> STUDENTS.id (student_db)"
    }
```

| Schema           | Tables                          |
|------------------|-----------------------------------|
| `course_db`      | COURSES                           |
| `student_db`     | STUDENTS, PRIORITIES              |
| `management_db`  | ROOMS, SCHEDULE, ALLOCATIONS       |

## 10. Allocation Algorithm (MVP default)

**Priority-first-fit**: process students in registration order; for each
student, assign them to their highest-ranked course that still has free
capacity (bounded by the room's capacity for that course's time slot).
Unmatched priorities are simply skipped. This is easy to explain/demo and can
be swapped for a fairer/optimizing algorithm later without changing the API
contracts.

## 11. Deployment Architecture

```mermaid
flowchart TB
    subgraph compose[docker-compose network: elective-net]
        TS["teacher-service<br/>FastAPI :8001"]
        SS["student-service<br/>FastAPI :8002"]
        MS["management-service<br/>FastAPI :8003"]
        DB[("mysql:8<br/>schemas: course_db, student_db, management_db")]
    end

    TS -->|SQL| DB
    SS -->|SQL| DB
    MS -->|SQL| DB
    MS -->|REST GET /courses| TS
    MS -->|REST GET /priorities| SS
    TS -->|REST GET /schedule/course/:id| MS
    SS -->|REST GET /schedule/student/:id| MS
```

`docker-compose.yml` will define 4 containers: `teacher-service`,
`student-service`, `management-service`, and `mysql`, all on one bridge
network, with each app service reading its DB connection string (including
schema name) from environment variables.

## 12. MVP Simplifications / Non-Goals

- No authentication/authorization — any actor can call any endpoint.
- No message broker — all cross-service calls are synchronous REST.
- Single MySQL instance shared by all three services (three schemas, not
  three DB containers) — acceptable for a demo; a production system would
  give each service its own DB instance.
- No retry/circuit-breaker logic on cross-service REST calls.
- Allocation algorithm is intentionally simple (see §10), not an optimizer.
- No real frontend — FastAPI's `/docs` (Swagger UI) is the actor interface.

## 13. Next Steps (implementation plan)

1. Scaffold repo: `teacher-service/`, `student-service/`, `management-service/`,
   shared `docker-compose.yml`, MySQL init scripts (create 3 schemas).
2. Implement Management Service first (rooms, schedule tables, allocation
   engine) since the other two depend on its `/schedule/*` endpoints.
3. Implement Teacher Service (courses CRUD + proxy calls to Management).
4. Implement Student Service (students/priorities CRUD + proxy calls to
   Management).
5. Wire up `docker-compose.yml`, smoke-test the full allocation flow end to
   end via the sequence in §7.
