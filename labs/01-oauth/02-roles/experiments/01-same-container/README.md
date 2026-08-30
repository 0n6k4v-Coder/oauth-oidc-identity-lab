# Experiment 01 — Same Container

> **Lab:** `01-oauth/02-roles`  
> **Experiment:** `01-same-container`  
> **Status:** Completed  
> **Focus:** Container boundary vs process boundary vs OAuth role boundary

---

## 1. What This Experiment Is Trying to Answer

This experiment asks a very specific architectural question:

> If the Authorization Server and Resource Server are placed inside the **same Docker container**, do they stop being separate OAuth roles?

The experiment is deliberately narrower than a general discussion about monoliths, microservices, or production architecture.

We are testing one deployment boundary:

```text
Container boundary
```

while deliberately preserving another:

```text
Process boundary
```

The target state is therefore:

```text
One Container
├── Authorization Server process
└── Resource Server process
```

The expected learning point is not merely that “Docker can run two processes.” The purpose is to observe that the two applications can share a container while still being implemented as distinct server processes with distinct endpoint responsibilities.

---

# 2. Experimental Variable

The experiment changes the **container topology** while preserving the **application responsibilities**.

Conceptually:

```text
Separate deployment components

Authorization Server → own container
Resource Server      → own container
```

becomes:

```text
Combined deployment component

One server container
├── Authorization Server process
└── Resource Server process
```

We intentionally do **not** combine the processes.

Therefore this experiment isolates:

```text
Container boundary
```

from:

```text
Process boundary
```

That distinction is important because the next experiment, `02-same-process`, changes the process boundary as well.

---

# 3. Experimental Hypothesis

The hypothesis tested by this experiment is:

```text
Changing the container boundary
will not change the logical OAuth role
performed by each application.
```

More concretely:

```text
Same Container
    +
Separate Processes
    +
Separate Endpoint Responsibilities
    ↓
Authorization Server and Resource Server
remain distinct roles
```

---

# 4. Files Created for the Experiment

The experiment required four new containerization files in addition to the copied application source:

```text
01-same-container/
├── Dockerfile
├── docker-compose.yml
├── run-services.sh
│
└── src/
    └── client/
        └── Dockerfile
```

The application source was copied from the Lab 02 baseline so that this experiment could be run independently without importing code from the baseline at runtime.

The important implementation split is:

```text
Dockerfile
    → builds the combined backend image

run-services.sh
    → starts the two backend processes

docker-compose.yml
    → defines the client and combined-server containers

src/client/Dockerfile
    → builds and runs the React/Vite client container
```

---

# 5. Combined Server Implementation

## 5.1 Dockerfile

The combined server image uses:

```text
python:3.14-slim
```

and installs Bash because the container entrypoint is a shell wrapper.

The Dockerfile then copies both backend dependency manifests:

```text
src/authorization-server/requirements.txt
src/resource-server/requirements.txt
```

and installs them into the same Python environment.

The two backend applications are then copied into different directories inside the same image:

```text
/code/authorization-server/app
/code/resource-server/app
```

Both ports are exposed:

```text
8000 → Resource Server
9000 → Authorization Server
```

Finally, the image uses:

```text
/code/run-services.sh
```

as its container command.

### Why this matters

The experiment is not simulating two applications merely by renaming directories. Both applications are physically present in the same container image and are launched as separate processes at runtime.

---

# 6. Multiple Processes in One Container

The central implementation mechanism is `run-services.sh`.

It starts:

```text
fastapi run /code/authorization-server/app/main.py
    → port 9000
```

and:

```text
fastapi run /code/resource-server/app/main.py
    → port 8000
```

Each command runs in the background and its process ID is captured:

```text
AUTH_PID
RESOURCE_PID
```

The wrapper also installs signal handling so the child processes are terminated when the container receives `SIGTERM` or `SIGINT`.

The script waits for either child process to exit and then terminates the remaining process.

### Why this implementation is significant

A single container is therefore not being treated as a single process.

The runtime model is explicitly:

```text
Container
│
├── Wrapper process
│
├── AS process
│
└── RS process
```

This is exactly the property that the experiment needs to observe.

Docker's official documentation explains that a container can run multiple processes, while noting that one service per container is the normal recommendation. This experiment intentionally uses multiple processes because the learning objective is to distinguish a container boundary from a process boundary.

---

# 7. Client Container

The React Client remains separate from the combined backend container.

Its Dockerfile:

```text
node:24-alpine
```

installs the existing Node dependencies with:

```text
npm ci
```

and starts Vite using:

```text
npm run dev -- --host 0.0.0.0
```

