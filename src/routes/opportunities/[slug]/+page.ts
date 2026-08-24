import { error } from '@sveltejs/kit';
import type { OutreachEvent } from '$lib/events';
import type { PageLoad } from './$types';

export const prerender = false;

export const load: PageLoad = async ({ fetch, params }) => {
	const response = await fetch(`/api/events/get/${params.slug}`, {
		headers: { Accept: 'application/json' }
	});

	if (response.status === 404) {
		throw error(404, 'Opportunity not found.');
	}

	if (!response.ok) {
		throw error(response.status, 'Unable to load this opportunity.');
	}

	return { event: await response.json() as OutreachEvent };
};
