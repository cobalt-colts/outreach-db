<script lang="ts">
    import type { Snippet } from "svelte";
    import type { HTMLButtonAttributes } from "svelte/elements";

    let { children, ...attributes }: HTMLButtonAttributes & { children?: Snippet } = $props();
</script>

<button {...attributes} class="{attributes.class} border-2 border-black p-2 active:translate-y-px transition-all duration-100 ease-out">
    {@render children?.()}
</button>
