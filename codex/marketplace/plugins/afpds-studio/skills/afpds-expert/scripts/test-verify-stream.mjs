#!/usr/bin/env node
// test-verify-stream.mjs — regression tests for verify-stream.mjs.
//
// A validator that never fails is worse than no validator: it manufactures
// confidence. These tests prove the checker still rejects the ways an AFP file
// is usually broken — a wrong Length, a mismatched begin/end pair, a non-zero
// Flags byte, a truncated file — and that it accepts both stream encodings.
//
// The two encodings matter. MO:DCA defines a structured field as an SFI plus
// data, and SFLength counts the structured field itself. Real platforms store
// the field with an extra X'5A' byte in front of it, and that byte is NOT
// counted in SFLength:
//   "Some platforms include structured fields in a larger platform-specific
//    record by surrounding the structured field with additional bytes (such as
//    the X'5A' prefix)."
// [mo-dca-reference-mixed-object-document-content-architecture-reference p.53]
// So the validator must accept a stream with the prefix and a stream without it.
//
// Usage:
//   node test-verify-stream.mjs

import { execFileSync } from 'node:child_process';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { writeFileSync, mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';

const HERE = dirname(fileURLToPath(import.meta.url));
const VERIFIER = join(HERE, 'verify-stream.mjs');

// MO:DCA structured field: Length(2B) | ID(3B) | Flags(1B) | Reserved(2B) | Data.
// Length counts the whole structured field, the introducer included, and is
// big-endian (UBIN).
function sf(hexid, data = Buffer.alloc(0), flags = 0) {
  const body = Buffer.concat([
    Buffer.from(hexid, 'hex'),
    Buffer.from([flags]),
    Buffer.from([0x00, 0x00]),
    data,
  ]);
  const length = body.length + 2;
  return Buffer.concat([Buffer.from([(length >> 8) & 0xff, length & 0xff]), body]);
}

// The same structured field with the platform-specific X'5A' prefix in front.
function sfPrefixed(hexid, data = Buffer.alloc(0), flags = 0) {
  return Buffer.concat([Buffer.from([0x5a]), sf(hexid, data, flags)]);
}

function build(encode) {
  const pgd = encode('D3A6AF', Buffer.alloc(15));
  const bag = encode('D3A8C9', Buffer.from('PAGEGRP ', 'latin1'));
  const eag = encode('D3A9C9', Buffer.from('PAGEGRP ', 'latin1'));
  const obp = encode('D3AC6B', Buffer.alloc(24));
  const bpg = encode('D3A8AF', Buffer.from('PAGE1   ', 'latin1'));
  const epg = encode('D3A9AF', Buffer.from('PAGE1   ', 'latin1'));
  const bdt = encode('D3A8A8', Buffer.from('DOC1    ', 'latin1'));
  const edt = encode('D3A9A8', Buffer.from('DOC1    ', 'latin1'));
  const bpf = encode('D3A8A5', Buffer.from('PRINTF   ', 'latin1'));
  const epf = encode('D3A9A5', Buffer.from('PRINTF   ', 'latin1'));
  return Buffer.concat([bpf, bdt, bpg, bag, pgd, eag, obp, epg, edt, epf]);
}

function run(data) {
  const dir = mkdtempSync(join(tmpdir(), 'vstest-'));
  const path = join(dir, 'sample.afp');
  try {
    writeFileSync(path, data);
    try {
      const stdout = execFileSync('node', [VERIFIER, path], { encoding: 'utf-8' });
      return { code: 0, out: stdout };
    } catch (e) {
      return { code: e.status, out: (e.stdout || '') + (e.stderr || '') };
    }
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
}

const failures = [];
let passed = 0;

function check(label, ok, detail) {
  if (ok) {
    passed += 1;
    console.log(`[PASS] ${label}`);
  } else {
    failures.push(`${label}: ${detail}`);
    console.log(`[FAIL] ${label}  ${detail}`);
  }
}

for (const [encoding, encode] of [
  ['no X\'5A\' prefix', sf],
  ['with X\'5A\' prefix', sfPrefixed],
]) {
  const good = build(encode);

  // 1. a well-formed stream passes
  const ok = run(good);
  check(`${encoding}: valid stream accepted`, ok.code === 0, `rc=${ok.code}\n${ok.out}`);

  // 2. a wrong Length must be caught (the Length field is the first two bytes
  //    of the structured field, i.e. bytes 1-2 when the prefix is present)
  const badLength = Buffer.from(good);
  const lenAt = encode === sf ? 0 : 1;
  badLength.writeUInt16BE(good.length + 4, lenAt);
  const r2 = run(badLength);
  check(`${encoding}: corrupted length rejected`, r2.code === 1 && r2.out.includes('ERROR'), `rc=${r2.code}\n${r2.out}`);

  // 3. a swapped begin/end pair must be caught
  const badPair = Buffer.from(good);
  const idx = badPair.indexOf(Buffer.from('D3A9C9', 'hex'));
  if (idx < 0) throw new Error('test setup: End AEG identifier not found');
  badPair.write('D3A8C9', idx, 'hex');
  const r3 = run(badPair);
  check(`${encoding}: mismatched begin/end rejected`, r3.code === 1 && r3.out.includes('ERROR'), `rc=${r3.code}\n${r3.out}`);

  // 4. non-zero Flags must be caught (Flags is the byte after the identifier)
  const badFlags = Buffer.from(good);
  const flagsAt = lenAt + 5;
  badFlags[flagsAt] = 0x80;
  const r4 = run(badFlags);
  check(`${encoding}: non-zero Flags rejected`, r4.code === 1 && r4.out.includes('Flags'), `rc=${r4.code}\n${r4.out}`);

  // 5. a truncated file must be caught
  const r5 = run(good.subarray(0, good.length - 4));
  check(`${encoding}: truncated file rejected`, r5.code === 1 && r5.out.includes('ERROR'), `rc=${r5.code}\n${r5.out}`);

  // 6. an unknown structure identifier is reported
  const badId = Buffer.from(good);
  badId.write('D3FF00', lenAt + 2, 'hex');
  const r6 = run(badId);
  check(`${encoding}: unknown identifier reported`, r6.code === 1 && (r6.out.includes('WARN') || r6.out.includes('ERROR')), `rc=${r6.code}\n${r6.out}`);

  // 7. a Length that is off by exactly ONE must still be caught.
  //    This is the case that a "the X'5A' prefix is optional" parser cannot
  //    see: the record swallows the next record's prefix byte as data, the
  //    chain still lines up, and the error disappears. The validator decides
  //    the prefix convention once for the whole stream and enforces it, which
  //    is what makes this case detectable.
  for (const delta of [1, -1]) {
    const offByOne = Buffer.from(good);
    const lowByte = lenAt + 1;
    offByOne[lowByte] = (offByOne[lowByte] + delta) & 0xff;
    const r7 = run(offByOne);
    check(`${encoding}: length off by ${delta > 0 ? '+' : '-'}1 rejected`, r7.code === 1 && r7.out.includes('ERROR'), `rc=${r7.code}\n${r7.out}`);
  }

  // 8. a missing X'5A' prefix must be caught in a prefixed stream
  if (encode === sfPrefixed) {
    const noPrefix = Buffer.from(good);
    const second = good.indexOf(0x5a, 1);
    if (second < 0) throw new Error('test setup: second prefix not found');
    noPrefix[second] = 0x00;
    const r8 = run(noPrefix);
    check(`${encoding}: missing X'5A' prefix rejected`, r8.code === 1 && r8.out.includes('ERROR'), `rc=${r8.code}\n${r8.out}`);
  }
}

if (failures.length) {
  console.log(`\n${failures.length} failure(s):`);
  for (const f of failures) console.log('- ' + f);
  process.exit(1);
}
console.log(`\nall ${passed} verify-stream tests passed`);
