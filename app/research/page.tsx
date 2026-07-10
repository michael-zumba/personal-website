import { Metadata } from "next";
import Link from "next/link";
import { ExternalLink, Trophy, FileText, PencilLine, Mic, BookOpen } from "lucide-react";
import { getPageData } from "@/lib/content";
import { MarkdownRenderer } from "@/components/shared/MarkdownRenderer";

export const metadata: Metadata = {
  title: "Research",
  description:
    "Research publications, working papers, grants, and editorial roles of Dr Yuqian Zhang.",
};

export default function ResearchPage() {
  const page = getPageData("research");
  const {
    publications,
    working_papers,
    grants,
    editorial,
    conferences,
    research_briefs,
  } = page as any;

  return (
    <div className="container px-4 py-12 md:py-20 max-w-4xl mx-auto">
      <div className="space-y-16">
        {/* Header */}
        <section className="space-y-4">
          <h1 className="text-4xl font-bold font-serif tracking-tight">
            Research
          </h1>
          <div className="prose dark:prose-invert max-w-none text-muted-foreground leading-relaxed">
            <MarkdownRenderer content={page.content} />
          </div>
        </section>

        {/* Journal Articles */}
        <section className="space-y-6">
          <div className="flex items-center gap-3">
            <FileText className="h-5 w-5 text-primary" />
            <h2 className="text-2xl font-bold font-serif">
              Journal Articles
            </h2>
          </div>
          <div className="space-y-5">
            {publications.map((pub: any, i: number) => (
              <div
                key={i}
                className="group p-5 rounded-lg border bg-card hover:bg-muted/30 hover:border-primary/20 transition-all"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="space-y-1 min-w-0">
                    <h3 className="font-semibold font-serif group-hover:text-primary transition-colors leading-snug">
                      {pub.doi ? (
                        <Link
                          href={pub.doi}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="hover:underline"
                        >
                          {pub.title}
                        </Link>
                      ) : (
                        pub.title
                      )}
                    </h3>
                    <p className="text-sm text-muted-foreground">
                      {pub.authors}
                    </p>
                    <div className="flex flex-wrap items-center gap-2 mt-1.5">
                      <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-primary/10 text-primary">
                        {pub.journal}
                      </span>
                      <span className="text-xs text-muted-foreground">
                        {pub.year}
                      </span>
                      {pub.status && (
                        <span className="text-xs px-2 py-0.5 rounded-full bg-muted text-muted-foreground">
                          {pub.status}
                        </span>
                      )}
                    </div>
                  </div>
                  {pub.doi && (
                    <Link
                      href={pub.doi}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="shrink-0 text-muted-foreground hover:text-primary transition-colors"
                      aria-label="View paper"
                    >
                      <ExternalLink className="h-4 w-4" />
                    </Link>
                  )}
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Working Papers */}
        {working_papers && working_papers.length > 0 && (
          <section className="space-y-6">
            <div className="flex items-center gap-3">
              <PencilLine className="h-5 w-5 text-primary" />
              <h2 className="text-2xl font-bold font-serif">
                Working Papers
              </h2>
            </div>
            <div className="space-y-3">
              {working_papers.map((wp: any, i: number) => (
                <div
                  key={i}
                  className="group p-4 rounded-lg border bg-card hover:bg-muted/30 transition-all"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="space-y-1 min-w-0">
                      <h3 className="font-medium group-hover:text-primary transition-colors">
                        {wp.link ? (
                          <Link
                            href={wp.link}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="hover:underline"
                          >
                            {wp.title}
                          </Link>
                        ) : (
                          wp.title
                        )}
                      </h3>
                      {wp.authors && (
                        <p className="text-xs text-muted-foreground">
                          {wp.authors}
                        </p>
                      )}
                      {wp.status && (
                        <span className="inline-block mt-1 text-xs px-2 py-0.5 rounded-full bg-primary/10 text-primary">
                          {wp.status}
                        </span>
                      )}
                    </div>
                    {wp.link && (
                      <Link
                        href={wp.link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="shrink-0 text-muted-foreground hover:text-primary transition-colors"
                        aria-label="View SSRN paper"
                      >
                        <ExternalLink className="h-4 w-4" />
                      </Link>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Research Briefs */}
        {research_briefs && research_briefs.length > 0 && (
          <section className="space-y-6">
            <div className="flex items-center gap-3">
              <BookOpen className="h-5 w-5 text-primary" />
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
                      <div className="flex flex-wrap items-center gap-2 mt-1">
                        <span className="text-xs text-muted-foreground">
                          {brief.date}
                        </span>
                        {brief.type && (
                          <span className="text-xs px-2 py-0.5 rounded-full bg-primary/10 text-primary">
                            {brief.type}
                          </span>
                        )}
                      </div>
                    </div>
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
              ))}
            </div>
          </section>
        )}

        {/* Grants & Awards */}
        {grants && grants.length > 0 && (
          <section className="space-y-6">
            <div className="flex items-center gap-3">
              <Trophy className="h-5 w-5 text-primary" />
              <h2 className="text-2xl font-bold font-serif">
                Grants and Awards
              </h2>
            </div>
            <div className="space-y-0">
              {grants.map((g: any, i: number) => (
                <div
                  key={i}
                  className="flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-4 py-2.5 border-b last:border-b-0"
                >
                  <span className="text-xs font-medium text-primary min-w-[5rem]">
                    {g.year}
                  </span>
                  <div>
                    <p className="font-medium text-sm">{g.name}</p>
                    {g.detail && (
                      <p className="text-xs text-muted-foreground">
                        {g.detail}
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Conference Presentations */}
        {conferences && conferences.length > 0 && (
          <section className="space-y-6">
            <div className="flex items-center gap-3">
              <Mic className="h-5 w-5 text-primary" />
              <h2 className="text-2xl font-bold font-serif">
                Conference Presentations
              </h2>
            </div>
            <div className="space-y-3">
              {conferences.map((c: any, i: number) => (
                <div
                  key={i}
                  className="group p-4 rounded-lg border bg-card hover:bg-muted/30 transition-all"
                >
                  <h3 className="font-medium group-hover:text-primary transition-colors">
                    {c.title}
                  </h3>
                  <div className="flex flex-wrap items-center gap-2 mt-1.5">
                    <span className="text-xs text-muted-foreground">
                      {c.event}
                    </span>
                    <span className="text-xs px-2 py-0.5 rounded-full bg-muted text-muted-foreground">
                      {c.date}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Editorial Roles */}
        {editorial && editorial.length > 0 && (
          <section className="space-y-6">
            <h2 className="text-2xl font-bold font-serif">
              Editorial Service
            </h2>
            <div className="space-y-5">
              {editorial.map((e: any, i: number) => (
                <div
                  key={i}
                  className="p-5 rounded-lg border bg-card"
                >
                  <h3 className="font-semibold font-serif mb-2">
                    {e.role}
                  </h3>
                  {e.journal && (
                    <div className="space-y-1">
                      <p className="text-sm">
                        <span className="font-medium">{e.journal}</span>
                        {e.detail && (
                          <span className="text-xs text-muted-foreground ml-2">
                            ({e.detail})
                          </span>
                        )}
                      </p>
                    </div>
                  )}
                  {e.journals && (
                    <div className="flex flex-wrap gap-1.5 mt-2">
                      {e.journals.map((j: string) => (
                        <span
                          key={j}
                          className="text-xs px-2 py-1 rounded-md bg-muted text-muted-foreground"
                        >
                          {j}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </section>
        )}
      </div>
    </div>
  );
}
