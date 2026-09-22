import type { ReactElement } from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import Dashboard from "../pages/Dashboard";
import * as api from "../services/api";

vi.spyOn(api, "listProjects").mockResolvedValue([]);

function renderWithProviders(ui: ReactElement) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter>{ui}</MemoryRouter>
    </QueryClientProvider>
  );
}

describe("Dashboard", () => {
  it("shows the first-time onboarding welcome when there are no projects", async () => {
    renderWithProviders(<Dashboard />);
    await waitFor(() => expect(screen.getByText("Welcome to CodeShieldAI")).toBeInTheDocument());
    expect(screen.getByText("Create your first project")).toBeInTheDocument();
  });
});
