/**
 * Generate academic journal-style .docx files from extracted JSON research reports.
 *
 * Author: Dr Yuqian Zhang
 * Date: 16 July 2026
 */

const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType,
  ShadingType, PageNumber, PageBreak, LevelFormat, TableOfContents
} = require('docx');

const JSON_DIR = path.join(__dirname, 'extracted_json');
const OUTPUT_DIR = path.join(__dirname, '..');
const MANIFEST_PATH = path.join(__dirname, '.report_manifest.json');

const PAGE_WIDTH = 12240;
const PAGE_HEIGHT = 15840;
const MARGIN = 1440;

const BODY_FONT = 'Times New Roman';
const HEADING_FONT = 'Times New Roman';
const FONT_SIZE = 24;
const LINE_SPACING = 276;

const border = { style: BorderStyle.SINGLE, size: 1, color: '999999' };
const borders = { top: border, bottom: border, left: border, right: border };
const headerShading = { fill: 'D9E2F3', type: ShadingType.CLEAR };

function makeParagraph(text, options = {}) {
  const { bold, italic, fontSize, alignment, spacing, indent, font } = options;
  const runOpts = { font: font || BODY_FONT, size: fontSize || FONT_SIZE };
  if (bold) runOpts.bold = true;
  if (italic) runOpts.italic = true;
  const paraOpts = {
    spacing: spacing || { after: 120, line: LINE_SPACING },
    children: [new TextRun({ ...runOpts, text })]
  };
  if (alignment) paraOpts.alignment = alignment;
  if (indent) paraOpts.indent = indent;
  return new Paragraph(paraOpts);
}


function makeHeading(text, level) {
  const sizes = { 1: 32, 2: 28, 3: 24 };
  return new Paragraph({
    heading: level === 1 ? HeadingLevel.HEADING_1 : level === 2 ? HeadingLevel.HEADING_2 : HeadingLevel.HEADING_3,
    spacing: { before: level === 1 ? 360 : 240, after: 180, line: LINE_SPACING },
    children: [new TextRun({ text, font: HEADING_FONT, size: sizes[level] || 24, bold: true })]
  });
}


function makeBulletList(items) {
  return items.map(item => new Paragraph({
    numbering: { reference: 'bullets', level: 0 },
    spacing: { after: 60, line: LINE_SPACING },
    children: [new TextRun({ text: item, font: BODY_FONT, size: FONT_SIZE })]
  }));
}


function makeNumberedList(items) {
  return items.map((item, i) => new Paragraph({
    numbering: { reference: 'numbers', level: 0 },
    spacing: { after: 60, line: LINE_SPACING },
    children: [new TextRun({ text: item, font: BODY_FONT, size: FONT_SIZE })]
  }));
}


function makeTable(caption, headers, rows, note) {
  const children = [];
  if (caption) {
    children.push(new Paragraph({
      spacing: { before: 240, after: 80, line: LINE_SPACING },
      children: [new TextRun({ text: caption, font: BODY_FONT, size: 22, bold: true, italic: true })]
    }));
  }

  const allCols = headers.length || (rows[0] ? rows[0].length : 2);
  const colWidth = Math.floor(9360 / allCols);

  const tableRows = [];
  if (headers.length > 0) {
    tableRows.push(new TableRow({
      cantSplit: true,
      tableHeader: true,
      children: headers.map(h => new TableCell({
        borders, shading: headerShading,
        width: { size: colWidth, type: WidthType.DXA },
        margins: { top: 60, bottom: 60, left: 100, right: 100 },
        children: [new Paragraph({
          spacing: { after: 0, line: 240 },
          children: [new TextRun({ text: h, font: BODY_FONT, size: 20, bold: true })]
        })]
      }))
    }));
  }

  for (const row of rows) {
    tableRows.push(new TableRow({
      cantSplit: true,
      children: row.map(cell => new TableCell({
        borders,
        width: { size: colWidth, type: WidthType.DXA },
        margins: { top: 50, bottom: 50, left: 100, right: 100 },
        children: [new Paragraph({
          spacing: { after: 0, line: 240 },
          children: [new TextRun({ text: cell, font: BODY_FONT, size: 20 })]
        })]
      }))
    }));
  }

  children.push(new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    columnWidths: Array(allCols).fill(colWidth),
    rows: tableRows
  }));

  if (note) {
    children.push(new Paragraph({
      spacing: { before: 60, after: 200, line: LINE_SPACING },
      children: [new TextRun({ text: 'Note: ' + note, font: BODY_FONT, size: 18, italic: true })]
    }));
  }

  return children;
}


