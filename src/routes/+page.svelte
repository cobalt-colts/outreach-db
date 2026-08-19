<script lang="ts">
    import Eventcard from "$lib/components/blocks/eventcard.svelte";
    import { formatLocation, type OutreachEvent } from "$lib/events";
    import Input from "$lib/components/ui/input.svelte";
    import Seo from "$lib/components/ui/seo.svelte";

    let { data }: { data: { events: OutreachEvent[] } } = $props();

    let searchbox: string = $state("");

    let searchedEvents = $derived(data.events.filter(event => {
      const search = searchbox.toLowerCase();
      return [
        event.name,
        event.description,
        formatLocation(event),
        event.zip_code,
        ...event.tags
        ].some(term => term.toLowerCase().includes(search))
    }))

    let filteredEvents = $derived(searchedEvents.filter(event => !event.tags.some(tag => tag === "Cooperative Extension")));

</script>

<Seo title="Outreach Opportunities" description="Browse community outreach opportunities." />

<main>
    <div class="mx-auto my-5 flex max-w-xl flex-col items-center justify-center gap-5">
        <h1 class="mt-25 mb-25 text-center text-5xl font-bold">
            Browse outreach opportunities
        </h1>
        <div class="flex flex-row gap-3 w-full min-w-0">
            <Input bind:value={searchbox} placeholder="Search opportunities..."/>
        </div>
        {#if filteredEvents.length > 0}
            <div class="grid w-full grid-cols-1 gap-4 sm:grid-cols-2">
                {#each filteredEvents as event}
                    <Eventcard event={event} />
                {/each}
            </div>
        {:else}
            <p>No outreach opportunities are available that match your search criteria.</p>
        {/if}
    </div>
</main>
