import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* other config options here */
  allowedDevOrigins: ["localhost:3000", "192.168.1.9:3000"],
};

export default nextConfig;