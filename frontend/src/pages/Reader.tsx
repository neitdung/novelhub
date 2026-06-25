import { Box, Heading, HStack, Spinner, Text } from "@chakra-ui/react";
import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
  useGetChapterQuery,
  useGetChaptersQuery,
  useGetNovelQuery,
} from "../store/api";

export function Reader() {
  const { id } = useParams<{ id: string }>();
  const novelId = Number(id);

  const { data: novel, isLoading: novelLoading } = useGetNovelQuery(novelId);
  const { data: chapters, isLoading: chaptersLoading } =
    useGetChaptersQuery(novelId);
  const [currentChapterIndex, setCurrentChapterIndex] = useState(0);

  const currentChapter = chapters?.[currentChapterIndex];

  const { data: chapterContent, isLoading: contentLoading } =
    useGetChapterQuery(
      { novelId, chapterId: currentChapter?.id ?? 0 },
      { skip: !currentChapter },
    );

  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (!chapters) return;

      if (e.key === "ArrowRight" || e.key === "ArrowDown") {
        e.preventDefault();
        setCurrentChapterIndex((prev) =>
          Math.min(prev + 1, chapters.length - 1),
        );
      } else if (e.key === "ArrowLeft" || e.key === "ArrowUp") {
        e.preventDefault();
        setCurrentChapterIndex((prev) => Math.max(prev - 1, 0));
      }
    },
    [chapters],
  );

  useEffect(() => {
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [handleKeyDown]);

  if (novelLoading || chaptersLoading) {
    return (
      <Box p={8} textAlign="center">
        <Spinner size="xl" />
      </Box>
    );
  }

  if (!novel || !chapters) {
    return (
      <Box p={8}>
        <Text>Novel not found.</Text>
        <Link to="/">
          <Box
            as="button"
            mt={4}
            px={4}
            py={2}
            bg="gray.200"
            borderRadius="md"
          >
            Back to Bookshelf
          </Box>
        </Link>
      </Box>
    );
  }

  return (
    <Box p={8}>
      <HStack justify="space-between" mb={4}>
        <Link to="/">
          <Box
            as="button"
            px={4}
            py={2}
            bg="gray.200"
            borderRadius="md"
          >
            ← Bookshelf
          </Box>
        </Link>
        <Heading size="lg">{novel.title}</Heading>
        <Box w={24} />
      </HStack>

      <HStack justify="space-between" mb={4}>
        <Box
          as="button"
          px={4}
          py={2}
          bg="gray.200"
          borderRadius="md"
          onClick={() => setCurrentChapterIndex((prev) => Math.max(prev - 1, 0))}
          opacity={currentChapterIndex === 0 ? 0.5 : 1}
        >
          Previous
        </Box>

        <select
          value={currentChapterIndex}
          onChange={(e) => setCurrentChapterIndex(Number(e.target.value))}
          style={{ maxWidth: "300px", padding: "8px", borderRadius: "6px", border: "1px solid #ccc" }}
        >
          {chapters.map((chapter, index) => (
            <option key={chapter.id} value={index}>
              {chapter.title || `Chapter ${chapter.chapter_number}`}
            </option>
          ))}
        </select>

        <Box
          as="button"
          px={4}
          py={2}
          bg="gray.200"
          borderRadius="md"
          onClick={() =>
            setCurrentChapterIndex((prev) =>
              Math.min(prev + 1, chapters.length - 1),
            )
          }
          opacity={currentChapterIndex === chapters.length - 1 ? 0.5 : 1}
        >
          Next
        </Box>
      </HStack>

      <Text color="gray.500" mb={4}>
        Chapter {currentChapterIndex + 1} of {chapters.length}
      </Text>

      <Box
        maxW="800px"
        mx="auto"
        p={8}
        bg="white"
        borderRadius="md"
        shadow="md"
        minH="400px"
      >
        {contentLoading ? (
          <Spinner />
        ) : (
          <Text whiteSpace="pre-wrap" lineHeight="tall">
            {chapterContent?.content || "No content available."}
          </Text>
        )}
      </Box>

      <HStack justify="center" mt={8}>
        <Box
          as="button"
          px={4}
          py={2}
          bg="gray.200"
          borderRadius="md"
          onClick={() => setCurrentChapterIndex((prev) => Math.max(prev - 1, 0))}
          opacity={currentChapterIndex === 0 ? 0.5 : 1}
        >
          ← Previous Chapter
        </Box>
        <Box
          as="button"
          px={4}
          py={2}
          bg="gray.200"
          borderRadius="md"
          onClick={() =>
            setCurrentChapterIndex((prev) =>
              Math.min(prev + 1, chapters.length - 1),
            )
          }
          opacity={currentChapterIndex === chapters.length - 1 ? 0.5 : 1}
        >
          Next Chapter →
        </Box>
      </HStack>
    </Box>
  );
}
