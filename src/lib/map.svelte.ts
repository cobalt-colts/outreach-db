import type { OutreachEvent } from '$lib/events';

type ZipCodeLookup = typeof import('zipcodes')['lookup'];

export type MapCoordinates = {
	lat: number;
	lng: number;
};

/** A ZIP-centroid location and every opportunity assigned to that ZIP. */
export type GeocodedEventGroup = {
	latitude: number;
	longitude: number;
	zip: string;
	events: OutreachEvent[];
};

export type EventGeocodingResult = {
	groups: GeocodedEventGroup[];
	unresolvedZipCodes: string[];
};

/**
 * Resolves a US ZIP code to its locally stored centroid.
 * Returns null when the ZIP is not present in the bundled data.
 */
export async function getCoordinatesFromZip(zip: string): Promise<MapCoordinates | null> {
	const { lookup } = await import('zipcodes');
	const location = lookup(zip.trim());
	return location ? { lat: location.latitude, lng: location.longitude } : null;
}

/**
 * Groups opportunities at their ZIP-code centroids using locally bundled data.
 * This avoids a network request for every opportunity and is safe to reuse in
 * any client-side feature that needs a map location.
 */
export async function geocodeEventsByZip(
	events: OutreachEvent[]
): Promise<EventGeocodingResult> {
	const { lookup } = await import('zipcodes');
	return groupEventsByZip(events, lookup);
}

/**
 * The synchronous form is useful when a caller already has a ZIP lookup, such
 * as a batch import or a server-side cache warmer.
 */
export function groupEventsByZip(
	events: OutreachEvent[],
	lookup: ZipCodeLookup
): EventGeocodingResult {
	const eventsByZip = new Map<string, OutreachEvent[]>();

	for (const event of events) {
		const group = eventsByZip.get(event.zip_code);
		if (group) {
			group.push(event);
		} else {
			eventsByZip.set(event.zip_code, [event]);
		}
	}

	const groups: GeocodedEventGroup[] = [];
	const unresolvedZipCodes: string[] = [];

	for (const [zip, zipEvents] of eventsByZip) {
		const location = lookup(zip);
		if (!location) {
			unresolvedZipCodes.push(zip);
			continue;
		}

		groups.push({
			latitude: location.latitude,
			longitude: location.longitude,
			zip,
			events: zipEvents
		});
	}

	return { groups, unresolvedZipCodes };
}
