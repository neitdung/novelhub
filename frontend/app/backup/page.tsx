"use client";

import { Box, Heading, VStack } from "@chakra-ui/react";
import { EmptyState } from "@/components";

export default function BackupPage() {
  return (
    <Box p={8}>
      <VStack gap={6} align="stretch">
        <Heading size="lg">Backup &amp; Restore</Heading>
        <EmptyState
          title="Backup Manager"
          message="Create full backups of your novel library, validate backup integrity, and restore from previous backups."
        />
      </VStack>
    </Box>
  );
}
