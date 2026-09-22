import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import { Sidebar } from "../layouts/Sidebar";

describe("Sidebar navigation", () => {
  it("renders all primary nav items", () => {
    const client = new QueryClient();
    render(
      <QueryClientProvider client={client}>
        <MemoryRouter>
          <Sidebar />
        </MemoryRouter>
      </QueryClientProvider>
    );
    ["Overview", "Projects", "Scans", "Findings", "Attack Surface", "Reports", "Knowledge", "Settings"].forEach((label) => {
      expect(screen.getByText(label)).toBeInTheDocument();
    });
  });
});
