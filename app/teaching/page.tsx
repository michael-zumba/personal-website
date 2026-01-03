import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Teaching | Dr. Yuqian Zhang",
  description: "Teaching experience and courses by Dr. Yuqian Zhang.",
};

export default function TeachingPage() {
  return (
    <div className="container px-4 py-12 md:py-20 max-w-4xl mx-auto">
      <div className="space-y-12">
        <section className="space-y-6">
          <h1 className="text-4xl font-bold font-serif tracking-tight">Teaching</h1>
          <div className="prose dark:prose-invert max-w-none">
            <p className="text-lg text-muted-foreground leading-relaxed">
              I believe in fostering a learning environment that combines theoretical foundations with practical applications.
              My courses often integrate data analytics tools to prepare students for the modern accounting landscape.
            </p>
          </div>
        </section>

        <section className="space-y-6">
          <h2 className="text-2xl font-bold font-serif border-b pb-2">Current Courses</h2>
          <div className="grid gap-6">
            <div className="p-6 rounded-lg border bg-card text-card-foreground shadow-sm">
              <h3 className="text-xl font-bold mb-2">Accounting Information Systems</h3>
              <p className="text-muted-foreground mb-4">Lincoln University</p>
              <p className="text-sm">
                Focuses on the role of information systems in accounting, including database management, 
                internal controls, and emerging technologies.
              </p>
            </div>
             {/* Add more courses here */}
             <div className="p-6 rounded-lg border bg-card text-card-foreground shadow-sm">
              <h3 className="text-xl font-bold mb-2">Advanced Financial Accounting</h3>
              <p className="text-muted-foreground mb-4">Lincoln University</p>
              <p className="text-sm">
                Covers complex financial reporting issues, consolidation, and international accounting standards.
              </p>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
