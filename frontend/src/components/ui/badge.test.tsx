import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { Badge } from "./badge";

describe("Badge", () => {
  it("renders children", () => {
    render(<Badge>Ready</Badge>);
    expect(screen.getByText("Ready")).toBeInTheDocument();
  });

  it("applies success variant", () => {
    render(<Badge variant="success">Done</Badge>);
    const badge = screen.getByText("Done");
    expect(badge.className).toContain("bg-green-100");
  });

  it("applies error variant", () => {
    render(<Badge variant="error">Failed</Badge>);
    const badge = screen.getByText("Failed");
    expect(badge.className).toContain("bg-red-100");
  });
});
