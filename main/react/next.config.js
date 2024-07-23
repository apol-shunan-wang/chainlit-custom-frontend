/** @type {import('next').NextConfig} */
const nextConfig = {
    output: 'standalone',
    reactStrictMode: true,
    swcMinify: false,
    env: {
      NEXTAUTH_SECRET: process.env.NEXTAUTH_SECRET,
      NEXTAUTH_URL: process.env.NEXTAUTH_URL,
      NEXT_PUBLIC_AUTH_END_POINT_URL: process.env.NEXT_PUBLIC_AUTH_END_POINT_URL,
    },
  };
  
  module.exports = nextConfig;
  