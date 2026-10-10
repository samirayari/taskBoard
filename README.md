# TaskBoard

TaskBoard is a small task management API written in Python with FastAPI.

It is the **common thread project** of the DevOps training week (first-year Master's in computer science). This version 1.0.0 is the starting point: the API works, is tested and is documented. During the workshops, you will make it evolve with Git, automated tests, Docker and a continuous integration pipeline.

The project is intentionally simple:

- no database: tasks are kept **in memory**;
- no graphical interface: you use the interactive API documentation and `curl`;
- few files, easy to read.

## Contents

1. [Prerequisites](#1-prerequisites)
2. [Create and activate a virtual environment](#2-create-and-activate-a-virtual-environment)
3. [Install the dependencies](#3-install-the-dependencies)
4. [Run the application](#4-run-the-application)
5. [Interactive documentation](#5-interactive-documentation)
6. [Request examples](#6-request-examples)
7. [Run the tests](#7-run-the-tests)
8. [Environment variables](#8-environment-variables)
9. [Commit messages](#9-commit-messages)
10. [Project structure](#10-project-structure)
11. [Troubleshooting](#11-troubleshooting)

## 1. Prerequisites

- **Python 3.12**: check with `python3.12 --version` (macOS/Linux) or `py -3.12 --version` (Windows);
- **pip** (shipped with Python);
- **curl** (already available on macOS, Linux and Windows 10/11);
- **Git**, to get the project and for the workshops.

All the commands below must be run **from the project root folder** (`taskBoard` after `git clone`), the one that contains this README.

## 2. Create and activate a virtual environment

A virtual environment (`.venv`) keeps the project's dependencies separate from the system's.

### macOS / Linux

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

### Windows PowerShell

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
```

Once the environment is active, the prompt starts with `(.venv)`. To leave it, type `deactivate`.

> The environment must be activated **in every new terminal** before running the application or the tests.

## 3. Install the dependencies

```bash
pip install -r requirements.txt
pre-commit install
```

`pre-commit install` enables the Git hook that checks commit messages (see [section 9](#9-commit-messages)). Run it once after each `git clone`.

The `requirements.txt` file pins exact versions:

| Package   | Purpose                                              |
|-----------|------------------------------------------------------|
| `fastapi` | API framework (also installs Pydantic)               |
| `uvicorn` | Server that runs the application                     |
| `httpx2`  | HTTP client used by the tests' `TestClient`          |
| `pytest`  | Test runner                                          |
| `pre-commit` | Runs the Git hook that checks commit messages     |

## 4. Run the application

### For development (port 8000)

```bash
uvicorn app.main:app --reload --port 8000
```

- `app.main:app` refers to the `app` object in `app/main.py`;
- `--reload` restarts the server automatically whenever the code changes.

The API answers on <http://localhost:8000>. Stop the server with `Ctrl+C`.

### Listening on all interfaces (preparing the Docker workshop)

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

By default, Uvicorn only listens on `127.0.0.1`, so only the local machine can reach it. With `--host 0.0.0.0`, it also accepts connections from other machines or from outside a container. This is required inside a Docker container: without this option, the API would be unreachable from outside the container.

### Two important limits of this version

- **Data disappears on restart.** Tasks are stored in memory. They are lost every time the server stops, including the automatic restarts triggered by `--reload`.
- **One server process only.** Each process has its own memory. Do not use the `--workers` option: with several processes, each one would have its own task list and responses would become inconsistent. A database, added in a later workshop, will remove both limits.

## 5. Interactive documentation

With the server running, open in a browser:

- **Swagger UI**: <http://localhost:8000/docs>. Click a route, then **Try it out** and **Execute** to send a real request;
- **ReDoc**: <http://localhost:8000/redoc>, a read-only documentation;
- **Raw OpenAPI schema**: <http://localhost:8000/openapi.json>.

## 6. Request examples

### Routes

| Method   | Route           | Purpose                                | Success |
|----------|-----------------|----------------------------------------|---------|
| `GET`    | `/health`       | Check that the API is running          | 200     |
| `GET`    | `/version`      | Application name and version           | 200     |
| `GET`    | `/tasks`        | List the tasks                         | 200     |
| `GET`    | `/tasks/{id}`   | Read a task                            | 200     |
| `POST`   | `/tasks`        | Create a task                          | 201     |
| `PATCH`  | `/tasks/{id}`   | Update the title and/or the status     | 200     |
| `DELETE` | `/tasks/{id}`   | Delete a task (empty response body)    | 204     |

A task looks like this:

```json
{"id": 1, "title": "Learn Git", "completed": false}
```

- `id` is assigned automatically (1, 2, 3…);
- `title` is stripped of leading and trailing whitespace, then must contain between 1 and 100 characters;
- `completed` is `false` on creation.

### With curl (macOS / Linux)

```bash
# API status
curl http://localhost:8000/health
# {"status":"ok"}

# Version
curl http://localhost:8000/version
# {"name":"TaskBoard","version":"1.0.0"}

# Create a task
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Learn Git"}'
# {"id":1,"title":"Learn Git","completed":false}

# List the tasks
curl http://localhost:8000/tasks
# [{"id":1,"title":"Learn Git","completed":false}]

# Read a task
curl http://localhost:8000/tasks/1

# Mark a task as completed
curl -X PATCH http://localhost:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'
# {"id":1,"title":"Learn Git","completed":true}

# Change the title
curl -X PATCH http://localhost:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"title": "Master Git"}'

# Delete a task (-i shows the HTTP status: 204 No Content, no body)
curl -i -X DELETE http://localhost:8000/tasks/1
```

### Error examples

```bash
# Unknown task → 404
curl -i http://localhost:8000/tasks/999
# {"detail":"Task 999 not found"}

# Title made only of spaces → 422
curl -i -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "   "}'
# {"detail":[{"type":"string_too_short","loc":["body","title"],
#             "msg":"String should have at least 1 character", ...}]}

# PATCH without any field → 422
curl -i -X PATCH http://localhost:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{}'
# ... "msg":"Value error, Provide at least one field: title or completed" ...
```

HTTP status codes used:

| Code  | Meaning                                                                |
|-------|------------------------------------------------------------------------|
| `200` | Success                                                                |
| `201` | Task created                                                           |
| `204` | Task deleted (no response body)                                        |
| `404` | The requested task does not exist                                      |
| `422` | Invalid data: empty or too long title, non-integer id, malformed JSON… |

### On Windows PowerShell

In PowerShell, `curl` may be an alias for `Invoke-WebRequest`, which does not accept the same options. Use **`curl.exe`**:

```powershell
curl.exe http://localhost:8000/health
```

To send JSON, the simplest way is `Invoke-RestMethod`:

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8000/tasks `
  -ContentType "application/json" -Body '{"title": "Learn Git"}'

Invoke-RestMethod -Method Patch -Uri http://localhost:8000/tasks/1 `
  -ContentType "application/json" -Body '{"completed": true}'

Invoke-RestMethod -Method Delete -Uri http://localhost:8000/tasks/1
```

You can also use the interactive documentation (<http://localhost:8000/docs>), which works the same way on every system.

## 7. Run the tests

With the virtual environment active, from the project root folder:

```bash
pytest          # summary
pytest -v       # details of each test
```

Expected result: `19 passed`.

The tests (`tests/test_api.py`) use FastAPI's `TestClient`: they call the API **without starting a server**. Before each test, a fixture empties the storage, so every test starts from an empty list, whatever the execution order.

To run a single test:

```bash
pytest tests/test_api.py::test_create_and_get_task
```

## 8. Environment variables

The application works **without any configuration** and without a `.env` file. Two variables let you change the default values:

| Variable      | Default value | Used for                                                   |
|---------------|---------------|------------------------------------------------------------|
| `APP_NAME`    | `TaskBoard`   | Name returned by `/version` and shown in `/docs`           |
| `APP_VERSION` | `1.0.0`       | Version returned by `/version` and shown in `/docs`        |

They are read **when the server starts**. After changing them, restart the server.

macOS / Linux, for a single command:

```bash
APP_NAME="TaskBoard Demo" APP_VERSION=1.0.1 uvicorn app.main:app --port 8000
```

Windows PowerShell, for the current terminal:

```powershell
$env:APP_NAME = "TaskBoard Demo"
$env:APP_VERSION = "1.0.1"
uvicorn app.main:app --port 8000
```

Check:

```bash
curl http://localhost:8000/version
# {"name":"TaskBoard Demo","version":"1.0.1"}
```

## 9. Commit messages

Commit messages must follow the [Conventional Commits](https://www.conventionalcommits.org/) convention:

```
type(optional scope): short description
```

| Type       | Use it for                                          |
|------------|-----------------------------------------------------|
| `feat`     | A new feature                                       |
| `fix`      | A bug fix                                           |
| `docs`     | Documentation only                                  |
| `style`    | Formatting, no code behavior change                 |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `perf`     | Performance improvement                             |
| `test`     | Adding or updating tests                            |
| `build`    | Dependencies, packaging                             |
| `ci`       | Continuous integration configuration                |
| `chore`    | Other maintenance tasks                             |
| `revert`   | Reverting a previous commit                         |

Examples:

```bash
git commit -m "feat: add task search"
git commit -m "fix(store): reset id counter"
git commit -m "docs: explain the Docker setup"
git commit -m "feat!: rename the /tasks route"   # "!" marks a breaking change
```

After `pre-commit install`, Git runs a check (`.pre-commit-config.yaml`) on every commit. A message that does not follow the convention is **rejected** and the commit is not created:

```
$ git commit -m "added stuff"
Conventional Commit......................................................Failed
[Bad commit message] >> added stuff
...
  - Expected value for type from: build, chore, ci, docs, feat, fix, perf, refactor, revert, style, test
```

Fix the message and commit again. Merge commits created by Git (`Merge branch ...`) are accepted as they are.

> This check runs on your machine only. It can be skipped with `git commit --no-verify`, so it is a safety net, not a guarantee. A CI pipeline can enforce it for everyone.

## 10. Project structure

```
taskBoard/
├── app/
│   ├── __init__.py      makes app/ a Python package
│   ├── main.py          FastAPI application, configuration and routes
│   ├── models.py        request and response models (validation)
│   └── store.py         in-memory task storage
├── tests/
│   ├── __init__.py
│   └── test_api.py      API tests
├── pytest.ini           pytest configuration
├── .pre-commit-config.yaml  Git hook checking commit messages
├── requirements.txt     pinned dependencies
├── .gitignore           files not to version (.venv, caches…)
└── README.md
```

The routes (`main.py`) do not know how tasks are stored: they only go through the methods of `store.py`. To use a database later, only `store.py` will need to be replaced.

## 11. Troubleshooting

**`ModuleNotFoundError: No module named 'fastapi'`, or `uvicorn` / `pytest` not found**
The virtual environment is not active, or the dependencies are not installed. Activate it (section 2), check that the prompt shows `(.venv)`, then run `pip install -r requirements.txt` again.

**`ModuleNotFoundError: No module named 'app'`, or `Could not import module "app.main"`**
The command is run from the wrong folder. Go to the project root folder, the one that contains `app/` and this README, then run it again.

**`python3.12: command not found`, or `py -3.12` cannot find Python**
Python 3.12 is not installed, or not under that name. Install it from <https://www.python.org/downloads/> (or with your system's package manager), then check with `python3.12 --version`. If the virtual environment was created with another version, delete the `.venv` folder and create it again.

**Windows: "running scripts is disabled on this system" when activating**
PowerShell blocks the activation script. Allow local scripts for your user, then activate again:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

**`[Errno 48] Address already in use` (macOS) or `[Errno 98]` (Linux): port 8000 is busy**
Another server, often a TaskBoard started in another terminal, is already using the port. Stop it with `Ctrl+C` in its terminal, or start this one on another port with `--port 8001`. To find which process uses the port: `lsof -i :8000` (macOS/Linux) or `netstat -ano | findstr :8000` (Windows).

**My tasks have disappeared**
This is expected: storage is in memory. Tasks are lost on every restart, including the automatic reload triggered by `--reload` after a code change.

**Responses are inconsistent: a created task is sometimes not found**
The server is probably running with several processes (`--workers 2` or more). Each process has its own memory. Restart the server without `--workers`.

**`422 Unprocessable Entity` response**
The data sent is invalid. The `detail` field of the response tells where the error is (`loc`) and why (`msg`). Common causes:
- title empty, made only of spaces, or longer than 100 characters;
- `PATCH` without `title` or `completed`;
- non-integer id (`/tasks/abc`);
- malformed JSON, or missing `Content-Type: application/json` header.

**`test_version` fails while the other tests pass**
The `APP_VERSION` or `APP_NAME` variable is probably set in your terminal. The test expects the default values (`TaskBoard`, `1.0.0`). Remove them with `unset APP_VERSION APP_NAME` (macOS/Linux) or `Remove-Item Env:APP_VERSION, Env:APP_NAME` (PowerShell), then run `pytest` again.

**`curl` in PowerShell fails on `-X` or `-H`**
Use `curl.exe` instead of `curl`, or `Invoke-RestMethod` (see section 6).

**My commit is rejected with `Conventional Commit ... Failed`**
The message does not follow the convention (section 9). Start it with an allowed type followed by `: `, for example `feat: add task search`. To fix the message you just typed, run `git commit --edit --file=.git/COMMIT_EDITMSG`.

**`git revert` is rejected**
Git's default revert message (`Revert "feat: ..."`) does not follow the convention. Run `git revert --no-commit <commit>`, then `git commit -m "revert: <what you undo>"`.

**Bad commit messages are accepted: the check does not run**
The hook is not enabled in this clone. Activate the virtual environment and run `pre-commit install`.

**`pre-commit: command not found`**
The virtual environment is not active, or the dependencies are not installed (see sections 2 and 3).
