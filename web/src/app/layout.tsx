import type { Metadata } from "next";
import "../styles/globals.css";

export const metadata: Metadata = {
  title: "NCRB Crime Analysis Dashboard",
  description: "Visual analytics and forecasting for Indian crime data",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="bg-midnight text-silver min-h-screen">
        <main>{children}</main>
      </body>
    </html>
  );
}
