<script lang="ts">
    import { page } from '$app/state';
    import { apiRequest } from '$lib/auth.svelte';
    import { onMount } from 'svelte';

    import ErrorMessage from '$lib/components/ui/error.svelte'
    import { LoaderCircle } from '@lucide/svelte';
    import type { OutreachEvent } from '$lib/events';

    const event_id = page.params.slug;

    let event = $state<OutreachEvent | null>(null);

    let errmsg: string = $state("");
    let loading: boolean = $state(false)

    async function getEvent(): Promise<void> {
        loading = true;
        try {
          const response = await apiRequest(`/api/events/get/${event_id}`, {
            method: "GET",
            headers: {
                Accept: "application/json",
            }
          })

          if (!response.ok) {
            console.error(response)
            errmsg = "Error fetching event."
            loading = false
            return;
          }

          event = await response.json()
        } catch (e) {
          console.error(e);
          errmsg = "Something went wrong, Please try again."
        }
        loading = false;
    }

    onMount(() => {
      getEvent();
    })
</script>
{#if errmsg}
    <div class="flex w-full min-w-0 m-5 justify-center flex-row">
        <ErrorMessage bind:content={errmsg} />
    </div>
{:else if loading}
    <div class="flex w-full min-w-0 m-5 justify-center flex-row">
        <p class="flex flex-row gap-2"><LoaderCircle class="animate-spin"/>Loading event</p>
    </div>
{:else if event}
    <div class="w-full items-center m-25 gap-5 flex-col flex">
        <h1 class="font-bold text-4xl">{event.name}</h1>
        <p class="text-md">{event.description}</p>
    </div>
{:else}
    <div class="flex w-full min-w-0 m-5 justify-center flex-row">
        <ErrorMessage content="Event not found." />
    </div>
{/if}
