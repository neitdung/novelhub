"use client";

import { Box, Flex, Heading, Text, VStack } from "@chakra-ui/react";
import Link from "next/link";

const QUICK_LINKS = [
  { label: "Bookshelf", href: "/bookshelf", desc: "Browse and upload novels" },
  { label: "Entities", href: "/entities", desc: "Manage character and entity knowledge base" },
  { label: "Wiki", href: "/wiki", desc: "View auto-generated wiki pages" },
  { label: "Analysis", href: "/analysis", desc: "Run AI-powered novel analysis" },
  { label: "Chat", href: "/chat", desc: "Chat with AI about your novels" },
  { label: "Graph", href: "/graph", desc: "Visualize entity relationships" },
  { label: "Timeline", href: "/timeline", desc: "Browse story events chronologically" },
  { label: "Settings", href: "/settings", desc: "Configure LLM and app settings" },
  { label: "Backup", href: "/backup", desc: "Backup and restore your library" },
  { label: "Export", href: "/export", desc: "Export novels and wiki content" },
];

export default function Home() {
  return (
    <Box p={8}>
      <VStack gap={6} align="center" mb={10}>
        <Heading size="xl">NovelHub</Heading>
        <Text fontSize="lg" color="gray.600" textAlign="center" maxW="600px">
          Local-first novel analysis and wiki application. Upload, read, and
          analyze your novels with AI-powered insights.
        </Text>
      </VStack>

      <Flex wrap="wrap" gap={4} justify="center" maxW="800px" mx="auto">
        {QUICK_LINKS.map((link) => (
          <Link key={link.href} href={link.href} style={{ textDecoration: "none" }}>
            <Box
              p={4}
              borderWidth="1px"
              borderRadius="lg"
              borderColor="gray.200"
              _hover={{
                borderColor: "blue.300",
                shadow: "md",
                bg: "blue.50",
              }}
              transition="all 0.15s"
              minW="200px"
              flex={1}
            >
              <Heading size="sm" mb={1}>
                {link.label}
              </Heading>
              <Text fontSize="sm" color="gray.500">
                {link.desc}
              </Text>
            </Box>
          </Link>
        ))}
      </Flex>
    </Box>
  );
}
