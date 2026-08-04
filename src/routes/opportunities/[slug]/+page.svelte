<script lang="ts">
    import { page } from '$app/state';
    import { apiRequest } from '$lib/auth.svelte';
    import { onMount } from 'svelte';

    import ErrorMessage from '$lib/components/ui/error.svelte'
    import { Check, Copy, Link, LoaderCircle, MapPin } from '@lucide/svelte';
    import type { OutreachEvent } from '$lib/events';
    import Button from '$lib/components/ui/button.svelte';

    const event_id = page.params.slug;

    let event = $state<OutreachEvent | null>(null);

    let errmsg: string = $state("");
    let loading: boolean = $state(false)
    let copied : boolean = $state(false)

    async function copyLink(): Promise<void> {
        navigator.clipboard.writeText(window.location.href)
        copied = true;
    }

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
            errmsg = "Error fetching opportunity."
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
    <div class="mx-auto flex w-full max-w-xl justify-center px-5 py-12">
        <ErrorMessage bind:content={errmsg} />
    </div>
{:else if loading}
    <div class="mx-auto flex w-full max-w-xl justify-center px-5 py-12">
        <p class="flex flex-row gap-2"><LoaderCircle class="animate-spin"/>Loading opportunity</p>
    </div>
{:else if event}
    <div class="mx-auto flex w-full max-w-3xl flex-col items-center gap-5 px-5 py-12 text-start sm:py-20">
        <h1 class="mb-20 w-full max-w-2xl text-center text-6xl font-bold">{event.name}</h1>
        <div class="w-full border-b border-neutral-400 flex flex-row justify-between">
            <Button variant="ghost" onclick={copyLink}>
                {#if !copied}
                <Copy class="size-4 self-center"/>
                Copy Event Link
                {:else}
                <Check class="size-4 self-center"/>
                Copied!
                {/if}
            </Button>
        </div>
        <p class="max-w-2xl text-md">{event.description}</p>
        <p class="flex w-full max-w-2xl flex-row gap-2"><MapPin class="size-5 self-center"/>{event.location}</p>
        <p class="flex w-full max-w-2xl flex-row gap-2"><Link class="size-5 self-center"/><a href="{event.link}" class="hover:border-b" target="_blank">{event.link}</a></p>
    </div>
{:else}
    <div class="mx-auto flex w-full max-w-xl justify-center px-5 py-12">
        <ErrorMessage content="Opportunity not found." />
    </div>
{/if}
