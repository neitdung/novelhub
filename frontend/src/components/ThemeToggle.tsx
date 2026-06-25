import { Box, HStack } from "@chakra-ui/react";
import { useTheme } from "../context/ThemeContext";

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();

  const options: { value: "light" | "dark" | "system"; label: string }[] = [
    { value: "light", label: "Light" },
    { value: "dark", label: "Dark" },
    { value: "system", label: "System" },
  ];

  return (
    <HStack gap={1}>
      {options.map((option) => (
        <Box
          key={option.value}
          as="button"
          px={3}
          py={1}
          borderRadius="md"
          bg={theme === option.value ? "blue.500" : "transparent"}
          color={theme === option.value ? "white" : "inherit"}
          _hover={{ bg: theme === option.value ? "blue.600" : "gray.100" }}
          onClick={() => setTheme(option.value)}
          fontSize="sm"
        >
          {option.label}
        </Box>
      ))}
    </HStack>
  );
}
