<script lang="ts">
    import Card from "$lib/components/ui/card.svelte";
    import type { Event } from "$lib/components/events";

    let { event }: {event: Event} = $props();
</script>

<Card class="min-w-0 hover:scale-[102%] hover:shadow-xl transition-all duration-100">
    <h1 class="font-bold text-xl">{event.name}</h1>
    <p class="min-w-0 break-words text-md text-neutral-700">
        {event.location} -
        <a class="break-all hover:underline" href={event.link} target="_blank" rel="noreferrer">
            {event.link}
        </a>
    </p>
</Card>
