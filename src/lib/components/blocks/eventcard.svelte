<script lang="ts">
    import Card from "$lib/components/ui/card.svelte";
    import type { Event } from "$lib/components/events";

    let { event }: {event: Event} = $props();
</script>

<Card>
    <h1 class="font-bold text-2xl">{event.name}</h1>
</Card>