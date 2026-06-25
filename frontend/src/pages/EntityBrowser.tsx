import { useState } from "react";
import { useParams } from "react-router-dom";
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
} from "@chakra-ui/react";
import {
  useGetEntitiesQuery,
  useCreateEntityMutation,
  useDeleteEntityMutation,
  useSearchQuery,
  useGetWikiPagesQuery,
  useGenerateWikiMutation,
} from "../store/api";

const ENTITY_TYPES = [
  "character",
  "location",
  "item",
  "organization",
  "event",
  "concept",
];

export function EntityBrowser() {
  const { novelId } = useParams<{ novelId: string }>();
  const numericNovelId = Number(novelId);

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

  const { data: entitiesData, isLoading: entitiesLoading } =
    useGetEntitiesQuery({
      novelId: numericNovelId,
      entityType: typeFilter || undefined,
      limit,
      offset: page * limit,
    });

  const { data: searchData } = useSearchQuery(
    { q: searchQuery, novelId: numericNovelId },
    { skip: !searchQuery }
  );

  const { data: wikiData } = useGetWikiPagesQuery({
    novelId: numericNovelId,
  });

  const [createEntity] = useCreateEntityMutation();
  const [deleteEntity] = useDeleteEntityMutation();
  const [generateWiki] = useGenerateWikiMutation();

  const handleCreateEntity = async () => {
    if (!newEntity.name) return;
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

  const handleGenerateWiki = async (entityId: number) => {
    await generateWiki({ novelId: numericNovelId, entityId });
  };

  const displayEntities = searchQuery
    ? searchData?.entities || []
    : entitiesData?.entities || [];
  const total = searchQuery
    ? searchData?.total || 0
    : entitiesData?.total || 0;

  if (entitiesLoading) {
    return (
      <Box p={8}>
        <Spinner size="xl" />
      </Box>
    );
  }

  return (
    <Box p={8}>
      <VStack gap={6} align="stretch">
        <HStack justify="space-between">
          <Heading size="lg">Knowledge Base</Heading>
          <Box
            as="button"
            px={4}
            py={2}
            bg="blue.500"
            color="white"
            borderRadius="md"
            _hover={{ bg: "blue.600" }}
            onClick={() => setShowCreate(true)}
          >
            Add Entity
          </Box>
        </HStack>

        <HStack gap={4}>
          <Input
            placeholder="Search entities..."
            value={searchQuery}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
              setSearchQuery(e.target.value)
            }
            maxW="400px"
          />
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            style={{
              padding: "8px 12px",
              borderRadius: "6px",
              border: "1px solid #e2e8f0",
              maxWidth: "200px",
            }}
          >
            <option value="">All types</option>
            {ENTITY_TYPES.map((type) => (
              <option key={type} value={type}>
                {type}
              </option>
            ))}
          </select>
        </HStack>

        <Tabs.Root defaultValue="entities">
          <Tabs.List>
            <Tabs.Trigger value="entities">Entities ({total})</Tabs.Trigger>
            <Tabs.Trigger value="wiki">
              Wiki Pages ({wikiData?.total || 0})
            </Tabs.Trigger>
          </Tabs.List>

          <Tabs.Content value="entities">
            {displayEntities.length === 0 ? (
              <Box p={4} bg="blue.50" borderRadius="md">
                <Text>
                  No entities found. Add some entities to get started.
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
                        </HStack>
                      </Table.Cell>
                      <Table.Cell>
                        <HStack gap={2}>
                          <Box
                            as="button"
                            px={3}
                            py={1}
                            bg="green.500"
                            color="white"
                            borderRadius="md"
                            fontSize="sm"
                            _hover={{ bg: "green.600" }}
                            onClick={() => handleGenerateWiki(entity.id)}
                          >
                            Generate Wiki
                          </Box>
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
                        </HStack>
                      </Table.Cell>
                    </Table.Row>
                  ))}
                </Table.Body>
              </Table.Root>
            )}

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
                  bg={(page + 1) * limit >= total ? "gray.300" : "gray.200"}
                  borderRadius="md"
                  onClick={() =>
                    (page + 1) * limit < total && setPage(page + 1)
                  }
                  cursor={
                    (page + 1) * limit >= total ? "not-allowed" : "pointer"
                  }
                >
                  Next
                </Box>
              </HStack>
            )}
          </Tabs.Content>

          <Tabs.Content value="wiki">
            {wikiData?.pages.length === 0 ? (
              <Box p={4} bg="blue.50" borderRadius="md">
                <Text>
                  No wiki pages yet. Generate one from an entity.
                </Text>
              </Box>
            ) : (
              <Table.Root>
                <Table.Header>
                  <Table.Row>
                    <Table.Cell>Title</Table.Cell>
                    <Table.Cell>Language</Table.Cell>
                    <Table.Cell>Version</Table.Cell>
                    <Table.Cell>Status</Table.Cell>
                  </Table.Row>
                </Table.Header>
                <Table.Body>
                  {wikiData?.pages.map((wpage) => (
                    <Table.Row key={wpage.id}>
                      <Table.Cell>
                        <Text fontWeight="bold">{wpage.title}</Text>
                      </Table.Cell>
                      <Table.Cell>{wpage.language}</Table.Cell>
                      <Table.Cell>v{wpage.version}</Table.Cell>
                      <Table.Cell>
                        <Badge
                          colorPalette={
                            wpage.is_published ? "green" : "yellow"
                          }
                        >
                          {wpage.is_published ? "Published" : "Draft"}
                        </Badge>
                      </Table.Cell>
                    </Table.Row>
                  ))}
                </Table.Body>
              </Table.Root>
            )}
          </Tabs.Content>
        </Tabs.Root>
      </VStack>

      {showCreate && (
        <Box
          position="fixed"
          top={0}
          left={0}
          right={0}
          bottom={0}
          bg="blackAlpha.600"
          display="flex"
          alignItems="center"
          justifyContent="center"
          zIndex={1000}
        >
          <Box
            bg="white"
            p={6}
            borderRadius="lg"
            minW="400px"
            boxShadow="lg"
          >
            <Heading size="md" mb={4}>
              Create Entity
            </Heading>
            <VStack gap={4}>
              <Input
                placeholder="Entity name"
                value={newEntity.name}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                  setNewEntity({ ...newEntity, name: e.target.value })
                }
              />
              <select
                value={newEntity.entityType}
                onChange={(e) =>
                  setNewEntity({ ...newEntity, entityType: e.target.value })
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
              <Input
                placeholder="Aliases (comma separated)"
                value={newEntity.aliases}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                  setNewEntity({ ...newEntity, aliases: e.target.value })
                }
              />
              <HStack gap={4}>
                <Box
                  as="button"
                  px={4}
                  py={2}
                  bg="blue.500"
                  color="white"
                  borderRadius="md"
                  _hover={{ bg: "blue.600" }}
                  onClick={handleCreateEntity}
                >
                  Create
                </Box>
                <Box
                  as="button"
                  px={4}
                  py={2}
                  bg="gray.200"
                  borderRadius="md"
                  _hover={{ bg: "gray.300" }}
                  onClick={() => setShowCreate(false)}
                >
                  Cancel
                </Box>
              </HStack>
            </VStack>
          </Box>
        </Box>
      )}
    </Box>
  );
}
