"use client";

import { Box, Heading, HStack, Input, Stack, Text } from "@chakra-ui/react";
import Link from "next/link";
import { useRef, useState } from "react";
import { useGetNovelsQuery, useUploadNovelMutation } from "@/store/api";

export default function Bookshelf() {
  const { data, isLoading } = useGetNovelsQuery();
  const [uploadNovel] = useUploadNovelMutation();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    try {
      await uploadNovel({ file }).unwrap();
    } catch (error) {
      console.error("Upload failed:", error);
    } finally {
      setUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };

  return (
    <Box p={8}>
      <HStack justify="space-between" mb={8}>
        <Heading size="xl">Bookshelf</Heading>
        <HStack>
          <Input
            ref={fileInputRef}
            type="file"
            accept=".txt,.md"
            display="none"
            onChange={handleUpload}
          />
          <Box
            as="button"
            px={4}
            py={2}
            bg="blue.500"
            color="white"
            borderRadius="md"
            _hover={{ bg: "blue.600" }}
            onClick={() => fileInputRef.current?.click()}
          >
            {uploading ? "Uploading..." : "Upload Novel"}
          </Box>
        </HStack>
      </HStack>

      {isLoading ? (
        <Text>Loading...</Text>
      ) : data?.novels.length === 0 ? (
        <Box p={6} borderWidth="1px" borderRadius="md">
          <Text color="gray.500">
            No novels yet. Upload a .txt or .md file to get started.
          </Text>
        </Box>
      ) : (
        <Stack gap={4}>
          {data?.novels.map((novel) => (
            <Box key={novel.id} p={4} borderWidth="1px" borderRadius="md">
              <HStack justify="space-between">
                <Box>
                  <Heading size="md">{novel.title}</Heading>
                  <Text color="gray.500" mt={1}>
                    {novel.author || "Unknown author"} &bull; {novel.language}
                  </Text>
                </Box>
                <Link
                  href={`/novel/${novel.id}`}
                  style={{
                    padding: "8px 16px",
                    background: "var(--chakra-colors-blue-500)",
                    color: "white",
                    borderRadius: "8px",
                    fontWeight: "600",
                    textDecoration: "none",
                  }}
                >
                  Read
                </Link>
              </HStack>
            </Box>
          ))}
        </Stack>
      )}
    </Box>
  );
}
