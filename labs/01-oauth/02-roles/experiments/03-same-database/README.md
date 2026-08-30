# Experiment 03 — Same Database

> **Lab:** `01-oauth/02-roles`  
> **Experiment:** `03-same-database`  
> **Status:** Completed  
> **Focus:** Shared database boundary vs OAuth role boundary

---

## 1. Experiment Question

This experiment asks:

> Can the Authorization Server and Resource Server remain separate OAuth roles and separate application processes while using the **same PostgreSQL database**?

The experiment intentionally changes the persistence boundary while keeping the application/runtime boundaries separate.

Target topology:

```text
Docker Host
│
├── Client container
│   └── Vite :5173
│
├── Authorization Server container
│   └── FastAPI :8300
│
├── Resource Server container
│   └── FastAPI :8400
│
└── PostgreSQL container
    └── PostgreSQL 18.6 :5432
```

The important relationship is:

```text
Authorization Server ──┐
                       ├── PostgreSQL database: lab_roles
Resource Server ───────┘
```

while the two server applications remain separate containers and separate processes.

---

# 2. Learning Objective

The purpose is to distinguish three different concepts:

```text
OAuth role
Process boundary
Database boundary
```

The experiment is designed to demonstrate that:

```text
Database Boundary
    ≠
OAuth Role Boundary
```

and specifically that two independently running server applications can connect to the same PostgreSQL database without becoming one application or one OAuth role.

This is an architectural observation from the experiment, not a claim that a shared database is required or preferred for OAuth deployments.

RFC 6749 defines the Authorization Server and Resource Server as OAuth roles and states that the authorization server may be the same server as the resource server or a separate entity. The specification does not define a Unix process or database deployment boundary for those roles. citeturn0search0

---

# 3. Experimental Variable

The experiment keeps the following boundaries separate:

```text
Application boundary
    → separate

Container boundary
    → separate

Process boundary
    → separate
```

and intentionally makes only this boundary shared:

```text
Database boundary
    → shared
```

Conceptually:

```text
Before / conceptual independent systems

AS → separate application/process
RS → separate application/process


Experiment

AS application/process ──┐
                         ├── same PostgreSQL database
RS application/process ──┘
```

This isolation is important. If the experiment also merged the containers or processes, we would no longer know whether an observed result came from the shared database or from another topology change.

---

# 4. Why This Is a Real Database Experiment

Simply putting the same `DATABASE_URL` into two environment blocks would only demonstrate configuration similarity.

This experiment therefore performs real database operations:

```text
Authorization Server
    ↓
PostgreSQL
    ↓
SELECT current_database() / SELECT 1
```

and:

```text
Resource Server
    ↓
PostgreSQL
    ↓
SELECT from resource.profiles
```

The Resource Server's `/api/profile` endpoint reads the profile from PostgreSQL instead of returning the profile directly from Python constants.

The database is therefore part of the application's runtime behavior, not merely part of the Docker topology.

---

# 5. Experiment Directory

```text
03-same-database/
├── README.md
├── docker-compose.yml
│
├── database/
│   └── init/
│       └── 001-init.sql
│
└── src/
    ├── authorization-server/
    │   ├── Dockerfile
    │   ├── requirements.txt
    │   ├── app/
    │   │   ├── __init__.py
    │   │   ├── database.py
    │   │   └── main.py
    │   └── tests/
    │       └── test_health.py
    │
    ├── resource-server/
    │   ├── Dockerfile
    │   ├── requirements.txt
    │   ├── app/
    │   │   ├── __init__.py
    │   │   ├── database.py
    │   │   └── main.py
    │   └── tests/
    │       └── test_profile.py
    │
    └── client/
        ├── Dockerfile
        ├── package.json
        ├── package-lock.json
        └── src/
            ├── App.jsx
            └── api/
                └── profile.js
```

---

# 6. PostgreSQL Version and Container

The database image is pinned to:

```text
postgres:18.6
```

This experiment deliberately pins the exact PostgreSQL patch version rather than using a moving major tag.

PostgreSQL initializes the database using the official image's initialization mechanism:

```text
/docker-entrypoint-initdb.d/001-init.sql
```

The Compose configuration mounts persistent PostgreSQL storage at:

```text
/var/lib/postgresql
```

which follows the PostgreSQL 18+ official image layout.

The official PostgreSQL image documents environment variables for initial database/user creation and execution of initialization scripts when the database cluster is initialized. citeturn0search1

---

# 7. Database Initialization

`database/init/001-init.sql` creates one PostgreSQL database containing two logical schemas:

