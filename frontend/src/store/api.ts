"use client";

import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

// ─── Domain Types ────────────────────────────────────────────────────────────

interface Novel {
  id: number;
  title: string;
  author: string;
  language: string;
  file_hash: string;
  chapter_count: number;
}

interface NovelList {
  novels: Novel[];
  total: number;
}

interface Chapter {
  id: number;
  novel_id: number;
  chapter_number: number;
  title: string;
  content?: string | null;
  raw_content?: string | null;
  source_url?: string | null;
  is_corrected?: boolean;
  corrected_at?: string | null;
  created_at: string;
}

interface ChapterListResponse {
  chapters: Chapter[];
  total: number;
}

interface ChapterUpdate {
  title?: string | null;
  content?: string | null;
  raw_content?: string | null;
}

interface BatchChapterUpdate {
  chapter_ids: number[];
  updates: ChapterUpdate[];
}

interface BatchDeleteRequest {
  chapter_ids?: number[];
  chapter_start?: number;
  chapter_end?: number;
}

interface ChapterSwapRequest {
  chapter_id_a: number;
  chapter_id_b: number;
}

interface Bookmark {
  id: number;
  novel_id: number;
  chapter_id: number;
  position: number;
  title: string;
}

interface BookmarkList {
  bookmarks: Bookmark[];
  total: number;
}

interface Progress {
  novel_id: number;
  chapter_id: number;
  position: number;
}

interface Entity {
  id: number;
  novel_id: number;
  name: string;
  entity_type: string;
  attributes: Record<string, unknown>;
  source_chapter: number | null;
  aliases: string[];
  created_at: string;
  updated_at: string;
}

interface EntityList {
  entities: Entity[];
  total: number;
}

interface WikiPage {
  id: number;
  novel_id: number;
  entity_id: number | null;
  title: string;
  content: string;
  language: string;
  version: number;
  source_chapters: number[];
  prompt_version: string;
  is_published: boolean;
  created_at: string;
  updated_at: string;
}

interface WikiPageList {
  pages: WikiPage[];
  total: number;
}

interface SearchResult {
  entities: Entity[];
  wiki_pages: WikiPage[];
  total: number;
}

// ─── Source Types ────────────────────────────────────────────────────────────

interface Source {
  id: number;
  name: string;
  url_template: string;
  css_selector: string;
  language: string;
  active: boolean;
  created_at: string;
  updated_at: string;
}

interface SourceList {
  sources: Source[];
  total: number;
}

interface SourceCreate {
  name: string;
  url_template: string;
  css_selector?: string;
  language?: string;
  active?: boolean;
}

interface SourceUpdate {
  name?: string | null;
  url_template?: string | null;
  css_selector?: string | null;
  language?: string | null;
  active?: boolean | null;
}

// ─── Analysis Types ──────────────────────────────────────────────────────────

interface AnalysisRequest {
  novel_id: number;
  chapter_start?: number;
  chapter_end?: number | null;
  provider?: string;
  model?: string;
}

interface AnalysisStatus {
  novel_id: number;
  state: string;
  chapters_processed: number;
  chapters_total: number;
  entities_count: number;
  facts_count: number;
  errors: Array<{ chapter: string; error: string }>;
}

// ─── Import Types ────────────────────────────────────────────────────────────

interface ImportRequest {
  source_id: number;
  chapter_start?: number;
  chapter_end?: number | null;
  url_template_params?: Record<string, string>;
}

interface ImportJobResponse {
  id: number;
  novel_id: number;
  source_id: number;
  chapter_start: number;
  chapter_end: number;
  status: string;
  progress: number;
  error?: string | null;
  created_at?: string;
}

interface ImportStatusResponse {
  id: number;
  status: string;
  progress: number;
  error?: string | null;
}

interface TxtImportResponse {
  novel_id: number;
  chapters_created: number;
  title: string;
}

// ─── Graph Types ─────────────────────────────────────────────────────────────

interface GraphData {
  nodes: Array<{ id: number; name: string; type: string }>;
  edges: Array<{ source: number; target: number; type: string }>;
  [key: string]: unknown;
}

