"use client";

import { Box, Heading, VStack } from "@chakra-ui/react";
import { EmptyState } from "@/components";

export default function ExportPage() {
  return (
    <Box p={8}>
      <VStack gap={6} align="stretch">
        <Heading size="lg">Export</Heading>
        <EmptyState
          title="Export Tools"
          message="Export novels as Markdown, JSON knowledge base data, or wiki content for sharing and offline use."
        />
      </VStack>
    </Box>
  );
}
