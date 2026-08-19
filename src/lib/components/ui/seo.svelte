<script lang="ts">
    let { title, description }: { title: string; description: string } = $props();
</script>

<svelte:head>
    <title>{title}</title>
    <meta name="description" content={description} />
    <meta property="og:title" content={title} />
    <meta property="og:description" content={description} />
</svelte:head>
