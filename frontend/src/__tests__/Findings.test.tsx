import type { ReactElement } from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import Findings from "../pages/Findings";
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

describe("Findings page", () => {
  it("shows an empty state when there are no findings", async () => {
    renderWithProviders(<Findings />);
    await waitFor(() => expect(screen.getByText("No verified findings detected")).toBeInTheDocument());
  });
});
