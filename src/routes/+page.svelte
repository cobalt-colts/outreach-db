<script lang="ts">
    import {apiRequest} from "$lib/auth.svelte";
    import ErrorMessage from "$lib/components/ui/error.svelte";
    import Eventcard from "$lib/components/blocks/eventcard.svelte";
    import type { OutreachEvent } from "$lib/events";
    import {onMount} from "svelte";
    import Input from "$lib/components/ui/input.svelte";
    import Button from "$lib/components/ui/button.svelte";
    import { LoaderCircle } from "@lucide/svelte";

    let events: OutreachEvent[] = $state([]);
    let error: string | null = $state(null);
    let loading = $state(true);

    let searchbox: string = $state("");

    let filteredEvents = $derived(events.filter(event => {
      const search = searchbox.toLowerCase();
      return [
        event.name,
        event.description,
        event.location
        ].some(term => term.toLowerCase().includes(search))
    }))

    async function getOutreachEvents(): Promise<void> {
        loading = true;
        error = null;

        try {
            const response = await apiRequest("/api/events/get", {
                method: "GET",
                headers: {
                    Accept: "application/json",
                }
            })

            if (!response.ok) {
                const payload: unknown = await response.json().catch(() => null);
                const detail =
                    typeof payload === "object" && payload !== null && "detail" in payload
                        ? payload.detail
                        : null;
                throw new Error(
                    typeof detail === "string"
                        ? detail
                        : response.statusText || "Unable to fetch events."
                );
            }

            const payload: unknown = await response.json();
            if (!Array.isArray(payload)) {
                throw new Error("The events service returned an invalid response.");
            }

            events = payload as OutreachEvent[];
        } catch (e) {
            console.error(e);
            error = e instanceof Error ? e.message : "Unable to fetch events.";
            events = [];
        } finally {
            loading = false;
        }
    }

    onMount(() => {
        getOutreachEvents();
    })
</script>

<main>
    <div class="mx-auto my-5 flex max-w-xl flex-col items-center justify-center gap-5">
        <h1 class="mt-25 mb-25 text-center text-5xl font-bold">
            Browse outreach opportunities
        </h1>
        <div class="flex flex-row gap-3 w-full min-w-0">
            <Input bind:value={searchbox} placeholder="Search opportunities..."/>
        </div>
        {#if error}
            <ErrorMessage content={error} />
            <Button onclick={getOutreachEvents}>Try again</Button>
        {:else if loading}
            <LoaderCircle class="animate-spin" />
        {:else if events.length > 0}
            <div class="grid w-full grid-cols-1 gap-4 sm:grid-cols-2">
                {#each filteredEvents as event}
                    <Eventcard event={event} />
                {/each}
            </div>
        {:else}
            <p>No outreach opportunities are available.</p>
        {/if}
    </div>
</main>
