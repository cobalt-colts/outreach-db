<script lang="ts">
	import { onMount } from 'svelte';
	import { apiRequest } from '$lib/auth.svelte';
	import { toast } from 'svelte-sonner';
	import { isCooperativeExtension, type OutreachEvent } from '$lib/events';
	import { geocodeEventsByZip, type GeocodedEventGroup } from '$lib/map.svelte';

	type Leaflet = typeof import('leaflet');
	type PointProperties = {
		groupIndex: number;
		opportunityCount: number;
	};
	type ClusterProperties = {
		opportunityCount: number;
	};

	let { class: className = '' }: { class?: string } = $props();

	let mapElement: HTMLDivElement;
	let map: import('leaflet').Map | undefined;

	function escapeHtml(value: string): string {
		return value.replace(/[&<>'"]/g, (character) => {
			return ({
				'&': '&amp;',
				'<': '&lt;',
				'>': '&gt;',
				"'": '&#39;',
				'"': '&quot;'
			})[character] ?? character;
		});
	}

	function popupContent(group: GeocodedEventGroup): string {
		const opportunities = group.events
			.map((event) => {
				const name = escapeHtml(event.name);
				return `<li><a href="/opportunities/${event.id}">${name}</a></li>`;
			})
			.join('');

		return `<div><strong>${group.events.length} ${group.events.length === 1 ? 'opportunity' : 'opportunities'} in ${escapeHtml(group.zip)}</strong><ul>${opportunities}</ul></div>`;
	}

	async function populateMap(L: Leaflet, isDestroyed: () => boolean) {
		try {
			const response = await apiRequest('/api/events/get', {
				headers: { Accept: 'application/json' }
			});

			if (!response.ok) {
				toast.error('Error fetching events.');
				return;
			}

			const data: unknown = await response.json();
			if (!Array.isArray(data)) {
				toast.error('The events service returned an invalid response.');
				return;
			}
			const visibleEvents = (data as OutreachEvent[]).filter(
				(event) => !isCooperativeExtension(event)
			);

			const [{ default: Supercluster }, { groups, unresolvedZipCodes }] = await Promise.all([
				import('supercluster'),
				geocodeEventsByZip(visibleEvents)
			]);
			if (isDestroyed() || !map) return;

			const clusterIndex = new Supercluster<PointProperties, ClusterProperties>({
				// A generous radius creates metro-scale groups at national and regional zooms.
				radius: 110,
				maxZoom: 10,
				minPoints: 2,
				nodeSize: 64,
				map: ({ opportunityCount }) => ({ opportunityCount }),
				reduce: (cluster, point) => {
					cluster.opportunityCount += point.opportunityCount;
				}
			}).load(
				groups.map((group, groupIndex) => ({
					type: 'Feature' as const,
					properties: {
						groupIndex,
						opportunityCount: group.events.length
					},
					geometry: {
						type: 'Point' as const,
						coordinates: [group.longitude, group.latitude]
					}
				}))
			);

			const activeMap = map;
			const markerLayer = L.layerGroup().addTo(activeMap);
			const pointRenderer = L.canvas({ padding: 0.5 });
			let scheduledRender: number | undefined;

			function renderVisibleClusters() {
				if (isDestroyed()) return;

				markerLayer.clearLayers();
				const bounds = activeMap.getBounds();
				const visibleFeatures = clusterIndex.getClusters(
					[
						Math.max(-180, bounds.getWest()),
						Math.max(-90, bounds.getSouth()),
						Math.min(180, bounds.getEast()),
						Math.min(90, bounds.getNorth())
					],
					Math.round(activeMap.getZoom())
				);

				for (const feature of visibleFeatures) {
					const [longitude, latitude] = feature.geometry.coordinates;
					if ('cluster' in feature.properties && feature.properties.cluster) {
						const {
							cluster_id: clusterId,
							point_count: zipCount,
							opportunityCount
						} = feature.properties;
						const digits = String(opportunityCount).length;
						const width = 22 + digits * 8;
						const height = opportunityCount >= 100 ? 30 : 27;
						const magnitude = opportunityCount >= 250 ? 'high' : opportunityCount >= 75 ? 'medium' : 'low';
						const marker = L.marker([latitude, longitude], {
							icon: L.divIcon({
								className: 'map-cluster-shell',
								html: `<span class="map-cluster-badge map-cluster-badge--${magnitude}">${opportunityCount}</span>`,
								iconSize: [width, height],
								iconAnchor: [width / 2, height / 2]
							})
						});

						marker
							.bindTooltip(`${opportunityCount} opportunities across ${zipCount} ZIP codes — click to expand`)
							.on('click', () => {
								const zoom = Math.min(clusterIndex.getClusterExpansionZoom(clusterId), activeMap.getMaxZoom());
								activeMap.setView([latitude, longitude], zoom);
							})
							.addTo(markerLayer);
						continue;
					}

					const { groupIndex } = feature.properties as PointProperties;
					const group = groups[groupIndex];
					L.circleMarker([latitude, longitude], {
						renderer: pointRenderer,
						radius: group.events.length > 1 ? 7 : 5,
						weight: 1,
						color: '#ffffff',
						fillColor: '#2563eb',
						fillOpacity: 0.85
					})
						.bindPopup(popupContent(group), { maxWidth: 320 })
						.bindTooltip(`${group.events.length} ${group.events.length === 1 ? 'opportunity' : 'opportunities'} in ZIP ${group.zip}`)
						.addTo(markerLayer);
				}
			}

			function scheduleRender() {
				if (scheduledRender !== undefined) cancelAnimationFrame(scheduledRender);
				scheduledRender = requestAnimationFrame(() => {
					scheduledRender = undefined;
					renderVisibleClusters();
				});
			}

			activeMap.on('moveend zoomend', scheduleRender);
			renderVisibleClusters();

			if (unresolvedZipCodes.length > 0) {
				toast.warning(`${unresolvedZipCodes.length} ZIP code${unresolvedZipCodes.length === 1 ? '' : 's'} could not be placed on the map.`);
			}
		} catch (error) {
			console.error(error);
			toast.error('Error fetching events.');
		}
	}

	onMount(() => {
		let destroyed = false;

		async function setupMap() {
			const L = await import('leaflet');
			await import('leaflet/dist/leaflet.css');

			if (destroyed) return;

			map = L.map(mapElement, { preferCanvas: true }).setView([39.0997, -94.5786], 4);

			L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
				maxZoom: 19,
				attribution:
					'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
			}).addTo(map);

			await populateMap(L, () => destroyed);
		}

		void setupMap();

		return () => {
			destroyed = true;
			map?.remove();
			map = undefined;
		};
	});
