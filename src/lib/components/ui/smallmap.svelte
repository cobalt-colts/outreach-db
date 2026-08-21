<script lang="ts">
	import { onMount } from 'svelte';
	import type { Map } from 'leaflet';
    import { getCoordinatesFromZip } from '$lib/map.svelte';
    import type { OutreachEvent } from '$lib/events';

	let mapElement: HTMLDivElement;
	let map: Map;

	let {event}: {event: OutreachEvent} = $props();

	onMount(() => {
		let destroyed = false;

		async function setupMap() {
			const L = await import('leaflet');
			await import('leaflet/dist/leaflet.css');

			if (destroyed) return;

			map = L.map(mapElement).setView([39.0997, -94.5786], 10);

			L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
				maxZoom: 19,
				attribution:
					'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
			}).addTo(map);

			const location = await getCoordinatesFromZip(event.zip_code);
			if (destroyed || !location) return;

			map.setView([location.lat, location.lng], 10);
			L.marker([location.lat, location.lng])
				.addTo(map)
				.bindPopup(`<b>${event.name}</b><br><a href="${event.link}" target="_blank">${event.link}</a>`)
				.openPopup();
		}

		setupMap();

		return () => {
			destroyed = true;
			map?.remove();
		};
	});
</script>

<div class="map" bind:this={mapElement}></div>

<style>
	.map {
		width: 100%;
		height: 500px;
		border-radius: 0.75rem;
		overflow: hidden;
	}
</style>
