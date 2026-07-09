import { Metadata } from "next";
import { getPageData } from "@/lib/content";
import { MarkdownRenderer } from "@/components/shared/MarkdownRenderer";
import Image from "next/image";
import { GraduationCap, Building2, Award } from "lucide-react";

export const metadata: Metadata = {
  title: "About",
  description:
    "About Dr Yuqian (Michael) Zhang, Senior Lecturer in Accounting at Auckland University of Technology.",
};

export default function AboutPage() {
  const page = getPageData("about");
  const {
    research_interests,
    skills,
    image,
    education,
    appointments,
    professional,
  } = page as any;

  return (
    <div className="container px-4 py-12 md:py-20 max-w-5xl mx-auto">
      <div className="space-y-16">
        {/* Profile Header */}
        <section className="flex flex-col md:flex-row gap-10 items-start">
          {image && (
            <div className="w-full md:w-1/3 shrink-0">
              <div className="relative aspect-[3/4] w-full overflow-hidden rounded-xl shadow-lg border">
                <Image
                  src={image}
                  alt="Dr Yuqian Zhang"
                  fill
                  className="object-cover"
                  priority
                />
              </div>
            </div>
          )}
          <div className="flex-1 space-y-6">
            <div>
              <p className="text-sm font-medium tracking-widest uppercase text-muted-foreground mb-2">
                Senior Lecturer (Above the Bar)
              </p>
              <h1 className="text-4xl font-bold font-serif tracking-tight">
                Dr Yuqian (Michael) Zhang
              </h1>
            </div>
            <div className="prose dark:prose-invert max-w-none text-muted-foreground leading-relaxed">
              <MarkdownRenderer content={page.content} />
            </div>
          </div>
        </section>

        {/* Academic Appointments */}
        {appointments && (
          <section className="space-y-6">
            <div className="flex items-center gap-3">
              <Building2 className="h-5 w-5 text-primary" />
              <h2 className="text-2xl font-bold font-serif">
                Academic Appointments
              </h2>
            </div>
            <div className="space-y-0">
              {appointments.map((item: any, i: number) => (
                <div
                  key={i}
                  className="flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-4 py-3 border-b last:border-b-0"
                >
                  <span className="text-sm font-medium text-primary min-w-[6rem]">
                    {item.period}
                  </span>
                  <div>
                    <p className="font-semibold">{item.role}</p>
                    <p className="text-sm text-muted-foreground">
                      {item.institution}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Education */}
        {education && (
          <section className="space-y-6">
            <div className="flex items-center gap-3">
              <GraduationCap className="h-5 w-5 text-primary" />
              <h2 className="text-2xl font-bold font-serif">Education</h2>
            </div>
            <div className="grid gap-4">
              {education.map((item: any, i: number) => (
                <div
                  key={i}
                  className="p-5 rounded-lg border bg-card hover:bg-muted/30 transition-colors"
                >
                  <h3 className="font-bold font-serif">{item.degree}</h3>
                  <p className="text-sm text-muted-foreground mt-1">
                    {item.school}
                  </p>
                  {item.detail && (
                    <p className="text-xs text-muted-foreground/70 mt-2">
                      {item.detail}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Research Interests */}
        {research_interests && (
          <section className="space-y-6">
            <h2 className="text-2xl font-bold font-serif">Research Interests</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {research_interests.map((item: string) => (
                <div
                  key={item}
                  className="flex items-center gap-3 p-4 rounded-lg border bg-card hover:bg-muted/30 hover:border-primary/20 transition-colors"
                >
                  <span className="w-2 h-2 rounded-full bg-primary shrink-0" />
                  <span className="text-sm">{item}</span>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Skills */}
        {skills && (
          <section className="space-y-6">
            <h2 className="text-2xl font-bold font-serif">Technical Skills</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div className="space-y-3">
                <h3 className="font-semibold text-sm uppercase tracking-wider text-muted-foreground">
                  Languages and Tools
                </h3>
                <div className="flex flex-wrap gap-2">
                  {skills.languages?.map((skill: string) => (
                    <span
                      key={skill}
                      className="px-3 py-1.5 bg-muted rounded-full text-sm font-medium"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
              <div className="space-y-3">
                <h3 className="font-semibold text-sm uppercase tracking-wider text-muted-foreground">
                  Methodologies
                </h3>
                <div className="flex flex-wrap gap-2">
                  {skills.methodologies?.map((skill: string) => (
                    <span
                      key={skill}
                      className="px-3 py-1.5 bg-muted rounded-full text-sm font-medium"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </section>
        )}

        {/* Professional */}
        {professional && (
          <section className="space-y-6">
            <div className="flex items-center gap-3">
              <Award className="h-5 w-5 text-primary" />
              <h2 className="text-2xl font-bold font-serif">
                Professional Affiliations
              </h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {professional.map((item: string) => (
                <div
                  key={item}
                  className="flex items-center gap-3 p-4 rounded-lg border bg-card"
                >
                  <span className="w-1.5 h-1.5 rounded-full bg-primary shrink-0" />
                  <span className="text-sm">{item}</span>
                </div>
              ))}
            </div>
          </section>
        )}
      </div>
    </div>
  );
}
