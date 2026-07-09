import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';
import { PrismLight as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/cjs/styles/prism';
import Image from 'next/image';

interface MarkdownRendererProps {
  content: string;
}

export function MarkdownRenderer({ content }: MarkdownRendererProps) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      rehypePlugins={[rehypeRaw]}
      components={{
        code({ node, className, children, ...props }) {
          const match = /language-(\w+)/.exec(className || '');
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
          );
        },
        img: (image) => {
          return (
            <span className="block my-8">
              <img
                src={image.src || ''}
                alt={image.alt || ''}
                className="rounded-lg shadow-md mx-auto max-w-full h-auto object-cover"
                style={{ maxHeight: '500px' }}
              />
              {image.title && (
                <span className="block text-center text-sm text-muted-foreground mt-2 italic">
                  {image.title}
                </span>
              )}
            </span>
          );
        },
        // Customize links to open in new tab if external
        a: ({ node, ...props }) => {
          const isExternal = props.href?.startsWith('http');
          return (
            <a
              {...props}
              target={isExternal ? '_blank' : undefined}
              rel={isExternal ? 'noopener noreferrer' : undefined}
              className="text-primary hover:underline font-medium"
            />
          );
        },
      }}
    >
      {content}
    </ReactMarkdown>
  );
}
