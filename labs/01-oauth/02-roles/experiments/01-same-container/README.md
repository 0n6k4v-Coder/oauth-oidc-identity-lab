# Experiment 01 — Same Container

> **Lab:** OAuth 2.0 Roles (`01-oauth/02-roles`)  
> **Experiment:** `01-same-container`  
> **Status:** Completed

---

## 1. Objective

Determine whether the **Authorization Server** and **Resource Server** must occupy separate Docker containers in order to remain distinct OAuth roles.

The experiment deliberately changes only the container boundary while keeping the two server processes separate.

### Target topology

```text
Docker Host
│
├── Client Container
│   └── React / Vite
│
└── Server Container
    ├── Process 1 → Authorization Server :9000
    └── Process 2 → Resource Server :8000
```

The experiment is designed to establish these runtime facts:

```text
Authorization Server
    +
Resource Server
        ↓
Same Container
```

while also preserving:

```text
Authorization Server
    ≠
Resource Server
```

and:

```text
Process 1
    ≠
Process 2
```

---

## 2. What Is Being Changed

The original Lab 02 layout represents the roles as independent application components.

This experiment changes their deployment boundary:

```text
Before

AS → separate container
RS → separate container


After

AS ──┐
     ├── same container
RS ──┘
```

The **process boundary is intentionally not removed**.

That makes this experiment different from the next experiment, `02-same-process`.

---

# 3. Experiment Structure

```text
01-same-container/
├── Dockerfile
├── docker-compose.yml
├── run-services.sh
├── README.md
│
└── src/
    ├── authorization-server/
    │   ├── app/
    │   │   └── main.py
    │   ├── tests/
    │   │   └── test_health.py
    │   └── requirements.txt
    │
    ├── resource-server/
    │   ├── app/
    │   │   └── main.py
    │   ├── tests/
    │   │   └── test_profile.py
    │   └── requirements.txt
    │
    └── client/
        ├── Dockerfile
        ├── package.json
        ├── package-lock.json
        └── src/
```

The combined server image copies the Authorization Server and Resource Server application code into one image and starts them as separate FastAPI processes.

---

# 4. Implementation

## 4.1 Combined Server Image

`Dockerfile` builds one server image containing both backend applications.

The image exposes both ports:

```text
8000 → Resource Server
9000 → Authorization Server
```

Dependencies are installed from the two existing application requirement files.

The image uses the official Python 3.14 image and Bash for the wrapper script.

---

## 4.2 Multiple Processes

`run-services.sh` starts two independent FastAPI processes:

```text
fastapi run /code/authorization-server/app/main.py ... --port 9000

fastapi run /code/resource-server/app/main.py ... --port 8000
```

The processes run in the background and the wrapper tracks their process IDs.

The observed runtime state was:

```text
PID 7
→ FastAPI
→ Authorization Server
→ :9000

PID 8
→ FastAPI
→ Resource Server
→ :8000
```

Both processes were observed inside the same `server-1` container.

Docker's official documentation permits multiple processes in one container, while noting that one service per container remains the usual best practice. This experiment intentionally uses the multi-process pattern because demonstrating the container/process distinction is the learning objective.

---

## 4.3 Client Container

The React Client remains a separate container.

It runs Vite on:

```text
:5173
```

The Client's `VITE_API_BASE_URL` points to:

```text
http://127.0.0.1:8000
```

The Client therefore continues to request the Resource Server endpoint rather than the Authorization Server.

---

# 5. Execution

Start the experiment from this directory:

```bash
docker compose up
```

The expected container state is:

```text
client-1  → Up
server-1  → Up
```

The actual run produced:

```text
01-same-container-client-1   → 5173
01-same-container-server-1   → 8000, 9000
```

The server container successfully started both FastAPI applications:

```text
Authorization Server → http://0.0.0.0:9000
Resource Server      → http://0.0.0.0:8000
```

Both applications reached:

```text
Application startup complete.
```

---

# 6. Verification

## 6.1 Container-Level Verification

The command:

```bash
docker compose ps
```

showed two containers:

```text
01-same-container-client-1
01-same-container-server-1
```

The server container exposes both backend ports:

```text
0.0.0.0:8000->8000/tcp
0.0.0.0:9000->9000/tcp
```

This establishes that the two backend roles share the same container deployment.

---

## 6.2 Process-Level Verification

The container initially did not provide the `ps` utility, so process inspection was performed through `/proc`.

The observed process table was:

