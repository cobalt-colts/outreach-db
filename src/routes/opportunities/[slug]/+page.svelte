<script lang="ts">
    import { Check, Copy, Link, MapPin } from '@lucide/svelte';
    import { formatLocation, type OutreachEvent } from '$lib/events';
    import Button from '$lib/components/ui/button.svelte';

    let { data }: { data: { event: OutreachEvent } } = $props();
    let copied : boolean = $state(false)

    async function copyLink(): Promise<void> {
        navigator.clipboard.writeText(window.location.href)
        copied = true;
    }

</script>

<svelte:head>
    <title>{data.event.name} | Outreach DB</title>
    <meta name="description" content={data.event.description} />
    <meta property="og:title" content={data.event.name} />
    <meta property="og:description" content={data.event.description} />
    <meta property="og:type" content="website" />
</svelte:head>

<div class="mx-auto flex w-full max-w-3xl flex-col items-center gap-5 px-5 py-12 text-start sm:py-20">
        <h1 class="mb-20 w-full max-w-2xl text-center text-6xl font-bold">{data.event.name}</h1>
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
        <p class="max-w-2xl text-md">{data.event.description}</p>
        <p class="flex w-full max-w-2xl flex-row gap-2"><MapPin class="size-5 self-center"/>{formatLocation(data.event)} {data.event.zip_code}</p>
        <p class="flex w-full max-w-2xl flex-row gap-2"><Link class="size-5 self-center"/><a href="{data.event.link}" class="hover:underline" target="_blank">{data.event.link}</a></p>
        {#if data.event.tags.length > 0}
            <ul class="flex w-full max-w-2xl flex-row flex-wrap gap-2">
                {#each data.event.tags as tag}
                    <li class="rounded-full bg-neutral-100 px-3 py-1 text-sm text-neutral-700">{tag}</li>
                {/each}
            </ul>
        {/if}
</div>
