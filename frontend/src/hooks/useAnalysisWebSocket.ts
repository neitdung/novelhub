"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useGetAnalysisStatusQuery } from "@/store/api";

// ─── Types ───────────────────────────────────────────────────────────────────

export interface ChapterTaskStatus {
  state: string;
  attempts: number;
  error: string | null;
  started_at: string | null;
  completed_at: string | null;
}

export interface AnalysisProgress {
  novel_id: number;
  state: string;
  chapters_processed: number;
  chapters_total: number;
  entities_count: number;
  facts_count: number;
  errors: Array<{ chapter: string; error: string }>;
  tasks?: Record<string, ChapterTaskStatus>;
}

export type ConnectionStatus =
  | "connecting"
  | "connected"
  | "disconnected"
  | "polling";

interface UseAnalysisWebSocketOptions {
  /** Interval in ms for polling fallback (default 3000) */
  pollInterval?: number;
  /** Whether to enable the connection (default true) */
  enabled?: boolean;
}

// ─── Hook ────────────────────────────────────────────────────────────────────

export function useAnalysisWebSocket(
  novelId: number | null,
  options: UseAnalysisWebSocketOptions = {},
) {
  const { pollInterval = 3000, enabled = true } = options;

  const [progress, setProgress] = useState<AnalysisProgress | null>(null);
  const [connectionStatus, setConnectionStatus] =
    useState<ConnectionStatus>("disconnected");
  const [wsError, setWsError] = useState<string | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const pingIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const reconnectAttemptRef = useRef(0);
  const maxReconnectDelay = 30000;
  const isUnmountedRef = useRef(false);

  // ── RTK Query polling fallback ──────────────────────────────────────────
  const { data: pollData } = useGetAnalysisStatusQuery(novelId ?? 0, {
    skip: !novelId || connectionStatus === "connected",
    pollingInterval: connectionStatus === "polling" ? pollInterval : 0,
  });

  // Sync polling data into progress state
  useEffect(() => {
    if (pollData && connectionStatus !== "connected") {
      setProgress({
        novel_id: pollData.novel_id,
        state: pollData.state,
        chapters_processed: pollData.chapters_processed,
        chapters_total: pollData.chapters_total,
        entities_count: pollData.entities_count,
        facts_count: pollData.facts_count,
        errors: pollData.errors,
      });
    }
  }, [pollData, connectionStatus]);

  // ── WebSocket connection ────────────────────────────────────────────────
  const connect = useCallback(() => {
    if (!novelId || !enabled || isUnmountedRef.current) return;

    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const host = window.location.host;
    const url = `${protocol}//${host}/ws/analysis/${novelId}`;

    setConnectionStatus("connecting");
    setWsError(null);

    try {
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        if (isUnmountedRef.current) {
          ws.close();
          return;
        }
        setConnectionStatus("connected");
        reconnectAttemptRef.current = 0;

        // Send ping every 30 seconds to keep alive
        pingIntervalRef.current = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send("ping");
          }
        }, 30000);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);

          if (data.type === "pong") {
            return; // Ignore pong responses
          }

          setProgress((prev) => ({
            ...prev,
            ...data,
            novel_id: data.novel_id ?? prev?.novel_id ?? novelId,
          }));
        } catch {
          // Ignore non-JSON messages
        }
      };

      ws.onerror = () => {
        setWsError("WebSocket connection error");
      };

      ws.onclose = () => {
        if (pingIntervalRef.current) {
          clearInterval(pingIntervalRef.current);
          pingIntervalRef.current = null;
        }

        if (isUnmountedRef.current) return;

        setConnectionStatus("disconnected");

        // Exponential backoff reconnect
        const delay = Math.min(
          1000 * 2 ** reconnectAttemptRef.current,
          maxReconnectDelay,
        );
        reconnectAttemptRef.current += 1;

        reconnectTimerRef.current = setTimeout(() => {
          if (!isUnmountedRef.current) {
            connect();
          }
        }, delay);
      };
    } catch (err) {
      setWsError(
        err instanceof Error ? err.message : "Failed to connect",
      );
      setConnectionStatus("polling");
    }
  }, [novelId, enabled]);

  // ── Lifecycle ───────────────────────────────────────────────────────────
  useEffect(() => {
    isUnmountedRef.current = false;

    if (novelId && enabled) {
      connect();
    }

    return () => {
      isUnmountedRef.current = true;
      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current);
        reconnectTimerRef.current = null;
      }
      if (pingIntervalRef.current) {
        clearInterval(pingIntervalRef.current);
        pingIntervalRef.current = null;
      }
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [novelId, enabled, connect]);

  // ── Polling fallback activation ─────────────────────────────────────────
  useEffect(() => {
    if (connectionStatus === "disconnected" && novelId && enabled) {
      const timer = setTimeout(() => {
        if (!isUnmountedRef.current) {
          setConnectionStatus("polling");
        }
      }, 5000); // Fall back to polling after 5s of disconnection
      return () => clearTimeout(timer);
    }
    return;
  }, [connectionStatus, novelId, enabled]);

  return {
    progress,
    connectionStatus,
    wsError,
  };
}
