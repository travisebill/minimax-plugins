#!/usr/bin/env node
// verify-stream.mjs — structurally validate an AFP data stream.
//
// Why this exists: an AFP stream is self-describing. Every MO:DCA structured field
// carries its own Length, so "is this file well-formed?" is a mechanical question —
// you do not need to understand the page content to answer it. A generator that
// miscomputes a Length produces a file that is rejected (or worse, silently
// misrendered) only on a printer. This script answers the question locally.
//
// What it checks (MO:DCA / IS-3 layer):
//   * every structured field's Length lands exactly on the next field boundary
//   * Length >= 8 (the introducer) and Length <= X'7FF0' (IS/3 limit)
//   * Flags and Reserved are X'0000' (IS/3 requirement)
//   * the structure identifier is a known MO:DCA structure (unknown ones are reported)
//   * begin/end structures are properly nested
//   * with --triplets, the triplet chain inside a chosen field's data is walked and
//     every Tlength is validated
//
// Every rule below is traced to a corpus page. The rules and their sources:
//   SFI layout  Length(2B) Identifier(3B) Flags(1B) Reserved X'0000'
//               [mo-dca-reference-mixed-object-document-content-architecture-reference p.52]
//   SFLength    "Defines the length of the structured field, including itself."
//               [mo-dca-reference-mixed-object-document-content-architecture-reference p.53]
//   IS/3 Flag   "The Flag byte (byte 5) in the Structured Field Introducer (SFI) must be
//                set to X'00'."   and   "The maximum structured field length in IS/3 is
//                limited to X'7FF0' = 32,752."
//               [mo-dca-reference-mixed-object-document-content-architecture-reference p.550]
//   Triplet     Tlength(1B) | Tid(1B) | data, Tlength counting itself
//               [mo-dca-reference-mixed-object-document-content-architecture-reference p.392]
//
// It checks STRUCTURE, not SEMANTICS. It will not tell you that your page
// descriptor is the wrong size for the page — only that the byte stream is
// internally consistent.
//
// Usage:
//   node verify-stream.mjs <file.afp> [--layer modca|ipds|auto] [--triplets <HEX>]
//                          [--tree] [--quiet]
//
// Exit code: 0 = structurally consistent, 1 = errors found, 2 = usage/IO problem.

import { readFileSync } from 'node:fs';
import { MO_DCA_STRUCTURES } from './mo-dca-structures.mjs';

const INTRODUCER = 8; // Length(2) ID(3) Flags(1) Reserved(2)
const MAX_LENGTH = 0x7ff0; // MO:DCA IS/3 limit

const byHex = new Map();
for (const s of MO_DCA_STRUCTURES) {
  byHex.set(s.hex, s);
  for (const a of s.aliases) byHex.set(a.toUpperCase(), s);
}

// Structures that open a scope and the structures that close it.
// The pairs are derived from the authoritative structure table: every MO:DCA structure
// named "Begin X" is closed by the one named "End X" (verified: all 24 Begin* names
// have exactly one End* counterpart, and BDA/BDD have none because they are data
// structures, not scopes). Deriving them beats hand-listing them.
const PAIRS = (() => {
  const ends = MO_DCA_STRUCTURES.filter((s) => s.name.startsWith('End '));
  const out = [];
  for (const b of MO_DCA_STRUCTURES) {
    if (!b.name.startsWith('Begin ')) continue;
    const want = 'End ' + b.name.slice('Begin '.length);
    const match = ends.find((e) => e.name === want);
    if (match) out.push([b.acronym, match.acronym]);
  }
  return out;
})();
const OPENER = new Map(PAIRS.map(([b]) => [b, true]));
const CLOSER = new Map(PAIRS.map(([, e]) => [e, true]));
const PAIR_OF = new Map(PAIRS.flatMap(([b, e]) => [[b, e], [e, b]]));

function hex(buf, off, n) {
  return buf.subarray(off, off + n).toString('hex').toUpperCase();
}

function parseArgs(argv) {
  const positional = [];
  const flags = { layer: 'auto', triplets: null, tree: false, quiet: false };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--layer') flags.layer = argv[++i];
    else if (a === '--triplets') flags.triplets = String(argv[++i]).replace(/^X?/i, '').toUpperCase();
    else if (a === '--tree') flags.tree = true;
    else if (a === '--quiet') flags.quiet = true;
    else positional.push(a);
  }
  return { positional, flags };
}

function describe(sf) {
  const known = byHex.get(sf.hex);
  const acro = known ? known.acronym : '???';
  return {
    ...sf,
    acronym: acro,
    name: known ? known.name : 'unknown structure',
    known: Boolean(known),
  };
}

