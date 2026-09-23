> [!CAUTION]
> bro ts project is a work in progress don't slime me out for the ai generated readme until its at least 1.0

# Outreach DB

Outreach DB uses a SvelteKit Node server for the web application and FastAPI for
the API. The SvelteKit server renders public pages on the server, so opportunity
pages have useful HTML for crawlers and link previews before JavaScript loads.

## Development

Install the JavaScript and Python dependencies, then start both development
servers:

```sh
bun install
uv sync
bun run dev
```

Vite serves the frontend and proxies `/api` requests to FastAPI on port 8000.

## Production

Build the frontend and run FastAPI alongside the SvelteKit server:

```sh
bun run build
uv run main.py
API_ORIGIN=http://127.0.0.1:8000 bun run start
```

Expose the SvelteKit server (port 3000 by default) publicly. It proxies `/api`
requests to `API_ORIGIN`; FastAPI should remain private to the application
network. Set `HOST` and `PORT` if the frontend must listen on different values.

## Docker Compose

Every push to `main` builds and pushes an image to
`ghcr.io/cobalt-colts/outreach-db:latest` via `.github/workflows/docker-image.yml`.

For local development, build and start the complete application with:

```sh
docker compose up --build -d
```

Open `http://localhost:3000`. Set `APP_PORT` to publish a different host port,
for example `APP_PORT=8080 docker compose up --build -d`.

On a deployment host that only has `compose.yaml` (no source checkout, no
`Dockerfile`), pull the CI-built image instead of building:

```sh
docker compose pull
docker compose up -d
```

The GHCR package defaults to private. Either make it public under the repo's
Packages settings, or authenticate the host first:

```sh
echo "$GITHUB_TOKEN" | docker login ghcr.io -u <github-username> --password-stdin
```

The token needs `read:packages` scope.

The container runs both the SvelteKit Node server and FastAPI. Only SvelteKit is
published; it proxies `/api` to FastAPI inside the container. SQLite data and
the automatically generated JWT keypair are stored in the named
`outreach-data` volume and survive container replacement. `docker compose down`
keeps this volume; use `docker compose down --volumes` only when you intend to
delete the application data.

To initialize or refresh the database from the CSV bundled in `tools/`, run:

```sh
docker compose exec outreach-db python tools/csv_to_event.py
```
