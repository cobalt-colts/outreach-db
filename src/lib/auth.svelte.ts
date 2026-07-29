let authToken = $state<string | null>(
    typeof window === "undefined" ? null : localStorage.getItem("authToken")
);

export function getAuthToken(): string | null {
    return authToken;
}

export async function signIn(email: string, password: string): Promise<void> {
    const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
    });

    if (!response.ok) {
        const payload = await response.json().catch(() => null);
        throw new Error(payload?.detail ?? "Unable to sign in.");
    }

    const data: { access_token: string; token_type: string } = await response.json();
    authToken = data.access_token;
    localStorage.setItem("authToken", authToken);
}

export function signOut(): void {
    authToken = null;
    localStorage.removeItem("authToken");
}

export async function apiRequest(url: string, options: RequestInit = {}): Promise<Response> {
    const headers = new Headers(options.headers);
    if (authToken) {
        headers.set("Authorization", `Bearer ${authToken}`);
    }

    return await fetch(url, {
        ...options,
        headers,
    });
}