```text
lab_roles
│
├── authz
│   └── authorizations
│
└── resource
    └── profiles
```

The SQL creates:

```sql
CREATE SCHEMA IF NOT EXISTS authz;
CREATE SCHEMA IF NOT EXISTS resource;
```

The `authz` schema stores authorization-related seed data:

```text
subject_id = demo-user
permission = read:profile
```

The `resource` schema stores the profile used by the Resource Server:

```text
id           = demo-user
display_name = Lab User
```

The two schemas are intentionally separate even though they reside in the same PostgreSQL database.

This demonstrates:

```text
Same physical database
    +
Separate logical namespaces
```

PostgreSQL documents schemas as namespaces within a database and supports qualified object names such as `schema.table`. citeturn0search2

---

# 8. Database Schema Design

The authorization data table is:

```text
authz.authorizations
├── id
├── subject_id
└── permission
```

The resource data table is:

```text
resource.profiles
├── id
└── display_name
```

The important design decision is that AS and RS do **not** share one table simply because they share one database.

The experiment therefore distinguishes:

```text
Database sharing
        ≠
Table sharing
        ≠
Data ownership sharing
```

This is useful because a shared database does not inherently require every application to read and write every table.

---

# 9. Application Database Access

Both server applications use SQLAlchemy and Psycopg.

Their dependency manifests contain:

```text
fastapi[standard]
sqlalchemy
psycopg[binary]
pytest
httpx2
```

The `psycopg[binary]` package is used because the application runs in `python:3.14-slim`; Psycopg documents the binary installation option as a convenient way to install the driver together with the required client library components. citeturn0search3

Both applications construct a SQLAlchemy engine from:

```text
DATABASE_URL
```

using the PostgreSQL/Psycopg URL form:

```text
postgresql+psycopg://...
```

SQLAlchemy documents the PostgreSQL dialect and Psycopg connection URL forms for SQLAlchemy 2.x. citeturn0search4

---

# 10. Authorization Server Database Usage

The Authorization Server receives:

```text
DATABASE_URL=postgresql+psycopg://lab_user:lab_password@db:5432/lab_roles
```

The `/health` endpoint performs:

```sql
SELECT 1
```

before returning the health response.

This means a successful health response now proves more than FastAPI startup:

```text
Authorization Server
    ↓
SQLAlchemy Engine
    ↓
Psycopg
    ↓
PostgreSQL
    ↓
SELECT 1
    ↓
success
```

The `/database-check` endpoint executes:

```sql
SELECT current_database()
```

and returns the database name observed by the AS process.

Expected result:

```json
{
  "service": "authorization-server",
  "database": "lab_roles"
}
```

---

# 11. Resource Server Database Usage

The Resource Server receives the same database URL:

```text
postgresql+psycopg://lab_user:lab_password@db:5432/lab_roles
```

Its `/health` endpoint also executes:

```sql
SELECT 1
```

The significant difference is `/api/profile`.

Instead of constructing the profile directly in Python, it executes:

```sql
SELECT id, display_name
FROM resource.profiles
WHERE id = :id
```

with:

```text
:id = demo-user
```

The response is then constructed from the returned database row:

```text
PostgreSQL row
    ↓
SQLAlchemy mapping
    ↓
Resource Server response
```

This makes the Resource Server response an observable consequence of the shared database state.

---

# 12. Docker Build Design

The Authorization Server and Resource Server each have their own Dockerfile.

Both use:

```text
python:3.14-slim
```

and copy their own:

```text
requirements.txt
app/
tests/
```

Their build contexts are intentionally independent:

```yaml
authorization-server:
  build:
    context: ./src/authorization-server

resource-server:
  build:
    context: ./src/resource-server
```

This preserves their application/container separation while allowing both to point to the same database service.

The official FastAPI container documentation demonstrates the general pattern of copying dependency definitions, installing dependencies, copying application code, and serving with `fastapi run`. citeturn0search5

---

# 13. Docker Compose Topology

The Compose file defines four services:

```text
1. db
2. authorization-server
3. resource-server
4. client
```

The final topology is:

```text
                         Docker Host
                              │
       ┌──────────────────────┼───────────────────────┐
       │                      │                       │
       ▼                      ▼                       ▼
 Client Container       AS Container            RS Container
    :5173                  :8300                   :8400
       │                      │                       │
       │                      └────────┐   ┌──────────┘
       │                               │   │
       │                               ▼   ▼
       │                         PostgreSQL
       │                         :5432
       │                             │
       │                         lab_roles
       │                         ├── authz
       │                         └── resource
       │
       └── browser access :5373
```

