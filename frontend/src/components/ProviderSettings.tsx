"use client";

import { useState } from "react";
import {
  Box,
  Heading,
  VStack,
  Text,
  Input,
  HStack,
  Spinner,
} from "@chakra-ui/react";
import { useHealthQuery } from "@/store/api";

interface Settings {
  llmProvider: string;
  llmModel: string;
  apiEndpoint: string;
}

const LLM_PROVIDERS = [
  { value: "ollama", label: "Ollama (Local)" },
  { value: "openai", label: "OpenAI-compatible" },
  { value: "anthropic", label: "Anthropic" },
];

const LLM_MODELS: Record<string, string[]> = {
  ollama: ["llama3.2", "llama3.1", "mistral", "codellama", "phi3", "qwen2"],
  openai: ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
  anthropic: [
    "claude-sonnet-4-20250514",
    "claude-3-5-haiku-20241022",
    "claude-3-opus-20240229",
  ],
};

const STORAGE_KEY = "novelhub-settings";

export function ProviderSettings() {
  const [settings, setSettings] = useState<Settings>(() => {
    if (typeof window === "undefined") {
      return {
        llmProvider: "ollama",
        llmModel: "llama3.2",
        apiEndpoint: "http://localhost:11434",
      };
    }
    const saved = localStorage.getItem(STORAGE_KEY);
    return saved
      ? JSON.parse(saved)
      : {
          llmProvider: "ollama",
          llmModel: "llama3.2",
          apiEndpoint: "http://localhost:11434",
        };
  });

  const [saved, setSaved] = useState(false);
  const [testing, setTesting] = useState(false);
  const [healthResult, setHealthResult] = useState<{
    status: string;
    message: string;
  } | null>(null);

  const { data: healthData, isError: healthError } = useHealthQuery(undefined, {
    pollingInterval: 30000,
  });

  const handleSave = () => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const handleTestConnection = async () => {
    setTesting(true);
    setHealthResult(null);
    try {
      const res = await fetch("/api/health");
      if (res.ok) {
        const body = await res.json();
        setHealthResult({
          status: "connected",
          message: body.status === "ok" ? "Server is healthy" : body.status,
        });
      } else {
        setHealthResult({
          status: "disconnected",
          message: `Server returned ${res.status}`,
        });
      }
    } catch {
      setHealthResult({
        status: "disconnected",
        message: "Cannot reach server. Is the backend running?",
      });
    } finally {
      setTesting(false);
    }
  };

  const models = LLM_MODELS[settings.llmProvider] || [];

  const healthOk =
    healthData?.status === "ok" || healthData?.status === "healthy";

  return (
    <VStack gap={6} align="stretch">
      {/* Provider Configuration */}
      <Box p={4} borderWidth="1px" borderRadius="md">
        <Heading size="md" mb={4}>
          LLM Provider Configuration
        </Heading>
        <VStack gap={4} align="stretch">
          <Box>
            <Text mb={2} fontWeight="medium">
              Provider
            </Text>
            <select
              value={settings.llmProvider}
              onChange={(e) =>
                setSettings({
                  ...settings,
                  llmProvider: e.target.value,
                  llmModel: LLM_MODELS[e.target.value]?.[0] || "",
                })
              }
              style={{
                width: "100%",
                padding: "8px 12px",
                borderRadius: "6px",
                border: "1px solid #e2e8f0",
                fontSize: "14px",
              }}
            >
              {LLM_PROVIDERS.map((p) => (
                <option key={p.value} value={p.value}>
                  {p.label}
                </option>
              ))}
            </select>
          </Box>

          <Box>
            <Text mb={2} fontWeight="medium">
              Model
            </Text>
            <select
              value={settings.llmModel}
              onChange={(e) =>
                setSettings({ ...settings, llmModel: e.target.value })
              }
              style={{
                width: "100%",
                padding: "8px 12px",
                borderRadius: "6px",
                border: "1px solid #e2e8f0",
                fontSize: "14px",
              }}
            >
              {models.length === 0 ? (
                <option value="">No models available</option>
              ) : (
                models.map((m) => (
                  <option key={m} value={m}>
                    {m}
                  </option>
                ))
              )}
            </select>
          </Box>

          <Box>
            <Text mb={2} fontWeight="medium">
              API Endpoint
            </Text>
            <Input
              value={settings.apiEndpoint}
              onChange={(e) =>
                setSettings({ ...settings, apiEndpoint: e.target.value })
              }
              placeholder={
                settings.llmProvider === "ollama"
                  ? "http://localhost:11434"
                  : "https://api.openai.com/v1"
              }
            />
            <Text fontSize="sm" color="gray.500" mt={1}>
              {settings.llmProvider === "ollama"
                ? "Default Ollama endpoint is http://localhost:11434"
                : "Enter the full API base URL for your provider"}
            </Text>
          </Box>
        </VStack>
      </Box>

      {/* Health Status */}
      <Box p={4} borderWidth="1px" borderRadius="md">
        <Heading size="md" mb={4}>
          Server Health
        </Heading>
        <VStack gap={3} align="stretch">
          <HStack gap={3}>
            <Box
              w={3}
              h={3}
              borderRadius="full"
              bg={healthError ? "red.500" : healthOk ? "green.500" : "gray.400"}
              flexShrink={0}
            />
            <Text>
              {healthError
                ? "Backend disconnected"
                : healthOk
                  ? "Backend connected"
                  : "Checking..."}
            </Text>
          </HStack>
          {healthData && (
            <Text fontSize="sm" color="gray.600">
              Database: {healthData.database ?? "unknown"}
            </Text>
          )}
        </VStack>
      </Box>

      {/* Connection Test */}
      <Box p={4} borderWidth="1px" borderRadius="md">
        <Heading size="md" mb={4}>
          Connection Test
        </Heading>
        <VStack gap={3} align="stretch">
          <Box
            as="button"
            px={4}
            py={2}
            bg="blue.500"
            color="white"
            borderRadius="md"
            _hover={{ bg: "blue.600" }}
            onClick={handleTestConnection}
            aria-disabled={testing}
            opacity={testing ? 0.6 : 1}
            alignSelf="flex-start"
          >
            {testing ? "Testing..." : "Test Connection"}
          </Box>

          {testing && (
            <HStack gap={2}>
              <Spinner size="sm" />
              <Text fontSize="sm" color="gray.600">
                Testing connection...
              </Text>
            </HStack>
          )}

          {healthResult && (
            <HStack gap={2}>
              <Box
                w={2}
                h={2}
                borderRadius="full"
                bg={
                  healthResult.status === "connected"
                    ? "green.500"
                    : "red.500"
                }
              />
              <Text
                fontSize="sm"
                color={
                  healthResult.status === "connected"
                    ? "green.600"
                    : "red.600"
                }
              >
                {healthResult.message}
              </Text>
            </HStack>
          )}
        </VStack>
      </Box>

      {/* Save */}
      <HStack gap={4}>
        <Box
          as="button"
          px={6}
          py={3}
          bg="blue.500"
          color="white"
          borderRadius="md"
          fontWeight="semibold"
          _hover={{ bg: "blue.600" }}
          onClick={handleSave}
        >
          Save Settings
        </Box>
        {saved && (
          <Text color="green.600" fontSize="sm">
            Settings saved!
          </Text>
        )}
      </HStack>
    </VStack>
  );
}
