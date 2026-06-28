"use client";

import {
  Box,
  Button,
  HStack,
  IconButton,
  Separator,
  Spinner,
  Text,
  Textarea,
  VStack,
} from "@chakra-ui/react";
import { useEffect, useRef, useState, type FormEvent } from "react";
import ReactMarkdown from "react-markdown";
import rehypeSanitize from "rehype-sanitize";
import remarkGfm from "remark-gfm";
import {
  useAddMessageMutation,
  useListMessagesQuery,
} from "@/store/api";
import { CitationPanel, type CitationData } from "./CitationPanel";
import { ToolExecution, type ToolCallData } from "./ToolExecution";
import { LoadingState } from "./LoadingState";
import { EmptyState } from "./EmptyState";
import { ErrorState } from "./ErrorState";

interface ChatViewProps {
  convId: number;
  onDelete?: (convId: number) => void;
  onExport?: (convId: number) => void;
}

function MessageContent({ content }: { content: string }) {
  return (
    <Box
      className="markdown-content"
      css={{
        "& p": { mb: 2, lineHeight: "1.6" },
        "& ul, & ol": { pl: 5, mb: 2 },
        "& li": { mb: 1 },
        "& code": {
          px: 1,
          py: 0.5,
          bg: "gray.100",
          borderRadius: "sm",
          fontSize: "sm",
          fontFamily: "mono",
        },
        "& pre": {
          p: 3,
          bg: "gray.100",
          borderRadius: "md",
          overflow: "auto",
          mb: 3,
          fontSize: "sm",
        },
        "& pre code": {
          bg: "transparent",
          p: 0,
        },
        "& h1, & h2, & h3, & h4": {
          fontWeight: "bold",
          mt: 3,
          mb: 2,
        },
        "& h1": { fontSize: "xl" },
        "& h2": { fontSize: "lg" },
        "& h3": { fontSize: "md" },
        "& blockquote": {
          borderLeft: "4px solid",
          borderColor: "gray.300",
          pl: 3,
          py: 1,
          my: 2,
          color: "gray.600",
          fontStyle: "italic",
        },
        "& a": {
          color: "blue.500",
          textDecoration: "underline",
        },
        "& table": {
          borderCollapse: "collapse",
          width: "full",
          mb: 3,
        },
        "& th, & td": {
          border: "1px solid",
          borderColor: "gray.300",
          px: 3,
          py: 2,
          textAlign: "left",
        },
        "& th": {
          bg: "gray.100",
          fontWeight: "bold",
        },
        "& hr": {
          my: 4,
          borderColor: "gray.200",
        },
      }}
    >
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeSanitize]}
      >
        {content}
      </ReactMarkdown>
    </Box>
  );
}

function MessageBubble({
  role,
  content,
  citations,
  toolCalls,
}: {
  role: string;
  content: string;
  citations: CitationData[];
  toolCalls: ToolCallData[];
}) {
  const isUser = role === "user";

  return (
    <Box
      maxW="80%"
      alignSelf={isUser ? "flex-end" : "flex-start"}
      bg={isUser ? "blue.500" : "gray.100"}
      color={isUser ? "white" : "inherit"}
      p={3}
      borderRadius="lg"
      borderBottomRightRadius={isUser ? "sm" : "lg"}
      borderBottomLeftRadius={isUser ? "lg" : "sm"}
      _dark={isUser ? {} : { bg: "gray.700" }}
    >
      {role === "assistant" && (
        <Text fontSize="xs" fontWeight="bold" color="blue.600" mb={1} _dark={{ color: "blue.300" }}>
          Assistant
        </Text>
      )}
      {isUser ? (
        <Text whiteSpace="pre-wrap">{content}</Text>
      ) : content ? (
        <MessageContent content={content} />
      ) : null}

      {toolCalls.length > 0 && <ToolExecution toolCalls={toolCalls} />}
      {citations.length > 0 && <CitationPanel citations={citations} />}
    </Box>
  );
}

export function ChatView({ convId, onDelete, onExport }: ChatViewProps) {
  const {
    data: messagesData,
    isLoading,
    isError,
    refetch,
  } = useListMessagesQuery({ convId, limit: 200 });

  const [addMessage, { isLoading: isSending }] = useAddMessageMutation();
  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const messages = messagesData?.messages ?? [];

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages.length]);

  const handleSend = async (e?: FormEvent) => {
    e?.preventDefault();
    const text = input.trim();
    if (!text || isSending) return;

    setInput("");
    try {
      await addMessage({
        convId,
        data: {
          role: "user",
          content: text,
          citations: [],
          tool_calls: [],
        },
      }).unwrap();
      // Auto-refetch to get the assistant response
      setTimeout(() => refetch(), 500);
    } catch (error) {
      console.error("Failed to send message:", error);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    // Ctrl+Enter or Cmd+Enter to send
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      e.preventDefault();
      handleSend();
    }
  };

  // Auto-resize textarea
  useEffect(() => {
    const ta = textareaRef.current;
    if (ta) {
      ta.style.height = "auto";
      ta.style.height = Math.min(ta.scrollHeight, 200) + "px";
    }
  }, [input]);

  if (isLoading) {
    return <LoadingState message="Loading messages..." />;
  }

  if (isError) {
    return (
      <ErrorState
        message="Failed to load messages"
        onRetry={refetch}
      />
    );
  }

  return (
    <VStack gap={0} height="100%" align="stretch">
      {/* Conversation header */}
      <HStack justify="flex-end" px={4} py={2} gap={2}>
        {onExport && (
          <Button size="sm" variant="outline" onClick={() => onExport(convId)}>
            Export
          </Button>
        )}
        {onDelete && (
          <Button
            size="sm"
            variant="ghost"
            color="red.500"
            _hover={{ bg: "red.50" }}
            onClick={() => onDelete(convId)}
          >
            Delete
          </Button>
        )}
      </HStack>
      <Separator />

      {/* Messages area */}
      <Box flex={1} overflowY="auto" px={4} py={4}>
        {messages.length === 0 ? (
          <EmptyState
            title="Start a conversation"
            message="Send a message to begin chatting. Ask about characters, events, or anything in your novels."
          />
        ) : (
          <VStack gap={4} align="stretch">
            {messages.map((msg) => (
              <MessageBubble
                key={msg.id}
                role={msg.role}
                content={msg.content}
                citations={msg.citations as CitationData[]}
                toolCalls={msg.tool_calls as ToolCallData[]}
              />
            ))}
            <div ref={messagesEndRef} />
          </VStack>
        )}
      </Box>

      {/* Input area */}
      <Box borderTopWidth="1px" borderColor="gray.200" p={4} bg="white" _dark={{ bg: "gray.800", borderColor: "gray.700" }}>
        <form onSubmit={handleSend}>
          <HStack gap={3} align="flex-end">
            <Box flex={1} position="relative">
              <Textarea
                ref={textareaRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Type a message... (Ctrl+Enter to send)"
                rows={1}
                minH="44px"
                maxH="200px"
                resize="none"
                pr={12}
                disabled={isSending}
              />
              <IconButton
                type="submit"
                position="absolute"
                right={2}
                bottom={2}
                size="sm"
                colorPalette="blue"
                disabled={!input.trim() || isSending}
                aria-label="Send message"
              >
                {isSending ? <Spinner size="sm" /> : "➤"}
              </IconButton>
            </Box>
          </HStack>
        </form>
        <Text fontSize="xs" color="gray.400" mt={1} textAlign="right">
          Ctrl+Enter to send
        </Text>
      </Box>
    </VStack>
  );
}
