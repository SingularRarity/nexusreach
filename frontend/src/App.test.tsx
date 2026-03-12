import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { describe, it, expect, beforeEach } from "vitest";
import App from "./App";
import { useAuthStore } from "@/stores/auth-store";

function renderApp(initialRoute = "/login") {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[initialRoute]}>
        <App />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("App", () => {
  beforeEach(() => {
    useAuthStore.getState().reset();
  });

  it("renders the login page by default for unauthenticated users", () => {
    renderApp("/login");
    expect(screen.getByText("Sign in to your account")).toBeInTheDocument();
  });

  it("renders the register page", () => {
    renderApp("/register");
    expect(screen.getByText("Create your account")).toBeInTheDocument();
  });

  it("redirects unauthenticated users to login", () => {
    renderApp("/dashboard");
    expect(screen.getByText("Sign in to your account")).toBeInTheDocument();
  });

  it("renders the NexusReach branding on login page", () => {
    renderApp("/login");
    expect(screen.getByText("NexusReach")).toBeInTheDocument();
  });
});
