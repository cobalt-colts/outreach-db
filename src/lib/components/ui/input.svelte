<script lang="ts">
    import type { HTMLInputAttributes } from "svelte/elements";

    let { value = $bindable(), ...attributes }: HTMLInputAttributes = $props();
</script>

<input {...attributes} bind:value class={["w-full border-2 border-black p-2", attributes.class]} />
