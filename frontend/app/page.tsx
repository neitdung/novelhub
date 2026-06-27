"use client";

import { Box, Heading, HStack, Text, VStack } from "@chakra-ui/react";
import Link from "next/link";

export default function Home() {
  return (
    <Box p={8}>
      <VStack gap={6} align="center">
        <Heading size="xl">NovelHub</Heading>
        <Text fontSize="lg" color="gray.600" textAlign="center" maxW="600px">
          Local-first novel analysis and wiki application. Upload, read, and
          analyze your novels with AI-powered insights.
        </Text>
        <HStack>
          <Link
            href="/bookshelf"
            style={{
              padding: "12px 24px",
              background: "var(--chakra-colors-blue-500)",
              color: "white",
              borderRadius: "8px",
              fontWeight: "600",
              textDecoration: "none",
            }}
          >
            Go to Bookshelf
          </Link>
        </HStack>
      </VStack>
    </Box>
  );
}