The host ports are deliberately isolated from earlier experiments:

```text
Client → 5373
AS     → 8300
RS     → 8400
DB     → 15432
```

Inside the Compose network, AS and RS connect to:

```text
db:5432
```

not to the host-published `15432` port.

Docker Compose uses service names for inter-service networking on the Compose network. citeturn0search6

---

# 14. Database Health Dependency

The database service includes a healthcheck based on:

```text
pg_isready -U lab_user -d lab_roles
```

The AS and RS use:

```yaml
depends_on:
  db:
    condition: service_healthy
```

The important reason for this is that the applications require an actual PostgreSQL connection, not merely a container that has started.

The intended startup sequence is:

```text
PostgreSQL container starts
        ↓
PostgreSQL accepts connections
        ↓
healthcheck = healthy
        ↓
AS / RS are allowed to start
```

---

# 15. Execution and Initialization

The experiment was started with:

```bash
docker compose up
```

The first successful initialization produced:

```text
PostgreSQL 18.6
```

followed by:

```text
running /docker-entrypoint-initdb.d/001-init.sql
```

and the SQL script reported:

```text
CREATE SCHEMA
CREATE SCHEMA
CREATE TABLE
CREATE TABLE
INSERT 0 1
INSERT 0 1
```

PostgreSQL then reported:

```text
database system is ready to accept connections
```

This establishes that the database was freshly initialized and that both schema/table creation and seed inserts completed successfully.

---

# 16. Important Initialization Detail

During development of this experiment, PostgreSQL initialization initially failed because the schema name `authorization` conflicted with PostgreSQL's reserved keyword `AUTHORIZATION`.

The schema was therefore renamed to:

```text
authz
```

The final SQL uses:

```text
authz.authorizations
```

rather than attempting to use `authorization` as an unquoted schema identifier.

This correction is important to the final experiment record because the final schema is the one actually initialized successfully.

PostgreSQL's keyword reference lists `AUTHORIZATION` as a reserved SQL keyword. citeturn0search7

---

# 17. PostgreSQL 18 Storage Layout Correction

The experiment also initially used the older PostgreSQL volume mount:

```text
/var/lib/postgresql/data
```

With PostgreSQL 18's official Docker image, this caused the image to detect an incompatible data-directory layout.

The volume was changed to:

```text
/var/lib/postgresql
```

After deleting the old experiment volume and starting again, PostgreSQL initialized successfully under:

```text
/var/lib/postgresql/18/docker
```

This final configuration is the one used by the completed experiment.

---

# 18. Runtime Verification — Container State

`docker compose ps` showed four running services with these published host ports:

```text
Client
0.0.0.0:5373 → 5173

Authorization Server
0.0.0.0:8300 → 8300

Resource Server
0.0.0.0:8400 → 8400

PostgreSQL
0.0.0.0:15432 → 5432
```

This demonstrates that AS and RS remained separate runtime containers even though they share PostgreSQL.

---

# 19. Runtime Verification — Authorization Server

The following endpoint was verified:

```text
GET http://127.0.0.1:8300/health
```

Observed response:

```json
{
  "status": "ok",
  "service": "authorization-server",
  "role": "authorization_server"
}
```

The database-backed health implementation also executes:

```sql
SELECT 1
```

so the successful request verifies both AS application startup and database connectivity.

The database identity was verified through:

```text
GET http://127.0.0.1:8300/database-check
```

which returns the current database name as `lab_roles`.

---

# 20. Runtime Verification — Resource Server

The following endpoint was verified:

```text
GET http://127.0.0.1:8400/health
```

Observed response:

```json
{
  "status": "ok"
}
```

The Resource Server also executes `SELECT 1` for this endpoint.

Its `/database-check` endpoint reports the PostgreSQL database name observed by the RS process.

The `/api/profile` endpoint performs the real data query against:

```text
resource.profiles
```

and returned:

```json
{
  "id": "demo-user",
  "display_name": "Lab User",
  "resource": "protected"
}
```

The important change from earlier experiments is that this profile is now retrieved from PostgreSQL.

---

# 21. Runtime Verification — Database Contents

The PostgreSQL container was entered using:

```bash
docker compose exec db psql -U lab_user -d lab_roles
```

Once inside `psql`, database commands were executed directly.

For example:

```sql
SELECT current_database();
```

and schema/table inspection commands such as:

```text
\dn
```

and queries against:

```text
authz.authorizations
resource.profiles
```

The initialized database contained the two expected logical schemas and the seeded records.

This provides direct database-side evidence for the application-side observations.

---

# 22. Runtime Verification — Client