</script>

<div class="map {className}" bind:this={mapElement}></div>

<style>
	.map {
		width: 100%;
		height: 500px;
		border-radius: 0.75rem;
		overflow: hidden;
	}

	:global(.map-cluster-shell) {
		border: 0;
		background: transparent;
	}

	:global(.map-cluster-badge) {
		display: flex;
		width: 100%;
		height: 100%;
		align-items: center;
		justify-content: center;
		box-sizing: border-box;
		border: 2px solid rgb(255 255 255 / 96%);
		border-radius: 9999px;
		box-shadow:
			0 1px 2px rgb(15 23 42 / 22%),
			0 3px 9px rgb(15 23 42 / 18%);
		color: white;
		font-family: ui-monospace, 'SFMono-Regular', Consolas, monospace;
		font-size: 0.68rem;
		font-weight: 750;
		font-variant-numeric: tabular-nums;
		letter-spacing: -0.03em;
		line-height: 1;
		text-align: center;
		transition:
			transform 120ms ease,
			box-shadow 120ms ease;
	}

	:global(.map-cluster-badge--low) {
		background: rgb(37 99 235 / 90%);
	}

	:global(.map-cluster-badge--medium) {
		background: rgb(30 64 175 / 92%);
	}

	:global(.map-cluster-badge--high) {
		background: rgb(30 58 138 / 94%);
	}

	:global(.map-cluster-shell:hover .map-cluster-badge),
	:global(.map-cluster-shell:focus .map-cluster-badge) {
		transform: translateY(-1px) scale(1.06);
		box-shadow:
			0 2px 3px rgb(15 23 42 / 20%),
			0 5px 12px rgb(15 23 42 / 24%);
	}

	@media (prefers-reduced-motion: reduce) {
		:global(.map-cluster-badge) {
			transition: none;
		}
	}
</style>
