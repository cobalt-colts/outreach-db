<script lang="ts">
    import Button from "$lib/components/ui/button.svelte";

    import { LoaderCircle, Plus, X } from "@lucide/svelte"
    import Card from "../ui/card.svelte";
    import Input from "../ui/input.svelte";
    import ErrorMessage from "../ui/error.svelte";

    import Textarea from "../ui/textarea.svelte";
    import {apiRequest} from "$lib/auth.svelte";
    import {toast} from "svelte-sonner";

    let dialog = $state<HTMLDialogElement>()

    let error = $state("")

    let submitting: boolean = $state(false)

    // Mirrors the POST /api/events/create body, not the full read model.
    let event = $state({
        name: "",
        city: "",
        state: "",
        zip_code: "",
        description: "",
        link: "",
        tags: [] as string[]
    })

    let tags = $state("")

    function handleOutsideClick(event: Event): void {
        if (event.target === dialog) {
            dialog.close()
        }
    }

    async function createEvent(): Promise<void> {
        submitting = true;
        event.tags = tags.split(',').map(tag => tag.trim()).filter(Boolean)
        event.state = event.state.trim().toUpperCase()
        try {
            const response = await apiRequest("/api/events/create", {
                method: "POST",
                body: JSON.stringify(event),
                headers: {
                    "Content-Type": "application/json"
                }
            })

            const responseBody = await response.json();

            if (!response.ok) {
                console.error(response)
                error = responseBody.detail;
                submitting = false;
                return;
            }
            dialog?.close()
            toast.success("Successfully created opportunity!")
        } catch (e) {
            error = "Error creating opportunity, please try again."
            console.error(e)
        }
        submitting = false;
    }
</script>

<Button onclick={() => dialog?.showModal()}>
    <Plus /> Create Opportunity
</Button>

<dialog
    bind:this={dialog}
    onclick={handleOutsideClick}
    aria-label="Create event"
    class="fixed inset-0 m-0 h-dvh w-dvw max-h-none max-w-none place-items-center overflow-visible border-0 bg-transparent p-0 backdrop:bg-black/20 backdrop:backdrop-blur-xs open:grid open:animate-fade-in"
>
    <Card>
        <form class="flex w-full flex-col gap-4" onsubmit={createEvent}>
            <div class="flex w-full flex-row flex-1 min-w-0 justify-between">
                <h1 class="font-bold text-xl">Create Opportunity</h1>
                <button type="button" onclick={() => dialog?.close()} class="active:scale-95 transition-all duration-100">
                    <X class="self-center"/>
                </button>
            </div>
            <label for="name">Opportunity Name:</label>
            <Input bind:value={event.name} id="name" required placeholder="Bee Emporium Volunteering" />
            <label for="description">Opportunity Description:</label>
            <Textarea bind:value={event.description} id="description" required placeholder="Volunteer at this fun local event!" />
            <label for="city">Opportunity City:</label>
            <Input bind:value={event.city} id="city" required placeholder="Kansas City"/>
            <label for="state">Opportunity State (two letters):</label>
            <Input bind:value={event.state} id="state" required placeholder="MO"/>
            <label for="zip_code">Opportunity ZIP Code:</label>
            <Input bind:value={event.zip_code} id="zip_code" required placeholder="64111"/>
            <label for="link">Opportunity Link:</label>
            <Input bind:value={event.link} id="link" required placeholder="https://beeemporium.org/volunteer"/>
            <label for="tags">Opportunity Tags (separated by commas):</label>
            <Input bind:value={tags} id="tags" placeholder="Bees,Volunteering,Fun"/>
            {#if error}
                <ErrorMessage content={error} />
            {/if}
            <Button type="submit">
                {#if submitting}
                    <LoaderCircle class="animate-spin" /> Creating Opportunity
                {:else}
                    Create Opportunity
                {/if}
            </Button>
        </form>
    </Card>

</dialog>

<style>
    dialog[open]::backdrop {
        animation: backdrop-in 160ms ease-out both;
    }

    dialog[open] > :global(div) {
        animation: modal-in 180ms cubic-bezier(0.16, 1, 0.3, 1) both;
    }

    @keyframes backdrop-in {
        from { opacity: 0; }
        to { opacity: 1; }
    }

    @keyframes modal-in {
        from {
            opacity: 0;
            transform: translateY(0.75rem) scale(0.98);
        }

        to {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
    }

    @media (prefers-reduced-motion: reduce) {
        dialog[open]::backdrop,
        dialog[open] > :global(div) {
            animation: none;
        }
    }
</style>
