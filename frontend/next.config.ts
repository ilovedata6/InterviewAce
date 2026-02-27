import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Enable standalone output for Docker deployments
  output: "standalone",

  // Image optimization config
  images: {
    remotePatterns: [],
  },

  // Redirect /home to /dashboard for authenticated users
  async redirects() {
    return [];
  },
};

export default nextConfig;
