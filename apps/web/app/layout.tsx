import type { Metadata } from "next";
import "./globals.css";

/**
 * Root metadata.
 */
export const metadata: Metadata = {
  title: "AEO Report Card",
  description: "AEO diagnostic dashboard for Amazon listing visibility.",
};

/**
 * Root layout.
 */
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

