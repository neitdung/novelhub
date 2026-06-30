"use client";

import {
  Box,
  Button,
  Code,
  HStack,
  Heading,
  IconButton,
  Text,
  Textarea,
  VStack,
} from "@chakra-ui/react";
import { useCallback, useEffect, useRef, useState } from "react";
import {
  useCreateConversationMutation,
  useListConversationsQuery,
  useDeleteConversationMutation,
  useListMessagesQuery,
  useAddMessageMutation,
  useGetNovelsQuery,
} from "@/store/api";
import { ToolExecution } from "./ToolExecution";
import { CitationPanel } from "./CitationPanel";

// ─── Types ──────────────────────────────────────────────────────────────────

interface MessageDisplay {
  id: number;
  role: string;
  content: string;
  citations: Array<Record<string, unknown>>;
  tool_calls: Array<Record<string, unknown>>;
  created_at: string;
}

// ─── Simple Markdown Renderer ───────────────────────────────────────────────

function SimpleMarkdown({ content }: { content: string }) {
  const lines = content.split("\n");
  const elements: React.ReactNode[] = [];
  let inCodeBlock = false;
  let codeLines: string[] = [];

  const renderInline = (text: string) => {
    const parts: React.ReactNode[] = [];
    const regex = /(\*\*\*(.+?)\*\*\*|\*\*(.+?)\*\*|\*(.+?)\*|`(.+?)`)/g;
    let lastIndex = 0;
    let match;
    let key = 0;

    while ((match = regex.exec(text)) !== null) {
      if (match.index > lastIndex) {
        parts.push(text.slice(lastIndex, match.index));
      }
      if (match[2]) {
        parts.push(
          <Text as="span" fontWeight="bold" fontStyle="italic" key={key++}>
            {match[2]}
          </Text>
        );
      } else if (match[3]) {
        parts.push(
          <Text as="span" fontWeight="bold" key={key++}>
            {match[3]}
          </Text>
        );
      } else if (match[4]) {
        parts.push(
          <Text as="span" fontStyle="italic" key={key++}>
            {match[4]}
          </Text>
        );
      } else if (match[5]) {
        parts.push(
          <Code fontSize="sm" px={1} key={key++}>
            {match[5]}
          </Code>
        );
      }
      lastIndex = match.index + match[0].length;
    }
    if (lastIndex < text.length) {
      parts.push(text.slice(lastIndex));
    }
    return parts.length > 0 ? parts : text;
  };

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    if (line.startsWith("```")) {
      if (inCodeBlock) {
        elements.push(
          <Code
            key={`code-${i}`}
            display="block"
            p={3}
            borderRadius="md"
            fontSize="sm"
            whiteSpace="pre-wrap"
            overflowX="auto"
            mb={2}
          >
            {codeLines.join("\n")}
          </Code>
        );
        codeLines = [];
        inCodeBlock = false;
      } else {
        inCodeBlock = true;
      }
      continue;
    }

    if (inCodeBlock) {
      codeLines.push(line);
      continue;
    }

    if (line.startsWith("### ")) {
      elements.push(
        <Heading key={i} size="sm" mt={3} mb={1}>
          {renderInline(line.slice(4))}
        </Heading>
      );
    } else if (line.startsWith("## ")) {
      elements.push(
        <Heading key={i} size="md" mt={3} mb={1}>
          {renderInline(line.slice(3))}
        </Heading>
      );
    } else if (line.startsWith("# ")) {
      elements.push(
        <Heading key={i} size="lg" mt={3} mb={1}>
          {renderInline(line.slice(2))}
        </Heading>
      );
    } else if (line.match(/^[-*]\s/)) {
      elements.push(
        <HStack key={i} align="flex-start" pl={4}>
          <Text>•</Text>
          <Text>{renderInline(line.slice(2))}</Text>
        </HStack>
      );
    } else if (line.match(/^\d+\.\s/)) {
      const num = line.match(/^(\d+)\./)?.[1] || "1";
      elements.push(
        <HStack key={i} align="flex-start" pl={4}>
          <Text>{num}.</Text>
          <Text>{renderInline(line.replace(/^\d+\.\s/, ""))}</Text>
        </HStack>
      );
    } else if (line.startsWith("> ")) {
      elements.push(
        <Box
          key={i}
          pl={3}
          borderLeft="3px solid"
          borderColor="gray.300"
          color="gray.600"
          fontStyle="italic"
        >
          {renderInline(line.slice(2))}
        </Box>
      );
    } else if (line.trim() === "") {
      elements.push(<Box key={i} h={1} />);
    } else {
      elements.push(
        <Text key={i} whiteSpace="pre-wrap">
          {renderInline(line)}
        </Text>
      );
    }
  }

  return <VStack align="stretch" gap={0}>{elements}</VStack>;
}

