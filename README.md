# Hello World CI/CD

A small Flask application used to demonstrate a simple **GitLab CI/CD → Docker Registry → production server** deployment workflow.

The project uses **uv** for Python dependency management and **Docker** for packaging. GitLab CI builds and pushes an image, then deploys that exact image to a production server through SSH and Docker Compose.

## Architecture

```text
Git repository
     |
     v
GitLab Runner
     |
     | docker build
     v
GitLab Container Registry
     |
     | docker compose pull
     v
Production Server
     |
     v
Flask container :8000
```

## Application

Endpoints:

- `GET /` — returns the hello-world message
- `GET /health` — returns `OK!!!`

The application listens on `0.0.0.0:8000` inside the container.

## Local development with uv

Install [uv](https://docs.astral.sh/uv/) and create the environment:

```bash
uv sync
```

Run the application:

```bash
uv run python app.py
```

Then open:

```text
http://localhost:8000
http://localhost:8000/health
```

## Docker

Build the image:

```bash
docker build -t hello-world-cicd .
```

Run it:

```bash
docker run --rm -p 8000:8000 hello-world-cicd
```

Test it:

```bash
curl http://localhost:8000/health
```

## GitLab CI/CD

The pipeline has two stages:

1. **build** — builds the Docker image and pushes it to the GitLab Container Registry.
2. **deploy** — connects to the production server over SSH, updates the `IMAGE` value in `/opt/hello-world/.env`, pulls the new image, and starts it with Docker Compose.

Images are tagged with the GitLab commit short SHA:

```text
$CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA
```

This means each deployment points to an immutable image tag instead of `latest`.

### Required GitLab CI/CD variables

Configure these variables in **Settings → CI/CD → Variables**:

| Variable | Type | Purpose |
|---|---|---|
| `SSH_PRIVATE_KEY` | File | Private SSH key used by the deploy job |
| `DEPLOY_HOST` | Variable | Production server hostname/IP |
| `DEPLOY_USER` | Variable | SSH user on the production server |

The deploy server is expected to contain:

```text
/opt/hello-world/
├── docker-compose.yml
└── .env
```

The `.env` file should contain an `IMAGE` variable, for example:

```dotenv
IMAGE=registry.example.com/group/project:initial
```

The Docker Compose file should use that variable for the application image.

## SSH security

For production, prefer a dedicated deployment user with access limited to the required deployment commands rather than using `root`.

The CI job uses `ssh-keyscan` to populate `known_hosts`. For a higher-security setup, store a verified host key as a protected CI/CD variable instead of trusting the key returned by `ssh-keyscan` during every pipeline.

## Recommended improvements

For this intentionally small example, the current setup is enough to demonstrate the workflow. For a real service, consider adding:

- **Automated tests** before the Docker build.
- **A pinned `uv.lock`** committed to the repository for fully reproducible dependency resolution. Generate it with `uv lock` in an environment with access to PyPI.
- **Protected GitLab variables** and protected deployment branches/environments.
- **A dedicated deployment user** on the production server.
- **Container image vulnerability scanning** in CI.
- **Docker image cleanup/retention policies** in the GitLab Container Registry.
- **A real WSGI server**, such as Gunicorn, instead of Flask's development server for production traffic.
- **Application logging and monitoring** with your existing monitoring stack.

## Project files

```text
.
├── .gitignore
├── .gitlab-ci.yml
├── Dockerfile
├── README.md
├── app.py
└── pyproject.toml
```

## Test

Run the test suite with uv:

```bash
uv sync
uv run pytest -v
```

The GitLab pipeline runs this test stage before the Docker build. If tests fail, the build and deploy stages do not run.
