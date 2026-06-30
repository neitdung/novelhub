"use client";

import {
  Box,
  Badge,
  HStack,
  Link,
  Text,
  VStack,
  Collapsible,
  useDisclosure,
} from "@chakra-ui/react";

interface Citation {
  id?: number | string;
  text?: string;
  source?: string;
  chapter?: number | string;
  page?: number;
  entity_name?: string;
  entity_id?: number;
  confidence?: number;
  url?: string;
  [key: string]: unknown;
}

interface CitationPanelProps {
  citations: Citation[];
}

export function CitationPanel({ citations }: CitationPanelProps) {
  if (!citations || citations.length === 0) return null;

  return (
    <VStack align="stretch" gap={2} mt={2}>
      {citations.map((citation, idx) => (
        <CitationItem key={citation.id || idx} citation={citation} index={idx} />
      ))}
    </VStack>
  );
}

function CitationItem({
  citation,
  index,
}: {
  citation: Citation;
  index: number;
}) {
  const { open, onToggle } = useDisclosure({ defaultOpen: false });

  return (
    <Collapsible.Root open={open} onOpenChange={onToggle}>
      <Box borderWidth="1px" borderRadius="md" bg="chakra-subtle-bg">
        <Collapsible.Trigger asChild>
          <HStack
            px={3}
            py={2}
            cursor="pointer"
            justify="space-between"
            _hover={{ bg: "chakra-subtle-bg" }}
          >
            <HStack gap={2} flex={1} minH={0}>
              <Badge colorScheme="blue" fontSize="xs">
                [{index + 1}]
              </Badge>
              <Text
                fontSize="sm"
                flex={1}
                style={{
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                  whiteSpace: "nowrap",
                }}
              >
                {citation.text || citation.source || "Source"}
              </Text>
              {citation.confidence !== undefined && (
                <Badge
                  colorScheme={citation.confidence > 0.8 ? "green" : "yellow"}
                  fontSize="xs"
                >
                  {Math.round(citation.confidence * 100)}%
                </Badge>
              )}
            </HStack>
            <Text fontSize="xs" color="gray.500">
              {open ? "▲" : "▼"}
            </Text>
          </HStack>
        </Collapsible.Trigger>
        <Collapsible.Content>
          <VStack align="stretch" gap={2} px={3} pb={3}>
            {citation.text && (
              <Box>
                <Text fontSize="xs" fontWeight="bold" color="gray.500" mb={1}>
                  Quoted Text
                </Text>
                <Box
                  pl={3}
                  borderLeft="3px solid"
                  borderColor="blue.300"
                  fontSize="sm"
                  fontStyle="italic"
                  color="gray.600"
                >
                  {citation.text}
                </Box>
              </Box>
            )}
            <HStack gap={3} flexWrap="wrap">
              {citation.source && (
                <HStack gap={1}>
                  <Text fontSize="xs" fontWeight="bold" color="gray.500">
                    Source:
                  </Text>
                  <Text fontSize="xs">{citation.source}</Text>
                </HStack>
              )}
              {citation.chapter !== undefined && (
                <HStack gap={1}>
                  <Text fontSize="xs" fontWeight="bold" color="gray.500">
                    Chapter:
                  </Text>
                  <Text fontSize="xs">{String(citation.chapter)}</Text>
                </HStack>
              )}
              {citation.page !== undefined && (
                <HStack gap={1}>
                  <Text fontSize="xs" fontWeight="bold" color="gray.500">
                    Page:
                  </Text>
                  <Text fontSize="xs">{citation.page}</Text>
                </HStack>
              )}
              {citation.entity_name && (
                <HStack gap={1}>
                  <Text fontSize="xs" fontWeight="bold" color="gray.500">
                    Entity:
                  </Text>
                  <Badge colorScheme="purple" fontSize="xs">
                    {citation.entity_name}
                  </Badge>
                </HStack>
              )}
            </HStack>
            {citation.url && (
              <Link
                href={citation.url}
                target="_blank"
                rel="noopener noreferrer"
                fontSize="xs"
                color="blue.500"
              >
                View source →
              </Link>
            )}
          </VStack>
        </Collapsible.Content>
      </Box>
    </Collapsible.Root>
  );
}