The Client was published on the dedicated host port:

```text
http://localhost:5373
```

The Client code reads:

```javascript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
```

and requests:

```text
/api/profile
```

The experiment configures:

```text
VITE_API_BASE_URL=http://127.0.0.1:8400
```

Therefore the browser request is:

```text
http://127.0.0.1:8400/api/profile
```

CORS was configured specifically for:

```text
http://localhost:5373
```

because the page origin includes its port and therefore differs from the earlier Client origin used by previous experiments.

Vite documents `VITE_*` variables as client-exposed values, so this variable is suitable for a public API URL but must not contain a secret. citeturn0search8

---

# 23. Why the Client Still Talks Only to the Resource Server

The Client makes:

```text
GET /api/profile
```

to:

```text
127.0.0.1:8400
```

It does not call the Authorization Server.

Therefore the current Client flow is still:

```text
Browser
   ↓
Client
   ↓
Resource Server
   ↓
PostgreSQL
   ↓
resource.profiles
```

The Authorization Server separately connects to the same database:

```text
Authorization Server
   ↓
PostgreSQL
   ↓
lab_roles
```

This is deliberate. The experiment is testing database topology, not adding an OAuth authorization flow that the Lab has not implemented yet.

---

# 24. What the Experiment Actually Demonstrated

The final runtime system has:

```text
2 backend containers
2 backend processes
1 PostgreSQL database
```

More specifically:

```text
Authorization Server
    ✅ separate application
    ✅ separate container
    ✅ separate process
    ✅ connects to lab_roles

Resource Server
    ✅ separate application
    ✅ separate container
    ✅ separate process
    ✅ connects to lab_roles

PostgreSQL
    ✅ one database
    ✅ authz schema
    ✅ resource schema
```

The two applications can therefore share the same PostgreSQL database without becoming the same runtime process or the same logical OAuth role.

---

# 25. Security Boundary Observation

The experiment also reveals an important distinction that is **not fully implemented as a security isolation experiment yet**.

The completed Compose configuration gives both AS and RS the same database credentials:

```text
lab_user
```

Therefore the actual privilege model is currently:

```text
AS ──┐
     ├── same PostgreSQL role / credentials
RS ──┘
```

This proves shared database connectivity, but it does **not** prove least-privilege isolation between AS and RS.

A stronger production security design could instead use separate database roles and grants, for example:

```text
AS → authz_db_user
RS → resource_db_user
```

with permissions restricted to the relevant schemas/tables.

PostgreSQL's privilege system allows permissions to be granted at schema/table/object level. citeturn0search9

This distinction is important:

```text
Same Database
    ≠
Same Database User
    ≠
Same Database Privileges
```

The current experiment demonstrates the first relationship only.

---

# 26. What We Learned

The experiment answers the original question:

> Does sharing a PostgreSQL database force the Authorization Server and Resource Server to become one OAuth role?

**No.**

The experiment successfully ran:

```text
AS container/process
        ↓
     PostgreSQL
        ↑
RS container/process
```

while preserving separate:

```text
applications
containers
processes
endpoint responsibilities
```

Therefore:

```text
Database Boundary
    ≠
Process Boundary
    ≠
Container Boundary
    ≠
OAuth Role Boundary
```

The important lesson is that these are different architectural dimensions. They can be aligned in a deployment, but one boundary does not inherently define another.

---

# 27. What We Did Not Learn

This experiment does **not** establish that:

```text
Shared databases are recommended for OAuth systems.

AS and RS should use the same database in production.

AS and RS should use the same database credentials.

A shared database provides security isolation by itself.

OAuth requires either shared or separate database deployment.
```

Those questions require a different experiment or production architecture analysis.

---

# 28. Why This Experiment Is Different from Experiments 01 and 02

The three experiments now isolate different deployment boundaries:

### Experiment 01 — Same Container

```text
1 container
2 backend processes
```

Learning focus:

```text
Container boundary ≠ process boundary
```

### Experiment 02 — Same Process

```text
1 container
1 backend process
2 role responsibilities
```

Learning focus:

```text
Process boundary ≠ OAuth role boundary
```

### Experiment 03 — Same Database

```text
2 backend containers
2 backend processes
1 PostgreSQL database
```

Learning focus:

```text
Database boundary ≠ OAuth role boundary
```

Each experiment therefore changes a different architectural boundary rather than repeating the previous experiment under a new name.

---

# 29. Reproduction

From:

```text
labs/01-oauth/02-roles/experiments/03-same-database/
```

Start:

```bash
docker compose up
```

Check the services:

