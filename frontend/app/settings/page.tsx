"use client";

import { useState } from "react";
import { Box, Heading, VStack, Text, Input } from "@chakra-ui/react";

interface Settings {
  llmProvider: string;
  llmModel: string;
  apiEndpoint: string;
}

const LLM_PROVIDERS = [
  { value: "ollama", label: "Ollama (Local)" },
  { value: "openai", label: "OpenAI" },
  { value: "anthropic", label: "Anthropic" },
];

const LLM_MODELS: Record<string, string[]> = {
  ollama: ["llama3.2", "llama3.1", "mistral", "codellama"],
  openai: ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"],
  anthropic: ["claude-sonnet-4-20250514", "claude-3-5-haiku-20241022"],
};

export default function Settings() {
  const [settings, setSettings] = useState<Settings>(() => {
    if (typeof window === "undefined") {
      return {
        llmProvider: "ollama",
        llmModel: "llama3.2",
        apiEndpoint: "http://localhost:11434",
      };
    }
    const saved = localStorage.getItem("novelhub-settings");
    return saved
      ? JSON.parse(saved)
      : {
          llmProvider: "ollama",
          llmModel: "llama3.2",
          apiEndpoint: "http://localhost:11434",
        };
  });

  const handleSave = () => {
    localStorage.setItem("novelhub-settings", JSON.stringify(settings));
  };

  const models = LLM_MODELS[settings.llmProvider] || [];

  return (
    <Box p={8}>
      <VStack gap={6} align="stretch" maxW="600px">
        <Heading size="lg">Settings</Heading>

        <Box p={4} bg="gray.50" borderRadius="md">
          <Heading size="md" mb={4}>
            LLM Configuration
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
                }}
              >
                {models.map((m) => (
                  <option key={m} value={m}>
                    {m}
                  </option>
                ))}
              </select>
            </Box>

            {settings.llmProvider !== "ollama" && (
              <Box>
                <Text mb={2} fontWeight="medium">
                  API Endpoint
                </Text>
                <Input
                  value={settings.apiEndpoint}
                  onChange={(e) =>
                    setSettings({ ...settings, apiEndpoint: e.target.value })
                  }
                  placeholder="https://api.example.com"
                />
              </Box>
            )}
          </VStack>
        </Box>

        <Box
          as="button"
          px={6}
          py={3}
          bg="blue.500"
          color="white"
          borderRadius="md"
          _hover={{ bg: "blue.600" }}
          onClick={handleSave}
          alignSelf="flex-start"
        >
          Save Settings
        </Box>
      </VStack>
    </Box>
  );
}