function verifyModca(buf, opts) {
  const errors = [];
  const warnings = [];
  const fields = [];

  let off = 0;
  while (off < buf.length) {
    // A MO:DCA structured field is often stored with the platform-specific
    // X'5A' prefix in front of it. The prefix is NOT part of the structured
    // field and is NOT counted in SFLength:
    //   "Some platforms include structured fields in a larger platform-specific
    //    record by surrounding the structured field with additional bytes (such
    //    as the X'5A' prefix)."
    // [mo-dca-reference-mixed-object-document-content-architecture-reference p.53]
    // So the SFI starts after the prefix, and the next record starts at
    // sfi + length. A stream that already has the prefix stripped is also
    // accepted, because SFLength defines the structured field either way.
    const sfi = buf[off] === 0x5A ? off + 1 : off;
    if (buf.length - sfi < INTRODUCER) {
      errors.push(
        `offset ${off}: only ${buf.length - off} byte(s) left — a structured field introducer needs ${INTRODUCER}`,
      );
      break;
    }
    const length = buf.readUInt16BE(sfi);
    const id = hex(buf, sfi + 2, 3);
    const flags = buf[sfi + 5];
    const reserved = buf.readUInt16BE(sfi + 6);

    if (length < INTRODUCER) {
      errors.push(
        `offset ${off}: Length=${length} is smaller than the ${INTRODUCER}-byte introducer`,
      );
      break;
    }
    if (length > MAX_LENGTH) {
      warnings.push(
        `offset ${off}: Length=0x${length.toString(16).toUpperCase()} exceeds the MO:DCA IS/3 limit 0x${MAX_LENGTH.toString(16).toUpperCase()}`,
      );
    }
    if (flags !== 0x00) {
      errors.push(`offset ${off}: Flags=0x${flags.toString(16).toUpperCase()} — IS/3 requires 0x00`);
    }
    if (reserved !== 0x0000) {
      errors.push(
        `offset ${off}: Reserved=0x${reserved.toString(16).toUpperCase()} — IS/3 requires 0x0000`,
      );
    }
    if (sfi + length > buf.length) {
      errors.push(
        `offset ${off}: Length=${length} runs past the end of the file (${buf.length - sfi} byte(s) left)`,
      );
      break;
    }

    const sf = describe({ off, length, hex: id, flags });
    if (!sf.known) {
      warnings.push(
        `offset ${off}: identifier ${id} is not in the MO:DCA structure table — ` +
          `check the page before trusting it`,
      );
    }
    sf.dataOff = sfi + INTRODUCER;
    sf.dataLen = length - INTRODUCER;
    sf.data = buf.subarray(sf.dataOff, sfi + length);
    fields.push(sf);
    off = sfi + length;
  }

  // begin/end nesting
  const stack = [];
  for (const sf of fields) {
    if (!sf.known) continue;
    if (OPENER.has(sf.acronym)) {
      stack.push(sf);
    } else if (CLOSER.has(sf.acronym)) {
      const want = PAIR_OF.get(sf.acronym);
      const top = stack.pop();
      if (!top) {
        errors.push(`offset ${sf.off}: ${sf.acronym} closes a scope that was never opened`);
      } else if (top.acronym !== want) {
        errors.push(
          `offset ${sf.off}: ${sf.acronym} closes ${top.acronym} — expected ${want}`,
        );
      }
    }
  }
  for (const open of stack) {
    errors.push(`offset ${open.off}: ${open.acronym} is never closed`);
  }

  // optional triplet chain check
  if (opts.triplets) {
    const target = fields.find((f) => f.hex === opts.triplets);
    if (!target) {
      errors.push(
        `--triplets ${opts.triplets}: no structured field with that identifier in the file`,
      );
    } else {
      const problems = walkTriplets(target.data, target.dataOff);
      errors.push(...problems);
    }
  }

  return { errors, warnings, fields, layer: 'modca' };
}

// Triplet format: Tlength(1B) | Tid(1B) | data. Tlength counts itself and the id.
function walkTriplets(data, baseOff) {
  const errors = [];
  let off = 0;
  while (off < data.length) {
    if (data.length - off < 2) {
      errors.push(
        `offset ${baseOff + off}: ${data.length - off} trailing byte(s) — a triplet needs at least Tlength+Tid`,
      );
      break;
    }
    const tlen = data[off];
    const tid = data[off + 1];
    if (tlen < 3) {
      errors.push(
        `offset ${baseOff + off}: triplet Tlength=${tlen} — the minimum is 3 (Tlength + Tid + one data byte)`,
      );
      break;
    }
    if (tlen > 254) {
      errors.push(
        `offset ${baseOff + off}: triplet Tlength=${tlen} — the maximum is 254`,
      );
      break;
    }
    if (off + tlen > data.length) {
      errors.push(
        `offset ${baseOff + off}: triplet Tlength=${tlen} runs past the end of the field data (${data.length - off} byte(s) left)`,
      );
      break;
    }
    off += tlen;
  }
  return errors;
}

