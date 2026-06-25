import { Box, Spinner, Text, VStack } from "@chakra-ui/react";

interface LoadingStateProps {
  message?: string;
}

export function LoadingState({ message = "Loading..." }: LoadingStateProps) {
  return (
    <Box p={8} display="flex" justifyContent="center" alignItems="center">
      <VStack gap={4}>
        <Spinner size="xl" color="blue.500" />
        <Text color="gray.600">{message}</Text>
      </VStack>
    </Box>
  );
}
