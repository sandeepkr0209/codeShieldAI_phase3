import { describe, it, expect, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import App from "../App";
import { AuthProvider } from "../hooks/useAuth";
import * as api from "../services/api";

function renderApp(initialPath: string) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={[initialPath]}>
        <AuthProvider>
          <App />
        </AuthProvider>
      </MemoryRouter>
    </QueryClientProvider>
  );
}

describe("Public vs protected routing", () => {
  it("shows the public landing page at / without authentication", async () => {
    vi.spyOn(api, "getCurrentUser").mockRejectedValue(new Error("unauthenticated"));
    renderApp("/");
    await waitFor(() => expect(screen.getByText(/Find vulnerabilities/i)).toBeInTheDocument());
  });

  it("redirects an unauthenticated visitor away from a protected route to /login", async () => {
    vi.spyOn(api, "getCurrentUser").mockRejectedValue(new Error("unauthenticated"));
    renderApp("/dashboard");
    await waitFor(() => expect(screen.getByText("Welcome back")).toBeInTheDocument());
  });

  it("does not force login to view the public site", async () => {
    vi.spyOn(api, "getCurrentUser").mockRejectedValue(new Error("unauthenticated"));
    renderApp("/");
    await waitFor(() => expect(screen.queryByText("Welcome back")).not.toBeInTheDocument());
  });
});
