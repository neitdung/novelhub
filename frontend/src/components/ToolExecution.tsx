"use client";

import { Box, Button, CollapsibleContent, CollapsibleRoot, CollapsibleTrigger, HStack, Text, VStack } from "@chakra-ui/react";
import { useState } from "react";

export interface ToolCallData {
  tool?: string;
  name?: string;
  arguments?: Record<string, unknown>;
  result?: unknown;
  error?: string | null;
}

interface ToolExecutionProps {
  toolCalls: ToolCallData[];
}

function formatValue(value: unknown): string {
  if (typeof value === "string") return value;
  try {
    return JSON.stringify(value, null, 2);
  } catch {
    return String(value);
  }
}

function ToolCallItem({ toolCall }: { toolCall: ToolCallData }) {
  const toolName = toolCall.tool || toolCall.name || "Unknown Tool";
  const hasArguments = toolCall.arguments && Object.keys(toolCall.arguments).length > 0;
  const hasResult = toolCall.result !== undefined;
  const hasError = !!toolCall.error;
  const [resultOpen, setResultOpen] = useState(false);

  return (
    <Box
      p={3}
      bg="gray.50"
      borderRadius="md"
      borderWidth="1px"
      borderColor="gray.200"
      _dark={{ bg: "gray.700", borderColor: "gray.600" }}
    >
      <HStack justify="space-between" mb={hasArguments || hasResult || hasError ? 2 : 0}>
        <Text fontSize="sm" fontWeight="bold" color="blue.600" _dark={{ color: "blue.300" }}>
          🔧 {toolName}
        </Text>
      </HStack>

      {hasError && (
        <Text fontSize="sm" color="red.500" mb={2}>
          ⚠ Error: {toolCall.error}
        </Text>
      )}

      {hasArguments && (
        <Box mb={2}>
          <Text fontSize="xs" fontWeight="semibold" color="gray.500" mb={1}>
            Arguments:
          </Text>
          <Box
            as="pre"
            p={2}
            bg="gray.100"
            borderRadius="sm"
            fontSize="xs"
            whiteSpace="pre-wrap"
            fontFamily="mono"
            maxH="120px"
            overflowY="auto"
            _dark={{ bg: "gray.600" }}
          >
            {formatValue(toolCall.arguments)}
          </Box>
        </Box>
      )}

      {hasResult && (
        <CollapsibleRoot open={resultOpen} onOpenChange={(e) => setResultOpen(e.open)}>
          <CollapsibleTrigger asChild>
            <Button size="xs" variant="ghost" colorPalette="gray" mb={1}>
              {resultOpen ? "▼" : "▶"} Result
            </Button>
          </CollapsibleTrigger>
          <CollapsibleContent>
            <Box
              as="pre"
              p={2}
              bg="green.50"
              borderRadius="sm"
              fontSize="xs"
              whiteSpace="pre-wrap"
              fontFamily="mono"
              maxH="300px"
              overflowY="auto"
              _dark={{ bg: "green.900", color: "green.100" }}
            >
              {formatValue(toolCall.result)}
            </Box>
          </CollapsibleContent>
        </CollapsibleRoot>
      )}
    </Box>
  );
}

export function ToolExecution({ toolCalls }: ToolExecutionProps) {
  if (!toolCalls || toolCalls.length === 0) return null;

  return (
    <VStack gap={2} align="stretch" mt={2}>
      {toolCalls.map((tc, idx) => (
        <ToolCallItem key={idx} toolCall={tc} />
      ))}
    </VStack>
  );
}
