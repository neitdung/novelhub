import type { Metadata } from "next";
import { Providers } from "./providers";

export const metadata: Metadata = {
  title: "NovelHub",
  description:
    "Local-first novel analysis and wiki application. Upload, read, and analyze your novels with AI-powered insights.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
