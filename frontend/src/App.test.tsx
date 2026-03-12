import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import App from "./App";

describe("App", () => {
  it("renders the NexusReach heading", () => {
    render(<App />);
    expect(screen.getByText("NexusReach")).toBeInTheDocument();
  });

  it("renders the tagline", () => {
    render(<App />);
    expect(
      screen.getByText("AI-powered influencer-brand intelligence platform")
    ).toBeInTheDocument();
  });
});
