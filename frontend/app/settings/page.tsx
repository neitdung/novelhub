"use client";

import { Box, Heading, VStack } from "@chakra-ui/react";
import { ProviderSettings } from "@/components";

export default function SettingsPage() {
  return (
    <Box p={8}>
      <VStack gap={6} align="stretch" maxW="700px">
        <Heading size="lg">Settings</Heading>
        <ProviderSettings />
      </VStack>
    </Box>
  );
}
