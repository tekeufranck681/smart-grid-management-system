// app/layout.jsx (SERVER)

import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import Providers from "./providers";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
  display: "swap",
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
  display: "swap",
});

export const metadata = {
  title: {
    default: "SGMS - SmartGrid Management System",
    template: "%s · SGMS",
  },
  description:
    "A comprehensive platform for managing and optimizing electrical grids.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body
        className={[
          geistSans.variable,
          geistMono.variable,
          "antialiased",
          "bg-background",
          "text-foreground",
        ].join(" ")}
      >
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