interface ShortestPathResponse {
  path: Array<{ id: number; name: string }> | null;
  found: boolean;
}

// ─── Event/Timeline Types ────────────────────────────────────────────────────

interface EventCreate {
  novel_id: number;
  chapter_id?: number | null;
  event_type?: string;
  title?: string;
  description?: string;
  importance?: number;
  participants?: number[];
  attributes?: Record<string, unknown>;
}

interface EventResponse {
  id: number;
  novel_id: number;
  chapter_id: number | null;
  event_type: string;
  title: string;
  description: string;
  importance: number;
  participants: number[];
  attributes: Record<string, unknown>;
  created_at: string;
}

interface EventList {
  events: EventResponse[];
  total: number;
}

// ─── Chat Types ──────────────────────────────────────────────────────────────

interface ConversationCreate {
  novel_id: number;
  title?: string;
}

interface ConversationResponse {
  id: number;
  novel_id: number;
  title: string;
  created_at: string;
  updated_at: string;
}

interface ConversationList {
  conversations: ConversationResponse[];
  total: number;
}

interface MessageCreate {
  role?: string;
  content?: string;
  citations?: Array<Record<string, unknown>>;
  tool_calls?: Array<Record<string, unknown>>;
}

interface MessageResponse {
  id: number;
  conversation_id: number;
  role: string;
  content: string;
  citations: Array<Record<string, unknown>>;
  tool_calls: Array<Record<string, unknown>>;
  created_at: string;
}

interface MessageList {
  messages: MessageResponse[];
  total: number;
}

interface ToolDescriptor {
  name: string;
  description: string;
  [key: string]: unknown;
}

// ─── Merge / Mention Types ───────────────────────────────────────────────────

interface MergeRequest {
  source_entity_id: number;
  target_entity_id: number;
  keep_name?: string | null;
}

interface MentionCreate {
  chapter_id: number;
  position?: number;
  context?: string | null;
}

// ─── Backup Types ────────────────────────────────────────────────────────────

interface BackupValidationResult {
  valid: boolean;
  checks?: Record<string, unknown>;
  [key: string]: unknown;
}

interface BackupRestoreResult {
  status: string;
  error?: string;
}

// ─── API Definition ──────────────────────────────────────────────────────────

