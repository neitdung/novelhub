"use client";

import { Box, HStack, Table, Text, VStack } from "@chakra-ui/react";
import { useMemo } from "react";

// ─── Types ───────────────────────────────────────────────────────────────────

export interface ChapterRow {
  chapter_number: number;
  title?: string;
  state: string;
  error?: string | null;
  attempts?: number;
}

interface ChapterStatusTableProps {
  chapters: ChapterRow[];
  totalChapters: number;
}

// ─── Status color map ────────────────────────────────────────────────────────

const statusColors: Record<string, string> = {
  pending: "gray.400",
  running: "blue.500",
  completed: "green.500",
  complete: "green.500",
  failed: "red.500",
  error: "red.500",
  cancelled: "orange.500",
  paused: "yellow.500",
};

const statusLabels: Record<string, string> = {
  pending: "Pending",
  running: "Running",
  completed: "Complete",
  complete: "Complete",
  failed: "Error",
  error: "Error",
  cancelled: "Cancelled",
  paused: "Paused",
};

// ─── Component ───────────────────────────────────────────────────────────────

export function ChapterStatusTable({
  chapters,
  totalChapters,
}: ChapterStatusTableProps) {
  // Generate full chapter list from 1..totalChapters
  const rows = useMemo(() => {
    const map = new Map<number, ChapterRow>();
    for (const ch of chapters) {
      map.set(ch.chapter_number, ch);
    }

    const result: ChapterRow[] = [];
    for (let i = 1; i <= totalChapters; i++) {
      const existing = map.get(i);
      result.push(
        existing ?? {
          chapter_number: i,
          title: `Chapter ${i}`,
          state: "pending",
        },
      );
    }
    return result;
  }, [chapters, totalChapters]);

  if (rows.length === 0) {
    return (
      <Box p={4} textAlign="center">
        <Text color="gray.500">No chapters to display.</Text>
      </Box>
    );
  }

  return (
    <Box overflowX="auto">
      <Table.Root variant="outline" size="sm" width="100%">
        <Table.Header>
          <Table.Row>
            <Table.ColumnHeader>#</Table.ColumnHeader>
            <Table.ColumnHeader>Title</Table.ColumnHeader>
            <Table.ColumnHeader>Status</Table.ColumnHeader>
            <Table.ColumnHeader>Details</Table.ColumnHeader>
          </Table.Row>
        </Table.Header>
        <Table.Body>
          {rows.map((row) => {
            const color = statusColors[row.state] ?? "gray.400";
            const label = statusLabels[row.state] ?? row.state;

            return (
              <Table.Row key={row.chapter_number}>
                <Table.Cell>{row.chapter_number}</Table.Cell>
                <Table.Cell>
                  <Text noOfLines={1} maxWidth="300px">
                    {row.title ?? `Chapter ${row.chapter_number}`}
                  </Text>
                </Table.Cell>
                <Table.Cell>
                  <HStack gap={2}>
                    <Box
                      w="10px"
                      h="10px"
                      borderRadius="full"
                      bg={color}
                      flexShrink={0}
                    />
                    <Text color={color} fontWeight="medium">
                      {label}
                    </Text>
                  </HStack>
                </Table.Cell>
                <Table.Cell>
                  {row.state === "failed" || row.state === "error" ? (
                    <VStack align="start" gap={1}>
                      <Text fontSize="sm" color="red.600">
                        {row.error ?? "Unknown error"}
                      </Text>
                      {row.attempts != null && row.attempts > 1 && (
                        <Text fontSize="xs" color="gray.500">
                          Retried {row.attempts - 1} time
                          {row.attempts > 2 ? "s" : ""}
                        </Text>
                      )}
                    </VStack>
                  ) : row.state === "running" ? (
                    <Text fontSize="sm">Processing...</Text>
                  ) : (
                    <Text fontSize="sm" color="gray.400">
                      —
                    </Text>
                  )}
                </Table.Cell>
              </Table.Row>
            );
          })}
        </Table.Body>
      </Table.Root>
    </Box>
  );
}
