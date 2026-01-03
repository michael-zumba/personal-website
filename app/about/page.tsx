import { Metadata } from "next";

export const metadata: Metadata = {
  title: "About | Dr. Yuqian Zhang",
  description: "About Dr. Yuqian Zhang, Senior Lecturer in Accounting at Lincoln University.",
};

export default function AboutPage() {
  return (
    <div className="container px-4 py-12 md:py-20 max-w-4xl mx-auto">
      <div className="space-y-12">
        <section className="space-y-6">
          <h1 className="text-4xl font-bold font-serif tracking-tight">About Me</h1>
          <div className="prose dark:prose-invert max-w-none">
            <p className="text-lg text-muted-foreground leading-relaxed">
              Hello! I'm Michael (Yuqian Zhang), an accounting scholar based in Lincoln University (New Zealand).
              I serve as a Senior Lecturer in Accounting.
            </p>
            <p className="text-lg text-muted-foreground leading-relaxed mt-4">
              My research focuses on the application of emerging digital technologies in accounting. 
              I also explore the behavioural and linguistic dimensions of accounting research. 
              In my leisure time, I engage in web scraping using R and fetch my daily reading materials through Python.
            </p>
          </div>
        </section>

        <section className="space-y-6">
          <h2 className="text-2xl font-bold font-serif">Research Interests</h2>
          <ul className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[
              "Digital Technologies in Accounting",
              "Behavioral Accounting",
              "Linguistic Analysis in Finance",
              "Data Analytics & Web Scraping",
              "Machine Learning applications in Accounting"
            ].map((item) => (
              <li key={item} className="flex items-center p-4 bg-muted/50 rounded-lg border">
                <span className="w-2 h-2 bg-primary rounded-full mr-3" />
                {item}
              </li>
            ))}
          </ul>
        </section>

        <section className="space-y-6">
          <h2 className="text-2xl font-bold font-serif">Technical Skills</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="space-y-4">
              <h3 className="font-semibold text-lg">Languages & Tools</h3>
              <div className="flex flex-wrap gap-2">
                {["Python", "R", "SQL", "LaTeX", "Stata"].map((skill) => (
                  <span key={skill} className="px-3 py-1 bg-secondary text-secondary-foreground rounded-full text-sm">
                    {skill}
                  </span>
                ))}
              </div>
            </div>
            <div className="space-y-4">
              <h3 className="font-semibold text-lg">Methodologies</h3>
              <div className="flex flex-wrap gap-2">
                {["Econometrics", "Machine Learning", "Natural Language Processing", "Experimental Design"].map((skill) => (
                  <span key={skill} className="px-3 py-1 bg-secondary text-secondary-foreground rounded-full text-sm">
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