export const api = createApi({
  reducerPath: "api",
  baseQuery: fetchBaseQuery({ baseUrl: "/api" }),
  tagTypes: [
    "Novel",
    "Chapter",
    "Entity",
    "WikiPage",
    "Source",
    "Analysis",
    "ImportJob",
    "Conversation",
    "Message",
    "Event",
    "Graph",
    "Backup",
  ],
  endpoints: (builder) => ({
    // ── Health ─────────────────────────────────────────────────────────────
    health: builder.query<{ status: string; database: string }, void>({
      query: () => "health",
    }),

    // ── Novels ─────────────────────────────────────────────────────────────
    getNovels: builder.query<NovelList, void>({
      query: () => "novels",
      providesTags: ["Novel"],
    }),

    getNovel: builder.query<Novel, number>({
      query: (id) => `novels/${id}`,
      providesTags: (_result, _error, id) => [{ type: "Novel", id }],
    }),

    uploadNovel: builder.mutation<
      Novel,
      { file: File; title?: string; author?: string; language?: string }
    >({
      query: ({ file, title, author, language }) => {
        const formData = new FormData();
        formData.append("file", file);
        if (title) formData.append("title", title);
        if (author) formData.append("author", author);
        if (language) formData.append("language", language);
        return { url: "novels", method: "POST", body: formData };
      },
      invalidatesTags: ["Novel"],
    }),

    // ── Chapters ───────────────────────────────────────────────────────────
    getChapters: builder.query<Chapter[], number>({
      query: (novelId) => `novels/${novelId}/chapters`,
      providesTags: (_result, _error, novelId) => [
        { type: "Chapter", id: novelId },
      ],
    }),

    getChapter: builder.query<
      Chapter,
      { novelId: number; chapterId: number }
    >({
      query: ({ novelId, chapterId }) =>
        `novels/${novelId}/chapters/${chapterId}`,
      providesTags: (_result, _error, { novelId }) => [
        { type: "Chapter", id: novelId },
      ],
    }),

    updateChapter: builder.mutation<
      Chapter,
      {
        novelId: number;
        chapterId: number;
        data: ChapterUpdate;
      }
    >({
      query: ({ novelId, chapterId, data }) => ({
        url: `novels/${novelId}/chapters/${chapterId}`,
        method: "PUT",
        body: data,
      }),
      invalidatesTags: (_result, _error, { novelId }) => [
        { type: "Chapter", id: novelId },
      ],
    }),

    reimportChapter: builder.mutation<
      Chapter,
      { novelId: number; chapterId: number; resetContent?: boolean }
    >({
      query: ({ novelId, chapterId, resetContent }) => ({
        url: `novels/${novelId}/chapters/${chapterId}/reimport`,
        method: "POST",
        params: resetContent ? { reset_content: "true" } : undefined,
      }),
      invalidatesTags: (_result, _error, { novelId }) => [
        { type: "Chapter", id: novelId },
      ],
    }),

    reparseChapter: builder.mutation<
      Chapter,
      { novelId: number; chapterId: number }
    >({
      query: ({ novelId, chapterId }) => ({
        url: `novels/${novelId}/chapters/${chapterId}/reparse`,
        method: "POST",
      }),
      invalidatesTags: (_result, _error, { novelId }) => [
        { type: "Chapter", id: novelId },
      ],
    }),

    deleteChapter: builder.mutation<
      { status: string },
      { novelId: number; chapterId: number }
    >({
      query: ({ novelId, chapterId }) => ({
        url: `novels/${novelId}/chapters/${chapterId}`,
        method: "DELETE",
      }),
      invalidatesTags: (_result, _error, { novelId }) => [
        { type: "Chapter", id: novelId },
      ],
    }),

    batchDeleteChapters: builder.mutation<
      { deleted: number },
      { novelId: number; data: BatchDeleteRequest }
    >({
      query: ({ novelId, data }) => ({
        url: `novels/${novelId}/chapters/batch-delete`,
        method: "POST",
        body: data,
      }),
      invalidatesTags: (_result, _error, { novelId }) => [
        { type: "Chapter", id: novelId },
      ],
    }),

    batchCorrectChapters: builder.mutation<
      ChapterListResponse,
      { novelId: number; data: BatchChapterUpdate }
    >({
      query: ({ novelId, data }) => ({
        url: `novels/${novelId}/chapters/batch-correct`,
        method: "POST",
        body: data,
      }),
      invalidatesTags: (_result, _error, { novelId }) => [
        { type: "Chapter", id: novelId },
      ],
    }),

    swapChapters: builder.mutation<
      ChapterListResponse,
      { novelId: number; data: ChapterSwapRequest }
    >({
      query: ({ novelId, data }) => ({
        url: `novels/${novelId}/chapters/swap`,
        method: "POST",
        body: data,
      }),
      invalidatesTags: (_result, _error, { novelId }) => [
        { type: "Chapter", id: novelId },
      ],
    }),

    // ── Import ─────────────────────────────────────────────────────────────
    importFromSource: builder.mutation<
      ImportJobResponse,
      { novelId: number; data: ImportRequest }
    >({
      query: ({ novelId, data }) => ({
        url: `novels/${novelId}/import`,
        method: "POST",
        body: data,
      }),
      invalidatesTags: ["Chapter", "ImportJob"],
    }),

    getImportStatus: builder.query<
      ImportStatusResponse,
      { novelId: number; jobId: number }
    >({
      query: ({ novelId, jobId }) =>
        `novels/${novelId}/import/status/${jobId}`,
      providesTags: ["ImportJob"],
    }),

    listImportJobs: builder.query<ImportJobResponse[], number>({
      query: (novelId) => `novels/${novelId}/import/jobs`,
      providesTags: ["ImportJob"],
    }),

    importTxtFile: builder.mutation<
      TxtImportResponse,
      { file: File; title?: string; author?: string; language?: string }
    >({
      query: ({ file, title, author, language }) => {
        const formData = new FormData();
        formData.append("file", file);
        if (title) formData.append("title", title);
        if (author) formData.append("author", author);
        if (language) formData.append("language", language);
        return { url: "novels/import/txt", method: "POST", body: formData };
      },
      invalidatesTags: ["Novel", "Chapter"],
    }),

    // ── Bookmarks ──────────────────────────────────────────────────────────
    getBookmarks: builder.query<BookmarkList, number>({
      query: (novelId) => `novels/${novelId}/bookmarks`,
      providesTags: (_result, _error, novelId) => [
        { type: "Novel", id: novelId },
      ],
    }),

    createBookmark: builder.mutation<
      Bookmark,
      { novelId: number; chapterId: number; position: number; title: string }
    >({
      query: ({ novelId, ...body }) => ({
        url: `novels/${novelId}/bookmarks`,
        method: "POST",
        body,
      }),
      invalidatesTags: (_result, _error, { novelId }) => [
        { type: "Novel", id: novelId },
      ],
    }),

    deleteBookmark: builder.mutation<
      void,
      { novelId: number; bookmarkId: number }
    >({
      query: ({ novelId, bookmarkId }) => ({
        url: `novels/${novelId}/bookmarks/${bookmarkId}`,
        method: "DELETE",
      }),
      invalidatesTags: (_result, _error, { novelId }) => [
        { type: "Novel", id: novelId },
      ],
    }),

    // ── Progress ───────────────────────────────────────────────────────────
    getProgress: builder.query<Progress, number>({
      query: (novelId) => `novels/${novelId}/progress`,
      providesTags: (_result, _error, novelId) => [
        { type: "Novel", id: novelId },
      ],
    }),

    updateProgress: builder.mutation<
      Progress,
      { novelId: number; chapterId: number; position: number }
    >({
      query: ({ novelId, ...body }) => ({
        url: `novels/${novelId}/progress`,
        method: "PUT",
        body,
      }),
      invalidatesTags: (_result, _error, { novelId }) => [
        { type: "Novel", id: novelId },
      ],
    }),

    // ── Knowledge Base: Entities ──────────────────────────────────────────
    getEntities: builder.query<
      EntityList,
      {
        novelId: number;
        entityType?: string;
        limit?: number;
        offset?: number;
      }
    >({
      query: ({ novelId, entityType, limit = 50, offset = 0 }) => {
        const params = new URLSearchParams({
          novel_id: String(novelId),
          limit: String(limit),
          offset: String(offset),
        });
        if (entityType) params.append("entity_type", entityType);
        return `kb/entities?${params.toString()}`;
      },
      providesTags: ["Entity"],
    }),

    getEntity: builder.query<Entity, number>({
      query: (id) => `kb/entities/${id}`,
      providesTags: (_result, _error, id) => [{ type: "Entity", id }],
    }),

    createEntity: builder.mutation<
      Entity,
      {
        novelId: number;
        name: string;
        entityType?: string;
        attributes?: Record<string, unknown>;
        aliases?: string[];
      }
    >({
      query: ({ novelId, ...body }) => ({
        url: "kb/entities",
        method: "POST",
        body: { novel_id: novelId, ...body },
      }),
      invalidatesTags: ["Entity"],
    }),

    updateEntity: builder.mutation<
      Entity,
      {
        id: number;
        name?: string;
        entityType?: string;
        attributes?: Record<string, unknown>;
      }
    >({
      query: ({ id, ...body }) => ({
        url: `kb/entities/${id}`,
        method: "PATCH",
        body,
      }),
      invalidatesTags: (_result, _error, { id }) => [{ type: "Entity", id }],
    }),

    deleteEntity: builder.mutation<void, number>({
      query: (id) => ({
        url: `kb/entities/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["Entity"],
    }),

    resolveAlias: builder.query<
      Entity | null,
      { name: string; novelId: number }
    >({
      query: ({ name, novelId }) =>
        `kb/resolve?name=${encodeURIComponent(name)}&novel_id=${novelId}`,
    }),

    mergeEntities: builder.mutation<Entity, MergeRequest>({
      query: (data) => ({
        url: "kb/merge",
        method: "POST",
        body: data,
      }),
      invalidatesTags: ["Entity"],
    }),

    addMention: builder.mutation<
      { status: string },
      { entityId: number; data: MentionCreate }
    >({
      query: ({ entityId, data }) => ({
        url: `kb/entities/${entityId}/mentions`,
        method: "POST",
        body: data,
      }),
    }),

    // ── Search ─────────────────────────────────────────────────────────────
    search: builder.query<
      SearchResult,
      { q: string; type?: string; novelId?: number }
    >({
      query: ({ q, type = "all", novelId }) => {
        const params = new URLSearchParams({ q, type });
        if (novelId) params.append("novel_id", String(novelId));
        return `search?${params.toString()}`;
      },
    }),

    // ── Wiki ───────────────────────────────────────────────────────────────
    getWikiPages: builder.query<
      WikiPageList,
      {
        novelId: number;
        entityId?: number;
        limit?: number;
        offset?: number;
      }
    >({
      query: ({ novelId, entityId, limit = 50, offset = 0 }) => {
        const params = new URLSearchParams({
          novel_id: String(novelId),
          limit: String(limit),
          offset: String(offset),
        });
        if (entityId) params.append("entity_id", String(entityId));
        return `wiki/pages?${params.toString()}`;
      },
      providesTags: ["WikiPage"],
    }),

    getWikiPage: builder.query<WikiPage, number>({
      query: (id) => `wiki/pages/${id}`,
      providesTags: (_result, _error, id) => [{ type: "WikiPage", id }],
    }),

    generateWiki: builder.mutation<
      WikiPage,
      {
        novelId: number;
        entityId?: number;
        title?: string;
        language?: string;
      }
    >({
      query: ({ novelId, ...body }) => ({
        url: "wiki/generate",
        method: "POST",
        body: { novel_id: novelId, ...body },
      }),
      invalidatesTags: ["WikiPage"],
    }),

    deleteWikiPage: builder.mutation<void, number>({
      query: (id) => ({
        url: `wiki/pages/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["WikiPage"],
    }),

    // ── Sources ────────────────────────────────────────────────────────────
    getSources: builder.query<SourceList, void>({
      query: () => "sources",
      providesTags: ["Source"],
    }),

    createSource: builder.mutation<Source, SourceCreate>({
      query: (data) => ({
        url: "sources",
        method: "POST",
        body: data,
      }),
      invalidatesTags: ["Source"],
    }),

    updateSource: builder.mutation<Source, { id: number; data: SourceUpdate }>(
      {
        query: ({ id, data }) => ({
          url: `sources/${id}`,
          method: "PUT",
          body: data,
        }),
        invalidatesTags: (_result, _error, { id }) => [{ type: "Source", id }],
      },
    ),

    deleteSource: builder.mutation<{ status: string }, number>({
      query: (id) => ({
        url: `sources/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["Source"],
    }),

    seedDefaultSources: builder.mutation<SourceList, void>({
      query: () => ({
        url: "sources/defaults",
        method: "POST",
      }),
      invalidatesTags: ["Source"],
    }),

    // ── Analysis ───────────────────────────────────────────────────────────
    startAnalysis: builder.mutation<AnalysisStatus, AnalysisRequest>({
      query: (data) => ({
        url: "analysis/start",
        method: "POST",
        body: data,
      }),
      invalidatesTags: ["Analysis"],
    }),

    getAnalysisStatus: builder.query<AnalysisStatus, number>({
      query: (novelId) => `analysis/${novelId}/status`,
      providesTags: (_result, _error, novelId) => [
        { type: "Analysis", id: novelId },
      ],
    }),

    pauseAnalysis: builder.mutation<{ status: string }, number>({
      query: (novelId) => ({
        url: `analysis/${novelId}/pause`,
        method: "POST",
      }),
      invalidatesTags: (_result, _error, novelId) => [
        { type: "Analysis", id: novelId },
      ],
    }),

    resumeAnalysis: builder.mutation<{ status: string }, number>({
      query: (novelId) => ({
        url: `analysis/${novelId}/resume`,
        method: "POST",
      }),
      invalidatesTags: (_result, _error, novelId) => [
        { type: "Analysis", id: novelId },
      ],
    }),

    cancelAnalysis: builder.mutation<{ status: string }, number>({
      query: (novelId) => ({
        url: `analysis/${novelId}/cancel`,
        method: "POST",
      }),
      invalidatesTags: (_result, _error, novelId) => [
        { type: "Analysis", id: novelId },
      ],
    }),

    // ── Graph ──────────────────────────────────────────────────────────────
    getGraphData: builder.query<
      GraphData,
      { novelId: number; entityType?: string }
    >({
      query: ({ novelId, entityType }) => {
        const params = entityType
          ? `?entity_type=${encodeURIComponent(entityType)}`
          : "";
        return `graph/${novelId}${params}`;
      },
      providesTags: (_result, _error, { novelId }) => [
        { type: "Graph", id: novelId },
      ],
    }),

    getShortestPath: builder.query<
      ShortestPathResponse,
      { novelId: number; sourceId: number; targetId: number }
    >({
      query: ({ novelId, sourceId, targetId }) =>
        `graph/${novelId}/path?source_id=${sourceId}&target_id=${targetId}`,
    }),

    // ── Events/Timeline ────────────────────────────────────────────────────
    createEvent: builder.mutation<EventResponse, EventCreate>({
      query: (data) => ({
        url: "events",
        method: "POST",
        body: data,
      }),
      invalidatesTags: ["Event"],
    }),

    listEvents: builder.query<
      EventList,
      {
        novelId: number;
        eventType?: string;
        chapterId?: number;
        limit?: number;
        offset?: number;
      }
    >({
      query: ({ novelId, eventType, chapterId, limit = 100, offset = 0 }) => {
        const params = new URLSearchParams({
          limit: String(limit),
          offset: String(offset),
        });
        if (eventType) params.append("event_type", eventType);
        if (chapterId) params.append("chapter_id", String(chapterId));
        return `events/${novelId}?${params.toString()}`;
      },
      providesTags: (_result, _error, { novelId }) => [
        { type: "Event", id: novelId },
      ],
    }),

    // ── Chat ───────────────────────────────────────────────────────────────
    createConversation: builder.mutation<
      ConversationResponse,
      ConversationCreate
    >({
      query: (data) => ({
        url: "chat/conversations",
        method: "POST",
        body: data,
      }),
      invalidatesTags: ["Conversation"],
    }),

    listConversations: builder.query<
      ConversationList,
      { novelId: number; limit?: number; offset?: number }
    >({
      query: ({ novelId, limit = 50, offset = 0 }) =>
        `chat/conversations?novel_id=${novelId}&limit=${limit}&offset=${offset}`,
      providesTags: ["Conversation"],
    }),

    getConversation: builder.query<ConversationResponse, number>({
      query: (convId) => `chat/conversations/${convId}`,
      providesTags: (_result, _error, convId) => [
        { type: "Conversation", id: convId },
      ],
    }),

    deleteConversation: builder.mutation<{ status: string }, number>({
      query: (convId) => ({
        url: `chat/conversations/${convId}`,
        method: "DELETE",
      }),
      invalidatesTags: (_result, _error, convId) => [
        { type: "Conversation", id: convId },
      ],
    }),

    addMessage: builder.mutation<
      MessageResponse,
      { convId: number; data: MessageCreate }
    >({
      query: ({ convId, data }) => ({
        url: `chat/conversations/${convId}/messages`,
        method: "POST",
        body: data,
      }),
      invalidatesTags: (_result, _error, { convId }) => [
        { type: "Message", id: convId },
      ],
    }),

    listMessages: builder.query<
      MessageList,
      { convId: number; limit?: number; offset?: number }
    >({
      query: ({ convId, limit = 100, offset = 0 }) =>
        `chat/conversations/${convId}/messages?limit=${limit}&offset=${offset}`,
      providesTags: (_result, _error, { convId }) => [
        { type: "Message", id: convId },
      ],
    }),

    listChatTools: builder.query<ToolDescriptor[], void>({
      query: () => "chat/tools",
    }),

    executeTool: builder.mutation<
      Record<string, unknown>,
      { toolName: string; arguments: Record<string, unknown> }
    >({
      query: ({ toolName, arguments: args }) => ({
        url: `chat/tools/${toolName}`,
        method: "POST",
        body: args,
      }),
    }),

    // ── Export ─────────────────────────────────────────────────────────────
    exportNovelMarkdown: builder.query<string, number>({
      query: (novelId) => ({
        url: `export/novel/${novelId}/markdown`,
        responseHandler: (response) => response.text(),
      }),
    }),

    exportNovelJson: builder.query<Record<string, unknown>, number>({
      query: (novelId) => `export/novel/${novelId}/json`,
    }),

    exportWikiMarkdown: builder.query<string, number>({
      query: (novelId) => ({
        url: `export/novel/${novelId}/wiki/markdown`,
        responseHandler: (response) => response.text(),
      }),
    }),

    // ── Backup ─────────────────────────────────────────────────────────────
    createBackup: builder.mutation<Blob, void>({
      query: () => ({
        url: "backup/create",
        method: "POST",
        responseHandler: (response) => response.blob(),
      }),
      invalidatesTags: ["Backup"],
    }),

    validateBackup: builder.mutation<BackupValidationResult, File>({
      query: (file) => {
        const formData = new FormData();
        formData.append("backup_data", file);
        return {
          url: "backup/validate",
          method: "POST",
          body: formData,
        };
      },
    }),

    restoreBackup: builder.mutation<BackupRestoreResult, File>({
      query: (file) => {
        const formData = new FormData();
        formData.append("backup_data", file);
        return {
          url: "backup/restore",
          method: "POST",
          body: formData,
        };
      },
    }),
  }),
});

// ─── Exported Hooks ──────────────────────────────────────────────────────────

export const {
  // Health
  useHealthQuery,

  // Novels
  useGetNovelsQuery,
  useGetNovelQuery,
  useUploadNovelMutation,

  // Chapters
  useGetChaptersQuery,
  useGetChapterQuery,
  useUpdateChapterMutation,
  useReimportChapterMutation,
  useReparseChapterMutation,
  useDeleteChapterMutation,
  useBatchDeleteChaptersMutation,
  useBatchCorrectChaptersMutation,
  useSwapChaptersMutation,

  // Import
  useImportFromSourceMutation,
  useGetImportStatusQuery,
  useListImportJobsQuery,
  useImportTxtFileMutation,

  // Bookmarks
  useGetBookmarksQuery,
  useCreateBookmarkMutation,
  useDeleteBookmarkMutation,

  // Progress
  useGetProgressQuery,
  useUpdateProgressMutation,

  // Entities
  useGetEntitiesQuery,
  useGetEntityQuery,
  useCreateEntityMutation,
  useUpdateEntityMutation,
  useDeleteEntityMutation,
  useResolveAliasQuery,
  useMergeEntitiesMutation,
  useAddMentionMutation,

  // Search
  useSearchQuery,

  // Wiki
  useGetWikiPagesQuery,
  useGetWikiPageQuery,
  useGenerateWikiMutation,
  useDeleteWikiPageMutation,

  // Sources
  useGetSourcesQuery,
  useCreateSourceMutation,
  useUpdateSourceMutation,
  useDeleteSourceMutation,
  useSeedDefaultSourcesMutation,

  // Analysis
  useStartAnalysisMutation,
  useGetAnalysisStatusQuery,
  usePauseAnalysisMutation,
  useResumeAnalysisMutation,
  useCancelAnalysisMutation,

  // Graph
  useGetGraphDataQuery,
  useGetShortestPathQuery,

  // Events
  useCreateEventMutation,
  useListEventsQuery,

  // Chat
  useCreateConversationMutation,
  useListConversationsQuery,
  useGetConversationQuery,
  useDeleteConversationMutation,
  useAddMessageMutation,
  useListMessagesQuery,
  useListChatToolsQuery,
  useExecuteToolMutation,

  // Export
  useExportNovelMarkdownQuery,
  useExportNovelJsonQuery,
  useExportWikiMarkdownQuery,

  // Backup
  useCreateBackupMutation,
  useValidateBackupMutation,
  useRestoreBackupMutation,
} = api;
