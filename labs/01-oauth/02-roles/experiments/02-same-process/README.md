# Experiment 02 — Same Process

> **Lab:** `01-oauth/02-roles`  
> **Experiment:** `02-same-process`  
> **Status:** Completed  
> **Focus:** Process boundary vs OAuth role boundary

---

## 1. Experiment Question

This experiment asks:

> Can Authorization Server and Resource Server responsibilities be implemented inside the **same application process** while remaining separate protocol responsibilities?

The experiment intentionally removes the process boundary that existed in Experiment 01.

Experiment 01 used:

```text
One server container
├── AS process
└── RS process
```

Experiment 02 uses:

```text
One server container
└── One FastAPI process
    ├── Authorization Server responsibility
    └── Resource Server responsibility
```

The experiment therefore changes one important runtime property:

```text
2 backend processes
        ↓
1 backend process
```

while keeping the logical responsibilities distinct through separate route modules.

---

# 2. Learning Objective

The objective is to develop a concrete understanding that an OAuth role is a **protocol responsibility**, not a synonym for a Unix process.

The experiment should allow us to observe all of the following in one running FastAPI process:

```text
Authorization responsibility
Resource-serving responsibility
Separate endpoint groups
```

The target conclusion is:

```text
Process Boundary
    ≠
OAuth Role Boundary
```

This is an architectural observation demonstrated by the Lab implementation. It should not be interpreted as an OAuth requirement that implementations must use one process.

RFC 6749 defines the Authorization Server and Resource Server as OAuth roles and states that the Authorization Server may be the same server as the Resource Server or a separate entity. The RFC does not prescribe a process model. citeturn593962search0

---

# 3. Starting Point

The previous experiment established that the two roles could share one container while remaining two processes:

```text
Experiment 01

Docker Host
│
├── Client container
│
└── Server container
    ├── AS process
    └── RS process
```

Experiment 02 intentionally collapses the two backend processes into one FastAPI application process.

The Client remains separate.

Final target topology:

```text
Docker Host
│
├── Client container
│   └── Vite :5173
│
└── Server container
    └── FastAPI process :8200
        ├── Authorization Server routes
        └── Resource Server routes
```

---

# 4. What Changed in the Implementation

Instead of maintaining two separate backend applications, the experiment uses one FastAPI application and two `APIRouter` modules.

The server source is organized as:

```text
src/server/
├── Dockerfile
├── requirements.txt
├── app/
│   ├── main.py
│   └── routers/
│       ├── __init__.py
│       ├── authorization.py
│       └── resource.py
└── tests/
    └── test_roles.py
```

This is the core implementation change.

---

## 4.1 Single FastAPI Application

`app/main.py` creates exactly one `FastAPI` instance:

```python
app = FastAPI(
    title="OAuth 2.0 Identity Lab — Same Process",
    version="0.1.0",
)
```

It then mounts two routers into that same application:

```python
app.include_router(
    authorization.router,
    prefix="/oauth",
    tags=["authorization-server"],
)

app.include_router(
    resource.router,
    prefix="/api",
    tags=["resource-server"],
)
```

The result is one application containing two logically named groups of endpoints.

FastAPI's official documentation describes `APIRouter` as a way to structure larger applications into separate modules while including those routes into one `FastAPI` application. citeturn593962search1

---

## 4.2 Authorization Server Responsibility

`app/routers/authorization.py` defines an `APIRouter` and exposes:

```http
GET /oauth/health
```

The endpoint returns:

```json
{
  "status": "ok",
  "service": "authorization-server",
  "role": "authorization_server"
}
```

This endpoint is deliberately a role-identification endpoint rather than an implementation of the OAuth Authorization Endpoint.

There is still no:

```text
/oauth/authorize
```

or token issuance behavior in this experiment.

---

## 4.3 Resource Server Responsibility

`app/routers/resource.py` defines a second `APIRouter` and exposes:

```http
GET /api/health
GET /api/profile
```

`GET /api/profile` returns:

```json
{
  "id": "demo-user",
  "display_name": "Lab User",
  "resource": "protected"
}
```

The route therefore remains the Resource Server side of the experiment.

---

# 5. Why `APIRouter` Is Important Here

The experiment deliberately separates source modules without separating runtime processes.

