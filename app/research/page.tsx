import { Metadata } from "next";
import Link from "next/link";
import { FileText, ExternalLink } from "lucide-react";

export const metadata: Metadata = {
  title: "Research | Dr. Yuqian Zhang",
  description: "Research publications and projects by Dr. Yuqian Zhang.",
};

interface Publication {
  title: string;
  authors: string;
  journal: string;
  year: string;
  link?: string;
  status?: string; // e.g., "Published", "Under Review", "Working Paper"
}

const publications: Publication[] = [
  // Example Placeholder - User can update this list
  {
    title: "Example Publication Title: Digital Transformation in Accounting",
    authors: "Zhang, Y., Author, B.",
    journal: "Journal of Accounting Research",
    year: "2024",
    status: "Working Paper"
  },
  // Add more here
];

export default function ResearchPage() {
  return (
    <div className="container px-4 py-12 md:py-20 max-w-4xl mx-auto">
      <div className="space-y-12">
        <section className="space-y-6">
          <h1 className="text-4xl font-bold font-serif tracking-tight">Research</h1>
          <p className="text-lg text-muted-foreground">
            My research primarily focuses on... (Add detailed research philosophy here)
          </p>
        </section>

        <section className="space-y-8">
          <h2 className="text-2xl font-bold font-serif border-b pb-2">Selected Publications</h2>
          <div className="space-y-6">
            {publications.map((pub, index) => (
              <div key={index} className="group relative pl-6 border-l-2 border-muted hover:border-primary transition-colors">
                <div className="space-y-2">
                  <h3 className="text-xl font-semibold group-hover:text-primary transition-colors">
                    {pub.title}
                  </h3>
                  <p className="text-muted-foreground">{pub.authors} ({pub.year})</p>
                  <div className="flex items-center gap-2 text-sm">
                    <span className="font-medium">{pub.journal}</span>
                    {pub.status && (
                      <span className="px-2 py-0.5 rounded-full bg-secondary text-secondary-foreground text-xs">
                        {pub.status}
                      </span>
                    )}
                  </div>
                  {pub.link && (
                    <Link 
                      href={pub.link}
                      target="_blank"
                      className="inline-flex items-center text-sm text-primary hover:underline mt-2"
                    >
                      View Paper <ExternalLink className="ml-1 w-3 h-3" />
                    </Link>
                  )}
                </div>
              </div>
            ))}
            
            {publications.length === 0 && (
               <p className="text-muted-foreground italic">Publication list to be updated.</p>
            )}
          </div>
        </section>
      </div>
    </div>
  );
}
