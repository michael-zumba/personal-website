import Link from "next/link";
import { GraduationCap, Mail } from "lucide-react";

export function Footer() {
  return (
    <footer className="border-t bg-muted/30">
      <div className="container mx-auto px-4 md:px-6 py-8 md:py-12">
        <div className="flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="flex flex-col items-center md:items-start gap-1.5">
            <span className="text-sm font-semibold">
              Dr Yuqian (Michael) Zhang
            </span>
            <span className="text-xs text-muted-foreground">
              Senior Lecturer in Accounting, Auckland University of Technology
            </span>
            <span className="text-xs text-muted-foreground">
              CPA Australia
            </span>
          </div>

          <div className="flex items-center gap-5">
            <Link
              href="mailto:yuqian.zhang@aut.ac.nz"
              className="text-muted-foreground hover:text-primary transition-colors"
              aria-label="Email"
            >
              <Mail className="h-5 w-5" />
            </Link>
            <Link
              href="https://scholar.google.com/citations?user=9pnGWz0AAAAJ&hl=en"
              target="_blank"
              rel="noopener noreferrer"
              className="text-muted-foreground hover:text-primary transition-colors"
              aria-label="Google Scholar"
            >
              <GraduationCap className="h-5 w-5" />
            </Link>
            <Link
              href="https://orcid.org/0000-0001-5667-4002"
              target="_blank"
              rel="noopener noreferrer"
              className="text-muted-foreground hover:text-primary transition-colors"
              aria-label="ORCID"
            >
              <svg className="h-5 w-5" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 0C5.372 0 0 5.372 0 12s5.372 12 12 12 12-5.372 12-12S18.628 0 12 0zM7.369 4.378c.525 0 .947.431.947.947s-.422.947-.947.947a.95.95 0 0 1-.947-.947c0-.525.422-.947.947-.947zm-.722 3.038h1.444v10.041H6.647V7.416zm3.562 0h3.9c3.712 0 5.344 2.653 5.344 5.025 0 2.578-2.016 5.025-5.325 5.025h-3.919V7.416zm1.444 1.303v7.444h2.297c3.272 0 4.022-2.484 4.022-3.722 0-2.016-1.284-3.722-3.938-3.722h-2.381z"/>
              </svg>
            </Link>
            <Link
              href="https://github.com/michael-zumba"
              target="_blank"
              rel="noopener noreferrer"
              className="text-muted-foreground hover:text-primary transition-colors"
              aria-label="GitHub"
            >
              <svg className="h-5 w-5" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"/>
              </svg>
            </Link>
            <Link
              href="https://ssrn.com/author=4358667"
              target="_blank"
              rel="noopener noreferrer"
              className="text-muted-foreground hover:text-primary transition-colors"
              aria-label="SSRN"
            >
              <svg className="h-5 w-5" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm0 2c5.523 0 10 4.477 10 10s-4.477 10-10 10S2 17.523 2 12 6.477 2 12 2zm1.5 3a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3zm-3 7a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3zm6 0a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3zm-3 3a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3z"/>
              </svg>
            </Link>
          </div>
        </div>

        <div className="mt-8 pt-6 border-t text-center">
          <p className="text-xs text-muted-foreground">
            &copy; {new Date().getFullYear()} Dr Yuqian Zhang. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}
