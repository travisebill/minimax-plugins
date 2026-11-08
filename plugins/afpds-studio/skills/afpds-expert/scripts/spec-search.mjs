#!/usr/bin/env node
// spec-search.mjs — search and page-read the AFPDS spec corpus with page citations.
//
// Why this exists: an AFP fact is only usable if it can be traced to a spec page.
// Every hit is reported as `doc / page / line`, so a claim can always be checked
// against the source document.
//
// Corpus resolution order:
//   1. $AFPDS_CORPUS
//   2. <skill-dir>/corpus   (the copy bundled with this skill)
//
// Usage:
//   node spec-search.mjs docs
//   node spec-search.mjs search "<phrase>" [--doc <slug>] [-n 20] [-C 2] [--regex]
//   node spec-search.mjs page <slug> <start> [end]

import { readFileSync, existsSync, readdirSync } from 'node:fs';
import { join, dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const SKILL_DIR = resolve(HERE, '..');
const PAGE_RE = /^<<<PAGE (\d+)>>>$/;

function resolveCorpus() {
  const candidates = [
    process.env.AFPDS_CORPUS,
    join(SKILL_DIR, 'corpus'),
  ].filter(Boolean);

  for (const c of candidates) {
    const dir = resolve(c);
    if (existsSync(join(dir, 'index.json'))) return dir;
  }

  console.error('[spec-search] corpus not found. Looked in:');
  for (const c of candidates) console.error(`  - ${resolve(c)}`);
  console.error(
    '[spec-search] Set $AFPDS_CORPUS to a corpus directory, or restore the corpus/\n' +
      '  directory bundled next to this script (it holds index.json plus one .txt per\n' +
      '  AFPC publication, pages delimited by "<<<PAGE n>>>" markers).',
  );
  process.exit(1);
}

const CORPUS = resolveCorpus();
const INDEX = JSON.parse(readFileSync(join(CORPUS, 'index.json'), 'utf-8'));

function parseArgs(argv) {
  const positional = [];
  const flags = { doc: null, limit: 20, context: 2, regex: false };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--doc') flags.doc = argv[++i];
    else if (a === '-n' || a === '--limit') flags.limit = Number(argv[++i]);
    else if (a === '-C' || a === '--context') flags.context = Number(argv[++i]);
    else if (a === '--regex') flags.regex = true;
    else positional.push(a);
  }
  return { positional, flags };
}

function resolveDocs(filter) {
  if (!filter) return INDEX.documents;
  // Match loosely so abbreviations work: "modca" must hit "mo-dca-reference-...".
  // Compare with punctuation stripped from both sides.
  const needle = filter.toLowerCase().replace(/[^a-z0-9]/g, '');
  const norm = (s) => (s || '').toLowerCase().replace(/[^a-z0-9]/g, '');

  const scored = [];
  for (const d of INDEX.documents) {
    const slug = norm(d.text_path.replace(/\.txt$/, ''));
    const title = norm(d.title);
    const docNo = norm(d.doc_number);
    let score = 0;
    if (slug === needle || title === needle || docNo === needle) score = 4;
    else if (slug.startsWith(needle) || title.startsWith(needle)) score = 3;
    else if (slug.includes(needle) || title.includes(needle) || docNo.includes(needle)) score = 1;
    if (score > 0) scored.push({ d, score });
  }
  // Best match first, so `page modca` picks the MO:DCA Reference over mo-dca-l.
  // Tie-break on page count: an abbreviation usually means the big primary
  // specification rather than a side document that shares its prefix.
  scored.sort(
    (a, b) =>
      b.score - a.score ||
      (b.d.pages || 0) - (a.d.pages || 0) ||
      a.d.text_path.localeCompare(b.d.text_path),
  );
  return scored.map((s) => s.d);
}

