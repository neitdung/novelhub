"use client";

import { Box, Heading, VStack } from "@chakra-ui/react";
import { ExportPanel } from "@/components";

export default function ExportPage() {
  return (
    <Box p={8}>
      <VStack gap={6} align="stretch" maxW="700px">
        <Heading size="lg">Export</Heading>
        <ExportPanel />
      </VStack>
    </Box>
  );
}
