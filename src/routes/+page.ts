import { error } from '@sveltejs/kit';
import type { OutreachEvent } from '$lib/events';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch }) => {
	const response = await fetch('/api/events/get', {
		headers: { Accept: 'application/json' }
	});

	if (!response.ok) {
		throw error(response.status, 'Unable to load outreach opportunities.');
	}

	const events: unknown = await response.json();
	if (!Array.isArray(events)) {
		throw error(502, 'The events service returned an invalid response.');
	}

	return { events: events as OutreachEvent[] };
};
