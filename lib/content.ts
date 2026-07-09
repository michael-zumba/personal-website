import fs from "fs";
import path from "path";
import matter from "gray-matter";

const pagesDirectory = path.join(process.cwd(), "content/pages");

export interface PageData {
  slug: string;
  title: string;
  description?: string;
  content: string;
  [key: string]: any;
}

export function getPageData(slug: string): PageData {
  const fullPath = path.join(pagesDirectory, `${slug}.md`);
  // Check for .md or .mdx
  let fileContents = "";
  if (fs.existsSync(fullPath)) {
    fileContents = fs.readFileSync(fullPath, "utf8");
  } else if (fs.existsSync(path.join(pagesDirectory, `${slug}.mdx`))) {
    fileContents = fs.readFileSync(path.join(pagesDirectory, `${slug}.mdx`), "utf8");
  } else {
    throw new Error(`Page content for ${slug} not found.`);
  }

  const matterResult = matter(fileContents);

  return {
    slug,
    content: matterResult.content,
    ...(matterResult.data as { title: string; description?: string }),
  };
}
