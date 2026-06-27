"use client";

import { Box, Text, VStack } from "@chakra-ui/react";

interface ErrorStateProps {
  message?: string;
  onRetry?: () => void;
}

export function ErrorState({
  message = "Something went wrong",
  onRetry,
}: ErrorStateProps) {
  return (
    <Box p={8} display="flex" justifyContent="center" alignItems="center">
      <VStack gap={4}>
        <Text color="red.500" fontSize="lg" fontWeight="bold">
          Error
        </Text>
        <Text color="gray.600">{message}</Text>
        {onRetry && (
          <Box
            as="button"
            px={4}
            py={2}
            bg="blue.500"
            color="white"
            borderRadius="md"
            _hover={{ bg: "blue.600" }}
            onClick={onRetry}
          >
            Try Again
          </Box>
        )}
      </VStack>
    </Box>
  );
}
