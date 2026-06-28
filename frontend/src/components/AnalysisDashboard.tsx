"use client";

import {
  Box,
  Button,
  Card,
  HStack,
  Input,
  Text,
  VStack,
} from "@chakra-ui/react";
import { useCallback, useEffect, useState } from "react";
import {
  useCancelAnalysisMutation,
  useGetAnalysisStatusQuery,
  useGetChaptersQuery,
  useGetNovelsQuery,
  usePauseAnalysisMutation,
  useResumeAnalysisMutation,
  useStartAnalysisMutation,
} from "@/store/api";
import { useAnalysisWebSocket } from "@/hooks/useAnalysisWebSocket";
import type { AnalysisProgress } from "@/hooks/useAnalysisWebSocket";
import { ChapterStatusTable } from "./ChapterStatusTable";
import { LoadingState } from "./LoadingState";
import { ErrorState } from "./ErrorState";
import { EmptyState } from "./EmptyState";

// ─── Types ───────────────────────────────────────────────────────────────────

type AnalysisAction = "start" | "pause" | "resume" | "cancel";

// ─── Component ───────────────────────────────────────────────────────────────

export function AnalysisDashboard() {
  // ── Novels ──────────────────────────────────────────────────────────────
  const {
    data: novelsData,
    isLoading: novelsLoading,
    isError: novelsError,
  } = useGetNovelsQuery();
  const novels = novelsData?.novels ?? [];

  const [selectedNovelId, setSelectedNovelId] = useState<number | null>(null);

  // ── Chapters for range ──────────────────────────────────────────────────
  const { data: chapters, isLoading: chaptersLoading } = useGetChaptersQuery(
    selectedNovelId ?? 0,
    { skip: !selectedNovelId },
  );
  const totalChapters = chapters?.length ?? 0;

  const [chapterStart, setChapterStart] = useState(1);
  const [chapterEnd, setChapterEnd] = useState<number | null>(null);

  // Update chapter range when novel changes
  useEffect(() => {
    setChapterStart(1);
    setChapterEnd(totalChapters > 0 ? totalChapters : null);
  }, [totalChapters, selectedNovelId]);

  // ── Analysis API mutations ──────────────────────────────────────────────
  const [startAnalysis, { isLoading: isStarting }] = useStartAnalysisMutation();
  const [pauseAnalysis, { isLoading: isPausing }] = usePauseAnalysisMutation();
  const [resumeAnalysis, { isLoading: isResuming }] =
    useResumeAnalysisMutation();
  const [cancelAnalysis, { isLoading: isCancelling }] =
    useCancelAnalysisMutation();

  // ── Analysis status via REST (for initial load and polling fallback) ────
  const {
    data: restStatus,
    isLoading: statusLoading,
    refetch: refetchStatus,
  } = useGetAnalysisStatusQuery(selectedNovelId ?? 0, {
    skip: !selectedNovelId,
  });

  // ── WebSocket hook for real-time updates ────────────────────────────────
  const { progress: wsProgress, connectionStatus, wsError } =
    useAnalysisWebSocket(selectedNovelId, {
      enabled: selectedNovelId != null,
    });

  // ── Merged progress ─────────────────────────────────────────────────────
  const [mergedProgress, setMergedProgress] =
    useState<AnalysisProgress | null>(null);

  useEffect(() => {
    // Prefer WebSocket data, fall back to REST
    if (wsProgress) {
      setMergedProgress(wsProgress);
    } else if (restStatus) {
      setMergedProgress({
        novel_id: restStatus.novel_id,
        state: restStatus.state,
        chapters_processed: restStatus.chapters_processed,
        chapters_total: restStatus.chapters_total,
        entities_count: restStatus.entities_count,
        facts_count: restStatus.facts_count,
        errors: restStatus.errors,
      });
    }
  }, [wsProgress, restStatus]);

  // ── Action handlers ─────────────────────────────────────────────────────
  const handleAction = useCallback(
    async (action: AnalysisAction) => {
      if (!selectedNovelId) return;

      try {
        switch (action) {
          case "start":
            await startAnalysis({
              novel_id: selectedNovelId,
              chapter_start: chapterStart,
              chapter_end: chapterEnd,
            }).unwrap();
            break;
          case "pause":
            await pauseAnalysis(selectedNovelId).unwrap();
            break;
          case "resume":
            await resumeAnalysis(selectedNovelId).unwrap();
            break;
          case "cancel":
            await cancelAnalysis(selectedNovelId).unwrap();
            break;
        }
      } catch (err) {
        console.error(`Analysis ${action} failed:`, err);
      }
    },
    [
      selectedNovelId,
      chapterStart,
      chapterEnd,
      startAnalysis,
      pauseAnalysis,
      resumeAnalysis,
      cancelAnalysis,
    ],
  );

  // ── Error handling ──────────────────────────────────────────────────────
  const [showErrors, setShowErrors] = useState(false);
  const errors = mergedProgress?.errors ?? [];
  const displayErrors = showErrors ? errors : errors.slice(0, 5);

  // ── Connection state ────────────────────────────────────────────────────
  const isRunning =
    mergedProgress?.state === "running" ||
    mergedProgress?.state === "pending";
  const isPaused = mergedProgress?.state === "paused";
  const isCompleted = mergedProgress?.state === "completed";
  const isFailed = mergedProgress?.state === "failed";
  const isCancelled = mergedProgress?.state === "cancelled";
  const hasActiveAnalysis = isRunning || isPaused;

  // ── Loading state ───────────────────────────────────────────────────────
  if (novelsLoading) {
    return <LoadingState message="Loading novels..." />;
  }

  if (novelsError) {
    return (
      <ErrorState
        message="Failed to load novels. Please check your connection."
        onRetry={() => window.location.reload()}
      />
    );
  }

  if (novels.length === 0) {
    return (
      <EmptyState
        title="No Novels Found"
        message="Upload a novel first to run analysis."
      />
    );
  }

  return (
    <VStack gap={6} align="stretch">
      {/* ── Connection Status Banner ───────────────────────────────────── */}
      {connectionStatus === "polling" && (
        <Box
          p={3}
          bg="yellow.50"
          borderRadius="md"
          borderWidth="1px"
          borderColor="yellow.200"
        >
          <Text fontSize="sm" color="yellow.800">
            Real-time updates unavailable. Using polling mode.
          </Text>
        </Box>
      )}
      {connectionStatus === "connecting" && (
        <Box
          p={3}
          bg="blue.50"
          borderRadius="md"
          borderWidth="1px"
          borderColor="blue.200"
        >
          <Text fontSize="sm" color="blue.800">
            Connecting to real-time updates...
          </Text>
        </Box>
      )}
      {wsError && (
        <Box
          p={3}
          bg="red.50"
          borderRadius="md"
          borderWidth="1px"
          borderColor="red.200"
        >
          <Text fontSize="sm" color="red.800">
            WebSocket error: {wsError}
          </Text>
        </Box>
      )}

      {/* ── Novel Selector ─────────────────────────────────────────────── */}
      <Card.Root variant="outline">
        <Card.Body>
          <VStack gap={4} align="stretch">
            <Text fontWeight="bold" fontSize="lg">
              Analysis Target
            </Text>
            <select
              value={selectedNovelId?.toString() ?? ""}
              onChange={(e) => {
                const val = e.target.value;
                setSelectedNovelId(val ? Number(val) : null);
              }}
              style={{
                width: "100%",
                padding: "8px 12px",
                border: "1px solid #CBD5E0",
                borderRadius: "8px",
                fontSize: "16px",
                background: "white",
              }}
            >
              <option value="">Select a novel...</option>
              {novels.map((novel) => (
                <option key={novel.id} value={novel.id.toString()}>
                  {novel.title}
                </option>
              ))}
            </select>

            {/* Chapter Range */}
            <HStack gap={4} align="end">
              <Box flex={1}>
                <Text mb={1} fontSize="sm" color="gray.600">
                  Start Chapter
                </Text>
                <Input
                  type="number"
                  min={1}
                  max={totalChapters || 1}
                  value={chapterStart}
                  onChange={(e) => {
                    const val = Number(e.target.value);
                    setChapterStart(
                      Math.max(1, Math.min(val, totalChapters || 1)),
                    );
                  }}
                  disabled={hasActiveAnalysis}
                />
              </Box>
              <Box flex={1}>
                <Text mb={1} fontSize="sm" color="gray.600">
                  End Chapter
                </Text>
                <Input
                  type="number"
                  min={chapterStart}
                  max={totalChapters || 1}
                  value={chapterEnd ?? totalChapters}
                  onChange={(e) => {
                    const val = Number(e.target.value);
                    setChapterEnd(
                      val > 0
                        ? Math.max(
                            chapterStart,
                            Math.min(val, totalChapters || 1),
                          )
                        : null,
                    );
                  }}
                  disabled={hasActiveAnalysis}
                />
              </Box>
              <Text fontSize="sm" color="gray.500" whiteSpace="nowrap">
                of {totalChapters} chapters
              </Text>
            </HStack>
          </VStack>
        </Card.Body>
      </Card.Root>

      {/* ── Controls ───────────────────────────────────────────────────── */}
      <Card.Root variant="outline">
        <Card.Body>
          <HStack gap={4} wrap="wrap">
            {!hasActiveAnalysis && !isCompleted && !isFailed && !isCancelled && (
              <Button
                colorPalette="blue"
                onClick={() => handleAction("start")}
                loading={isStarting}
                disabled={!selectedNovelId}
              >
                Start Analysis
              </Button>
            )}

            {isRunning && (
              <Button
                colorPalette="yellow"
                onClick={() => handleAction("pause")}
                loading={isPausing}
              >
                Pause
              </Button>
            )}

            {isPaused && (
              <Button
                colorPalette="green"
                onClick={() => handleAction("resume")}
                loading={isResuming}
              >
                Resume
              </Button>
            )}

            {hasActiveAnalysis && (
              <Button
                colorPalette="red"
                variant="outline"
                onClick={() => handleAction("cancel")}
                loading={isCancelling}
              >
                Cancel
              </Button>
            )}

            {(isCompleted || isFailed || isCancelled) && (
              <Button
                colorPalette="blue"
                variant="outline"
                onClick={() => handleAction("start")}
                loading={isStarting}
                disabled={!selectedNovelId}
              >
                Restart Analysis
              </Button>
            )}
          </HStack>
        </Card.Body>
      </Card.Root>

      {/* ── Status Summary ──────────────────────────────────────────────── */}
      {selectedNovelId && mergedProgress && (
        <Card.Root variant="outline">
          <Card.Body>
            <Text fontWeight="bold" fontSize="lg" mb={3}>
              Progress Summary
            </Text>
            <Box
              display="grid"
              gridTemplateColumns="repeat(4, 1fr)"
              gap={4}
            >
              <Box
                p={3}
                bg="blue.50"
                borderRadius="md"
                textAlign="center"
              >
                <Text fontSize="2xl" fontWeight="bold" color="blue.700">
                  {mergedProgress.chapters_processed}
                </Text>
                <Text fontSize="sm" color="blue.600">
                  Chapters Processed
                </Text>
                <Text fontSize="xs" color="blue.400">
                  of {mergedProgress.chapters_total}
                </Text>
              </Box>
              <Box
                p={3}
                bg="green.50"
                borderRadius="md"
                textAlign="center"
              >
                <Text fontSize="2xl" fontWeight="bold" color="green.700">
                  {mergedProgress.entities_count}
                </Text>
                <Text fontSize="sm" color="green.600">
                  Entities Found
                </Text>
              </Box>
              <Box
                p={3}
                bg="purple.50"
                borderRadius="md"
                textAlign="center"
              >
                <Text fontSize="2xl" fontWeight="bold" color="purple.700">
                  {mergedProgress.facts_count}
                </Text>
                <Text fontSize="sm" color="purple.600">
                  Facts Found
                </Text>
              </Box>
              <Box
                p={3}
                borderRadius="md"
                textAlign="center"
                bg={errors.length > 0 ? "red.50" : "gray.50"}
              >
                <Text
                  fontSize="2xl"
                  fontWeight="bold"
                  color={errors.length > 0 ? "red.700" : "gray.500"}
                >
                  {errors.length}
                </Text>
                <Text
                  fontSize="sm"
                  color={errors.length > 0 ? "red.600" : "gray.500"}
                >
                  Errors
                </Text>
              </Box>
            </Box>
          </Card.Body>
        </Card.Root>
      )}

      {/* ── Chapter Status Table ────────────────────────────────────────── */}
      {selectedNovelId && mergedProgress && (
        <Card.Root variant="outline">
          <Card.Header>
            <HStack justify="space-between">
              <Text fontWeight="bold" fontSize="lg">
                Chapter Status
              </Text>
              <Text fontSize="sm" color="gray.500">
                State: {mergedProgress.state}
              </Text>
            </HStack>
          </Card.Header>
          <Card.Body>
            {chaptersLoading ? (
              <LoadingState message="Loading chapter list..." />
            ) : (
              <ChapterStatusTable
                chapters={(chapters ?? []).map((ch) => ({
                  chapter_number: ch.chapter_number,
                  title: ch.title,
                  state: getChapterState(
                    ch.chapter_number,
                    mergedProgress,
                  ),
                  error: getChapterError(
                    ch.chapter_number,
                    mergedProgress,
                  ),
                  attempts: getChapterAttempts(
                    ch.chapter_number,
                    mergedProgress,
                  ),
                }))}
                totalChapters={mergedProgress.chapters_total}
              />
            )}
          </Card.Body>
        </Card.Root>
      )}

      {/* ── Errors Section ──────────────────────────────────────────────── */}
      {errors.length > 0 && (
        <Card.Root variant="outline" borderColor="red.200">
          <Card.Header>
            <HStack justify="space-between">
              <Text fontWeight="bold" color="red.600">
                Errors ({errors.length})
              </Text>
              {errors.length > 5 && (
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => setShowErrors(!showErrors)}
                >
                  {showErrors ? "Show Less" : "Show All"}
                </Button>
              )}
            </HStack>
          </Card.Header>
          <Card.Body>
            <VStack gap={2} align="stretch">
              {displayErrors.map((err, i) => (
                <Box
                  key={i}
                  p={3}
                  bg="red.50"
                  borderRadius="md"
                  borderWidth="1px"
                  borderColor="red.100"
                >
                  <HStack justify="space-between">
                    <VStack align="start" gap={1}>
                      <Text fontWeight="medium" fontSize="sm">
                        Chapter {err.chapter}
                      </Text>
                      <Text fontSize="sm" color="red.700">
                        {err.error}
                      </Text>
                    </VStack>
                    {isFailed && (
                      <Button
                        size="xs"
                        colorPalette="blue"
                        variant="outline"
                        onClick={() => handleAction("start")}
                      >
                        Retry
                      </Button>
                    )}
                  </HStack>
                </Box>
              ))}
            </VStack>
          </Card.Body>
        </Card.Root>
      )}

      {/* ── Empty State ────────────────────────────────────────────────── */}
      {!selectedNovelId && (
        <EmptyState
          title="Select a Novel"
          message="Choose a novel from the dropdown above to begin analysis."
        />
      )}
    </VStack>
  );
}

