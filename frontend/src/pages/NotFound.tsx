import { Box, Heading, Text } from "@chakra-ui/react";

export function NotFound() {
  return (
    <Box p={8} textAlign="center">
      <Heading size="xl">404</Heading>
      <Text mt={4} color="gray.600">
        Page not found.
      </Text>
    </Box>
  );
}
