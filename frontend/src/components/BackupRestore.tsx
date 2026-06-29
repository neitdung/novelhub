"use client";

import { useState } from "react";
import {
  Box,
  Heading,
  VStack,
  Text,
  HStack,
  Spinner,
} from "@chakra-ui/react";
import {
  useCreateBackupMutation,
  useValidateBackupMutation,
  useRestoreBackupMutation,
} from "@/store/api";

type OperationStatus = "idle" | "loading" | "success" | "error";

interface BackupStatus {
  type: "create" | "validate" | "restore";
  status: OperationStatus;
  message: string;
}

export function BackupRestore() {
  const [createBackup] = useCreateBackupMutation();
  const [validateBackup] = useValidateBackupMutation();
  const [restoreBackup] = useRestoreBackupMutation();

  const validateInputId = "validate-backup-file";
  const restoreInputId = "restore-backup-file";

  const [status, setStatus] = useState<BackupStatus>({
    type: "create",
    status: "idle",
    message: "",
  });

  const [showRestoreConfirm, setShowRestoreConfirm] = useState(false);
  const [pendingRestoreFile, setPendingRestoreFile] = useState<File | null>(
    null
  );

  const setOpStatus = (
    type: BackupStatus["type"],
    s: OperationStatus,
    message: string
  ) => {
    setStatus({ type, status: s, message });
  };

  // ── Create Backup ──────────────────────────────────────────────────────

  const handleCreateBackup = async () => {
    setOpStatus("create", "loading", "Creating backup...");
    try {
      const blob = await createBackup().unwrap();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      const date = new Date().toISOString().replace(/[:.]/g, "-");
      a.download = `novelhub-backup-${date}.zip`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      setOpStatus("create", "success", "Backup downloaded successfully.");
    } catch (err) {
      const msg =
        err instanceof Error ? err.message : "Failed to create backup.";
      setOpStatus("create", "error", msg);
    }
  };

  // ── Validate Backup ────────────────────────────────────────────────────

  const handleValidateFileSelect = async (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setOpStatus("validate", "loading", "Validating backup...");
    try {
      const result = await validateBackup(file).unwrap();
      if (result.valid) {
        setOpStatus("validate", "success", "Backup is valid and intact.");
      } else {
        const detail = result.checks
          ? JSON.stringify(result.checks)
          : "unknown";
        setOpStatus("validate", "error", `Backup invalid: ${detail}`);
      }
    } catch (err) {
      const msg =
        err instanceof Error ? err.message : "Failed to validate backup.";
      setOpStatus("validate", "error", msg);
    }
  };

  // ── Restore Backup ─────────────────────────────────────────────────────

  const handleRestoreFileSelect = (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setPendingRestoreFile(file);
    setShowRestoreConfirm(true);
  };

  const handleConfirmRestore = async () => {
    if (!pendingRestoreFile) return;
    setShowRestoreConfirm(false);
    setOpStatus("restore", "loading", "Restoring backup...");
    try {
      const result = await restoreBackup(pendingRestoreFile).unwrap();
      if (result.status === "ok" || result.status === "success") {
        setOpStatus(
          "restore",
          "success",
          "Backup restored successfully. The page will reload shortly."
        );
        setTimeout(() => {
          window.location.reload();
        }, 3000);
      } else {
        setOpStatus(
          "restore",
          "error",
          result.error || "Restore failed with unknown error."
        );
      }
    } catch (err) {
      const msg =
        err instanceof Error ? err.message : "Failed to restore backup.";
      setOpStatus("restore", "error", msg);
    }
  };

  const handleCancelRestore = () => {
    setShowRestoreConfirm(false);
    setPendingRestoreFile(null);
  };

  // ── Render helpers ────────────────────────────────────────────────────

  const StatusLine = (s: BackupStatus) => {
    if (s.status === "idle") return null;
    return (
      <HStack
        gap={2}
        p={3}
        borderRadius="md"
        bg={
          s.status === "loading"
            ? "blue.50"
            : s.status === "success"
              ? "green.50"
              : "red.50"
        }
      >
        {s.status === "loading" && <Spinner size="sm" />}
        <Box
          w={2}
          h={2}
          borderRadius="full"
          bg={
            s.status === "loading"
              ? "blue.500"
              : s.status === "success"
                ? "green.500"
                : "red.500"
          }
        />
        <Text
          fontSize="sm"
          color={
            s.status === "loading"
              ? "blue.700"
              : s.status === "success"
                ? "green.700"
                : "red.700"
          }
        >
          {s.message}
        </Text>
      </HStack>
    );
  };

  const isCreateLoading =
    status.type === "create" && status.status === "loading";
  const isValidateLoading =
    status.type === "validate" && status.status === "loading";
  const isRestoreLoading =
    status.type === "restore" && status.status === "loading";

  return (
    <VStack gap={6} align="stretch">
      {/* Create Backup */}
      <Box p={4} borderWidth="1px" borderRadius="md">
        <Heading size="md" mb={2}>
          Create Backup
        </Heading>
        <Text fontSize="sm" color="gray.600" mb={4}>
          Download a complete backup of your novel library, knowledge base, and
          settings as a ZIP archive.
        </Text>
        <Box
          as="button"
          px={4}
          py={2}
          bg="blue.500"
          color="white"
          borderRadius="md"
          _hover={{ bg: "blue.600" }}
          onClick={handleCreateBackup}
          opacity={isCreateLoading ? 0.7 : 1}
        >
          {isCreateLoading ? "Creating..." : "Create Backup"}
        </Box>
        {status.type === "create" && StatusLine(status)}
      </Box>

      {/* Validate Backup */}
      <Box p={4} borderWidth="1px" borderRadius="md">
        <Heading size="md" mb={2}>
          Validate Backup
        </Heading>
        <Text fontSize="sm" color="gray.600" mb={4}>
          Upload a backup ZIP file to verify its integrity before restoring.
        </Text>
        <input
          id={validateInputId}
          type="file"
          accept=".zip"
          style={{ display: "none" }}
          onChange={handleValidateFileSelect}
        />
        <Box
          as="button"
          px={4}
          py={2}
          bg="blue.500"
          color="white"
          borderRadius="md"
          _hover={{ bg: "blue.600" }}
          onClick={() =>
            document.getElementById(validateInputId)?.click()
          }
          opacity={isValidateLoading ? 0.7 : 1}
        >
          {isValidateLoading ? "Validating..." : "Select Backup File to Validate"}
        </Box>
        {status.type === "validate" && StatusLine(status)}
      </Box>

      {/* Restore Backup */}
      <Box
        p={4}
        borderWidth="1px"
        borderColor="red.300"
        borderRadius="md"
      >
        <Heading size="md" mb={2} color="red.700">
          Restore Backup
        </Heading>
        <Text fontSize="sm" color="gray.600" mb={2}>
          Restore your library from a backup ZIP file. This will replace all
          existing data.
        </Text>
        <Text fontSize="sm" color="red.600" fontWeight="bold" mb={4}>
          Warning: This operation is destructive and cannot be undone. All
          current data will be replaced.
        </Text>
        <input
          id={restoreInputId}
          type="file"
          accept=".zip"
          style={{ display: "none" }}
          onChange={handleRestoreFileSelect}
        />
        <Box
          as="button"
          px={4}
          py={2}
          bg="red.500"
          color="white"
          borderRadius="md"
          _hover={{ bg: "red.600" }}
          onClick={() =>
            document.getElementById(restoreInputId)?.click()
          }
          opacity={isRestoreLoading ? 0.7 : 1}
        >
          {isRestoreLoading
            ? "Restoring..."
            : "Select Backup File to Restore"}
        </Box>
        {status.type === "restore" && StatusLine(status)}
      </Box>

      {/* Restore Confirmation Dialog */}
      {showRestoreConfirm && pendingRestoreFile && (
        <Box
          p={6}
          borderWidth="2px"
          borderColor="red.400"
          borderRadius="md"
          bg="red.50"
        >
          <VStack gap={4} align="stretch">
            <Heading size="sm" color="red.700">
              Confirm Restore
            </Heading>
            <Text fontSize="sm" color="red.700">
              You are about to restore from:{" "}
              <strong>{pendingRestoreFile.name}</strong> (
              {(pendingRestoreFile.size / 1024 / 1024).toFixed(2)} MB)
            </Text>
            <Text fontSize="sm" color="red.700" fontWeight="bold">
              This will replace ALL current data with the backup contents.
              This action cannot be undone.
            </Text>
            <HStack gap={4}>
              <Box
                as="button"
                px={6}
                py={2}
                bg="red.600"
                color="white"
                borderRadius="md"
                fontWeight="semibold"
                _hover={{ bg: "red.700" }}
                onClick={handleConfirmRestore}
              >
                Yes, Restore
              </Box>
              <Box
                as="button"
                px={6}
                py={2}
                bg="gray.300"
                color="gray.800"
                borderRadius="md"
                fontWeight="semibold"
                _hover={{ bg: "gray.400" }}
                onClick={handleCancelRestore}
              >
                Cancel
              </Box>
            </HStack>
          </VStack>
        </Box>
      )}
    </VStack>
  );
}
