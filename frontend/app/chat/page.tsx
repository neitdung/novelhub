"use client";

import { Box, Heading, VStack } from "@chakra-ui/react";
import { EmptyState } from "@/components";

export default function ChatPage() {
  return (
    <Box p={8}>
      <VStack gap={6} align="stretch">
        <Heading size="lg">Chat</Heading>
        <EmptyState
          title="Chat Interface"
          message="Chat with AI about your novels. Ask questions, search entities, and explore story details through natural conversation."
        />
      </VStack>
    </Box>
  );
}
