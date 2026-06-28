"use client";

import { Box, Heading, VStack } from "@chakra-ui/react";
import { EmptyState } from "@/components";

export default function TimelinePage() {
  return (
    <Box p={8}>
      <VStack gap={6} align="stretch">
        <Heading size="lg">Timeline</Heading>
        <EmptyState
          title="Event Timeline"
          message="View novel events chronologically. Filter by chapter, event type, or importance to track the story progression."
        />
      </VStack>
    </Box>
  );
}
