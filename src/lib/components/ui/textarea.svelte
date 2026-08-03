<script lang="ts">
    import type { HTMLTextareaAttributes } from "svelte/elements";

    let { value = $bindable(), ...attributes }: HTMLTextareaAttributes = $props();
</script>

<textarea {...attributes} bind:value class={["w-full border-2 border-black p-2", attributes.class]}></textarea>
