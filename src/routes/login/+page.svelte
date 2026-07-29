<script lang="ts">
    import {getAuthToken, signIn} from "$lib/auth.svelte";

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
        } catch (cause) {
            error = cause instanceof Error ? cause.message : "Unable to sign in.";
        } finally {
            submitting = false;
        }
    }

</script>

{#if !getAuthToken()}
    <main class="flex min-h-screen items-center justify-center p-6">
        <form class="flex w-full max-w-sm flex-col gap-4 rounded-lg border-2 border-black p-6" onsubmit={logIn}>
            <h1 class="text-2xl font-extrabold">Login</h1>

            <input class="w-full border-2 border-black p-2" bind:value={email} type="email" autocomplete="email" placeholder="Email" required />
            <input class="w-full border-2 border-black p-2" bind:value={password} type="password" autocomplete="current-password" placeholder="Password" required />
            <button class="border-2 border-black p-2" type="submit" disabled={submitting}>
                {submitting ? "Logging in…" : "Login"}
            </button>
            {#if error}
                <p role="alert">{error}</p>
            {/if}
        </form>
    </main>
{:else}
    <main class="min-h-screen items-center justify-center p-6">
        <h1 class="text-2xl font-extrabold">logged in!</h1>
        <p>You are logged in.</p>
        <p>auth token: {getAuthToken()}</p>
    </main>
{/if}
