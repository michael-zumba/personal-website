import { Metadata } from "next";
import { getPostData, getSortedPostsData } from "@/lib/posts";
import { formatDate } from "@/lib/utils";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeRaw from "rehype-raw";
import { PrismLight as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/cjs/styles/prism';

// Since we are using static export, we need generateStaticParams
export function generateStaticParams() {
  const posts = getSortedPostsData();
  return posts.map((post) => ({
    slug: post.slug,
  }));
}

export async function generateMetadata({ params }: { params: { slug: string } }): Promise<Metadata> {
  const post = getPostData(params.slug);
  return {
    title: `${post.title} | Dr. Yuqian Zhang`,
    description: post.description,
  };
}

export default function PostPage({ params }: { params: { slug: string } }) {
  const post = getPostData(params.slug);

  return (
    <div className="container px-4 py-12 md:py-20 max-w-3xl mx-auto">
      <article className="space-y-8">
        <header className="space-y-4 text-center border-b pb-8">
          <time dateTime={post.date} className="text-sm text-muted-foreground">
            {formatDate(post.date)}
          </time>
          <h1 className="text-3xl md:text-5xl font-bold font-serif tracking-tight text-balance">
            {post.title}
          </h1>
          {post.tags && (
             <div className="flex gap-2 justify-center">
                {post.tags.map(tag => (
                  <span key={tag} className="bg-muted px-2 py-0.5 rounded-md text-xs text-muted-foreground">
                    #{tag}
                  </span>
                ))}
              </div>
          )}
        </header>

        <div className="prose dark:prose-invert max-w-none prose-headings:font-serif prose-a:text-primary hover:prose-a:text-primary/80">
          <ReactMarkdown 
            remarkPlugins={[remarkGfm]}
            components={{
              code({node, className, children, ...props}) {
                const match = /language-(\w+)/.exec(className || '')
                return match ? (
                  // @ts-ignore
                  <SyntaxHighlighter
                    {...props}
                    style={oneDark}
                    language={match[1]}
                    PreTag="div"
                  >
                    {String(children).replace(/\n$/, '')}
                  </SyntaxHighlighter>
                ) : (
                  <code {...props} className={className}>
                    {children}
                  </code>
                )
              }
            }}
          >
            {post.content}
          </ReactMarkdown>
        </div>
      </article>
    </div>
  );
}
