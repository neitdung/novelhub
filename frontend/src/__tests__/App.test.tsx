import { render, screen } from "@testing-library/react";
import { Provider } from "react-redux";
import { ChakraProvider, defaultSystem } from "@chakra-ui/react";
import { MemoryRouter } from "react-router-dom";
import { store } from "../store";
import { ThemeProvider } from "../context/ThemeContext";
import { Layout } from "../components/Layout";
import { Home } from "../pages/Home";

function renderWithProviders(ui: React.ReactElement) {
  return render(
    <Provider store={store}>
      <ChakraProvider value={defaultSystem}>
        <ThemeProvider>
          <MemoryRouter>
            <Layout>{ui}</Layout>
          </MemoryRouter>
        </ThemeProvider>
      </ChakraProvider>
    </Provider>,
  );
}

describe("App integration", () => {
  it("renders the home page within layout", () => {
    renderWithProviders(<Home />);
    expect(screen.getAllByText("NovelHub").length).toBeGreaterThanOrEqual(1);
  });

  it("renders the description", () => {
    renderWithProviders(<Home />);
    expect(
      screen.getByText(/Local-first novel analysis and wiki application/),
    ).toBeInTheDocument();
  });
});
