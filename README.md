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

Build and start the complete application with:

```sh
docker compose up --build -d
```

Open `http://localhost:3000`. Set `APP_PORT` to publish a different host port,
for example `APP_PORT=8080 docker compose up --build -d`.

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
