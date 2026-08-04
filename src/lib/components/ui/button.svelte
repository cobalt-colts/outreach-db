<script lang="ts">
    import type { Snippet } from "svelte";
    import type { HTMLButtonAttributes } from "svelte/elements";

    let { children, variant = "default", ...attributes }: HTMLButtonAttributes & { children?: Snippet; variant?: string } = $props();
</script>

{#if variant === "default"}
    <button {...attributes} class="{attributes.class} border-2 border-black p-2 active:translate-y-px transition-all duration-100 ease-out flex flex-row gap-2">
        {@render children?.()}
    </button>
{:else if variant === "ghost"}
  <button {...attributes} class="{attributes.class} p-2 active:translate-y-px transition-all duration-100 ease-out flex flex-row gap-2 align-bottom">
      {@render children?.()}
  </button>
{/if}
