import type { Handle } from '@sveltejs/kit';

const apiOrigin = process.env.API_ORIGIN ?? 'http://127.0.0.1:8000';

/**
 * Keep the browser-facing API at /api while the FastAPI service runs separately
 * from the SvelteKit Node server.
 */
export const handle: Handle = async ({ event, resolve }) => {
	if (!event.url.pathname.startsWith('/api/')) {
		return resolve(event);
	}

	const target = new URL(`${event.url.pathname}${event.url.search}`, apiOrigin);
	return fetch(new Request(target, event.request));
};
