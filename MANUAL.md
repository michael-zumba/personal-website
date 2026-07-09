# Website User Manual

This manual provides instructions on how to manage, update, and deploy your personal academic website.

## 1. Environment Setup

Before you begin, ensure you have the following installed on your computer:

- **Node.js**: Required to run the website. [Download here](https://nodejs.org/).
- **Git**: Required for version control. [Download here](https://git-scm.com/).
- **Visual Studio Code (VS Code)**: Recommended editor for updating content.

## 2. Running the Website Locally

To preview changes before they go live:

1. Open your terminal (or VS Code terminal).
2. Navigate to the project folder.
3. Install dependencies (only needed the first time or after adding new packages):
   ```bash
   npm install
   ```
4. Start the local server:
   ```bash
   npm run dev
   ```
5. Open your browser and visit: `http://localhost:3000`

## 3. Updating Website Content

The website content is managed through simple text files located in the `content/` directory. You do **not** need to touch the code (`.tsx` files) to update text or lists.

### 3.1 Updating Pages (About, Research, Teaching)

Navigate to `content/pages/` to find the Markdown files for each page.

#### About Page (`content/pages/about.md`)

- **Main Text**: Edit the text below the `---` separator.
- **Skills**: Update the lists under `languages` and `methodologies` in the top section.
- **Research Interests**: Update the list under `research_interests`.
- **Education**: Update entries in the `education` list.
- **Appointments**: Update entries in the `appointments` list.
- **Professional Affiliations**: Update entries in the `professional` list.

When adding strings with colons (e.g., "Languages: English"), wrap them in quotes: `"Languages: English"`.

#### Research Page (`content/pages/research.md`)

- **Intro Text**: Edit the text below the `---` separator.
- **Journal Articles**: Add new entries under the `publications` list.
- **Working Papers**: Add entries under `working_papers`.
- **Grants**: Add entries under `grants`.
- **Editorial Roles**: Add entries under `editorial`.
- **Conferences**: Add entries under `conferences`.

#### Teaching Page (`content/pages/teaching.md`)

- **Teaching Philosophy**: Edit the text below the `---` separator.
- **Courses**: Add new courses under the `courses` list.
- **PhD Supervision**: Update `phd_supervision.principal` and `phd_supervision.associate` lists.
- **Master Supervision**: Update the `master_supervision` list.

### 3.2 Adding Blog Posts

1. Create a new file in `content/blog/` with the name `your-post-title.mdx`.
2. Copy the structure from existing posts:
   ```markdown
   ---
   title: "Your Post Title"
   date: "2026-07-01"
   description: "A short summary of your post."
   tags: ["topic1", "topic2"]
   ---

   Write your content here using Markdown...
   ```

## 4. Markdown Guide

You can use standard Markdown syntax in your content files:

- **Bold**: `**text**`
- *Italic*: `*text*`
- [Links](https://example.com): `[Link Text](URL)`
- Headers: `# Heading 1`, `## Heading 2`
- Lists: `- Item 1`
- Code blocks: ` ```python ... ``` `

## 5. Deploying to GitHub Pages

### Option A: Automatic Deployment (Recommended)

1. Go to your GitHub repository: `https://github.com/michael-zumba/personal-website`
2. Navigate to **Settings** > **Pages**
3. Under **Build and deployment**, select **Source: GitHub Actions**
4. Create a file at `.github/workflows/deploy.yml` with the following:

   ```yaml
   name: Deploy to GitHub Pages

   on:
     push:
       branches: [main]
     workflow_dispatch:

   permissions:
     contents: read
     pages: write
     id-token: write

   concurrency:
     group: "pages"
     cancel-in-progress: false

   jobs:
     build:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - uses: actions/setup-node@v4
           with:
             node-version: 20
             cache: npm
         - run: npm ci
         - run: npm run build
         - uses: actions/upload-pages-artifact@v3
           with:
             path: ./out
         - uses: actions/deploy-pages@v4
   ```

5. Push the workflow file to GitHub. The site will deploy automatically on every push to `main`.

### Option B: Manual Deployment

1. Build the site:
   ```bash
   npm run build
   ```
2. The static files are generated in the `out/` directory.
3. Push the contents of `out/` to the `gh-pages` branch, or configure GitHub Pages to serve from the `out/` directory on the `main` branch.

## 6. Uploading to GitHub

Once you are happy with your changes locally:

1. Open the terminal.
2. Stage your changes:
   ```bash
   git add .
   ```
3. Commit your changes with a message:
   ```bash
   git commit -m "Update research publications"
   ```
4. Push to GitHub:
   ```bash
   git push origin main
   ```

## 7. Offline Build Verification

To verify the production build before deploying:

```bash
npm run build
```

Check the `out/` directory for the generated static files. You can serve them locally with any static file server:

```bash
npx serve out
```
