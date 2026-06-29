"use client";

import { useState } from "react";
import {
  Box,
  Heading,
  Text,
  VStack,
  HStack,
  Input,
  Badge,
  Spinner,
  Tabs,
  Table,
  Portal,
  Dialog,
  Select,
  createListCollection,
} from "@chakra-ui/react";
import {
  useGetEntitiesQuery,
  useGetNovelsQuery,
  useCreateEntityMutation,
  useDeleteEntityMutation,
  useSearchQuery,
} from "@/store/api";

const ENTITY_TYPES = [
  "character",
  "location",
  "item",
  "organization",
  "event",
  "concept",
];

const entityTypeCollection = createListCollection({
  items: ENTITY_TYPES.map((t) => ({ label: t, value: t })),
});

const novelCollection = createListCollection<{ label: string; value: string }>({
  items: [],
});

export default function EntitiesPage() {
  const [selectedNovelId, setSelectedNovelId] = useState<number | "">("");
  const [searchQuery, setSearchQuery] = useState("");
  const [typeFilter, setTypeFilter] = useState<string>("");
  const [page, setPage] = useState(0);
  const limit = 20;
  const [showCreate, setShowCreate] = useState(false);
  const [newEntity, setNewEntity] = useState({
    name: "",
    entityType: "character",
    aliases: "",
  });

  const { data: novelsData } = useGetNovelsQuery();
  const novelItems =
    novelsData?.novels.map((n) => ({
      label: n.title,
      value: String(n.id),
    })) ?? [];

  const numericNovelId =
    typeof selectedNovelId === "number" ? selectedNovelId : 0;

  const { data: entitiesData, isLoading: entitiesLoading } =
    useGetEntitiesQuery(
      {
        novelId: numericNovelId,
        entityType: typeFilter || undefined,
        limit,
        offset: page * limit,
      },
      { skip: numericNovelId === 0 },
    );

  const { data: searchData } = useSearchQuery(
    { q: searchQuery, novelId: numericNovelId || undefined },
    { skip: !searchQuery || numericNovelId === 0 },
  );

  const [createEntity, { isLoading: isCreating }] =
    useCreateEntityMutation();
  const [deleteEntity] = useDeleteEntityMutation();

  const handleCreateEntity = async () => {
    if (!newEntity.name || !numericNovelId) return;
    await createEntity({
      novelId: numericNovelId,
      name: newEntity.name,
      entityType: newEntity.entityType,
      aliases: newEntity.aliases
        .split(",")
        .map((a) => a.trim())
        .filter(Boolean),
    });
    setNewEntity({ name: "", entityType: "character", aliases: "" });
    setShowCreate(false);
  };

  const handleDeleteEntity = async (id: number) => {
    if (confirm("Delete this entity?")) {
      await deleteEntity(id);
    }
  };

  const displayEntities = searchQuery
    ? searchData?.entities || []
    : entitiesData?.entities || [];
  const total = searchQuery
    ? searchData?.total || 0
    : entitiesData?.total || 0;

  return (
    <Box p={8}>
      <VStack gap={6} align="stretch">
        <HStack justify="space-between">
          <Heading size="lg">Entities</Heading>
          <Box
            as="button"
            px={4}
            py={2}
            bg="blue.500"
            color="white"
            borderRadius="md"
            _hover={{ bg: "blue.600" }}
            onClick={() => setShowCreate(true)}
            opacity={numericNovelId === 0 ? 0.5 : 1}
            pointerEvents={numericNovelId === 0 ? "none" : "auto"}
          >
            New Entity
          </Box>
        </HStack>

        {/* Novel selector */}
        <HStack gap={4}>
          <Select.Root
            collection={createListCollection({
              items: novelItems,
            })}
            value={selectedNovelId !== "" ? [String(selectedNovelId)] : []}
            onValueChange={(e) => {
              const val = e.value[0];
              setSelectedNovelId(val ? Number(val) : "");
              setPage(0);
              setSearchQuery("");
              setTypeFilter("");
            }}
            width="300px"
          >
            <Select.Control>
              <Select.Trigger>
                <Select.ValueText placeholder="Select a novel" />
              </Select.Trigger>
            </Select.Control>
            <Portal>
              <Select.Content>
                {novelItems.map((item) => (
                  <Select.Item key={item.value} item={item}>
                    {item.label}
                  </Select.Item>
                ))}
              </Select.Content>
            </Portal>
          </Select.Root>
        </HStack>

        {numericNovelId === 0 ? (
          <Box p={8} textAlign="center">
            <Text color="gray.500" fontSize="lg">
              Select a novel to browse its entities.
            </Text>
          </Box>
        ) : (
          <>
            {/* Filters */}
            <HStack gap={4}>
              <Input
                placeholder="Search entities..."
                value={searchQuery}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                  setSearchQuery(e.target.value);
                  setPage(0);
                }}
                maxW="400px"
              />
              <Select.Root
                collection={entityTypeCollection}
                value={typeFilter ? [typeFilter] : []}
                onValueChange={(e) => {
                  setTypeFilter(e.value[0] || "");
                  setPage(0);
                }}
                width="200px"
              >
                <Select.Control>
                  <Select.Trigger>
                    <Select.ValueText placeholder="All types" />
                  </Select.Trigger>
                </Select.Control>
                <Portal>
                  <Select.Content>
                    {entityTypeCollection.items.map((item) => (
                      <Select.Item key={item.value} item={item}>
                        {item.label}
                      </Select.Item>
                    ))}
                  </Select.Content>
                </Portal>
              </Select.Root>
            </HStack>

            {/* Entity table */}
            {entitiesLoading ? (
              <Box p={8} display="flex" justifyContent="center">
                <Spinner size="xl" color="blue.500" />
              </Box>
            ) : displayEntities.length === 0 ? (
              <Box
                p={6}
                bg="blue.50"
                borderRadius="md"
                _dark={{ bg: "blue.900" }}
              >
                <Text>
                  No entities found.{" "}
                  {searchQuery
                    ? "Try a different search."
                    : "Create an entity to get started."}
                </Text>
              </Box>
            ) : (
              <Table.Root>
                <Table.Header>
                  <Table.Row>
                    <Table.Cell>Name</Table.Cell>
                    <Table.Cell>Type</Table.Cell>
                    <Table.Cell>Aliases</Table.Cell>
                    <Table.Cell>Actions</Table.Cell>
                  </Table.Row>
                </Table.Header>
                <Table.Body>
                  {displayEntities.map((entity) => (
                    <Table.Row key={entity.id}>
                      <Table.Cell>
                        <Text fontWeight="bold">{entity.name}</Text>
                      </Table.Cell>
                      <Table.Cell>
                        <Badge colorPalette="purple">
                          {entity.entity_type}
                        </Badge>
                      </Table.Cell>
                      <Table.Cell>
                        <HStack gap={1} flexWrap="wrap">
                          {entity.aliases.map((alias) => (
                            <Badge key={alias} size="sm">
                              {alias}
                            </Badge>
                          ))}
                          {entity.aliases.length === 0 && (
                            <Text fontSize="sm" color="gray.400">
                              -
                            </Text>
                          )}
                        </HStack>
                      </Table.Cell>
                      <Table.Cell>
                        <Box
                          as="button"
                          px={3}
                          py={1}
                          bg="red.500"
                          color="white"
                          borderRadius="md"
                          fontSize="sm"
                          _hover={{ bg: "red.600" }}
                          onClick={() => handleDeleteEntity(entity.id)}
                        >
                          Delete
                        </Box>
                      </Table.Cell>
                    </Table.Row>
                  ))}
                </Table.Body>
              </Table.Root>
            )}

            {/* Pagination */}
            {total > limit && (
              <HStack justify="center" mt={4}>
                <Box
                  as="button"
                  px={4}
                  py={2}
                  bg={page === 0 ? "gray.300" : "gray.200"}
                  borderRadius="md"
                  onClick={() => page > 0 && setPage(page - 1)}
                  cursor={page === 0 ? "not-allowed" : "pointer"}
                  _dark={{ bg: page === 0 ? "gray.600" : "gray.700" }}
                >
                  Previous
                </Box>
                <Text>
                  Page {page + 1} of {Math.ceil(total / limit)}
                </Text>
                <Box
                  as="button"
                  px={4}
                  py={2}
                  bg={
                    (page + 1) * limit >= total ? "gray.300" : "gray.200"
                  }
                  borderRadius="md"
                  onClick={() =>
                    (page + 1) * limit < total && setPage(page + 1)
                  }
                  cursor={
                    (page + 1) * limit >= total ? "not-allowed" : "pointer"
                  }
                  _dark={{
                    bg:
                      (page + 1) * limit >= total ? "gray.600" : "gray.700",
                  }}
                >
                  Next
                </Box>
              </HStack>
            )}
          </>
        )}
      </VStack>

      {/* Create Entity Dialog */}
      <Dialog.Root
        open={showCreate}
        onOpenChange={(e) => setShowCreate(e.open)}
      >
        <Portal>
          <Dialog.Backdrop />
          <Dialog.Positioner>
            <Dialog.Content>
              <Dialog.Header>
                <Dialog.Title>Create Entity</Dialog.Title>
              </Dialog.Header>
              <Dialog.Body>
                <VStack gap={4}>
                  <Input
                    placeholder="Entity name"
                    value={newEntity.name}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                      setNewEntity({ ...newEntity, name: e.target.value })
                    }
                  />
                  <Select.Root
                    collection={entityTypeCollection}
                    value={[newEntity.entityType]}
                    onValueChange={(e) =>
                      setNewEntity({
                        ...newEntity,
                        entityType: e.value[0],
                      })
                    }
                  >
                    <Select.Control>
                      <Select.Trigger>
                        <Select.ValueText />
                      </Select.Trigger>
                    </Select.Control>
                    <Portal>
                      <Select.Content>
                        {entityTypeCollection.items.map((item) => (
                          <Select.Item key={item.value} item={item}>
                            {item.label}
                          </Select.Item>
                        ))}
                      </Select.Content>
                    </Portal>
                  </Select.Root>
                  <Input
                    placeholder="Aliases (comma separated)"
                    value={newEntity.aliases}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                      setNewEntity({ ...newEntity, aliases: e.target.value })
                    }
                  />
                </VStack>
              </Dialog.Body>
              <Dialog.Footer>
                <Dialog.CloseTrigger asChild>
                  <Box
                    as="button"
                    px={4}
                    py={2}
                    bg="gray.200"
                    borderRadius="md"
                    _hover={{ bg: "gray.300" }}
                    mr={3}
                  >
                    Cancel
                  </Box>
                </Dialog.CloseTrigger>
                <Box
                  as="button"
                  px={4}
                  py={2}
                  bg="blue.500"
                  color="white"
                  borderRadius="md"
                  _hover={{ bg: "blue.600" }}
                  onClick={handleCreateEntity}
                  opacity={
                    !newEntity.name || isCreating || !numericNovelId
                      ? 0.5
                      : 1
                  }
                  pointerEvents={
                    !newEntity.name || isCreating || !numericNovelId
                      ? "none"
                      : "auto"
                  }
                >
                  {isCreating ? "Creating..." : "Create"}
                </Box>
              </Dialog.Footer>
            </Dialog.Content>
          </Dialog.Positioner>
        </Portal>
      </Dialog.Root>
    </Box>
  );
}