// IPDS framing: Length(2B) | Command(2B) | Flags(1B) | [CID(2B)] | Data
function verifyIpds(buf) {
  const errors = [];
  const warnings = [];
  const fields = [];
  let off = 0;
  while (off < buf.length) {
    if (buf.length - off < 5) {
      errors.push(`offset ${off}: only ${buf.length - off} byte(s) left — an IPDS command needs at least 5`);
      break;
    }
    const length = buf.readUInt16BE(off);
    const cmd = hex(buf, off + 2, 2);
    if (length < 5) {
      errors.push(`offset ${off}: Length=${length} is smaller than the 5-byte IPDS command header`);
      break;
    }
    if (off + length > buf.length) {
      errors.push(`offset ${off}: Length=${length} runs past the end of the file (${buf.length - off} byte(s) left)`);
      break;
    }
    fields.push({ off, length, hex: cmd, acronym: cmd, name: 'IPDS command', known: true, dataLen: length - 5 });
    off += length;
  }
  return { errors, warnings, fields, layer: 'ipds' };
}

function looksLikeModca(buf) {
  if (buf.length < INTRODUCER) return false;
  // Try both alignments: with the platform-specific X'5A' prefix in front of
  // the structured field, and with the prefix already stripped.
  for (const sfi of [buf[0] === 0x5A ? 1 : 0, 0]) {
    if (sfi + INTRODUCER > buf.length) continue;
    const length = buf.readUInt16BE(sfi);
    if (length < INTRODUCER || length > buf.length) continue;
    const id = hex(buf, sfi + 2, 3);
    if (byHex.has(id) || id.startsWith('D3')) return true;
  }
  return false;
}

function printTree(fields, opts) {
  const stack = [];
  let depth = 0;
  for (const sf of fields) {
    if (CLOSER.has(sf.acronym) && stack.length) {
      depth = Math.max(0, depth - 1);
      stack.pop();
    }
    const indent = '  '.repeat(depth);
    const label = sf.known
      ? `${sf.acronym.padEnd(4)} ${sf.hex}  len=${String(sf.length).padStart(6)}`
      : `${'????'.padEnd(4)} ${sf.hex}  len=${String(sf.length).padStart(6)}  (unknown)`;
    console.log(`${indent}${label}  ${sf.name}`);
    if (OPENER.has(sf.acronym)) {
      stack.push(sf);
      depth += 1;
    }
  }
}

function main() {
  const { positional, flags } = parseArgs(process.argv.slice(2));
  if (!positional.length) {
    console.error(
      'usage: verify-stream.mjs <file.afp> [--layer modca|ipds|auto] [--triplets <HEX>] [--tree] [--quiet]',
    );
    process.exit(2);
  }

  let buf;
  try {
    buf = readFileSync(positional[0]);
  } catch (e) {
    console.error(`[verify-stream] cannot read ${positional[0]}: ${e.message}`);
    process.exit(2);
  }

  let layer = flags.layer;
  if (layer === 'auto') layer = looksLikeModca(buf) ? 'modca' : 'ipds';

  const result = layer === 'ipds' ? verifyIpds(buf) : verifyModca(buf, flags);

  if (!flags.quiet) {
    console.log(`file    : ${positional[0]}`);
    console.log(`size    : ${buf.length} bytes`);
    console.log(`layer   : ${result.layer}`);
    console.log(`fields  : ${result.fields.length}`);
    console.log('');
  }

  if (flags.tree && !flags.quiet) {
    printTree(result.fields, flags);
    console.log('');
  }

  for (const w of result.warnings) console.log(`WARN  ${w}`);
  for (const e of result.errors) console.log(`ERROR ${e}`);

  if (result.errors.length) {
    console.log(`\nFAIL: ${result.errors.length} structural error(s).`);
    process.exit(1);
  }
  console.log(
    `PASS: ${result.fields.length} structured field(s) form a consistent chain` +
      (result.warnings.length ? ` (${result.warnings.length} warning(s))` : ''),
  );
  process.exit(0);
}

main();
