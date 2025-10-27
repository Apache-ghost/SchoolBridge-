const fs = require('fs').promises;
const path = require('path');
const crypto = require('crypto');

const ROOT = path.resolve(__dirname, '..');
const OUT = path.join(ROOT, 'project-index.json');
const IGNORE = ['.git', 'node_modules', '.vscode'];

async function hashFile(filePath) {
  const hash = crypto.createHash('sha1');
  const data = await fs.readFile(filePath);
  hash.update(data);
  return hash.digest('hex');
}

async function statSafe(p) {
  try {
    return await fs.stat(p);
  } catch (e) {
    return null;
  }
}

async function walk(dir) {
  const entries = [];
  const items = await fs.readdir(dir, { withFileTypes: true });
  for (const it of items) {
    if (IGNORE.includes(it.name)) continue;
    const full = path.join(dir, it.name);
    if (it.isDirectory()) {
      const sub = await walk(full);
      entries.push(...sub);
    } else if (it.isFile()) {
      const s = await statSafe(full);
      const rel = path.relative(ROOT, full).replace(/\\/g, '/');
      const fileEntry = {
        path: rel,
        size: s ? s.size : null,
        mtime: s ? s.mtime.toISOString() : null,
      };
      // try to hash (skip large files > 10MB)
      if (s && s.size <= 10 * 1024 * 1024) {
        try {
          fileEntry.sha1 = await hashFile(full);
        } catch (e) {
          fileEntry.sha1 = null;
        }
      }
      entries.push(fileEntry);
    }
  }
  return entries;
}

async function main() {
  console.log('Scanning', ROOT);
  const files = await walk(ROOT);
  const index = {
    generated: new Date().toISOString(),
    root: ROOT,
    count: files.length,
    files
  };
  await fs.writeFile(OUT, JSON.stringify(index, null, 2), 'utf8');
  console.log('Wrote', OUT, 'with', files.length, 'files');
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
