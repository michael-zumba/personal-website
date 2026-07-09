import type { Metadata } from "next";
import { Inter, Merriweather } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "@/components/theme-provider";
import { Navbar } from "@/components/shared/Navbar";
import { Footer } from "@/components/shared/Footer";
import { cn } from "@/lib/utils";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });
const merriweather = Merriweather({
  weight: ["300", "400", "700", "900"],
  subsets: ["latin"],
  variable: "--font-merriweather",
});

export const metadata: Metadata = {
  title: {
    default: "Dr Yuqian (Michael) Zhang | Senior Lecturer in Accounting | AUT",
    template: "%s | Dr Yuqian Zhang",
  },
  description:
    "Dr Yuqian (Michael) Zhang is a Senior Lecturer in Accounting at Auckland University of Technology. Research interests include digital technologies in accounting, textual analysis, ESG disclosure, and cross-cultural financial reporting.",
  keywords: [
    "accounting research",
    "digital transformation",
    "ESG disclosure",
    "textual analysis",
    "AUT",
    "New Zealand",
    "Yuqian Zhang",
  ],
  authors: [{ name: "Dr Yuqian Zhang" }],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={cn(
          "min-h-screen bg-background font-sans antialiased",
          inter.variable,
          merriweather.variable
        )}
      >
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <div className="flex flex-col min-h-screen">
            <Navbar />
            <main className="flex-1">{children}</main>
            <Footer />
          </div>
        </ThemeProvider>
      </body>
    </html>
  );
}
