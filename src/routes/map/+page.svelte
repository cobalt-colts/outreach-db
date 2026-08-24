<script lang="ts">
    import Map from "$lib/components/blocks/map.svelte"
    import Seo from "$lib/components/ui/seo.svelte";
</script>

<Seo title="Outreach Map" description="Map of outreach events across the United States."/>

<main>
    <div class="mx-auto my-5 flex max-w-xl flex-col items-center justify-center gap-5">
        <h1 class="mt-25 mb-25 text-center text-5xl font-bold">
            Outreach Map
        </h1>
    </div>
    <div class="mx-4 mb-8 sm:mx-6">
        <Map />
    </div>
</main>
