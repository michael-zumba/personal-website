import Link from "next/link";
import { ArrowRight, BookOpen, Code, GraduationCap } from "lucide-react";

export default function Home() {
  return (
    <div className="flex flex-col min-h-[calc(100vh-4rem)]">
      {/* Hero Section */}
      <section className="flex-1 flex flex-col justify-center items-center text-center px-4 py-20 md:py-32 space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-1000">
        <div className="space-y-4 max-w-3xl">
          <h1 className="text-4xl md:text-6xl font-bold tracking-tighter font-serif text-foreground">
            Hi, I'm <span className="text-primary">Michael</span>.
          </h1>
          <h2 className="text-xl md:text-2xl text-muted-foreground font-light">
            Dr. Yuqian Zhang
          </h2>
          <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
            I am a Senior Lecturer in Accounting at Lincoln University, New Zealand. 
            My research explores the intersection of emerging digital technologies, 
            behavioral accounting, and data analytics.
          </p>
        </div>
        
        <div className="flex flex-wrap gap-4 justify-center">
          <Link
            href="/about"
            className="inline-flex h-10 items-center justify-center rounded-md bg-primary px-8 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
          >
            More About Me
          </Link>
          <Link
            href="/research"
            className="inline-flex h-10 items-center justify-center rounded-md border border-input bg-background px-8 text-sm font-medium shadow-sm transition-colors hover:bg-accent hover:text-accent-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
          >
            My Research
          </Link>
        </div>
      </section>

      {/* Feature Grid */}
      <section className="container px-4 py-16 md:py-24 bg-muted/50">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="flex flex-col items-center text-center space-y-4 p-6 bg-background rounded-xl shadow-sm border transition-all hover:shadow-md">
            <div className="p-3 bg-primary/10 rounded-full">
              <GraduationCap className="w-6 h-6 text-primary" />
            </div>
            <h3 className="text-xl font-bold">Academic Research</h3>
            <p className="text-muted-foreground text-sm">
              Focusing on digital technologies in accounting, web scraping, and linguistic analysis.
            </p>
            <Link href="/research" className="text-sm font-medium text-primary hover:underline inline-flex items-center">
              View Publications <ArrowRight className="ml-1 w-4 h-4" />
            </Link>
          </div>

          <div className="flex flex-col items-center text-center space-y-4 p-6 bg-background rounded-xl shadow-sm border transition-all hover:shadow-md">
            <div className="p-3 bg-primary/10 rounded-full">
              <Code className="w-6 h-6 text-primary" />
            </div>
            <h3 className="text-xl font-bold">Data & Code</h3>
            <p className="text-muted-foreground text-sm">
              Extensive use of Python and R for data analysis. Sharing tools and methodologies.
            </p>
            <Link href="https://github.com" target="_blank" className="text-sm font-medium text-primary hover:underline inline-flex items-center">
              Visit GitHub <ArrowRight className="ml-1 w-4 h-4" />
            </Link>
          </div>

          <div className="flex flex-col items-center text-center space-y-4 p-6 bg-background rounded-xl shadow-sm border transition-all hover:shadow-md">
            <div className="p-3 bg-primary/10 rounded-full">
              <BookOpen className="w-6 h-6 text-primary" />
            </div>
            <h3 className="text-xl font-bold">Writings & Thoughts</h3>
            <p className="text-muted-foreground text-sm">
              Sharing insights on accounting research, academic life, and technical tutorials.
            </p>
            <Link href="/blog" className="text-sm font-medium text-primary hover:underline inline-flex items-center">
              Read Blog <ArrowRight className="ml-1 w-4 h-4" />
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
