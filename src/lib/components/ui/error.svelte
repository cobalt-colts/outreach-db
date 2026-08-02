<script lang="ts">

    let { content = $bindable() }: {content: string} = $props()
</script>

<div class="border border-red-500 flex flex-col text-red-500 p-3 gap-3 max-w-xl">
    <p class="text-md">{content}</p>
</div>