"use client";

import { Box, Heading, VStack } from "@chakra-ui/react";
import { EmptyState } from "@/components";

export default function WikiPage() {
  return (
    <Box p={8}>
      <VStack gap={6} align="stretch">
        <Heading size="lg">Wiki</Heading>
        <EmptyState
          title="Wiki Browser"
          message="Browse auto-generated wiki pages for entities. Search, filter, and regenerate wiki content on demand."
        />
      </VStack>
    </Box>
  );
}
