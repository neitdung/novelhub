import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Use default server mode (not static export) to support dynamic routes
  // Proxy /api requests to the FastAPI backend
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
