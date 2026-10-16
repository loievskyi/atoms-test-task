# atoms-test-task
Technical assessment for Atoms.

## 1. Navigate to the project root
```shell
cd atoms-test-task
```

## 2. Create the `.env` file
```shell
cp .env.example .env
```

**Note:** Update the database credentials and other settings in `.env` as needed.

## 3. Start PostgreSQL in Docker
```shell
docker run -d --name atoms-postgres --restart unless-stopped --env-file .env -p 5432:5432 -v atoms_postgres_data:/var/lib/postgresql/data postgres:16-alpine
```

## 4. Load environment variables
```shell
set -a && source .env && set +a
```

## 5. Apply database migrations
```shell
set -a && source .env && set +a && uv run python braincomua_project/manage.py migrate
```

## 6. Create a superuser
```shell
set -a && source .env && set +a && uv run python braincomua_project/manage.py createsuperuser
```

## 7. Start the Django development server
```shell
set -a && source .env && set +a && uv run python braincomua_project/manage.py runserver
```

## 8. Run the scraper
```shell
set -a && source .env && set +a && PYTHONPATH="$(pwd)" uv run python modules/selenium_scraper.py
```

## 9. Stop and remove the PostgreSQL container
```shell
docker stop atoms-postgres && docker rm atoms-postgres
```

**Note:** Removing the container does not delete the `atoms_postgres_data` volume, so your database data will be preserved.
