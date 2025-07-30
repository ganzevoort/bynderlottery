import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // No need for trailing slash handling since nginx handles routing
  // No need for rewrites since nginx handles API proxying

  // Note: allowedDevOrigins is a Next.js 15 feature that may not be fully implemented yet
  // The cross-origin warning is informational and doesn't affect functionality

  // Enable standalone output for optimized production builds
  output: 'standalone',
};

export default nextConfig;