The code organization is:

```text
One process
│
└── FastAPI application
    │
    ├── authorization.py
    │      └── /oauth/*
    │
    └── resource.py
           └── /api/*
```

This gives us a useful distinction:

```text
Source module
    ≠
Process

Route group
    ≠
Process

OAuth role
    ≠
Process
```

The fact that `authorization.py` and `resource.py` are separate files is therefore not evidence of separate processes. The runtime process is determined by how the application is launched.

---

# 6. Test Coverage

The experiment uses a single test module:

```text
src/server/tests/test_roles.py
```

It tests all three functional endpoints:

```text
/oauth/health
/api/health
/api/profile
```

and also verifies that an unknown route returns:

```text
404
```

The test module imports the same application object:

```python
from app.main import app
```

and constructs one `TestClient` around it.

That is consistent with the runtime architecture: the tests exercise one FastAPI application that contains both route groups.

FastAPI's official testing documentation uses `TestClient` to test the application directly and commonly combines it with pytest. citeturn593962search1

---

# 7. Dependency Definition

The server uses:

```text
fastapi[standard]
pytest
httpx2
```

The important application choice is `fastapi[standard]`, because this experiment launches the application with the `fastapi run` CLI.

The Docker image installs dependencies from the application's `requirements.txt`, keeping dependency definition separate from the Docker build instructions.

---

# 8. Docker Image

The server Dockerfile is located at:

```text
src/server/Dockerfile
```

The build context is the server directory itself:

```yaml
server:
  build:
    context: ./src/server
```

Therefore Dockerfile `COPY` paths are relative to:

```text
./src/server
```

The image copies:

```text
requirements.txt
app/
```

and starts:

```text
fastapi run app/main.py --host 0.0.0.0 --port 8200
```

The official FastAPI container documentation follows the same general pattern: copy the requirements first, install them, copy the application, and use the exec form of `CMD` with `fastapi run`. citeturn593962search1

---

# 9. Client Container

The Client remains a separate container.

Its image uses:

```text
node:24-alpine
```

and runs Vite with:

```text
npm run dev -- --host 0.0.0.0
```

The host port was deliberately changed for this experiment:

```text
Host :5273
    ↓
Container :5173
```

This avoids conflict with ports used by other projects and experiments.

Vite exposes variables prefixed with `VITE_` through `import.meta.env`; this experiment therefore uses:

```text
VITE_API_BASE_URL=http://127.0.0.1:8200
```

Vite's documentation also warns that `VITE_*` variables are exposed to client-side code, so they must not contain secrets. citeturn593962search2

---

# 10. Compose Topology

The experiment's `docker-compose.yml` defines exactly two services:

```yaml
services:
  server:
    build:
      context: ./src/server
    ports:
      - "8200:8200"

  client:
    build:
      context: ./src/client
    ports:
      - "5273:5173"
    environment:
      VITE_API_BASE_URL: http://127.0.0.1:8200
```

Therefore the actual Docker topology is:

```text
Docker Host
│
├── 02-same-process-client-1
│   └── Vite :5173
│       ↑
│       Host :5273
│
└── 02-same-process-server-1
    └── FastAPI :8200
```

There is **one backend container**, and inside it there is **one FastAPI application process**.

Docker's documentation describes a container as running while its main process is running and explains that containers can contain multiple processes, although one service per container is generally the recommended pattern. citeturn593962search3

---

# 11. Execution

The Dockerized experiment was started with:

```bash
docker compose up
```

Docker created:

```text
02-same-process-server-1
02-same-process-client-1
```

The Client started Vite successfully:

```text
VITE v8.2.2 ready
Local: http://localhost:5173/
Network: http://172.19.0.3:5173/
```

The server started successfully:

```text
Starting FastAPI in production mode
Using import string: app.main:app
Server started at http://0.0.0.0:8200
Documentation at http://0.0.0.0:8200/docs
```

Most importantly, the server reported:

```text
Started server process [1]
Waiting for application startup.
Application startup complete.
Uvicorn running on http://0.0.0.0:8200
```

Only one FastAPI server process was started.

---

# 12. Endpoint Verification

The following endpoints were executed against the same port and same FastAPI application.

## 12.1 Authorization Server route

```bash
curl http://127.0.0.1:8200/oauth/health
```

