import { render, screen } from "@testing-library/react";
import { ChakraProvider, defaultSystem } from "@chakra-ui/react";
import { NotFound } from "../pages/NotFound";

function renderWithChakra(ui: React.ReactElement) {
  return render(<ChakraProvider value={defaultSystem}>{ui}</ChakraProvider>);
}

describe("NotFound", () => {
  it("renders 404 heading", () => {
    renderWithChakra(<NotFound />);
    expect(screen.getByText("404")).toBeInTheDocument();
  });

  it("renders page not found text", () => {
    renderWithChakra(<NotFound />);
    expect(screen.getByText("Page not found.")).toBeInTheDocument();
  });
});
