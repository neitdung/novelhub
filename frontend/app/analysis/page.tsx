"use client";

import { Box, Heading } from "@chakra-ui/react";
import { AnalysisDashboard } from "@/components/AnalysisDashboard";

export default function AnalysisPage() {
  return (
    <Box p={8}>
      <Heading size="xl" mb={6}>
        Analysis Dashboard
      </Heading>
      <AnalysisDashboard />
    </Box>
  );
}