// ─── Helper functions ────────────────────────────────────────────────────────

function getChapterState(
  chapterNumber: number,
  progress: AnalysisProgress,
): string {
  if (progress.tasks) {
    const task = progress.tasks[String(chapterNumber)];
    if (task) return task.state;
  }

  // Derive state from summary data
  const chapterStr = String(chapterNumber);
  const hasError = progress.errors.some((e) => e.chapter === chapterStr);

  if (hasError) return "error";

  if (chapterNumber <= progress.chapters_processed) return "completed";
  if (progress.state === "running" || progress.state === "pending") {
    if (chapterNumber === progress.chapters_processed + 1) return "running";
    return "pending";
  }

  return "pending";
}

function getChapterError(
  chapterNumber: number,
  progress: AnalysisProgress,
): string | null {
  if (progress.tasks) {
    const task = progress.tasks[String(chapterNumber)];
    if (task?.error) return task.error;
  }

  const chapterStr = String(chapterNumber);
  const error = progress.errors.find((e) => e.chapter === chapterStr);
  return error?.error ?? null;
}

function getChapterAttempts(
  chapterNumber: number,
  progress: AnalysisProgress,
): number | undefined {
  if (progress.tasks) {
    const task = progress.tasks[String(chapterNumber)];
    return task?.attempts;
  }
  return undefined;
}