function makeCallout(text) {
  return [
    new Paragraph({
      spacing: { before: 200, after: 200, line: LINE_SPACING },
      indent: { left: 360 },
      border: { left: { style: BorderStyle.SINGLE, size: 6, color: '1E3A5F' } },
      children: [new TextRun({ text, font: BODY_FONT, size: FONT_SIZE, italics: true })]
    })
  ];
}


function renderContent(content) {
  const children = [];
  for (const item of content) {
    switch (item.type) {
      case 'paragraph':
        children.push(makeParagraph(item.text));
        break;
      case 'heading':
        children.push(makeHeading(item.text, item.level || 3));
        break;
      case 'bullet_list':
        children.push(...makeBulletList(item.items));
        break;
      case 'numbered_list':
        children.push(...makeNumberedList(item.items));
        break;
      case 'table':
        children.push(...makeTable(item.caption, item.headers, item.rows, item.note));
        break;
      case 'callout':
        children.push(...makeCallout(item.text));
        break;
    }
  }
  return children;
}


function buildDocument(data) {
  const children = [];

  children.push(new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 60, line: 360 },
    children: [new TextRun({ text: data.title, font: HEADING_FONT, size: 36, bold: true })]
  }));

  if (data.subtitle) {
    children.push(new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { after: 160, line: LINE_SPACING },
      children: [new TextRun({ text: data.subtitle, font: BODY_FONT, size: 26, italics: true })]
    }));
  }

  children.push(new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 40, line: LINE_SPACING },
    children: [new TextRun({ text: data.author || 'Dr Yuqian Zhang', font: BODY_FONT, size: 24 })]
  }));

  children.push(new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 300, line: LINE_SPACING },
    children: [new TextRun({ text: data.date || '2026', font: BODY_FONT, size: 22, italics: true })]
  }));

  if (data.abstract) {
    children.push(new Paragraph({
      spacing: { before: 120, after: 60, line: LINE_SPACING },
      children: [new TextRun({ text: 'Abstract', font: HEADING_FONT, size: 24, bold: true })]
    }));
    children.push(new Paragraph({
      spacing: { after: 200, line: LINE_SPACING },
      indent: { left: 360, right: 360 },
      children: [new TextRun({ text: data.abstract, font: BODY_FONT, size: FONT_SIZE, italics: true })]
    }));
  }

  children.push(new Paragraph({ children: [new PageBreak()] }));

  let sectionCounter = 0;
  for (const section of data.sections) {
    if (section.level === 1) {
      sectionCounter++;
    }

    const sectionChildren = renderContent(section.content);

    if (section.heading && section.level === 1) {
      children.push(makeHeading(section.heading, 1));
    } else if (section.heading && section.level === 2) {
      children.push(makeHeading(section.heading, 2));
    }

    children.push(...sectionChildren);
  }

  if (data.references && data.references.length > 0) {
    children.push(new Paragraph({ children: [new PageBreak()] }));
    children.push(makeHeading('References', 1));

    const refNumbers = {
      config: [{
        reference: 'refs',
        levels: [{
          level: 0,
          format: LevelFormat.DECIMAL,
          text: '[%1]',
          alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 540, hanging: 360 } } }
        }]
      }]
    };

    const refParagraphs = data.references.map(ref => {
      const text = ref.url ? `${ref.text} (${ref.url})` : ref.text;
      return new Paragraph({
        numbering: { reference: 'refs', level: 0 },
        spacing: { after: 80, line: 240 },
        children: [new TextRun({ text, font: BODY_FONT, size: 20 })]
      });
    });

    const doc = new Document({
      numbering: refNumbers,
      styles: { default: { document: { run: { font: BODY_FONT, size: FONT_SIZE } } } },
      sections: [{ children: refParagraphs }]
    });
    children.push(...refParagraphs);
  }

  return children;
}


