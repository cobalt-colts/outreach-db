<script lang="ts">
    let name = $state('')
</script>

<h1>Welcome to SvelteKit</h1>
<p>Visit <a href="https://svelte.dev/docs/kit">svelte.dev/docs/kit</a> to read the documentation</p>
<input bind:value={name} type="text" placeholder="Your name" />
{#if name}
    <p>Hello, {name}</p>
{/if}
