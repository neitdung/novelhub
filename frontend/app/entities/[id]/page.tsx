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
  Input,
  Textarea,
} from "@chakra-ui/react";
import Link from "next/link";
import { useState } from "react";
import {
  useGetEntityQuery,
  useUpdateEntityMutation,
  useDeleteEntityMutation,
  useGenerateWikiMutation,
  useGetWikiPagesQuery,
} from "@/store/api";

const ENTITY_TYPES = [
  "character",
  "location",
  "item",
  "organization",
  "event",
  "concept",
];

export default function EntityDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const entityId = Number(params.id);

  const { data: entity, isLoading, error } = useGetEntityQuery(entityId);
  const [updateEntity] = useUpdateEntityMutation();
  const [deleteEntity] = useDeleteEntityMutation();
  const [generateWiki] = useGenerateWikiMutation();

  const [editing, setEditing] = useState(false);
  const [editForm, setEditForm] = useState({
    name: "",
    entityType: "character",
    attributes: "",
    aliases: "",
  });
  const [generating, setGenerating] = useState(false);
  const [deleting, setDeleting] = useState(false);

  // Fetch wiki page for this entity
  const { data: wikiPages } = useGetWikiPagesQuery(
    { novelId: entity?.novel_id ?? 0, entityId },
    { skip: !entity },
  );
  const wikiPage = wikiPages?.pages?.[0];

  const handleStartEdit = () => {
    if (!entity) return;
    setEditForm({
      name: entity.name,
      entityType: entity.entity_type,
      attributes: JSON.stringify(entity.attributes || {}, null, 2),
      aliases: (entity.aliases || []).join(", "),
    });
    setEditing(true);
  };

  const handleSaveEdit = async () => {
    if (!entity) return;
    let attributes: Record<string, unknown> = {};
    try {
      attributes = editForm.attributes ? JSON.parse(editForm.attributes) : {};
    } catch {
      // Keep empty if invalid JSON
    }
    await updateEntity({
      id: entity.id,
      name: editForm.name,
      entityType: editForm.entityType,
      attributes,
    });
    setEditing(false);
  };

  const handleDelete = async () => {
    if (!entity || deleting) return;
    if (!confirm(`Delete entity "${entity.name}"? This cannot be undone.`))
      return;
    setDeleting(true);
    try {
      await deleteEntity(entity.id);
      router.push("/entities");
    } catch {
      setDeleting(false);
    }
  };

  const handleGenerateWiki = async () => {
    if (!entity || generating) return;
    setGenerating(true);
    try {
      await generateWiki({
        novelId: entity.novel_id,
        entityId: entity.id,
      }).unwrap();
    } finally {
      setGenerating(false);
    }
  };

  if (isLoading) {
    return (
      <Box p={8}>
        <Spinner size="xl" />
      </Box>
    );
  }

  if (error || !entity) {
    return (
      <Box p={8}>
        <VStack gap={4} align="stretch">
          <Link
            href="/entities"
            style={{
              color: "var(--chakra-colors-blue-500)",
              textDecoration: "none",
            }}
          >
            &larr; Back to Entities
          </Link>
          <Text color="red.500">Entity not found.</Text>
        </VStack>
      </Box>
    );
  }

  return (
    <Box p={8}>
      <VStack gap={6} align="stretch">
        {/* Back link */}
        <Link
          href="/entities"
          style={{
            color: "var(--chakra-colors-blue-500)",
            textDecoration: "none",
            fontSize: "14px",
          }}
        >
          &larr; Back to Entities
        </Link>

        {/* Header */}
        <HStack justify="space-between" align="flex-start">
          <VStack align="flex-start" gap={2}>
            <Heading size="xl">{entity.name}</Heading>
            <HStack gap={3}>
              <Badge colorPalette="purple" fontSize="md" px={3} py={1}>
                {entity.entity_type}
              </Badge>
              {entity.source_chapter && (
                <Text fontSize="sm" color="gray.500">
                  First mentioned: Chapter {entity.source_chapter}
                </Text>
              )}
            </HStack>
          </VStack>
          <HStack gap={2}>
            {!editing && (
              <>
                {wikiPage ? (
                  <Link
                    href={`/wiki/${wikiPage.id}`}
                    style={{
                      padding: "8px 16px",
                      background: "var(--chakra-colors-teal-500)",
                      color: "white",
                      borderRadius: "8px",
                      textDecoration: "none",
                      fontSize: "14px",
                    }}
                  >
                    View Wiki
                  </Link>
                ) : (
                  <Box
                    as="button"
                    px={4}
                    py={2}
                    bg="green.500"
                    color="white"
                    borderRadius="md"
                    fontSize="sm"
                    _hover={{ bg: "green.600" }}
                    onClick={handleGenerateWiki}
                    opacity={generating ? 0.6 : 1}
                  >
                    {generating ? "Generating..." : "Generate Wiki"}
                  </Box>
                )}
                <Box
                  as="button"
                  px={4}
                  py={2}
                  bg="blue.500"
                  color="white"
                  borderRadius="md"
                  fontSize="sm"
                  _hover={{ bg: "blue.600" }}
                  onClick={handleStartEdit}
                >
                  Edit
                </Box>
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
                  {deleting ? "Deleting..." : "Delete"}
                </Box>
              </>
            )}
          </HStack>
        </HStack>

        {editing ? (
          /* ── Edit Form ── */
          <Box p={6} borderWidth="1px" borderRadius="md">
            <VStack gap={4}>
              <Box w="full">
                <Text mb={1} fontSize="sm" color="gray.600">
                  Name
                </Text>
                <Input
                  value={editForm.name}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                    setEditForm({ ...editForm, name: e.target.value })
                  }
                  placeholder="Entity name"
                />
              </Box>
              <Box w="full">
                <Text mb={1} fontSize="sm" color="gray.600">
                  Type
                </Text>
                <select
                  value={editForm.entityType}
                  onChange={(e) =>
                    setEditForm({ ...editForm, entityType: e.target.value })
                  }
                  style={{
                    padding: "8px 12px",
                    width: "100%",
                    borderRadius: "6px",
                    border: "1px solid #e2e8f0",
                  }}
                >
                  {ENTITY_TYPES.map((type) => (
                    <option key={type} value={type}>
                      {type}
                    </option>
                  ))}
                </select>
              </Box>
              <Input
                value={editForm.aliases}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                  setEditForm({ ...editForm, aliases: e.target.value })
                }
                placeholder="Aliases (comma separated)"
              />
              <Box w="full">
                <Text mb={1} fontSize="sm" color="gray.600">
                  Attributes (JSON)
                </Text>
                <Textarea
                  value={editForm.attributes}
                  onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) =>
                    setEditForm({ ...editForm, attributes: e.target.value })
                  }
                  placeholder='{"key": "value"}'
                  minH="100px"
                />
              </Box>
              <HStack gap={4}>
                <Box
                  as="button"
                  px={4}
                  py={2}
                  bg="blue.500"
                  color="white"
                  borderRadius="md"
                  _hover={{ bg: "blue.600" }}
                  onClick={handleSaveEdit}
                >
                  Save
                </Box>
                <Box
                  as="button"
                  px={4}
                  py={2}
                  bg="gray.200"
                  borderRadius="md"
                  _hover={{ bg: "gray.300" }}
                  onClick={() => setEditing(false)}
                >
                  Cancel
                </Box>
              </HStack>
            </VStack>
          </Box>
        ) : (
          <>
            {/* ── Aliases ── */}
            {entity.aliases && entity.aliases.length > 0 && (
              <Box p={4} borderWidth="1px" borderRadius="md">
                <Text fontWeight="bold" mb={2}>
                  Aliases
                </Text>
                <HStack gap={2} flexWrap="wrap">
                  {entity.aliases.map((alias) => (
                    <Badge key={alias} colorPalette="blue" px={2} py={1}>
                      {alias}
                    </Badge>
                  ))}
                </HStack>
              </Box>
            )}

            {/* ── Attributes ── */}
            {entity.attributes &&
              Object.keys(entity.attributes).length > 0 && (
                <Box p={4} borderWidth="1px" borderRadius="md">
                  <Text fontWeight="bold" mb={2}>
                    Attributes
                  </Text>
                  <VStack align="stretch" gap={2}>
                    {Object.entries(entity.attributes).map(
                      ([key, value]) => (
                        <HStack key={key} gap={2}>
                          <Text fontWeight="medium" fontSize="sm" minW="120px">
                            {key}:
                          </Text>
                          <Text fontSize="sm" color="gray.600">
                            {String(value)}
                          </Text>
                        </HStack>
                      ),
                    )}
                  </VStack>
                </Box>
              )}

            {/* ── Related Wiki Page ── */}
            {wikiPage && (
              <Box p={4} borderWidth="1px" borderRadius="md">
                <Text fontWeight="bold" mb={2}>
                  Wiki Page
                </Text>
                <Link
                  href={`/wiki/${wikiPage.id}`}
                  style={{
                    color: "var(--chakra-colors-blue-500)",
                    textDecoration: "none",
                  }}
                >
                  {wikiPage.title} &rarr;
                </Link>
                <Text fontSize="sm" color="gray.500" mt={1}>
                  Version {wikiPage.version} &bull;{" "}
                  {wikiPage.is_published ? "Published" : "Draft"}
                </Text>
              </Box>
            )}

            {/* ── Metadata ── */}
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
                    {entity.id}
                  </Text>
                </HStack>
                <HStack gap={2}>
                  <Text fontSize="sm" fontWeight="medium" minW="120px">
                    Novel ID:
                  </Text>
                  <Text fontSize="sm" color="gray.600">
                    {entity.novel_id}
                  </Text>
                </HStack>
                <HStack gap={2}>
                  <Text fontSize="sm" fontWeight="medium" minW="120px">
                    Created:
                  </Text>
                  <Text fontSize="sm" color="gray.600">
                    {new Date(entity.created_at).toLocaleString()}
                  </Text>
                </HStack>
                <HStack gap={2}>
                  <Text fontSize="sm" fontWeight="medium" minW="120px">
                    Updated:
                  </Text>
                  <Text fontSize="sm" color="gray.600">
                    {new Date(entity.updated_at).toLocaleString()}
                  </Text>
                </HStack>
              </VStack>
            </Box>
          </>
        )}
      </VStack>
    </Box>
  );
}
