"use client";

import { useParams, useRouter } from "next/navigation";
import {
  Box,
  Heading,
  Text,
  VStack,
  HStack,
  Badge,
  Spinner,
} from "@chakra-ui/react";
import Link from "next/link";
import { useState } from "react";
import {
  useGetWikiPageQuery,
  useDeleteWikiPageMutation,
  useGetEntitiesQuery,
} from "@/store/api";

export default function WikiPageDetail() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const pageId = Number(params.id);

  const { data: wikiPage, isLoading, error } = useGetWikiPageQuery(pageId);
  const [deleteWikiPage] = useDeleteWikiPageMutation();
  const [deleting, setDeleting] = useState(false);

  // Fetch the entity linked to this wiki page for backlinks
  const { data: entitiesData } = useGetEntitiesQuery(
    { novelId: wikiPage?.novel_id ?? 0, limit: 100, offset: 0 },
    { skip: !wikiPage },
  );
  const linkedEntity = entitiesData?.entities?.find(
    (e) => e.id === wikiPage?.entity_id,
  );

  const handleDelete = async () => {
    if (deleting) return;
    if (!confirm(`Delete wiki page "${wikiPage?.title}"? This cannot be undone.`))
      return;
    setDeleting(true);
    try {
      await deleteWikiPage(pageId);
      router.push("/wiki");
    } catch {
      setDeleting(false);
    }
  };

  if (isLoading) {
    return (
      <Box p={8}>
        <Spinner size="xl" />
      </Box>
    );
  }

  if (error || !wikiPage) {
    return (
      <Box p={8}>
        <VStack gap={4} align="stretch">
          <Link
            href="/wiki"
            style={{
              color: "var(--chakra-colors-blue-500)",
              textDecoration: "none",
            }}
          >
            &larr; Back to Wiki
          </Link>
          <Text color="red.500">Wiki page not found.</Text>
        </VStack>
      </Box>
    );
  }

  // Simple markdown-like rendering: render line breaks and basic formatting
  const renderContent = (content: string) => {
    return content.split("\n").map((line, i) => {
      // Headers
      if (line.startsWith("### ")) {
        return (
          <Text key={i} fontSize="md" fontWeight="bold" mt={3} mb={1}>
            {line.slice(4)}
          </Text>
        );
      }
      if (line.startsWith("## ")) {
        return (
          <Text key={i} fontSize="lg" fontWeight="bold" mt={4} mb={2}>
            {line.slice(3)}
          </Text>
        );
      }
      if (line.startsWith("# ")) {
        return (
          <Text key={i} fontSize="xl" fontWeight="bold" mt={4} mb={2}>
            {line.slice(2)}
          </Text>
        );
      }
      // Horizontal rule
      if (line.trim() === "---") {
        return <Box key={i} borderTop="1px solid" borderColor="gray.200" my={3} />;
      }
      // Empty line
      if (line.trim() === "") {
        return <Box key={i} h={3} />;
      }
      // Regular text (with basic link detection)
      return (
        <Text key={i} lineHeight="tall" mb={1}>
          {line}
        </Text>
      );
    });
  };

  const totalPages = Math.max(1, Math.ceil((wikiPage.content?.length || 0) / 2000));

  return (
    <Box p={8}>
      <VStack gap={6} align="stretch">
        {/* Back link */}
        <Link
          href="/wiki"
          style={{
            color: "var(--chakra-colors-blue-500)",
            textDecoration: "none",
            fontSize: "14px",
          }}
        >
          &larr; Back to Wiki
        </Link>

        {/* Header */}
        <HStack justify="space-between" align="flex-start" flexWrap="wrap" gap={4}>
          <VStack align="flex-start" gap={2}>
            <Heading size="xl">{wikiPage.title}</Heading>
            <HStack gap={3} flexWrap="wrap">
              <Badge
                colorPalette={wikiPage.is_published ? "green" : "yellow"}
                px={2}
                py={1}
              >
                {wikiPage.is_published ? "Published" : "Draft"}
              </Badge>
              <Badge colorPalette="blue" px={2} py={1}>
                v{wikiPage.version}
              </Badge>
              <Text fontSize="sm" color="gray.500">
                {wikiPage.language}
              </Text>
            </HStack>
          </VStack>
          <Box
            as="button"
            px={4}
            py={2}
            bg="red.500"
            color="white"
            borderRadius="md"
            fontSize="sm"
            _hover={{ bg: "red.600" }}
            onClick={handleDelete}
            opacity={deleting ? 0.6 : 1}
          >
            {deleting ? "Deleting..." : "Delete Page"}
          </Box>
        </HStack>

        {/* Linked Entity */}
        {linkedEntity && (
          <Box p={4} borderWidth="1px" borderRadius="md" bg="blue.50">
            <HStack gap={2}>
              <Text fontWeight="bold" fontSize="sm">
                Entity:
              </Text>
              <Link
                href={`/entities/${linkedEntity.id}`}
                style={{
                  color: "var(--chakra-colors-blue-600)",
                  textDecoration: "none",
                  fontSize: "14px",
                  fontWeight: "600",
                }}
              >
                {linkedEntity.name}
              </Link>
              <Badge colorPalette="purple" size="sm">
                {linkedEntity.entity_type}
              </Badge>
            </HStack>
          </Box>
        )}

        {/* Content */}
        <Box
          p={6}
          borderWidth="1px"
          borderRadius="md"
          bg="white"
          minH="300px"
        >
          {wikiPage.content ? (
            <Box>{renderContent(wikiPage.content)}</Box>
          ) : (
            <Text color="gray.500" fontStyle="italic">
              No content available.
            </Text>
          )}
        </Box>

        {/* Source Chapters */}
        {wikiPage.source_chapters && wikiPage.source_chapters.length > 0 && (
          <Box p={4} borderWidth="1px" borderRadius="md">
            <Text fontWeight="bold" mb={2}>
              Source Chapters
            </Text>
            <HStack gap={2} flexWrap="wrap">
              {wikiPage.source_chapters.map((ch) => (
                <Badge key={ch} colorPalette="orange" px={2} py={1}>
                  Chapter {ch}
                </Badge>
              ))}
            </HStack>
          </Box>
        )}

        {/* Backlinks Section - show other wiki pages that might reference this entity */}
        <Box p={4} borderWidth="1px" borderRadius="md">
          <Text fontWeight="bold" mb={2}>
            Backlinks
          </Text>
          {linkedEntity ? (
            <Text fontSize="sm" color="gray.600">
              This wiki page is linked to entity{" "}
              <Link
                href={`/entities/${linkedEntity.id}`}
                style={{
                  color: "var(--chakra-colors-blue-500)",
                  textDecoration: "none",
                }}
              >
                {linkedEntity.name}
              </Link>
              . Related pages will appear here when cross-referencing is available.
            </Text>
          ) : (
            <Text fontSize="sm" color="gray.500">
              No backlinks available. This page is not linked to any entity.
            </Text>
          )}
        </Box>

        {/* Metadata */}
        <Box p={4} borderWidth="1px" borderRadius="md">
          <Text fontWeight="bold" mb={2}>
            Metadata
          </Text>
          <VStack align="stretch" gap={2}>
            <HStack gap={2}>
              <Text fontSize="sm" fontWeight="medium" minW="120px">
                ID:
              </Text>
              <Text fontSize="sm" color="gray.600">
                {wikiPage.id}
              </Text>
            </HStack>
            <HStack gap={2}>
              <Text fontSize="sm" fontWeight="medium" minW="120px">
                Novel ID:
              </Text>
              <Text fontSize="sm" color="gray.600">
                {wikiPage.novel_id}
              </Text>
            </HStack>
            <HStack gap={2}>
              <Text fontSize="sm" fontWeight="medium" minW="120px">
                Prompt Version:
              </Text>
              <Text fontSize="sm" color="gray.600">
                {wikiPage.prompt_version || "—"}
              </Text>
            </HStack>
            <HStack gap={2}>
              <Text fontSize="sm" fontWeight="medium" minW="120px">
                Created:
              </Text>
              <Text fontSize="sm" color="gray.600">
                {new Date(wikiPage.created_at).toLocaleString()}
              </Text>
            </HStack>
            <HStack gap={2}>
              <Text fontSize="sm" fontWeight="medium" minW="120px">
                Updated:
              </Text>
              <Text fontSize="sm" color="gray.600">
                {new Date(wikiPage.updated_at).toLocaleString()}
              </Text>
            </HStack>
          </VStack>
        </Box>
      </VStack>
    </Box>
  );
}