function cmdDocs() {
  console.log(`${'slug'.padEnd(62)} ${'pages'.padStart(6)} ${'textKB'.padStart(8)}  doc#      title`);
  for (const d of [...INDEX.documents].sort((a, b) => (b.pages || 0) - (a.pages || 0))) {
    console.log(
      `${d.text_path.replace(/\.txt$/, '').padEnd(62)} ${String(d.pages || 0).padStart(6)} ` +
        `${String(Math.round((d.text_bytes || 0) / 1024)).padStart(8)}  ${(d.doc_number || '').padEnd(9)} ${d.title || ''}`,
    );
  }
  console.log(
    `\ntotal: ${INDEX.document_count} docs, ${INDEX.total_pages} pages, ` +
      `${(INDEX.total_text_bytes / 1048576).toFixed(1)} MB text`,
  );
}

function cmdSearch(query, flags) {
  const docs = resolveDocs(flags.doc);
  if (docs.length === 0) {
    console.error(`[spec-search] no document matches ${flags.doc}`);
    process.exit(1);
  }

  const test = flags.regex
    ? (() => {
        const re = new RegExp(query, 'i');
        return (line) => re.test(line);
      })()
    : (() => {
        const q = query.toLowerCase();
        return (line) => line.toLowerCase().includes(q);
      })();

  let hits = 0;
  for (const d of docs) {
    const path = join(CORPUS, d.text_path);
    if (!existsSync(path)) continue;
    const lines = readFileSync(path, 'utf-8').split('\n');
    let page = 0;
    for (let i = 0; i < lines.length; i++) {
      const pm = PAGE_RE.exec(lines[i]);
      if (pm) {
        page = Number(pm[1]);
        continue;
      }
      if (!test(lines[i])) continue;
      if (hits >= flags.limit) {
        console.log(`\n[spec-search] limit of ${flags.limit} reached; narrow the query or use --doc.`);
        return;
      }
      hits++;
      console.log(`\n--- ${d.text_path.replace(/\.txt$/, '')}  p.${page}  L${i + 1} ---`);
      const from = Math.max(0, i - flags.context);
      const to = Math.min(lines.length, i + flags.context + 1);
      for (let j = from; j < to; j++) {
        console.log(`${j === i ? '>>' : '  '} ${lines[j].slice(0, 240)}`);
      }
    }
  }
  if (hits === 0) {
    console.log(`no hits for ${JSON.stringify(query)}` + (flags.doc ? ` in ${flags.doc}` : ''));
  }
}

function cmdPage(docFilter, start, end) {
  const docs = resolveDocs(docFilter);
  if (docs.length === 0) {
    console.error(`[spec-search] no document matches ${docFilter}`);
    process.exit(1);
  }
  const d = docs[0];
  const path = join(CORPUS, d.text_path);
  if (!existsSync(path)) {
    console.error(`[spec-search] missing text file for ${d.text_path}`);
    process.exit(1);
  }
  const lines = readFileSync(path, 'utf-8').split('\n');
  console.log(`${d.title}  (${d.text_path})  pages ${start}-${end}`);
  let cur = null;
  for (const line of lines) {
    const pm = PAGE_RE.exec(line);
    if (pm) {
      cur = Number(pm[1]);
      continue;
    }
    if (cur !== null && cur >= start && cur <= end) console.log(`[p.${cur}] ${line}`);
  }
}

function main() {
  const { positional, flags } = parseArgs(process.argv.slice(2));
  const cmd = positional.shift();

  switch (cmd) {
    case 'docs':
      cmdDocs();
      break;
    case 'search':
      if (!positional.length) {
        console.error('usage: spec-search.mjs search "<query>" [--doc <slug>] [-n N] [-C N] [--regex]');
        process.exit(2);
      }
      cmdSearch(positional[0], flags);
      break;
    case 'page':
      if (positional.length < 2) {
        console.error('usage: spec-search.mjs page <slug> <start> [end]');
        process.exit(2);
      }
      cmdPage(positional[0], Number(positional[1]), Number(positional[2] ?? positional[1]));
      break;
    default:
      console.error(
        'usage:\n' +
          '  spec-search.mjs docs\n' +
          '  spec-search.mjs search "<phrase>" [--doc <slug>] [-n 20] [-C 2] [--regex]\n' +
          '  spec-search.mjs page <slug> <start> [end]',
      );
      process.exit(2);
  }
}

main();
