"use client";

import { Box, Heading, VStack } from "@chakra-ui/react";
import { BackupRestore } from "@/components";

export default function BackupPage() {
  return (
    <Box p={8}>
      <VStack gap={6} align="stretch" maxW="700px">
        <Heading size="lg">Backup &amp; Restore</Heading>
        <BackupRestore />
      </VStack>
    </Box>
  );
}
