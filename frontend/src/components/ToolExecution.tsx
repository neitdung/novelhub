"use client";

import {
  Box,
  Code,
  HStack,
  Text,
  VStack,
  Collapsible,
  useDisclosure,
} from "@chakra-ui/react";

interface ToolCall {
  id?: string;
  name?: string;
  arguments?: Record<string, unknown>;
  result?: unknown;
  status?: "pending" | "running" | "completed" | "error";
}

interface ToolExecutionProps {
  toolCalls: ToolCall[];
}

const statusColors: Record<string, string> = {
  pending: "gray.400",
  running: "blue.400",
  completed: "green.400",
  error: "red.400",
};

const statusLabels: Record<string, string> = {
  pending: "Pending",
  running: "Running...",
  completed: "Completed",
  error: "Error",
};

export function ToolExecution({ toolCalls }: ToolExecutionProps) {
  if (!toolCalls || toolCalls.length === 0) return null;

  return (
    <VStack align="stretch" gap={2} mt={2}>
      {toolCalls.map((call, idx) => (
        <ToolCallItem key={call.id || idx} call={call} />
      ))}
    </VStack>
  );
}

function ToolCallItem({ call }: { call: ToolCall }) {
  const { open, onToggle } = useDisclosure({ defaultOpen: false });
  const status = call.status || (call.result ? "completed" : "pending");

  return (
    <Collapsible.Root open={open} onOpenChange={onToggle}>
      <Box
        borderWidth="1px"
        borderRadius="md"
        bg="chakra-subtle-bg"
        overflow="hidden"
      >
        <Collapsible.Trigger asChild>
          <HStack
            px={3}
            py={2}
            cursor="pointer"
            justify="space-between"
            _hover={{ bg: "chakra-subtle-bg" }}
          >
            <HStack gap={2} flex={1} minH={0}>
              <Box w={2} h={2} borderRadius="full" bg={statusColors[status]} />
              <Text
                fontSize="sm"
                fontWeight="medium"
                style={{
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                  whiteSpace: "nowrap",
                }}
              >
                {call.name || "Tool Call"}
              </Text>
              <Text fontSize="xs" color="gray.500">
                {statusLabels[status]}
              </Text>
            </HStack>
            <Text fontSize="xs" color="gray.500">
              {open ? "▲" : "▼"}
            </Text>
          </HStack>
        </Collapsible.Trigger>
        <Collapsible.Content>
          <VStack align="stretch" gap={2} px={3} pb={3}>
            {call.arguments && Object.keys(call.arguments).length > 0 && (
              <Box>
                <Text fontSize="xs" fontWeight="bold" color="gray.500" mb={1}>
                  Arguments
                </Text>
                <Code
                  p={2}
                  borderRadius="md"
                  fontSize="xs"
                  whiteSpace="pre-wrap"
                  wordBreak="break-word"
                  overflowX="auto"
                  maxH={40}
                >
                  {JSON.stringify(call.arguments, null, 2)}
                </Code>
              </Box>
            )}
            {call.result !== undefined && (
              <Box>
                <Text fontSize="xs" fontWeight="bold" color="gray.500" mb={1}>
                  Result
                </Text>
                <Code
                  p={2}
                  borderRadius="md"
                  fontSize="xs"
                  whiteSpace="pre-wrap"
                  wordBreak="break-word"
                  overflowX="auto"
                  maxH={40}
                >
                  {typeof call.result === "string"
                    ? call.result
                    : JSON.stringify(call.result, null, 2)}
                </Code>
              </Box>
            )}
          </VStack>
        </Collapsible.Content>
      </Box>
    </Collapsible.Root>
  );
}
