"use client";

import { Box, Heading, VStack } from "@chakra-ui/react";
import { ErrorState, LoadingState, EmptyState } from "@/components";

export default function EntitiesPage() {
  return (
    <Box p={8}>
      <VStack gap={6} align="stretch">
        <Heading size="lg">Entities</Heading>
        <EmptyState
          title="Entity Browser"
          message="Browse and manage entities across all novels. Select a novel to view its characters, locations, items, and more."
        />
      </VStack>
    </Box>
  );
}
