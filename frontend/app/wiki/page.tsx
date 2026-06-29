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
  Table,
  Portal,
  Dialog,
  Select,
  createListCollection,
} from "@chakra-ui/react";
import {
  useGetWikiPagesQuery,
  useGetNovelsQuery,
  useGenerateWikiMutation,
  useDeleteWikiPageMutation,
} from "@/store/api";

export default function WikiPage() {
  const [selectedNovelId, setSelectedNovelId] = useState<number | "">("");
  const [searchQuery, setSearchQuery] = useState("");
  const [page, setPage] = useState(0);
  const limit = 20;
  const [showGenerate, setShowGenerate] = useState(false);
  const [generateTitle, setGenerateTitle] = useState("");

  const { data: novelsData } = useGetNovelsQuery();
  const novelItems =
    novelsData?.novels.map((n) => ({
      label: n.title,
      value: String(n.id),
    })) ?? [];

  const numericNovelId =
    typeof selectedNovelId === "number" ? selectedNovelId : 0;

  const { data: wikiData, isLoading: wikiLoading } = useGetWikiPagesQuery(
    {
      novelId: numericNovelId,
      limit,
      offset: page * limit,
    },
    { skip: numericNovelId === 0 },
  );

  const [generateWiki, { isLoading: isGenerating }] =
    useGenerateWikiMutation();
  const [deleteWikiPage] = useDeleteWikiPageMutation();

  const handleGenerate = async () => {
    if (!numericNovelId) return;
    await generateWiki({
      novelId: numericNovelId,
      title: generateTitle || undefined,
    });
    setGenerateTitle("");
    setShowGenerate(false);
  };

  const handleDeletePage = async (id: number) => {
    if (confirm("Delete this wiki page?")) {
      await deleteWikiPage(id);
    }
  };

  const allPages = wikiData?.pages || [];
  const filteredPages = searchQuery
    ? allPages.filter(
        (p) =>
          p.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
          p.content.toLowerCase().includes(searchQuery.toLowerCase()),
      )
    : allPages;
  const total = wikiData?.total || 0;

  return (
    <Box p={8}>
      <VStack gap={6} align="stretch">
        <HStack justify="space-between">
          <Heading size="lg">Wiki Browser</Heading>
          <Box
            as="button"
            px={4}
            py={2}
            bg="blue.500"
            color="white"
            borderRadius="md"
            _hover={{ bg: "blue.600" }}
            onClick={() => setShowGenerate(true)}
            opacity={numericNovelId === 0 ? 0.5 : 1}
            pointerEvents={numericNovelId === 0 ? "none" : "auto"}
          >
            Generate Wiki Page
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
              Select a novel to browse its wiki pages.
            </Text>
          </Box>
        ) : (
          <>
            {/* Search */}
            <Input
              placeholder="Search wiki pages..."
              value={searchQuery}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                setSearchQuery(e.target.value);
                setPage(0);
              }}
              maxW="400px"
            />

            {/* Wiki pages table */}
            {wikiLoading ? (
              <Box p={8} display="flex" justifyContent="center">
                <Spinner size="xl" color="blue.500" />
              </Box>
            ) : filteredPages.length === 0 ? (
              <Box
                p={6}
                bg="blue.50"
                borderRadius="md"
                _dark={{ bg: "blue.900" }}
              >
                <Text>
                  {searchQuery
                    ? "No wiki pages match your search."
                    : "No wiki pages yet. Generate one to get started."}
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
                    <Table.Cell>Updated</Table.Cell>
                    <Table.Cell>Actions</Table.Cell>
                  </Table.Row>
                </Table.Header>
                <Table.Body>
                  {filteredPages.map((wpage) => (
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
                      <Table.Cell>
                        <Text fontSize="sm" color="gray.500">
                          {new Date(wpage.updated_at).toLocaleDateString()}
                        </Text>
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
                          onClick={() => handleDeletePage(wpage.id)}
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

      {/* Generate Wiki Dialog */}
      <Dialog.Root
        open={showGenerate}
        onOpenChange={(e) => setShowGenerate(e.open)}
      >
        <Portal>
          <Dialog.Backdrop />
          <Dialog.Positioner>
            <Dialog.Content>
              <Dialog.Header>
                <Dialog.Title>Generate Wiki Page</Dialog.Title>
              </Dialog.Header>
              <Dialog.Body>
                <VStack gap={4}>
                  <Text fontSize="sm" color="gray.500">
                    Generate a wiki page for this novel. Optionally provide a
                    title; otherwise the AI will determine one.
                  </Text>
                  <Input
                    placeholder="Page title (optional)"
                    value={generateTitle}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                      setGenerateTitle(e.target.value)
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
                  onClick={handleGenerate}
                  opacity={isGenerating || !numericNovelId ? 0.5 : 1}
                  pointerEvents={
                    isGenerating || !numericNovelId ? "none" : "auto"
                  }
                >
                  {isGenerating ? "Generating..." : "Generate"}
                </Box>
              </Dialog.Footer>
            </Dialog.Content>
          </Dialog.Positioner>
        </Portal>
      </Dialog.Root>
    </Box>
  );
}