Observed:

```json
{
  "status": "ok",
  "service": "authorization-server",
  "role": "authorization_server"
}
```

---

## 12.2 Resource Server health route

```bash
curl http://127.0.0.1:8200/api/health
```

Observed:

```json
{
  "status": "ok"
}
```

---

## 12.3 Resource Server resource route

```bash
curl http://127.0.0.1:8200/api/profile
```

Observed:

```json
{
  "id": "demo-user",
  "display_name": "Lab User",
  "resource": "protected"
}
```

---

# 13. OpenAPI Verification

The following endpoint was opened:

```text
http://127.0.0.1:8200/docs
```

FastAPI generated one Swagger UI for the one application.

The application therefore exposes both responsibilities through the same OpenAPI application surface:

```text
/oauth/health
/api/health
/api/profile
```

This is significant because there is not one OpenAPI application for AS and another for RS. There is one application containing both route groups.

---

# 14. Process-Level Verification

To avoid depending on the `ps` utility being installed in the slim image, the container's `/proc` filesystem was inspected directly.

The command searched the process command lines for FastAPI/Uvicorn processes.

Observed:

```text
1: /usr/local/bin/python3.14 /usr/local/bin/fastapi run app/main.py --host 0.0.0.0 --port 8200
```

The inspection shell itself also appeared as another PID, but it was only the temporary command used for inspection:

```text
11: sh -c for p in /proc/[0-9]*; do ...
```

The important observation is that there was only **one FastAPI/Uvicorn application process**.

Therefore:

```text
FastAPI processes = 1
```

---

# 15. Client Verification

The Client container was published using the dedicated host port:

```text
http://localhost:5273
```

The application rendered the expected Resource Server data:

```text
OAuth 2.0 Identity Lab
Role: OAuth Client

Resource Server Response

ID
 demo-user

Display Name
 Lab User

Resource
 protected
```

This demonstrates that the Client continues to work against the same-process backend deployment.

---

# 16. What the Client Actually Calls

The Client API module uses:

```javascript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

fetch(`${API_BASE_URL}/api/profile`);
```

Therefore the Client continues to call:

```text
http://127.0.0.1:8200/api/profile
```

It does not call:

```text
/oauth/health
```

and it does not perform an OAuth authorization request.

This matters because the experiment changes **where the role implementations execute**, not the OAuth protocol flow itself.

---

# 17. Process and Role Comparison

At runtime we have:

```text
One FastAPI process
│
├── /oauth/health
│   └── Authorization Server responsibility
│
├── /api/health
│   └── Resource Server responsibility
│
└── /api/profile
    └── Resource Server responsibility
```

The same process is therefore capable of serving endpoint groups associated with two different OAuth roles.

This demonstrates the difference between:

```text
Logical role
```

and:

```text
Runtime process
```

---

# 18. Actual Learning Outcome

The experiment gives us a concrete implementation-level answer:

> Do Authorization Server and Resource Server responsibilities require two separate application processes?

**No.**

In this experiment we intentionally implemented both responsibilities in one FastAPI application process and successfully exposed both sets of routes.

The observed state was:

```text
1 FastAPI process
+
AS route group
+
RS route group
=
working application
```

Therefore, for the purpose of understanding deployment boundaries:

```text
Process Boundary
    ≠
OAuth Role Boundary
```

The important qualification is that this is an architectural experiment. OAuth 2.0 defines the roles and their protocol responsibilities; it does not require a particular process layout. RFC 6749 explicitly discusses the AS and RS as roles and permits them to be the same server or separate entities. citeturn593962search0

---

# 19. What We Can Now Distinguish

After Experiments 01 and 02:

```text
Experiment 01

Same Container
Different Processes
```

```text
Experiment 02

Same Container
Same Process
```

Both cases retained:

```text
Authorization Server responsibility
Resource Server responsibility
```

This gives us a useful hierarchy:

```text
OAuth Role
    ↓
logical responsibility

Process
    ↓
execution boundary

Container
    ↓
deployment boundary
```

A deployment can change one boundary without automatically changing the logical OAuth roles represented by the application.

---

# 20. What This Experiment Does Not Prove

This experiment does not prove:

