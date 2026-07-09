import Link from "next/link";
import {
  ArrowRight,
  BookOpen,
  FileText,
  GraduationCap,
  Microscope,
  Users,
} from "lucide-react";

export default function Home() {
  return (
    <div className="flex flex-col">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-primary/5 to-transparent" />
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-primary/8 via-transparent to-transparent" />
        <div className="container mx-auto px-4 md:px-6 relative">
          <div className="flex flex-col items-center text-center py-24 md:py-36 lg:py-44 space-y-8 max-w-4xl mx-auto">
            <div className="space-y-4 animate-in fade-in slide-in-from-bottom-6 duration-700">
              <p className="text-sm md:text-base font-medium tracking-widest uppercase text-muted-foreground">
                Senior Lecturer in Accounting
              </p>
              <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold font-serif tracking-tight text-balance leading-tight">
                Dr Yuqian
                <span className="text-primary"> (Michael) </span>
                Zhang
              </h1>
              <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed pt-2">
                Accounting scholar at Auckland University of Technology.
                Exploring the intersection of digital technologies, textual
                analysis, and financial reporting.
              </p>
            </div>

            <div className="flex flex-wrap gap-4 justify-center animate-in fade-in slide-in-from-bottom-6 duration-700 delay-150">
              <Link
                href="/about"
                className="inline-flex h-11 items-center justify-center rounded-lg bg-primary px-8 text-sm font-medium text-primary-foreground shadow-sm transition-all hover:bg-primary/90 hover:shadow-md focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
              >
                About Me
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
              <Link
                href="/research"
                className="inline-flex h-11 items-center justify-center rounded-lg border border-input bg-background px-8 text-sm font-medium shadow-sm transition-all hover:bg-muted hover:shadow-md focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
              >
                My Research
              </Link>
              <Link
                href="/blog"
                className="inline-flex h-11 items-center justify-center rounded-lg border border-input bg-background px-8 text-sm font-medium shadow-sm transition-all hover:bg-muted hover:shadow-md focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
              >
                Blog
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Bar */}
      <section className="border-y bg-muted/30">
        <div className="container mx-auto px-4 md:px-6">
          <div className="grid grid-cols-2 md:grid-cols-4 divide-x divide-border py-8">
            {[
              { value: "15+", label: "Journal Articles" },
              { value: "7", label: "PhD Candidates" },
              { value: "8+", label: "Years in Academia" },
              { value: "A*", label: "ABDC Journal Rank" },
            ].map((stat) => (
              <div
                key={stat.label}
                className="flex flex-col items-center justify-center px-4 py-2"
              >
                <span className="text-2xl md:text-3xl font-bold font-serif text-primary">
                  {stat.value}
                </span>
                <span className="text-xs md:text-sm text-muted-foreground mt-1 text-center">
                  {stat.label}
                </span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Research Areas */}
      <section className="container mx-auto px-4 md:px-6 py-20 md:py-28">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-16 space-y-3">
            <h2 className="text-3xl md:text-4xl font-bold font-serif tracking-tight">
              Research Areas
            </h2>
            <p className="text-muted-foreground max-w-xl mx-auto">
              My work sits at the intersection of accounting, technology, and
              human behaviour.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              {
                icon: <FileText className="h-6 w-6" />,
                title: "Textual Analysis",
                desc: "Applying NLP and machine learning to analyse corporate disclosures, annual reports, and earnings calls.",
              },
              {
                icon: <Microscope className="h-6 w-6" />,
                title: "Digital Transformation",
                desc: "Investigating how AI, blockchain, and metaverse technologies reshape accounting practice.",
              },
              {
                icon: <BookOpen className="h-6 w-6" />,
                title: "ESG Disclosure",
                desc: "Examining corporate sustainability reporting, green bonds, and environmental disclosure quality.",
              },
              {
                icon: <Users className="h-6 w-6" />,
                title: "Behavioural Accounting",
                desc: "Studying how psychological and linguistic factors influence accounting judgments and decisions.",
              },
              {
                icon: <GraduationCap className="h-6 w-6" />,
                title: "Cross-Cultural Reporting",
                desc: "Exploring international differences in financial reporting under IFRS across jurisdictions.",
              },
              {
                icon: <FileText className="h-6 w-6" />,
                title: "Cybersecurity Risk",
                desc: "Analysing cybersecurity risk disclosure and its implications for capital markets.",
              },
            ].map((area) => (
              <div
                key={area.title}
                className="group p-6 rounded-xl border bg-card hover:bg-muted/30 hover:border-primary/20 transition-all duration-300"
              >
                <div className="mb-4 w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center text-primary group-hover:bg-primary group-hover:text-primary-foreground transition-colors">
                  {area.icon}
                </div>
                <h3 className="text-lg font-bold mb-2 font-serif">
                  {area.title}
                </h3>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  {area.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Latest Publications Preview */}
      <section className="bg-muted/30 border-y">
        <div className="container mx-auto px-4 md:px-6 py-20 md:py-28">
          <div className="max-w-5xl mx-auto">
            <div className="flex flex-col md:flex-row md:items-end md:justify-between mb-12 gap-4">
              <div className="space-y-2">
                <h2 className="text-3xl md:text-4xl font-bold font-serif tracking-tight">
                  Selected Publications
                </h2>
                <p className="text-muted-foreground">
                  Recent work published in leading accounting journals.
                </p>
              </div>
              <Link
                href="/research"
                className="inline-flex items-center text-sm font-medium text-primary hover:underline shrink-0"
              >
                View all publications
                <ArrowRight className="ml-1 h-4 w-4" />
              </Link>
            </div>

            <div className="grid gap-4">
              {[
                {
                  title:
                    "Corporate culture as a catalyst for ESG disclosure: empirical evidence from the United States",
                  journal: "Journal of Accounting & Organizational Change",
                  year: "2026",
                  authors: "Nguyen, U., Gan, C., & Zhang, Y.",
                },
                {
                  title:
                    "Accounting for Purpose: Traditional Chinese Philosophies and Management Control Systems in Chinese Companies",
                  journal: "Meditari Accountancy Research",
                  year: "2025",
                  authors: "Yang, J., Akroyd, C., & Zhang, Y.",
                },
                {
                  title:
                    "The Impact of Digital Transformation on Firm's Financial Performance: Evidence from China",
                  journal: "Industrial Management & Data Systems",
                  year: "2024",
                  authors: "Chen, Y., & Zhang, Y.",
                },
                {
                  title:
                    "Probability estimation in Accounting: Subjective Numeracy Matters",
                  journal: "Journal of Applied Accounting Research",
                  year: "2024",
                  authors: "Zhang, Y., Seufert, J., & Dellaportas, S.",
                },
              ].map((pub) => (
                <div
                  key={pub.title}
                  className="group p-5 rounded-lg border bg-card hover:bg-muted/50 hover:border-primary/20 transition-all"
                >
                  <h3 className="font-semibold font-serif mb-1 group-hover:text-primary transition-colors leading-snug">
                    {pub.title}
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    {pub.authors}
                  </p>
                  <div className="flex items-center gap-2 mt-2">
                    <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-primary/10 text-primary">
                      {pub.journal}
                    </span>
                    <span className="text-xs text-muted-foreground">
                      {pub.year}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="container mx-auto px-4 md:px-6 py-20 md:py-28">
        <div className="max-w-2xl mx-auto text-center space-y-6">
          <h2 className="text-2xl md:text-3xl font-bold font-serif tracking-tight">
            Get in Touch
          </h2>
          <p className="text-muted-foreground leading-relaxed">
            I am always open to research collaborations, PhD supervision
            inquiries, and discussions about accounting and technology. Feel
            free to reach out.
          </p>
          <Link
            href="mailto:yuqian.zhang@aut.ac.nz"
            className="inline-flex h-11 items-center justify-center rounded-lg bg-primary px-8 text-sm font-medium text-primary-foreground shadow-sm transition-all hover:bg-primary/90 hover:shadow-md"
          >
            Email Me
          </Link>
        </div>
      </section>
    </div>
  );
}
