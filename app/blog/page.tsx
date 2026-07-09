import { Metadata } from "next";
import Link from "next/link";
import { getSortedPostsData } from "@/lib/posts";
import { formatDate } from "@/lib/utils";

export const metadata: Metadata = {
  title: "Blog | Dr. Yuqian Zhang",
  description: "Writings, tutorials, and updates from Dr. Yuqian Zhang.",
};

export default function BlogPage() {
  const posts = getSortedPostsData();

  return (
    <div className="container px-4 py-12 md:py-20 max-w-4xl mx-auto">
      <div className="space-y-12">
        <section className="space-y-6">
          <h1 className="text-4xl font-bold font-serif tracking-tight">Blog</h1>
          <p className="text-lg text-muted-foreground">
            Thoughts on accounting, technology, and academic life.
          </p>
        </section>

        <section className="grid gap-8">
          {posts.map((post) => (
            <article key={post.slug} className="group relative pl-6 border-l-2 border-muted hover:border-primary transition-colors flex flex-col space-y-3">
              <Link href={`/blog/${post.slug}`} className="block">
                <h2 className="text-2xl font-bold group-hover:text-primary transition-colors">
                  {post.title}
                </h2>
              </Link>
              <div className="flex items-center gap-4 text-sm text-muted-foreground">
                <time dateTime={post.date}>{formatDate(post.date)}</time>
                {post.tags && (
                  <div className="flex gap-2">
                    {post.tags.map(tag => (
                      <span key={tag} className="bg-muted px-2 py-0.5 rounded-md text-xs">
                        #{tag}
                      </span>
                    ))}
                  </div>
                )}
              </div>
              <p className="text-muted-foreground leading-relaxed">
                {post.description}
              </p>
              <Link
                href={`/blog/${post.slug}`}
                className="text-sm font-medium text-primary hover:underline inline-flex items-center w-fit"
              >
                Read more →
              </Link>
            </article>
          ))}

          {posts.length === 0 && (
            <p className="text-muted-foreground italic">No posts found. Check back soon!</p>
          )}
        </section>
      </div>
    </div>
  );
}
