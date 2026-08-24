<script lang="ts">
    import Card from "$lib/components/ui/card.svelte";
    import { formatLocation, type OutreachEvent } from "$lib/events";

    let { event }: {event: OutreachEvent} = $props();
</script>

<Card class="min-w-0 hover:scale-[102%] hover:shadow-xl transition-all duration-100">
    <h2 class="text-xl font-bold">
        <a class="hover:underline" href={`/opportunities/${event.id}`}>{event.name}</a>
    </h2>
    <p class="min-w-0 wrap-break-word text-md text-neutral-700">
        {formatLocation(event)} -
        <a class="break-all hover:underline" href={event.link} target="_blank" rel="noreferrer">
            {event.link}
        </a>
    </p>
</Card>
