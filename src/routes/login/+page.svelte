<script lang="ts">
    import { getAuthToken, signIn } from "$lib/auth.svelte";
    import Button from "$lib/components/ui/button.svelte";
    import Card from "$lib/components/ui/card.svelte";
    import Input from "$lib/components/ui/input.svelte";
    import { LoaderCircle } from "@lucide/svelte";
    import {onMount} from "svelte";

    let email = $state("");
    let password = $state("");
    let error = $state("");
    let submitting = $state(false);

    async function logIn(event: SubmitEvent): Promise<void> {
        event.preventDefault();
        error = "";
        submitting = true;
        try {
            await signIn(email, password);
            password = "";
            window.location.href = "/";
        } catch (cause) {
            error = cause instanceof Error ? cause.message : "Unable to sign in.";
        } finally {
            submitting = false;
        }
    }

    onMount(() => {
        if (getAuthToken()) {
            window.location.href = "/";
        }
    })
</script>

<main class="flex items-center align-middle justify-center p-6">
    <Card>
        <form onsubmit={logIn} class="flex flex-col gap-4">
            <h1 class="text-2xl font-extrabold">Login</h1>

            <Input bind:value={email} type="email" autocomplete="email" placeholder="Email" required />
            <Input bind:value={password} type="password" autocomplete="current-password" placeholder="Password" required />
            <Button type="submit" disabled={submitting}>
                {#if submitting}
                    <LoaderCircle class="animate-spin"/>
                    Logging in
                {:else}
                    Login
                {/if}
            </Button>
            {#if error}
                <p role="alert">{error}</p>
            {/if}
        </form>
    </Card>
</main>