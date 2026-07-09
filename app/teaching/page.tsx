import { Metadata } from "next";
import { getPageData } from "@/lib/content";
import { MarkdownRenderer } from "@/components/shared/MarkdownRenderer";
import { GraduationCap, Users } from "lucide-react";

export const metadata: Metadata = {
  title: "Teaching",
  description:
    "Teaching experience, courses, and PhD supervision by Dr Yuqian Zhang.",
};

export default function TeachingPage() {
  const page = getPageData("teaching");
  const { courses, phd_supervision, master_supervision } = page as any;

  return (
    <div className="container px-4 py-12 md:py-20 max-w-4xl mx-auto">
      <div className="space-y-16">
        {/* Header */}
        <section className="space-y-4">
          <h1 className="text-4xl font-bold font-serif tracking-tight">
            Teaching
          </h1>
          <div className="prose dark:prose-invert max-w-none text-muted-foreground leading-relaxed">
            <MarkdownRenderer content={page.content} />
          </div>
        </section>

        {/* Courses */}
        <section className="space-y-6">
          <h2 className="text-2xl font-bold font-serif">Courses</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {courses.map((course: any, i: number) => (
              <div
                key={i}
                className="p-5 rounded-lg border bg-card hover:bg-muted/30 hover:border-primary/20 transition-all"
              >
                <h3 className="font-bold font-serif mb-1">{course.title}</h3>
                <p className="text-xs text-primary font-medium mb-2">
                  {course.institution}
                </p>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  {course.description}
                </p>
              </div>
            ))}
          </div>
        </section>

        {/* PhD Supervision */}
        {phd_supervision && (
          <section className="space-y-6">
            <div className="flex items-center gap-3">
              <GraduationCap className="h-5 w-5 text-primary" />
              <h2 className="text-2xl font-bold font-serif">
                PhD Supervision
              </h2>
            </div>

            <div className="space-y-6">
              {phd_supervision.principal && (
                <div className="space-y-3">
                  <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
                    Principal Supervisor
                  </h3>
                  <div className="space-y-3">
                    {phd_supervision.principal.map((s: any, i: number) => (
                      <div
                        key={i}
                        className="p-4 rounded-lg border bg-card hover:bg-muted/30 transition-all"
                      >
                        <div className="flex items-start justify-between gap-4">
                          <div>
                            <p className="font-semibold">{s.name}</p>
                            <p className="text-sm text-muted-foreground mt-0.5">
                              {s.topic}
                            </p>
                          </div>
                          {s.period && (
                            <span className="text-xs px-2 py-0.5 rounded-full bg-primary/10 text-primary shrink-0">
                              {s.period}
                            </span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {phd_supervision.associate && (
                <div className="space-y-3">
                  <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
                    Associate Supervisor
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {phd_supervision.associate.map((s: any, i: number) => (
                      <div
                        key={i}
                        className="p-4 rounded-lg border bg-card hover:bg-muted/30 transition-all"
                      >
                        <p className="font-medium text-sm">{s.name}</p>
                        <p className="text-xs text-muted-foreground mt-1">
                          {s.topic}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </section>
        )}

        {/* Master Supervision */}
        {master_supervision && (
          <section className="space-y-6">
            <div className="flex items-center gap-3">
              <Users className="h-5 w-5 text-primary" />
              <h2 className="text-2xl font-bold font-serif">
                Master Supervision
              </h2>
            </div>
            <div className="p-5 rounded-lg border bg-card">
              {master_supervision.map((item: string, i: number) => (
                <p key={i} className="text-sm text-muted-foreground">
                  {item}
                </p>
              ))}
            </div>
          </section>
        )}
      </div>
    </div>
  );
}