function generateDocx(jsonPath, outputPath, slug) {
  const data = JSON.parse(fs.readFileSync(jsonPath, 'utf-8'));

  const numberingConfig = [
    {
      reference: 'bullets',
      levels: [{
        level: 0, format: LevelFormat.BULLET, text: '\u2022',
        alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 720, hanging: 360 } } }
      }]
    },
    {
      reference: 'numbers',
      levels: [{
        level: 0, format: LevelFormat.DECIMAL, text: '%1.',
        alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 720, hanging: 360 } } }
      }]
    },
    {
      reference: 'refs',
      levels: [{
        level: 0,
        format: LevelFormat.DECIMAL,
        text: '[%1]',
        alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 540, hanging: 360 } } }
      }]
    }
  ];

  const docChildren = buildDocument(data);

  const doc = new Document({
    numbering: { config: numberingConfig },
    styles: {
      default: {
        document: {
          run: { font: BODY_FONT, size: FONT_SIZE }
        }
      },
      paragraphStyles: [
        {
          id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true,
          run: { size: 32, bold: true, font: HEADING_FONT },
          paragraph: { spacing: { before: 360, after: 180 }, outlineLevel: 0, keepNext: false, keepLines: false }
        },
        {
          id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true,
          run: { size: 28, bold: true, font: HEADING_FONT },
          paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 1, keepNext: false, keepLines: false }
        },
        {
          id: 'Heading3', name: 'Heading 3', basedOn: 'Normal', next: 'Normal', quickFormat: true,
          run: { size: 24, bold: true, font: HEADING_FONT },
          paragraph: { spacing: { before: 200, after: 100 }, outlineLevel: 2, keepNext: false, keepLines: false }
        }
      ]
    },
    sections: [{
      properties: {
        page: {
          size: { width: PAGE_WIDTH, height: PAGE_HEIGHT },
          margin: { top: MARGIN, right: MARGIN, bottom: MARGIN, left: MARGIN }
        }
      },
      headers: {
        default: new Header({
          children: [new Paragraph({
            alignment: AlignmentType.RIGHT,
            children: [new TextRun({ text: data.title.substring(0, 60), font: BODY_FONT, size: 18, italics: true })]
          })]
        })
      },
      footers: {
        default: new Footer({
          children: [new Paragraph({
            alignment: AlignmentType.CENTER,
            children: [
              new TextRun({ text: 'Page ', font: BODY_FONT, size: 18 }),
              new TextRun({ children: [PageNumber.CURRENT], font: BODY_FONT, size: 18 })
            ]
          })]
        })
      },
      children: docChildren
    }]
  });

  Packer.toBuffer(doc).then(buffer => {
    fs.writeFileSync(outputPath, buffer);
    console.log(`  -> ${outputPath}`);
    console.log(`     Title: ${data.title.substring(0, 70)}`);
    console.log(`     Sections: ${data.sections.length}, Refs: ${data.references.length}`);
  });
}


function loadManifest() {
  if (!fs.existsSync(MANIFEST_PATH)) {
    console.error('ERROR: Manifest not found. Run sync_reports.py first.');
    process.exit(1);
  }
  return JSON.parse(fs.readFileSync(MANIFEST_PATH, 'utf-8'));
}

if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

const manifest = loadManifest();

for (const entry of manifest) {
  const { slug, docx_name } = entry;
  const jsonPath = path.join(JSON_DIR, `${slug}.json`);
  if (!fs.existsSync(jsonPath)) {
    console.log(`SKIP: ${jsonPath} not found`);
    continue;
  }
  const outputPath = path.join(OUTPUT_DIR, docx_name);
  generateDocx(jsonPath, outputPath, slug);
}
