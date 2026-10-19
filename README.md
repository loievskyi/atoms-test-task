# Atoms Test Task

Technical assessment for Atoms.

## Prerequisites

- Python 3.14
- [uv](https://docs.astral.sh/uv/)
- Docker

## 1. Navigate to the project root

```shell
cd atoms-test-task
```

## 2. Configure environment variables

```shell
cp .env.example .env
```

Update the database credentials and other settings in `.env` as needed.

## 3. Set up the Python environment

Install Python 3.14 if needed:

```shell
uv python install 3.14
```

Create and activate the virtual environment, then install the project dependencies:

```shell
uv python pin 3.14
uv venv --python 3.14
source .venv/bin/activate
uv sync
```

Verify the Python version:

```shell
python --version
```

## 4. Start PostgreSQL in Docker

```shell
docker run -d --name atoms-postgres --restart unless-stopped --env-file .env -p 5432:5432 -v atoms_postgres_data:/var/lib/postgresql/data postgres:16-alpine
```

## 5. Load environment variables

```shell
set -a && source .env && set +a
```

## 6. Apply database migrations

```shell
uv run python braincomua_project/manage.py migrate
```

## 7. Create a superuser

```shell
uv run python braincomua_project/manage.py createsuperuser
```

## 8. Start the Django development server

```shell
uv run python braincomua_project/manage.py runserver
```

## 9. Run the scraper

**Note:** Before running a scraper, make sure you have loaded the environment variables as described in Step 5:
```shell
set -a && source .env && set +a
```

### Requests

Run the scraper implemented with requests and BeautifulSoup4:
```shell
PYTHONPATH="$(pwd)" uv run python modules/bs4_scraper.py
```

### Selenium

Run the Selenium scraper:
```shell
PYTHONPATH="$(pwd)" uv run python modules/selenium_scraper.py
```

## 10. Stop and remove the PostgreSQL container

```shell
docker stop atoms-postgres && docker rm atoms-postgres
```

**Note:** Removing the container does not delete the `atoms_postgres_data` volume, so your database data will be preserved.
