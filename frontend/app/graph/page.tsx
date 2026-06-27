"use client";

import { Box, Heading, VStack } from "@chakra-ui/react";
import { EmptyState } from "@/components";

export default function GraphPage() {
  return (
    <Box p={8}>
      <VStack gap={6} align="stretch">
        <Heading size="lg">Graph</Heading>
        <EmptyState
          title="Knowledge Graph"
          message="Visualize entity relationships, find shortest paths between characters, and explore factions in your novels."
        />
      </VStack>
    </Box>
  );
}
