import { Box, Heading, HStack, Text, VStack } from "@chakra-ui/react";
import { Link } from "react-router-dom";

export function Home() {
  return (
    <Box p={8}>
      <VStack gap={6} align="center">
        <Heading size="xl">NovelHub</Heading>
        <Text fontSize="lg" color="gray.600" textAlign="center" maxW="600px">
          Local-first novel analysis and wiki application. Upload, read, and
          analyze your novels with AI-powered insights.
        </Text>
        <HStack>
          <Link to="/bookshelf">
            <Box
              as="button"
              px={6}
              py={3}
              bg="blue.500"
              color="white"
              borderRadius="md"
              _hover={{ bg: "blue.600" }}
            >
              Go to Bookshelf
            </Box>
          </Link>
        </HStack>
      </VStack>
    </Box>
  );
}