```text
AS and RS must be implemented in one process.

AS and RS should be combined in production.

AS and RS have identical security responsibilities.

The OAuth protocol treats AS and RS as the same role.

A single process is always architecturally preferable.
```

The experiment proves only the narrower implementation fact that the two role responsibilities can be represented by separate route modules within one FastAPI process in this Lab.

---

# 21. Why `03-shared-database` Is a Different Experiment

The current experiment changes runtime execution:

```text
2 processes
    ↓
1 process
```

The next experiment changes persistence topology instead:

```text
AS + RS
    ↓
shared PostgreSQL database
```

That is a different variable and therefore requires a different experiment rather than being inferred from this result.

---

# 22. Reproduction

From:

```text
labs/01-oauth/02-roles/experiments/02-same-process/
```

run:

```bash
docker compose build --no-cache
docker compose up
```

Verify the stack:

```bash
docker compose ps
```

Verify the AS route:

```bash
curl http://127.0.0.1:8200/oauth/health
```

Verify the RS health route:

```bash
curl http://127.0.0.1:8200/api/health
```

Verify the RS resource:

```bash
curl http://127.0.0.1:8200/api/profile
```

Verify the single FastAPI process:

```bash
docker compose exec server sh -c \
'for p in /proc/[0-9]*; do
    cmd=$(tr "\\0" " " < "$p/cmdline" 2>/dev/null)
    case "$cmd" in
        *fastapi*|*uvicorn*)
            printf "%s: %s\\n" "${p#/proc/}" "$cmd"
            ;;
    esac
done'
```

Open the Client:

```text
http://localhost:5273
```

---

# 23. Cleanup

After completing the experiment:

```bash
docker compose down --rmi all --volumes --remove-orphans
```

This removes resources created by this Compose project without using a global Docker cleanup command that could affect unrelated projects.

---

# 24. Official Sources Used

```text
IETF RFC 6749 — The OAuth 2.0 Authorization Framework
https://www.rfc-editor.org/rfc/rfc6749.html

Relevant points:
- OAuth defines four primary roles.
- The Authorization Server and Resource Server are logical protocol roles.
- The Authorization Server may be the same server as the Resource Server
  or a separate entity.
- The specification does not prescribe a Unix-process or container topology.


FastAPI — Bigger Applications / APIRouter
https://fastapi.tiangolo.com/tutorial/bigger-applications/

Relevant points:
- APIRouter supports modular route organization.
- Routers can be included into one FastAPI application.
- This experiment uses that model to keep role-specific route modules
  while running one FastAPI application process.


FastAPI — FastAPI in Containers
https://fastapi.tiangolo.com/deployment/docker/

Relevant points:
- Containerizing a FastAPI application with the official Python base image.
- Installing requirements before copying application code.
- Using `fastapi run` to serve the application.
- Using exec-form CMD for correct process and shutdown behavior.
- A container can contain subprocesses, although a single main process
  is the normal model.


Docker — Run multiple processes in a container
https://docs.docker.com/engine/containers/multi-service_container/

Relevant points:
- Containers can run multiple processes.
- One service per container is the general recommendation.
- Multi-process containers are possible when there is a specific reason.


Docker Compose Specification
https://docs.docker.com/reference/compose-file/

Relevant to:
- service definitions
- build contexts
- published ports
- environment configuration


Vite — Env Variables and Modes
https://vite.dev/guide/env-and-mode

Relevant points:
- `VITE_*` variables are exposed to client-side code.
- `VITE_API_BASE_URL` is therefore appropriate for a public API base URL,
  but must never contain a secret.
```

---

# 25. Final Experiment Record

```text
Experiment: 02-same-process

Question
    Can AS + RS responsibilities exist in one process?

Implementation
    ✅ One FastAPI application
    ✅ Two APIRouter modules
    ✅ One server container
    ✅ One FastAPI process

Authorization Server responsibility
    ✅ /oauth/health

Resource Server responsibility
    ✅ /api/health
    ✅ /api/profile

Client
    ✅ Separate container
    ✅ Host port 5273
    ✅ Requests /api/profile

Runtime evidence
    ✅ One FastAPI process observed
    ✅ AS route works
    ✅ RS routes work
    ✅ Client renders RS response

Learning result
    ✅ Process boundary is not the definition of the OAuth role

Result: PASS
```