```bash
docker compose ps
```

Check Authorization Server:

```bash
curl http://127.0.0.1:8300/health
curl http://127.0.0.1:8300/database-check
```

Check Resource Server:

```bash
curl http://127.0.0.1:8400/health
curl http://127.0.0.1:8400/database-check
curl http://127.0.0.1:8400/api/profile
```

Check PostgreSQL directly:

```bash
docker compose exec db psql -U lab_user -d lab_roles
```

Then from `psql`:

```sql
SELECT current_database();
\dn
SELECT * FROM authz.authorizations;
SELECT * FROM resource.profiles;
```

Open the Client:

```text
http://localhost:5373
```

---

# 30. Cleanup

Remove the resources created by this experiment with:

```bash
docker compose down --rmi all --volumes --remove-orphans
```

This removes the experiment's containers, network, images, and PostgreSQL volume without using a global Docker prune that could affect unrelated projects.

---

# 31. Implementation Notes / Issues Encountered

Several issues occurred while building the experiment, and each one exposed a useful implementation detail.

### FastAPI standard dependencies

The backend image initially installed the wrong FastAPI package variant for `fastapi run`. The final dependency manifest uses:

```text
fastapi[standard]
```

which supplies the standard FastAPI CLI/runtime dependencies used by this experiment.

### Psycopg on `python:3.14-slim`

Plain `psycopg` was insufficient in the slim image because the pure-Python path still required PostgreSQL client library support. The final experiment uses:

```text
psycopg[binary]
```

### Python package imports

The server applications use package-relative imports such as:

```python
from .database import engine
```

and therefore require `app` to be a Python package through:

```text
app/__init__.py
```

The applications are served through the FastAPI CLI's discovered `app.main:app` import path.

### PostgreSQL 18 storage layout

The official PostgreSQL 18 container requires the updated persistent-data mount layout used by this experiment:

```text
/var/lib/postgresql
```

### SQL keyword collision

The original schema name `authorization` was invalid as an unquoted schema identifier because `AUTHORIZATION` is a reserved keyword. The final schema is `authz`.

These issues are retained here because the README is intended to record what was actually learned while performing the experiment, not only the final clean state.

---

# 32. Official Sources

```text
IETF RFC 6749 — The OAuth 2.0 Authorization Framework
https://www.rfc-editor.org/rfc/rfc6749.html

PostgreSQL 18 Documentation
https://www.postgresql.org/docs/18/

PostgreSQL 18 — CREATE TABLE
https://www.postgresql.org/docs/18/sql-createtable.html

PostgreSQL 18 — Schemas
https://www.postgresql.org/docs/18/ddl-schemas.html

PostgreSQL 18 — SQL Keywords
https://www.postgresql.org/docs/18/sql-keywords-appendix.html

PostgreSQL Official Docker Image
https://hub.docker.com/_/postgres

SQLAlchemy 2.0 Documentation
https://docs.sqlalchemy.org/en/20/

SQLAlchemy 2.0 — PostgreSQL Dialect
https://docs.sqlalchemy.org/en/20/dialects/postgresql.html

Psycopg 3 — Installation
https://www.psycopg.org/psycopg3/docs/basic/install.html

FastAPI — FastAPI in Containers
https://fastapi.tiangolo.com/deployment/docker/

Docker Compose Specification
https://docs.docker.com/reference/compose-file/

Docker Compose — Networking
https://docs.docker.com/compose/how-tos/networking/

Vite — Env Variables and Modes
https://vite.dev/guide/env-and-mode
```

---

# 33. Final Experiment Record

```text
Experiment: 03-same-database

Question
    Can AS and RS remain separate roles/processes while sharing one database?

Database
    ✅ PostgreSQL 18.6
    ✅ database: lab_roles
    ✅ authz schema
    ✅ resource schema
    ✅ initialization script executed successfully

Authorization Server
    ✅ separate container
    ✅ separate process
    ✅ database connectivity

Resource Server
    ✅ separate container
    ✅ separate process
    ✅ database connectivity
    ✅ /api/profile reads from PostgreSQL

Client
    ✅ separate container
    ✅ dedicated host port 5373
    ✅ Client → Resource Server works

Shared persistence
    ✅ AS → PostgreSQL
    ✅ RS → PostgreSQL
    ✅ same database

Security qualification
    ⚠️ AS and RS currently use the same database credentials
    ⚠️ least-privilege database isolation was not tested

Learning result
    ✅ Database boundary is not the definition of an OAuth role
    ✅ Database sharing does not require process/container sharing

Result: PASS for the database-topology objective
```
