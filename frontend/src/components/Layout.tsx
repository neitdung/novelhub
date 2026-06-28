"use client";

import {
  Box,
  Flex,
  HStack,
  IconButton,
  Separator,
  Text,
  VStack,
} from "@chakra-ui/react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState, type ReactNode } from "react";
import { ThemeToggle } from "./ThemeToggle";

interface LayoutProps {
  children: ReactNode;
}

interface NavItem {
  label: string;
  href: string;
  emoji: string;
}

const NAV_ITEMS: NavItem[] = [
  { label: "Bookshelf", href: "/bookshelf", emoji: "\uD83D\uDCDA" },
  { label: "Entities", href: "/entities", emoji: "\uD83D\uDC64" },
  { label: "Wiki", href: "/wiki", emoji: "\uD83D\uDCD6" },
  { label: "Analysis", href: "/analysis", emoji: "\uD83D\uDCCA" },
  { label: "Chat", href: "/chat", emoji: "\uD83D\uDCAC" },
  { label: "Graph", href: "/graph", emoji: "\uD83D\uDD17" },
  { label: "Timeline", href: "/timeline", emoji: "\u23F0" },
  { label: "Settings", href: "/settings", emoji: "\u2699\uFE0F" },
  { label: "Backup", href: "/backup", emoji: "\uD83D\uDCBE" },
  { label: "Export", href: "/export", emoji: "\uD83D\uDCE4" },
];

const SIDEBAR_WIDTH = "240px";

function NavLink({ item, isActive }: { item: NavItem; isActive: boolean }) {
  return (
    <Link href={item.href} style={{ textDecoration: "none" }}>
      <Flex
        align="center"
        gap={3}
        px={4}
        py={2.5}
        borderRadius="md"
        bg={isActive ? "blue.50" : "transparent"}
        color={isActive ? "blue.600" : "inherit"}
        _hover={{
          bg: isActive ? "blue.100" : "gray.100",
        }}
        transition="background 0.15s"
      >
        <Text fontSize="lg" lineHeight={1}>
          {item.emoji}
        </Text>
        <Text fontSize="sm" fontWeight={isActive ? "600" : "400"}>
          {item.label}
        </Text>
      </Flex>
    </Link>
  );
}

function Sidebar({ pathname }: { pathname: string }) {
  return (
    <VStack
      gap={1}
      align="stretch"
      py={4}
      px={2}
      height="100%"
      overflowY="auto"
    >
      <Box px={4} mb={3}>
        <Link href="/" style={{ textDecoration: "none" }}>
          <Text fontSize="xl" fontWeight="bold" color="blue.600">
            NovelHub
          </Text>
        </Link>
      </Box>
      <Separator mb={3} />
      {NAV_ITEMS.map((item) => (
        <NavLink
          key={item.href}
          item={item}
          isActive={pathname.startsWith(item.href)}
        />
      ))}
    </VStack>
  );
}

function MobileNav({
  isOpen,
  onClose,
  pathname,
}: {
  isOpen: boolean;
  onClose: () => void;
  pathname: string;
}) {
  if (!isOpen) return null;

  return (
    <>
      {/* Overlay */}
      <Box
        position="fixed"
        inset={0}
        bg="blackAlpha.500"
        zIndex={999}
        onClick={onClose}
      />
      {/* Drawer */}
      <Box
        position="fixed"
        left={0}
        top={0}
        bottom={0}
        width="280px"
        bg="white"
        zIndex={1000}
        shadow="lg"
        overflowY="auto"
      >
        <Sidebar pathname={pathname} />
      </Box>
    </>
  );
}

export function Layout({ children }: LayoutProps) {
  const pathname = usePathname();
  const [mobileNavOpen, setMobileNavOpen] = useState(false);

  return (
    <Flex minH="100vh">
      {/* Desktop sidebar */}
      <Box
        display={{ base: "none", md: "block" }}
        w={SIDEBAR_WIDTH}
        borderRight="1px solid"
        borderColor="gray.200"
        position="fixed"
        left={0}
        top={0}
        bottom={0}
        bg="white"
        zIndex={100}
      >
        <Sidebar pathname={pathname} />
      </Box>

      {/* Mobile nav overlay + drawer */}
      <MobileNav
        isOpen={mobileNavOpen}
        onClose={() => setMobileNavOpen(false)}
        pathname={pathname}
      />

      {/* Main content area */}
      <Flex
        direction="column"
        flex={1}
        ml={{ base: 0, md: SIDEBAR_WIDTH }}
        minH="100vh"
      >
        {/* Top header bar */}
        <Box
          as="header"
          borderBottom="1px solid"
          borderColor="gray.200"
          bg="white"
          position="sticky"
          top={0}
          zIndex={50}
        >
          <HStack
            justify="space-between"
            px={4}
            py={2.5}
            maxW="1200px"
            mx="auto"
          >
            {/* Mobile hamburger */}
            <IconButton
              display={{ base: "flex", md: "none" }}
              onClick={() => setMobileNavOpen(!mobileNavOpen)}
              aria-label="Open navigation"
            >
              <Text fontSize="xl">☰</Text>
            </IconButton>

            {/* Spacer for mobile to push title */}
            <Box display={{ base: "block", md: "none" }}>
              <Link href="/" style={{ textDecoration: "none" }}>
                <Text fontSize="lg" fontWeight="bold" color="blue.600">
                  NovelHub
                </Text>
              </Link>
            </Box>

            {/* Right side: theme toggle */}
            <HStack gap={4}>
              <ThemeToggle />
            </HStack>
          </HStack>
        </Box>

        {/* Page content */}
        <Box flex={1} maxW="1200px" w="full" mx="auto">
          {children}
        </Box>
      </Flex>
    </Flex>
  );
}
