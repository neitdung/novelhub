"use client";

import { Box, Flex, HStack } from "@chakra-ui/react";
import Link from "next/link";
import type { ReactNode } from "react";
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
            <Link href="/" style={{ fontWeight: "bold", fontSize: "1.25rem" }}>
              NovelHub
            </Link>
            <Link href="/bookshelf">Bookshelf</Link>
            <Link href="/settings">Settings</Link>
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
