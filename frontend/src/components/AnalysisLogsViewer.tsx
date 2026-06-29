"use client";

import {
  Badge,
  Box,
  Button,
  Code,
  HStack,
  Text,
  VStack,
} from "@chakra-ui/react";
import { useMemo, useState } from "react";

// ─── Types ───────────────────────────────────────────────────────────────────

export interface LogEntry {
  timestamp: string;
  level: "info" | "warn" | "error";
  chapter?: number | string;
  message: string;
}

interface AnalysisLogsViewerProps {
  /** Current analysis state (e.g. "running", "paused", "completed", "failed") */
  analysisState?: string;
  /** Errors array from AnalysisProgress */
  errors?: Array<{ chapter: string; error: string }>;
  /** Task-level statuses from AnalysisProgress */
  tasks?: Record<string, { state: string; error: string | null; attempts: number }>;
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

function formatTimestamp(date: Date): string {
  return date.toISOString().replace("T", " ").slice(0, 19);
}

function stateToBadgeColor(state: string): string {
  switch (state) {
    case "running":
      return "blue";
    case "completed":
      return "green";
    case "failed":
    case "error":
      return "red";
    case "paused":
      return "yellow";
    case "cancelled":
      return "orange";
    default:
      return "gray";
  }
}

// ─── Component ───────────────────────────────────────────────────────────────

export function AnalysisLogsViewer({
  analysisState,
  errors = [],
  tasks = {},
}: AnalysisLogsViewerProps) {
  const [expanded, setExpanded] = useState(true);
  const [showAll, setShowAll] = useState(false);

  // Build log entries from available data
  const logs = useMemo(() => {
    const entries: LogEntry[] = [];
    const now = new Date();

    // Analysis state entry
    if (analysisState) {
      entries.push({
        timestamp: formatTimestamp(now),
        level: analysisState === "failed" ? "error" : "info",
        message: `Analysis state: ${analysisState}`,
      });
    }

    // Task-level logs (sorted by chapter number)
    const sortedChapters = Object.keys(tasks)
      .map(Number)
      .sort((a, b) => a - b);

    for (const ch of sortedChapters) {
      const task = tasks[String(ch)];
      if (!task) continue;

      entries.push({
        timestamp: formatTimestamp(now),
        level: task.state === "error" || task.state === "failed" ? "error" : "info",
        chapter: ch,
        message: `Chapter ${ch}: ${task.state}${task.attempts > 1 ? ` (${task.attempts} attempts)` : ""}`,
      });

      if (task.error) {
        entries.push({
          timestamp: formatTimestamp(now),
          level: "error",
          chapter: ch,
          message: `Chapter ${ch} error: ${task.error}`,
        });
      }
    }

    // Error-level entries from the errors array
    for (const err of errors) {
      entries.push({
        timestamp: formatTimestamp(now),
        level: "error",
        chapter: err.chapter,
        message: err.error,
      });
    }

    return entries;
  }, [analysisState, errors, tasks]);

  const displayedLogs = showAll ? logs : logs.slice(0, 50);
  const hasMore = logs.length > 50;

  if (logs.length === 0) {
    return (
      <Box p={4} textAlign="center">
        <Text fontSize="sm" color="gray.500">
          No analysis logs available. Start an analysis to see logs.
        </Text>
      </Box>
    );
  }

  return (
    <Box>
      <HStack justify="space-between" mb={2}>
        <HStack gap={2}>
          <Text fontWeight="bold" fontSize="sm">
            Logs ({logs.length})
          </Text>
          <Badge colorPalette="gray" size="sm">
            {errors.length} errors
          </Badge>
        </HStack>
        <HStack gap={2}>
          {hasMore && (
            <Button
              size="xs"
              variant="ghost"
              onClick={() => setShowAll(!showAll)}
            >
              {showAll ? "Show Less" : `Show All (${logs.length})`}
            </Button>
          )}
          <Button
            size="xs"
            variant="ghost"
            onClick={() => setExpanded(!expanded)}
          >
            {expanded ? "Collapse" : "Expand"}
          </Button>
        </HStack>
      </HStack>

      {expanded && (
        <Box
          maxH="400px"
          overflowY="auto"
          borderWidth="1px"
          borderRadius="md"
          bg="gray.900"
          p={3}
        >
          <VStack align="stretch" gap={1}>
            {displayedLogs.map((log, i) => (
              <HStack key={i} align="start" gap={2} fontFamily="mono">
                <Text
                  fontSize="xs"
                  color="gray.500"
                  whiteSpace="nowrap"
                  minW="170px"
                >
                  {log.timestamp}
                </Text>
                <Badge
                  colorPalette={log.level === "error" ? "red" : log.level === "warn" ? "yellow" : "blue"}
                  size="xs"
                  minW="45px"
                  justifyContent="center"
                >
                  {log.level.toUpperCase()}
                </Badge>
                {log.chapter != null && (
                  <Badge colorPalette="purple" size="xs" minW="30px" justifyContent="center">
                    Ch.{log.chapter}
                  </Badge>
                )}
                <Code
                  fontSize="xs"
                  bg="transparent"
                  color={log.level === "error" ? "red.300" : "gray.300"}
                  whiteSpace="pre-wrap"
                  wordBreak="break-word"
                >
                  {log.message}
                </Code>
              </HStack>
            ))}
          </VStack>
        </Box>
      )}
    </Box>
  );
}
