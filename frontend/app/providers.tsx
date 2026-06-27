"use client";

import { ChakraProvider, defaultSystem } from "@chakra-ui/react";
import { Provider } from "react-redux";
import { store } from "@/store";
import { ThemeProvider } from "@/context/ThemeContext";
import { Layout } from "@/components/Layout";

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ChakraProvider value={defaultSystem}>
      <Provider store={store}>
        <ThemeProvider>
          <Layout>{children}</Layout>
        </ThemeProvider>
      </Provider>
    </ChakraProvider>
  );
}
