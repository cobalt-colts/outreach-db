<script lang="ts">
    import type { Snippet } from "svelte";
    import type { HTMLButtonAttributes } from "svelte/elements";

    let { children, ...attributes }: HTMLButtonAttributes & { children?: Snippet } = $props();
</script>

<button {...attributes} class="">
    {@render children?.()}
</button>
