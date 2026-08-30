import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "OAuth 2.0 Confidential Client",
  description: "OAuth 2.0 Authorization Request Lab",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}