```text
1: /bin/bash /code/run-services.sh

7: /usr/local/bin/python3.14
   /usr/local/bin/fastapi run
   /code/authorization-server/app/main.py
   --host 0.0.0.0
   --port 9000

8: /usr/local/bin/python3.14
   /usr/local/bin/fastapi run
   /code/resource-server/app/main.py
   --host 0.0.0.0
   --port 8000
```

Therefore:

```text
AS PID = 7
RS PID = 8

7 ≠ 8
```

while both were observed inside the same container.

Final topology evidence:

```text
server-1
│
├── PID 7 → Authorization Server :9000
└── PID 8 → Resource Server      :8000
```

---

## 6.3 Authorization Server Verification

The following endpoint returned successfully:

```text
GET http://127.0.0.1:9000/health
```

Observed response:

```json
{
  "status": "ok",
  "service": "authorization-server",
  "role": "authorization_server"
}
```

The Authorization Server was therefore running independently within the combined container.

---

## 6.4 Resource Server Verification

The following endpoint returned successfully:

```text
GET http://127.0.0.1:8000/health
```

Observed response:

```json
{
  "status": "ok"
}
```

The protected-resource endpoint also returned successfully:

```text
GET http://127.0.0.1:8000/api/profile
```

Observed response:

```json
{
  "id": "demo-user",
  "display_name": "Lab User",
  "resource": "protected"
}
```

---

## 6.5 Client Verification

The React Client was accessible at:

```text
http://localhost:5173
```

The rendered result was:

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

---

## 6.6 Client → Resource Server Verification

After the Client was loaded, the Resource Server logged:

```text
172.19.0.1:51282 - "GET /api/profile HTTP/1.1" 200 OK
```

This proves that the Client continued to communicate with the Resource Server successfully after the Authorization Server and Resource Server were placed in the same container.

The Authorization Server was not involved in this request.

---

## 6.7 Independent Endpoint Verification Inside the Container

Both backend endpoints were also queried from inside the combined server container using Python's standard library HTTP client.

Observed:

```text
AS: {"status":"ok","service":"authorization-server","role":"authorization_server"}
RS: {"status":"ok"}
```

This confirms that both role-specific applications remained independently addressable inside the same container.

---

# 7. Observed Result

The experiment produced the following verified state:

```text
                    Docker
                      │
              ┌───────┴────────┐
              │ Server         │
              │ Container      │
              │                │
              │ PID 7 → AS     │ :9000
              │ PID 8 → RS     │ :8000
              └────────────────┘
```

Verified:

```text
AS + RS in same container       ✅
AS + RS remain separate processes ✅
AS endpoint works               ✅
RS endpoint works               ✅
Client → RS still works         ✅
AS involved in Client → RS      ❌
```

---

# 8. Learning Result

The experiment demonstrates from actual runtime behavior that the **container boundary is not the boundary that defines the OAuth role**.

The two applications can share one container while remaining separate processes with distinct endpoint responsibilities.

Therefore:

```text
OAuth Role Boundary
        ≠
Container Boundary
```

and independently:

```text
Container Boundary
        ≠
Process Boundary
```

The next experiment will intentionally remove the process boundary as well.

---

# 9. What This Experiment Does Not Prove

This experiment does not prove that:

```text
AS + RS can be the same process
```

because they are still separate processes.

It also does not prove anything about shared database architecture because no database is used here.

Those are separate experiments.

---

# 10. Official Sources

```text
Docker — Run multiple processes in a container
https://docs.docker.com/engine/containers/multi-service_container/

Used for:
- wrapper-script approach
- multi-process container behavior
- process lifecycle considerations


FastAPI — FastAPI in Containers
https://fastapi.tiangolo.com/deployment/docker/

Used for:
- official FastAPI container pattern
- Python 3.14 container base
- requirements installation
- `fastapi run`
- containerized FastAPI application execution


Docker Compose Specification
https://docs.docker.com/reference/compose-file/

Used for:
- Compose service definition
- port publishing
- build configuration


Vite — Env Variables and Modes
https://vite.dev/guide/env-and-mode

Used for:
- `VITE_API_BASE_URL`
- client-side environment configuration
```

---

# 11. Final Status

```text
Experiment 01 — Same Container

Implementation      ✅
Container runtime   ✅
AS verification     ✅
RS verification     ✅
Process verification ✅
Client verification ✅
Client → RS          ✅
Same-container proof ✅
Different-process proof ✅

Result: PASS
```