The published port is:

```text
5173
```

The Compose configuration sets:

```text
VITE_API_BASE_URL=http://127.0.0.1:8000
```

The Client code then requests:

```text
${API_BASE_URL}/api/profile
```

which is the Resource Server endpoint.

This is intentionally unchanged from the existing Client behavior: the experiment changes the backend deployment topology without introducing a new OAuth interaction.

---

# 8. Compose Topology

`docker-compose.yml` defines two containers:

```text
client
server
```

The important topology is:


```text
Docker Host
│
├── client container
│   └── React / Vite :5173
│
└── server container
    ├── Authorization Server process :9000
    └── Resource Server process      :8000
```

The server container publishes both backend ports:

```text
0.0.0.0:8000 → container:8000
0.0.0.0:9000 → container:9000
```

This means the two roles share one container lifecycle and one container identity even though they retain separate listening ports and separate processes.

---

# 9. Execution Procedure

The experiment was started from:

```text
labs/01-oauth/02-roles/experiments/01-same-container/
```

with:

```bash
docker compose up
```

The Compose runtime created:

```text
01-same-container-client-1
01-same-container-server-1
```

The Client container started Vite:

```text
VITE v8.2.2 ready
Local: http://localhost:5173/
```

The server container started both backend applications:

```text
Authorization Server
→ http://0.0.0.0:9000

Resource Server
→ http://0.0.0.0:8000
```

Both reached:

```text
Application startup complete.
```

---

# 10. Container-Level Evidence

The command:

```bash
docker compose ps
```

returned:

```text
NAME                         IMAGE                      COMMAND                  SERVICE   CREATED          STATUS          PORTS
01-same-container-client-1   01-same-container-client   "docker-entrypoint.s…"   client    ...              Up              0.0.0.0:5173->5173/tcp
01-same-container-server-1   01-same-container-server   "/code/run-services.…"   server    ...              Up              0.0.0.0:8000->8000/tcp, 0.0.0.0:9000->9000/tcp
```

The important observation is:

```text
One server container
    ↓
Two backend ports
    ↓
8000 and 9000
```

There is no separate Authorization Server container and no separate Resource Server container in this experiment.

---

# 11. Process-Level Evidence

The minimal Python image did not contain the `ps` command, so installing a process-inspection utility was unnecessary.

Instead, the Linux `/proc` filesystem was inspected from inside the server container.

The observed process table was:

```text
1: /bin/bash /code/run-services.sh

7: /usr/local/bin/python3.14 /usr/local/bin/fastapi run /code/authorization-server/app/main.py --host 0.0.0.0 --port 9000

8: /usr/local/bin/python3.14 /usr/local/bin/fastapi run /code/resource-server/app/main.py --host 0.0.0.0 --port 8000
```

This provides direct evidence of two distinct backend processes:

```text
AS PID = 7
RS PID = 8

7 ≠ 8
```

Both were observed from inside:

```text
01-same-container-server-1
```

Therefore the actual runtime topology was:

```text
server container
│
├── PID 7 → Authorization Server :9000
└── PID 8 → Resource Server      :8000
```

This is stronger evidence than simply observing two open ports because it proves that the two services are separate processes rather than two endpoints of one process.

---

# 12. Authorization Server Verification

The following request was made:

```http
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

This confirms that the Authorization Server process is independently running and responding on its own endpoint.

It does **not** indicate that an OAuth authorization flow exists yet.

The current Authorization Server remains intentionally minimal for this Lab.

---

# 13. Resource Server Verification

The following request was made:

```http
GET http://127.0.0.1:8000/health
```

Observed response:

```json
{
  "status": "ok"
}
```

The resource endpoint was then accessed:

```http
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

This confirms that the Resource Server process remained independently functional after being combined into the same container as the Authorization Server.

---

# 14. Client Verification

The Client was opened at:

```text
http://localhost:5173
```

The rendered application was:

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

The page therefore received the Resource Server response successfully.

---

# 15. Client → Resource Server Evidence

After loading the Client, the Resource Server emitted:

```text
172.19.0.1:51282 - "GET /api/profile HTTP/1.1" 200 OK
```

This is direct server-side evidence that the Client reached the Resource Server endpoint and received a successful HTTP response.

The request path was:

```text
Browser
   ↓
React Client
   ↓
GET /api/profile
   ↓
Resource Server process :8000
   ↓
200 OK
```

The Authorization Server process was not part of this request.

This is important because the experiment is about deployment topology, not about introducing a new OAuth flow.

---

# 16. Independent Endpoint Verification From Inside the Container

