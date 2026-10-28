import type { Metadata, Viewport } from "next";
import { Inter, Playfair_Display, Source_Serif_4 } from "next/font/google";
import "./globals.css";
import ClientLayout from "@/components/ClientLayout";
import Masthead from "@/components/layout/Masthead";
import SectionNav from "@/components/layout/SectionNav";
import SiteFooter from "@/components/layout/SiteFooter";
import { getEdition } from "@/lib/repository";
import type { EditionInfo } from "@/lib/types";

const playfair = Playfair_Display({
  variable: "--font-playfair",
  subsets: ["latin"],
  weight: ["600", "700", "900"],
  style: ["normal", "italic"],
  display: "swap",
});

const sourceSerif = Source_Serif_4({
  variable: "--font-source-serif",
  subsets: ["latin"],
  weight: ["400", "600", "700"],
  style: ["normal", "italic"],
  display: "swap",
});

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: {
    default: "The Daily Signal — News, context and credibility",
    template: "%s · The Daily Signal",
  },
  description:
    "A traditional newspaper for the web: live reporting from established publishers, read alongside transparent AI credibility indicators, eight-dimension content analysis and cross-source comparison.",
};

// The edition is assembled from live sources on request (cached in-process for a few minutes).
export const dynamic = "force-dynamic";

export const viewport: Viewport = {
  themeColor: "#FAF9F6",
};

// Marks the document as script-capable before paint so scroll reveals never hide content without JS.
const jsFlag = `document.documentElement.classList.add('js')`;

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  let edition: EditionInfo | null = null;
  try {
    edition = (await getEdition()).info;
  } catch {
    edition = null;
  }

  return (
    <html lang="en" suppressHydrationWarning className={`${playfair.variable} ${sourceSerif.variable} ${inter.variable}`}>
      <head>
        <script dangerouslySetInnerHTML={{ __html: jsFlag }} />
      </head>
      <body suppressHydrationWarning>
        <a href="#main" className="skip-link">Skip to the news</a>
        <ClientLayout>
          <Masthead edition={edition} />
          <SectionNav />
          <main id="main">{children}</main>
          <SiteFooter />
        </ClientLayout>
      </body>
    </html>
  );
}
