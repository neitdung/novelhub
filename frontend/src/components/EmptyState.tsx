import { Box, Text, VStack } from "@chakra-ui/react";

interface EmptyStateProps {
  title?: string;
  message?: string;
  action?: {
    label: string;
    onClick: () => void;
  };
}

export function EmptyState({
  title = "No data",
  message = "There's nothing to display yet.",
  action,
}: EmptyStateProps) {
  return (
    <Box p={8} display="flex" justifyContent="center" alignItems="center">
      <VStack gap={4}>
        <Text color="gray.500" fontSize="lg" fontWeight="bold">
          {title}
        </Text>
        <Text color="gray.600">{message}</Text>
        {action && (
          <Box
            as="button"
            px={4}
            py={2}
            bg="blue.500"
            color="white"
            borderRadius="md"
            _hover={{ bg: "blue.600" }}
            onClick={action.onClick}
          >
            {action.label}
          </Box>
        )}
      </VStack>
    </Box>
  );
}
