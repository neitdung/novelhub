import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

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
  content: string;
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

export const api = createApi({
  reducerPath: "api",
  baseQuery: fetchBaseQuery({ baseUrl: "/api" }),
  tagTypes: ["Novel", "Chapter", "Entity", "WikiPage"],
  endpoints: (builder) => ({
    health: builder.query<{ status: string; database: string }, void>({
      query: () => "health",
    }),
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
    getChapters: builder.query<Chapter[], number>({
      query: (novelId) => `novels/${novelId}/chapters`,
      providesTags: (_result, _error, novelId) => [
        { type: "Chapter", id: novelId },
      ],
    }),
    getChapter: builder.query<Chapter, { novelId: number; chapterId: number }>({
      query: ({ novelId, chapterId }) => `novels/${novelId}/chapters/${chapterId}`,
      providesTags: (_result, _error, { novelId }) => [
        { type: "Chapter", id: novelId },
      ],
    }),
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
    getEntities: builder.query<
      EntityList,
      { novelId: number; entityType?: string; limit?: number; offset?: number }
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
    getWikiPages: builder.query<
      WikiPageList,
      { novelId: number; entityId?: number; limit?: number; offset?: number }
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
      { novelId: number; entityId?: number; title?: string; language?: string }
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
  }),
});

export const {
  useHealthQuery,
  useGetNovelsQuery,
  useGetNovelQuery,
  useUploadNovelMutation,
  useGetChaptersQuery,
  useGetChapterQuery,
  useGetBookmarksQuery,
  useCreateBookmarkMutation,
  useDeleteBookmarkMutation,
  useGetProgressQuery,
  useUpdateProgressMutation,
  useGetEntitiesQuery,
  useGetEntityQuery,
  useCreateEntityMutation,
  useUpdateEntityMutation,
  useDeleteEntityMutation,
  useResolveAliasQuery,
  useSearchQuery,
  useGetWikiPagesQuery,
  useGetWikiPageQuery,
  useGenerateWikiMutation,
  useDeleteWikiPageMutation,
} = api;
