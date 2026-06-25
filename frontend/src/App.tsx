import { ChakraProvider, defaultSystem } from "@chakra-ui/react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Layout } from "./components/Layout";
import { ThemeProvider } from "./context/ThemeContext";
import { Bookshelf } from "./pages/Bookshelf";
import { EntityBrowser } from "./pages/EntityBrowser";
import { Home } from "./pages/Home";
import { NotFound } from "./pages/NotFound";
import { Reader } from "./pages/Reader";
import { Settings } from "./pages/Settings";

export function App() {
  return (
    <ChakraProvider value={defaultSystem}>
      <ThemeProvider>
        <BrowserRouter>
          <Layout>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/bookshelf" element={<Bookshelf />} />
              <Route path="/novel/:id" element={<Reader />} />
              <Route
                path="/novel/:novelId/entities"
                element={<EntityBrowser />}
              />
              <Route path="/settings" element={<Settings />} />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </Layout>
        </BrowserRouter>
      </ThemeProvider>
    </ChakraProvider>
  );
}
