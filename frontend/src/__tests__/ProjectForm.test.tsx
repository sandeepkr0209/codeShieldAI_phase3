import type { ReactElement } from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import Projects from "../pages/Projects";
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

describe("New project form", () => {
  it("shows a validation error when name is empty", async () => {
    renderWithProviders(<Projects />);
    await waitFor(() => screen.getByText("New project"));
    fireEvent.click(screen.getAllByText("New project")[0]);
    fireEvent.click(screen.getByText("Create project"));
    expect(await screen.findByText("Project name is required.")).toBeInTheDocument();
  });
});
