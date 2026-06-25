import { Box, Flex, HStack } from "@chakra-ui/react";
import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import { ThemeToggle } from "./ThemeToggle";

interface LayoutProps {
  children: ReactNode;
}

export function Layout({ children }: LayoutProps) {
  return (
    <Flex direction="column" minH="100vh">
      <Box as="nav" p={4} borderBottom="1px solid" borderColor="gray.200">
        <HStack justify="space-between">
          <HStack gap={6}>
            <Link to="/">
              <Box fontWeight="bold" fontSize="lg">
                NovelHub
              </Box>
            </Link>
            <Link to="/bookshelf">Bookshelf</Link>
            <Link to="/settings">Settings</Link>
          </HStack>
          <ThemeToggle />
        </HStack>
      </Box>
      <Box flex={1} p={4}>
        {children}
      </Box>
    </Flex>
  );
}