// ─── Message Bubble ─────────────────────────────────────────────────────────

function MessageBubble({ message }: { message: MessageDisplay }) {
  const isUser = message.role === "user";

  return (
    <HStack
      align="flex-start"
      justify={isUser ? "flex-end" : "flex-start"}
      w="100%"
      px={4}
    >
      <Box
        maxW="80%"
        px={4}
        py={3}
        borderRadius="lg"
        bg={isUser ? "blue.500" : "gray.100"}
        color={isUser ? "white" : "inherit"}
      >
        <Box fontSize="sm">
          <SimpleMarkdown content={message.content} />
        </Box>

        {!isUser &&
          message.tool_calls &&
          message.tool_calls.length > 0 && (
            <ToolExecution toolCalls={message.tool_calls as never[]} />
          )}

        {!isUser &&
          message.citations &&
          message.citations.length > 0 && (
            <CitationPanel citations={message.citations as never[]} />
          )}

        <Text
          fontSize="xs"
          mt={1}
          opacity={0.6}
          textAlign={isUser ? "right" : "left"}
        >
          {new Date(message.created_at).toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </Text>
      </Box>
    </HStack>
  );
}

// ─── Main ChatView ──────────────────────────────────────────────────────────

export function ChatView() {
  const [selectedConvId, setSelectedConvId] = useState<number | null>(null);
  const [inputText, setInputText] = useState("");
  const [selectedNovelId, setSelectedNovelId] = useState<number | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const { data: novelsData } = useGetNovelsQuery();
  const { data: conversationsData, isLoading: conversationsLoading } =
    useListConversationsQuery(
      { novelId: selectedNovelId! },
      { skip: selectedNovelId === null }
    );
  const { data: messagesData, isLoading: messagesLoading } =
    useListMessagesQuery(
      { convId: selectedConvId! },
      { skip: selectedConvId === null }
    );

  const [createConversation] = useCreateConversationMutation();
  const [deleteConversation] = useDeleteConversationMutation();
  const [addMessage, { isLoading: sendingMessage }] = useAddMessageMutation();

  const novels = novelsData?.novels || [];

  useEffect(() => {
    if (novelsData && novelsData.novels.length > 0 && !selectedNovelId) {
      setSelectedNovelId(novelsData.novels[0].id);
    }
  }, [novelsData, selectedNovelId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messagesData?.messages]);

  const handleNewConversation = useCallback(async () => {
    if (!selectedNovelId) return;
    try {
      const result = await createConversation({
        novel_id: selectedNovelId,
      }).unwrap();
      setSelectedConvId(result.id);
    } catch (err) {
      console.error("Failed to create conversation:", err);
    }
  }, [selectedNovelId, createConversation]);

  const handleDeleteConversation = useCallback(
    async (convId: number) => {
      try {
        await deleteConversation(convId).unwrap();
        if (selectedConvId === convId) {
          setSelectedConvId(null);
        }
      } catch (err) {
        console.error("Failed to delete conversation:", err);
      }
    },
    [selectedConvId, deleteConversation]
  );

  const handleSendMessage = useCallback(async () => {
    if (!selectedConvId || !inputText.trim()) return;
    const content = inputText.trim();
    setInputText("");

    try {
      await addMessage({
        convId: selectedConvId,
        data: { role: "user", content },
      }).unwrap();
    } catch (err) {
      console.error("Failed to send message:", err);
    }
  }, [selectedConvId, inputText, addMessage]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleSendMessage();
      }
    },
    [handleSendMessage]
  );

  const handleExport = useCallback(() => {
    if (!messagesData?.messages) return;
    const exportData = messagesData.messages.map((m) => ({
      role: m.role,
      content: m.content,
      citations: m.citations,
      tool_calls: m.tool_calls,
      created_at: m.created_at,
    }));
    const blob = new Blob([JSON.stringify(exportData, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `conversation-${selectedConvId}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }, [messagesData, selectedConvId]);

  const conversations = conversationsData?.conversations || [];
  const messages = messagesData?.messages || [];

  return (
    <HStack h="calc(100vh - 64px)" align="stretch" gap={0}>
      {/* Left Sidebar */}
      <VStack
        w="280px"
        minW="280px"
        borderRight="1px solid"
        borderColor="chakra-border-color"
        bg="chakra-subtle-bg"
        align="stretch"
        gap={0}
      >
        {/* Novel selector */}
        <Box px={3} py={2} borderBottom="1px solid" borderColor="chakra-border-color">
          <Text fontSize="xs" fontWeight="bold" color="gray.500" mb={1}>
            NOVEL
          </Text>
          <select
            style={{
              width: "100%",
              padding: "4px 8px",
              borderRadius: "6px",
              border: "1px solid var(--chakra-colors-chakra-border-color)",
              fontSize: "14px",
              background: "var(--chakra-colors-chakra-bg)",
            }}
            value={selectedNovelId || ""}
            onChange={(e) => {
              const val = e.target.value;
              setSelectedNovelId(val ? Number(val) : null);
              setSelectedConvId(null);
            }}
          >
            <option value="">Select a novel...</option>
            {novels.map((n) => (
              <option key={n.id} value={n.id}>
                {n.title}
              </option>
            ))}
          </select>
        </Box>

        {/* New conversation button */}
        <Box px={3} py={2} borderBottom="1px solid" borderColor="chakra-border-color">
          <Button
            size="sm"
            colorScheme="blue"
            w="100%"
            onClick={handleNewConversation}
            disabled={!selectedNovelId}
          >
            + New Conversation
          </Button>
        </Box>

        {/* Conversation list */}
        <VStack align="stretch" flex={1} overflowY="auto" gap={0}>
          {conversationsLoading ? (
            <Text p={4} fontSize="sm" color="gray.500" textAlign="center">
              Loading...
            </Text>
          ) : conversations.length === 0 ? (
            <Text p={4} fontSize="sm" color="gray.500" textAlign="center">
              {selectedNovelId
                ? "No conversations yet"
                : "Select a novel first"}
            </Text>
          ) : (
            conversations.map((conv) => (
              <HStack
                key={conv.id}
                px={3}
                py={2}
                cursor="pointer"
                bg={selectedConvId === conv.id ? "blue.50" : undefined}
                _hover={{ bg: "blue.50" }}
                borderBottom="1px solid"
                borderColor="chakra-border-color"
                justify="space-between"
                onClick={() => setSelectedConvId(conv.id)}
              >
                <Box flex={1} minH={0}>
                  <Text
                    fontSize="sm"
                    fontWeight="medium"
                    style={{
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      whiteSpace: "nowrap",
                    }}
                  >
                    {conv.title || `Conversation ${conv.id}`}
                  </Text>
                  <Text fontSize="xs" color="gray.500">
                    {new Date(conv.created_at).toLocaleDateString()}
                  </Text>
                </Box>
                <IconButton
                  size="xs"
                  variant="ghost"
                  colorScheme="red"
                  aria-label="Delete conversation"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDeleteConversation(conv.id);
                  }}
                >
                  ×
                </IconButton>
              </HStack>
            ))
          )}
        </VStack>
      </VStack>

      {/* Main Area */}
      <VStack flex={1} align="stretch" gap={0}>
        {/* Header */}
        <HStack
          px={4}
          py={2}
          borderBottom="1px solid"
          borderColor="chakra-border-color"
          justify="space-between"
        >
          <Heading size="sm">
            {selectedConvId
              ? conversations.find((c) => c.id === selectedConvId)?.title ||
                `Conversation ${selectedConvId}`
              : "Select a conversation"}
          </Heading>
          {selectedConvId && (
            <IconButton
              size="sm"
              variant="ghost"
              aria-label="Export conversation"
              onClick={handleExport}
            >
              ↓
            </IconButton>
          )}
        </HStack>

        {/* Messages */}
        <VStack
          flex={1}
          overflowY="auto"
          align="stretch"
          gap={3}
          py={4}
          px={2}
        >
          {!selectedConvId ? (
            <VStack flex={1} justify="center">
              <Text color="gray.500">
                Select or create a conversation to start chatting
              </Text>
            </VStack>
          ) : messagesLoading ? (
            <VStack flex={1} justify="center">
              <Text color="gray.500">Loading messages...</Text>
            </VStack>
          ) : messages.length === 0 ? (
            <VStack flex={1} justify="center">
              <Text color="gray.500">
                No messages yet. Type below to start the conversation.
              </Text>
            </VStack>
          ) : (
            messages.map((msg) => (
              <MessageBubble key={msg.id} message={msg} />
            ))
          )}
          <div ref={messagesEndRef} />
        </VStack>

        {/* Input */}
        {selectedConvId && (
          <Box px={4} py={3} borderTop="1px solid" borderColor="chakra-border-color">
            <HStack gap={2}>
              <Textarea
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Type your message..."
                size="sm"
                resize="none"
                rows={1}
                maxH={32}
                flex={1}
              />
              <IconButton
                size="sm"
                colorScheme="blue"
                aria-label="Send message"
                onClick={handleSendMessage}
                loading={sendingMessage}
                disabled={!inputText.trim()}
              >
                →
              </IconButton>
            </HStack>
          </Box>
        )}
      </VStack>
    </HStack>
  );
}
