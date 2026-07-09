import { Metadata } from "next";
import Link from "next/link";
import { Download, FileText, Database, ArrowRight } from "lucide-react";
import { getPageData } from "@/lib/content";
import { MarkdownRenderer } from "@/components/shared/MarkdownRenderer";

export const metadata: Metadata = {
  title: "Data & Code",
  description:
    "Datasets and methodology documentation from Dr Yuqian Zhang's research projects.",
};

export default function DataCodePage() {
  const page = getPageData("data-code");
  const { datasets } = page as any;

  return (
    <div className="container px-4 py-12 md:py-20 max-w-4xl mx-auto">
      <div className="space-y-16">
        {/* Header */}
        <section className="space-y-4">
          <h1 className="text-4xl font-bold font-serif tracking-tight">
            Data &amp; Code
          </h1>
          <div className="prose dark:prose-invert max-w-none text-muted-foreground leading-relaxed">
            <MarkdownRenderer content={page.content} />
          </div>
        </section>

        {/* Datasets */}
        {datasets && datasets.length > 0 && (
          <section className="space-y-10">
            {datasets.map((ds: any, dsIdx: number) => (
              <div key={dsIdx} className="space-y-6">
                <div className="flex items-center gap-3">
                  <Database className="h-5 w-5 text-primary" />
                  <h2 className="text-2xl font-bold font-serif">
                    {ds.project}
                  </h2>
                </div>

                <p className="text-muted-foreground leading-relaxed">
                  {ds.description}
                </p>

                {ds.report_url && (
                  <Link
                    href={ds.report_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center text-sm font-medium text-primary hover:underline"
                  >
                    View the full research brief
                    <ArrowRight className="ml-1 h-4 w-4" />
                  </Link>
                )}

                {/* File list */}
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <FileText className="h-4 w-4 text-muted-foreground" />
                    <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
                      Downloadable Files
                    </h3>
                  </div>
                  <div className="space-y-2">
                    {ds.files.map((f: any, fIdx: number) => (
                      <div
                        key={fIdx}
                        className="group p-4 rounded-lg border bg-card hover:bg-muted/30 hover:border-primary/20 transition-all"
                      >
                        <div className="flex items-start justify-between gap-4">
                          <div className="space-y-1 min-w-0">
                            <p className="font-medium group-hover:text-primary transition-colors break-all">
                              {f.name}
                            </p>
                            <p className="text-sm text-muted-foreground leading-relaxed">
                              {f.description}
                            </p>
                          </div>
                          <Link
                            href={f.url}
                            download
                            className="shrink-0 inline-flex items-center gap-1.5 text-sm font-medium text-primary hover:underline"
                          >
                            <Download className="h-4 w-4" />
                            <span className="hidden sm:inline">Download</span>
                          </Link>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </section>
        )}
      </div>
    </div>
  );
}