To verify that sharing one container did not collapse the two server responsibilities into one endpoint namespace, both services were queried from inside the combined server container using Python's standard-library HTTP client.

Observed output:

```text
AS: {"status":"ok","service":"authorization-server","role":"authorization_server"}
RS: {"status":"ok"}
```

This demonstrates that both applications remained independently addressable from within the same container:

```text
127.0.0.1:9000 → Authorization Server
127.0.0.1:8000 → Resource Server
```

---

# 17. What Actually Changed

The experiment changed exactly one architectural boundary:

```text
Container boundary
```

It did not change:

```text
OAuth roles
Endpoint responsibilities
Application source responsibilities
Process separation
Client → Resource Server behavior
```

The final runtime state was:

```text
                    Docker Host
                         │
             ┌───────────┴───────────┐
             │                       │
       Client Container        Server Container
             │                       │
       React / Vite             ┌────┴────┐
           :5173                │         │
                                │         │
                          AS Process   RS Process
                             :9000        :8000
```

---

# 18. Learning Outcome

The experiment gives us an evidence-based answer to the original question:

> Does placing the Authorization Server and Resource Server in the same container make them the same OAuth role?

**No.**

The observed system contained:

```text
1 server container
2 backend processes
2 backend endpoints
2 distinct application responsibilities
```

The Authorization Server continued to behave as the Authorization Server component, while the Resource Server continued to behave as the Resource Server component.

Therefore:

```text
OAuth Role Boundary
        ≠
Container Boundary
```

The experiment also establishes a second distinction:

```text
Container Boundary
        ≠
Process Boundary
```

A container can contain more than one process, and changing the container boundary does not automatically change the process boundary.

---

# 19. What We Have Proven vs What We Have Not Proven

## Proven by this experiment

```text
AS can run in the same container as RS.

AS and RS can remain separate processes inside that container.

AS and RS can retain separate ports/endpoints.

The Client can continue to reach the Resource Server.

The Authorization Server does not have to participate in the current Client → RS request.
```

## Not proven by this experiment

```text
AS and RS can run in the same process.

AS and RS should share a database.

AS and RS should be deployed as a production monolith.

AS and RS can be placed on different physical hosts.
```

Those questions require separate experiments and should not be inferred from this result.

---

# 20. Why the Next Experiment Is Different

`02-same-process` changes a different runtime property.

Current experiment:

```text
1 Container
2 Processes
```

Next experiment:

```text
1 Container
1 Process
```

The process boundary will therefore be removed deliberately.

That creates a new observable question:

> Can two OAuth role responsibilities exist inside one application process without becoming the same role?

That is a genuinely different experiment from this one.

---

# 21. Official Sources

```text
Docker — Run multiple processes in a container
https://docs.docker.com/engine/containers/multi-service_container/

Relevant because this experiment intentionally runs two server processes
inside one container and uses a wrapper script to coordinate them.


Docker — Dockerfile reference
https://docs.docker.com/reference/dockerfile/

Relevant to the image construction used for the combined server and
client containers.


Docker Compose Specification
https://docs.docker.com/reference/compose-file/

Relevant to the service definitions, build contexts, environment values,
and published ports used by this experiment.


FastAPI — FastAPI CLI
https://fastapi.tiangolo.com/fastapi-cli/

Relevant to the `fastapi run` commands used to launch the two backend
applications.


FastAPI — FastAPI in Containers
https://fastapi.tiangolo.com/deployment/docker/

Relevant to the containerized FastAPI application pattern and dependency
installation approach.


Vite — Env Variables and Modes
https://vite.dev/guide/env-and-mode

Relevant to the `VITE_API_BASE_URL` value consumed by the React Client.


IETF RFC 6749 — The OAuth 2.0 Authorization Framework
https://www.rfc-editor.org/rfc/rfc6749.html

Relevant to the distinction between the Authorization Server and Resource
Server as logical OAuth roles and to the fact that those roles are not
definitions of container boundaries.
```

---

# 22. Final Result

```text
Experiment: 01-same-container

Implementation                 ✅
Docker Compose startup         ✅
Client container               ✅
Combined server container      ✅
Authorization Server process   ✅
Resource Server process        ✅
Same container                 ✅
Different processes            ✅
Distinct AS endpoint           ✅
Distinct RS endpoint           ✅
Client → Resource Server       ✅
Authorization Server in that
Client → RS request            ❌ intentionally not involved

RESULT: PASS
```

The experiment successfully demonstrated the intended relationship:

```text
OAuth Roles
    ↓
remain logically distinct

while

Container Boundary
    ↓
can be shared

and

Process Boundary
    ↓
can remain separate
```
