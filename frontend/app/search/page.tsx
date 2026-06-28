"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import {
  Box,
  Heading,
  Text,
  VStack,
  HStack,
  Input,
  Badge,
  Spinner,
} from "@chakra-ui/react";
import {
  useGetNovelsQuery,
  useSearchQuery,
} from "@/store/api";
import { EmptyState } from "@/components";

const SEARCH_TYPES = [
  { value: "all", label: "All" },
  { value: "entities", label: "Entities" },
  { value: "wiki", label: "Wiki Pages" },
];

export default function SearchPage() {
  const { data: novelsData } = useGetNovelsQuery();
  const novels = novelsData?.novels || [];

  const [selectedNovelId, setSelectedNovelId] = useState<number | null>(null);
  const [query, setQuery] = useState("");
  const [debouncedQuery, setDebouncedQuery] = useState("");
  const [searchType, setSearchType] = useState("all");

  // Debounce search input
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(query);
    }, 300);
    return () => clearTimeout(timer);
  }, [query]);

  const activeNovelId =
    selectedNovelId ?? (novels.length > 0 ? novels[0].id : null);

  const {
    data: searchData,
    isLoading,
    error,
  } = useSearchQuery(
    {
      q: debouncedQuery,
      type: searchType,
      novelId: activeNovelId ?? undefined,
    },
    { skip: !debouncedQuery || !activeNovelId },
  );

  const handleNovelChange = (novelIdStr: string) => {
    const nid = novelIdStr ? Number(novelIdStr) : null;
    setSelectedNovelId(nid);
  };

  return (
    <Box p={8}>
      <VStack gap={6} align="stretch">
        {/* Header */}
        <HStack justify="space-between" flexWrap="wrap" gap={4}>
          <Heading size="lg">Search</Heading>
          <select
            value={activeNovelId ?? ""}
            onChange={(e) => handleNovelChange(e.target.value)}
            style={{
              padding: "8px 12px",
              borderRadius: "6px",
              border: "1px solid #e2e8f0",
              minWidth: "200px",
            }}
          >
            {novels.map((novel) => (
              <option key={novel.id} value={novel.id}>
                {novel.title}
              </option>
            ))}
          </select>
        </HStack>

        {/* Search Input */}
        <HStack gap={4} flexWrap="wrap">
          <Input
            placeholder="Search entities and wiki pages..."
            value={query}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
              setQuery(e.target.value)
            }
            size="lg"
            flex={1}
            maxW="600px"
            autoFocus
          />
          <HStack gap={2}>
            {SEARCH_TYPES.map((st) => (
              <Box
                key={st.value}
                as="button"
                px={3}
                py={1.5}
                borderRadius="full"
                fontSize="sm"
                bg={searchType === st.value ? "blue.500" : "gray.100"}
                color={searchType === st.value ? "white" : "gray.700"}
                _hover={{
                  bg: searchType === st.value ? "blue.600" : "gray.200",
                }}
                onClick={() => setSearchType(st.value)}
              >
                {st.label}
              </Box>
            ))}
          </HStack>
        </HStack>

        {/* No query state */}
        {!debouncedQuery && (
          <Box p={8} textAlign="center">
            <Text color="gray.500">
              Enter a search query to find entities and wiki pages.
            </Text>
          </Box>
        )}

        {/* Loading */}
        {debouncedQuery && isLoading && (
          <Box textAlign="center" py={8}>
            <Spinner size="xl" />
            <Text mt={4} color="gray.500">
              Searching...
            </Text>
          </Box>
        )}

        {/* Error */}
        {debouncedQuery && error && !isLoading && (
          <Box p={4} bg="red.50" borderRadius="md">
            <Text color="red.600">
              Search failed. Make sure the backend is running.
            </Text>
          </Box>
        )}

        {/* Results */}
        {debouncedQuery &&
          !isLoading &&
          !error &&
          searchData && (
            <>
              {/* Summary */}
              <Text fontSize="sm" color="gray.500">
                Found {searchData.total || 0} result
                {searchData.total !== 1 ? "s" : ""} for &ldquo;
                {debouncedQuery}
                &rdquo;
              </Text>

              {/* Entity Results */}
              {(searchType === "all" || searchType === "entities") &&
                searchData.entities &&
                searchData.entities.length > 0 && (
                  <Box>
                    <Heading size="sm" mb={3} color="gray.700">
                      Entities ({searchData.entities.length})
                    </Heading>
                    <VStack gap={3} align="stretch">
                      {searchData.entities.map((entity) => (
                        <Link
                          key={entity.id}
                          href={`/entities/${entity.id}`}
                          style={{ textDecoration: "none" }}
                        >
                          <Box
                            p={4}
                            borderWidth="1px"
                            borderRadius="md"
                            _hover={{
                              borderColor: "blue.300",
                              bg: "blue.50",
                            }}
                            transition="all 0.15s"
                          >
                            <HStack justify="space-between">
                              <VStack align="flex-start" gap={1}>
                                <Text
                                  fontWeight="bold"
                                  color="blue.600"
                                >
                                  {entity.name}
                                </Text>
                                <HStack gap={2}>
                                  <Badge colorPalette="purple" px={2}>
                                    {entity.entity_type}
                                  </Badge>
                                  {entity.aliases &&
                                    entity.aliases.length > 0 && (
                                      <Text
                                        fontSize="sm"
                                        color="gray.500"
                                      >
                                        Aliases:{" "}
                                        {entity.aliases
                                          .slice(0, 3)
                                          .join(", ")}
                                      </Text>
                                    )}
                                </HStack>
                              </VStack>
                              <Text fontSize="sm" color="blue.500">
                                View &rarr;
                              </Text>
                            </HStack>
                          </Box>
                        </Link>
                      ))}
                    </VStack>
                  </Box>
                )}

              {/* Wiki Page Results */}
              {(searchType === "all" || searchType === "wiki") &&
                searchData.wiki_pages &&
                searchData.wiki_pages.length > 0 && (
                  <Box>
                    <Heading size="sm" mb={3} color="gray.700">
                      Wiki Pages ({searchData.wiki_pages.length})
                    </Heading>
                    <VStack gap={3} align="stretch">
                      {searchData.wiki_pages.map((wpage) => (
                        <Link
                          key={wpage.id}
                          href={`/wiki/${wpage.id}`}
                          style={{ textDecoration: "none" }}
                        >
                          <Box
                            p={4}
                            borderWidth="1px"
                            borderRadius="md"
                            _hover={{
                              borderColor: "green.300",
                              bg: "green.50",
                            }}
                            transition="all 0.15s"
                          >
                            <HStack justify="space-between">
                              <VStack align="flex-start" gap={1}>
                                <Text
                                  fontWeight="bold"
                                  color="green.700"
                                >
                                  {wpage.title}
                                </Text>
                                <HStack gap={2}>
                                  <Badge colorPalette="cyan" px={2}>
                                    {wpage.language}
                                  </Badge>
                                  <Badge
                                    colorPalette={
                                      wpage.is_published
                                        ? "green"
                                        : "yellow"
                                    }
                                    px={2}
                                  >
                                    {wpage.is_published
                                      ? "Published"
                                      : "Draft"}
                                  </Badge>
                                  <Text
                                    fontSize="sm"
                                    color="gray.500"
                                  >
                                    v{wpage.version}
                                  </Text>
                                </HStack>
                              </VStack>
                              <Text fontSize="sm" color="green.600">
                                View &rarr;
                              </Text>
                            </HStack>
                          </Box>
                        </Link>
                      ))}
                    </VStack>
                  </Box>
                )}

              {/* No results */}
              {searchData.total === 0 && (
                <Box p={8} textAlign="center" bg="blue.50" borderRadius="md">
                  <Text color="gray.600">
                    No results found for &ldquo;
                    {debouncedQuery}
                    &rdquo;. Try a different search term.
                  </Text>
                </Box>
              )}
            </>
          )}

        {/* No novels */}
        {!novels.length && (
          <Box p={8} textAlign="center">
            <EmptyState
              title="No Novels"
              message="Upload a novel first to search its entities and wiki pages."
            />
          </Box>
        )}
      </VStack>
    </Box>
  );
}
