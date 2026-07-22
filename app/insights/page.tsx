import { Metadata } from "next";
import Link from "next/link";
import { Lightbulb, ExternalLink, ArrowRight, FileText } from "lucide-react";
import { getPageData } from "@/lib/content";
import { MarkdownRenderer } from "@/components/shared/MarkdownRenderer";

export const metadata: Metadata = {
  title: "Insights",
  description:
    "Research briefs, data-driven analyses, and evidence syntheses from Dr Yuqian Zhang.",
};

export default function InsightsPage() {
  const page = getPageData("insights");
  const { research_briefs } = page as any;

  return (
    <div className="container px-4 py-12 md:py-20 max-w-4xl mx-auto">
      <div className="space-y-16">
        {/* Header */}
        <section className="space-y-4">
          <h1 className="text-4xl font-bold font-serif tracking-tight">
            Insights
          </h1>
          <div className="prose dark:prose-invert max-w-none text-muted-foreground leading-relaxed">
            <MarkdownRenderer content={page.content} />
          </div>
          <Link
            href="/data-code"
            className="inline-flex items-center text-sm font-medium text-primary hover:underline mt-2"
          >
            View all datasets on the Data &amp; Code page
            <ArrowRight className="ml-1 h-4 w-4" />
          </Link>
        </section>

        {/* Research Briefs */}
        {research_briefs && research_briefs.length > 0 && (
          <section className="space-y-6">
            <div className="flex items-center gap-3">
              <Lightbulb className="h-5 w-5 text-primary" />
              <h2 className="text-2xl font-bold font-serif">
                Research Briefs
              </h2>
            </div>
            <div className="space-y-5">
              {research_briefs.map((brief: any, i: number) => (
                <div
                  key={i}
                  className="group p-5 rounded-lg border bg-card hover:bg-muted/30 hover:border-primary/20 transition-all"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="space-y-1.5 min-w-0">
                      <h3 className="font-semibold font-serif group-hover:text-primary transition-colors leading-snug">
                        <Link
                          href={brief.link}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="hover:underline"
                        >
                          {brief.title}
                        </Link>
                      </h3>
                      <p className="text-sm text-muted-foreground leading-relaxed">
                        {brief.description}
                      </p>
                      <div className="flex flex-wrap items-center gap-2 mt-1.5">
                        <span className="text-xs text-muted-foreground">
                          {brief.date}
                        </span>
                        {brief.topics && (
                          <div className="flex flex-wrap gap-1.5">
                            {brief.topics.map((t: string) => (
                              <span
                                key={t}
                                className="text-xs px-2 py-0.5 rounded-full bg-primary/10 text-primary"
                              >
                                {t}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                    <div className="shrink-0 flex items-center gap-3">
                      {brief.summary_link && (
                        <Link
                          href={brief.summary_link}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-1.5 text-sm font-medium px-3 py-1.5 rounded-md border border-muted-foreground/20 text-muted-foreground hover:text-primary hover:border-primary/30 hover:bg-primary/5 transition-colors"
                          aria-label="Read one-page summary"
                        >
                          <FileText className="h-3.5 w-3.5" />
                          Read Summary
                        </Link>
                      )}
                      <Link
                        href={brief.link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="shrink-0 text-muted-foreground hover:text-primary transition-colors"
                        aria-label="View research brief"
                      >
                        <ExternalLink className="h-4 w-4" />
                      </Link>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}
      </div>
    </div>
  );
}
