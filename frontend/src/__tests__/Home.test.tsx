import { render, screen } from "@testing-library/react";
import { ChakraProvider, defaultSystem } from "@chakra-ui/react";
import { MemoryRouter } from "react-router-dom";
import { Home } from "../pages/Home";

function renderWithProviders(ui: React.ReactElement) {
  return render(
    <ChakraProvider value={defaultSystem}>
      <MemoryRouter>{ui}</MemoryRouter>
    </ChakraProvider>,
  );
}

describe("Home", () => {
  it("renders the heading", () => {
    renderWithProviders(<Home />);
    expect(screen.getByText("NovelHub")).toBeInTheDocument();
  });

  it("renders the description", () => {
    renderWithProviders(<Home />);
    expect(
      screen.getByText(/Local-first novel analysis and wiki application/),
    ).toBeInTheDocument();
  });
});
