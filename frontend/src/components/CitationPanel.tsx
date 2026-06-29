"use client";

import { Box, HStack, Text, VStack } from "@chakra-ui/react";

export interface CitationData {
  source?: string;
  chapter_id?: number;
  chapter_title?: string;
  entity_id?: number;
  entity_name?: string;
  text?: string;
  page?: number;
  url?: string;
}

interface CitationPanelProps {
  citations: CitationData[];
}

export function CitationPanel({ citations }: CitationPanelProps) {
  if (!citations || citations.length === 0) return null;

  return (
    <Box
      mt={3}
      p={3}
      bg="yellow.50"
      borderRadius="md"
      borderWidth="1px"
      borderColor="yellow.200"
      _dark={{ bg: "yellow.900", borderColor: "yellow.700" }}
    >
      <Text fontSize="xs" fontWeight="bold" color="yellow.700" mb={2} _dark={{ color: "yellow.300" }}>
        📖 Sources
      </Text>
      <VStack gap={2} align="stretch">
        {citations.map((citation, idx) => (
          <CitationItem key={idx} citation={citation} index={idx + 1} />
        ))}
      </VStack>
    </Box>
  );
}

function CitationItem({ citation, index }: { citation: CitationData; index: number }) {
  const label =
    citation.entity_name ||
    citation.chapter_title ||
    citation.source ||
    `Source ${index}`;

  const detail = citation.text
    ? citation.text.length > 120
      ? citation.text.slice(0, 120) + "..."
      : citation.text
    : null;

  const href = citation.url || (citation.chapter_id ? `/novel/${citation.chapter_id}` : undefined);

  return (
    <HStack gap={2} align="flex-start">
      <Text
        as="span"
        fontSize="xs"
        fontWeight="bold"
        color="yellow.600"
        minW="20px"
        _dark={{ color: "yellow.400" }}
      >
        [{index}]
      </Text>
      <Box>
        {href ? (
          <Box
            css={{
              fontSize: "sm",
              fontWeight: "medium",
              color: "blue.600",
              textDecoration: "underline",
              cursor: "pointer",
              _dark: { color: "blue.300" },
            }}
          >
            <a href={href} target="_blank" rel="noopener noreferrer" style={{ color: "inherit", textDecoration: "inherit" }}>
              {label}
            </a>
          </Box>
        ) : (
          <Text fontSize="sm" fontWeight="medium">
            {label}
          </Text>
        )}
        {citation.source && citation.source !== label && (
          <Text fontSize="xs" color="gray.500">
            via {citation.source}
          </Text>
        )}
        {detail && (
          <Text fontSize="xs" color="gray.600" mt={0.5} fontStyle="italic">
            &ldquo;{detail}&rdquo;
          </Text>
        )}
      </Box>
    </HStack>
  );
}
