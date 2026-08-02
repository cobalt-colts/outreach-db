<script lang="ts">
    import Navbar from "$lib/components/blocks/navbar.svelte";
    import {apiRequest} from "$lib/auth.svelte";
    import ErrorMessage from "$lib/components/ui/error.svelte";
    import Eventcard from "\$lib/components/blocks/eventcard.svelte";
    import type { Event } from "$lib/components/events";
    import {onMount} from "svelte";
    import Input from "$lib/components/ui/input.svelte";
    import Button from "$lib/components/ui/button.svelte";

    let events: Event[] | undefined = $state();

    let error: string = $state("")

    let searchbox: string = $state("");

    async function getOutreachEvents(): Promise<void> {
        try {
            const response = await apiRequest("/api/events/get", {
                method: "GET",
                headers: {
                    Accept: "application/json",
                }
            })

            if (!response.ok) {
                const payload = await response.json().catch(() => null);
                throw new Error(payload?.detail ?? response.statusText ?? "Unable to fetch events.");
            }

            events = await response.json();
            error = "";
        } catch (e) {
            console.error(e);
            error = e instanceof Error ? e.message : "Unable to fetch events.";
        }
    }

    onMount(() => {
        getOutreachEvents();
    })
</script>

<main>
    <div class="mx-auto my-5 flex max-w-xl flex-col items-center justify-center gap-5">
        <h1 class="mt-25 mb-25 text-center text-5xl font-bold">
            Browse outreach events
        </h1>
        <div class="flex flex-row gap-3 w-full min-w-0">
            <Input bind:value={searchbox} placeholder="Search events..."/>
            <Button>
                Filter
            </Button>
        </div>
        {#if events}
            <div class="mx-auto grid grid-cols-2 justify-items-center gap-4 gap-y-2">
                {#each events as event}
                    <Eventcard event={event} />
                {/each}
            </div>
        {:else if error}
            <ErrorMessage bind:content={error} />
        {:else}
            <p class="animate-spin">fetching events</p>
        {/if}

    </div>
</main>
