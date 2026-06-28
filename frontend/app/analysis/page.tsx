"use client";

import { Box, Heading, VStack } from "@chakra-ui/react";
import { EmptyState } from "@/components";

export default function AnalysisPage() {
  return (
    <Box p={8}>
      <VStack gap={6} align="stretch">
        <Heading size="lg">Analysis</Heading>
        <EmptyState
          title="Analysis Dashboard"
          message="Run AI-powered analysis on your novels to extract entities, relationships, and generate wiki content. Select a novel to begin."
        />
      </VStack>
    </Box>
  );
}
