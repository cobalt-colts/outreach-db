export interface OutreachEvent {
	id: number;
	name: string;
	city: string;
	state: string;
	zip_code: string;
	description: string;
	link: string;
	audit_status: 'checked' | 'corrected';
	audit_notes: string | null;
	status: 'active' | 'archived' | 'flagged';
	tags: string[];
}

/** "Springfield, IL" — the display form of the split city/state columns. */
export function formatLocation(event: Pick<OutreachEvent, 'city' | 'state'>): string {
	return `${event.city}, ${event.state}`;
}
