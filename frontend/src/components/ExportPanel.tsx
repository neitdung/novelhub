"use client";

import { useState } from "react";
import {
  Box,
  Heading,
  VStack,
  Text,
  HStack,
  Spinner,
} from "@chakra-ui/react";
import { useGetNovelsQuery } from "@/store/api";

type ExportFormat = "markdown" | "json" | "wiki";

export function ExportPanel() {
  const { data: novelsData, isLoading: novelsLoading } = useGetNovelsQuery();

  const [selectedNovelId, setSelectedNovelId] = useState<number | null>(null);
  const [exporting, setExporting] = useState<ExportFormat | null>(null);
  const [error, setError] = useState<string | null>(null);

  const novels = novelsData?.novels ?? [];

  const triggerTextDownload = (content: string, filename: string) => {
    const blob = new Blob([content], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const triggerJsonDownload = (
    data: Record<string, unknown>,
    filename: string
  ) => {
    const blob = new Blob([JSON.stringify(data, null, 2)], {
      type: "application/json;charset=utf-8",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const getNovelTitle = (id: number): string => {
    const novel = novels.find((n) => n.id === id);
    return novel?.title ?? `novel-${id}`;
  };

  const handleExport = async (format: ExportFormat) => {
    if (selectedNovelId === null) return;

    setExporting(format);
    setError(null);

    const title = getNovelTitle(selectedNovelId);

    try {
      if (format === "markdown") {
        const res = await fetch(`/api/export/novel/${selectedNovelId}/markdown`);
        if (!res.ok) throw new Error(`Server returned ${res.status}`);
        const content = await res.text();
        triggerTextDownload(content, `${title}-export.md`);
      } else if (format === "json") {
        const res = await fetch(`/api/export/novel/${selectedNovelId}/json`);
        if (!res.ok) throw new Error(`Server returned ${res.status}`);
        const data = await res.json();
        triggerJsonDownload(data, `${title}-kb.json`);
      } else if (format === "wiki") {
        const res = await fetch(
          `/api/export/novel/${selectedNovelId}/wiki/markdown`
        );
        if (!res.ok) throw new Error(`Server returned ${res.status}`);
        const content = await res.text();
        triggerTextDownload(content, `${title}-wiki.md`);
      }
    } catch (err) {
      const msg =
        err instanceof Error ? err.message : "Export failed unexpectedly.";
      setError(msg);
    } finally {
      setExporting(null);
    }
  };

  const isLoading = exporting !== null;

  return (
    <VStack gap={6} align="stretch">
      {/* Novel Selection */}
      <Box p={4} borderWidth="1px" borderRadius="md">
        <Heading size="md" mb={4}>
          Select Novel
        </Heading>
        {novelsLoading ? (
          <HStack gap={2}>
            <Spinner size="sm" />
            <Text fontSize="sm" color="gray.600">
              Loading novels...
            </Text>
          </HStack>
        ) : novels.length === 0 ? (
          <Text fontSize="sm" color="gray.500">
            No novels found. Upload a novel first to enable exports.
          </Text>
        ) : (
          <select
            value={selectedNovelId ?? ""}
            onChange={(e) => {
              setSelectedNovelId(
                e.target.value ? Number(e.target.value) : null
              );
              setError(null);
            }}
            style={{
              width: "100%",
              padding: "8px 12px",
              borderRadius: "6px",
              border: "1px solid #e2e8f0",
              fontSize: "14px",
            }}
          >
            <option value="">Select a novel...</option>
            {novels.map((novel) => (
              <option key={novel.id} value={novel.id}>
                {novel.title}
                {novel.author ? ` by ${novel.author}` : ""} (
                {novel.chapter_count} chapters)
              </option>
            ))}
          </select>
        )}
      </Box>

      {/* Export Actions */}
      <Box p={4} borderWidth="1px" borderRadius="md">
        <Heading size="md" mb={4}>
          Export Options
        </Heading>
        <Text fontSize="sm" color="gray.600" mb={4}>
          Choose an export format for the selected novel.
        </Text>

        {!selectedNovelId ? (
          <Text fontSize="sm" color="gray.500">
            Select a novel above to enable exports.
          </Text>
        ) : (
          <VStack gap={3} align="stretch">
            {/* Export as Markdown */}
            <HStack
              justify="space-between"
              p={3}
              borderWidth="1px"
              borderRadius="md"
            >
              <Box>
                <Text fontWeight="medium">Export as Markdown</Text>
                <Text fontSize="sm" color="gray.600">
                  Download the full novel content as a Markdown file.
                </Text>
              </Box>
              <Box
                as="button"
                px={4}
                py={2}
                bg="green.500"
                color="white"
                borderRadius="md"
                fontSize="sm"
                _hover={{ bg: "green.600" }}
                _disabled={{ opacity: 0.6, cursor: "not-allowed" }}
                onClick={() => handleExport("markdown")}
                aria-disabled={isLoading}
              >
                {exporting === "markdown" ? (
                  <HStack gap={1}>
                    <Spinner size="xs" />
                    <Text>Exporting...</Text>
                  </HStack>
                ) : (
                  "Export Markdown"
                )}
              </Box>
            </HStack>

            {/* Export as JSON (KB) */}
            <HStack
              justify="space-between"
              p={3}
              borderWidth="1px"
              borderRadius="md"
            >
              <Box>
                <Text fontWeight="medium">Export Knowledge Base (JSON)</Text>
                <Text fontSize="sm" color="gray.600">
                  Download all entity and relationship data as JSON.
                </Text>
              </Box>
              <Box
                as="button"
                px={4}
                py={2}
                bg="purple.500"
                color="white"
                borderRadius="md"
                fontSize="sm"
                _hover={{ bg: "purple.600" }}
                _disabled={{ opacity: 0.6, cursor: "not-allowed" }}
                onClick={() => handleExport("json")}
                aria-disabled={isLoading}
              >
                {exporting === "json" ? (
                  <HStack gap={1}>
                    <Spinner size="xs" />
                    <Text>Exporting...</Text>
                  </HStack>
                ) : (
                  "Export JSON"
                )}
              </Box>
            </HStack>

            {/* Export Wiki as Markdown */}
            <HStack
              justify="space-between"
              p={3}
              borderWidth="1px"
              borderRadius="md"
            >
              <Box>
                <Text fontWeight="medium">Export Wiki (Markdown)</Text>
                <Text fontSize="sm" color="gray.600">
                  Download all wiki pages for this novel as Markdown.
                </Text>
              </Box>
              <Box
                as="button"
                px={4}
                py={2}
                bg="orange.500"
                color="white"
                borderRadius="md"
                fontSize="sm"
                _hover={{ bg: "orange.600" }}
                _disabled={{ opacity: 0.6, cursor: "not-allowed" }}
                onClick={() => handleExport("wiki")}
                aria-disabled={isLoading}
              >
                {exporting === "wiki" ? (
                  <HStack gap={1}>
                    <Spinner size="xs" />
                    <Text>Exporting...</Text>
                  </HStack>
                ) : (
                  "Export Wiki"
                )}
              </Box>
            </HStack>
          </VStack>
        )}

        {/* Error State */}
        {error && (
          <HStack gap={2} p={3} borderRadius="md" bg="red.50" mt={3}>
            <Box w={2} h={2} borderRadius="full" bg="red.500" />
            <Text fontSize="sm" color="red.700">
              {error}
            </Text>
          </HStack>
        )}
      </Box>
    </VStack>
  );
}
