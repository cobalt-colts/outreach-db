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
