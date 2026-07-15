const fs = require('fs');
const path = 'C:\\Users\\shange\\.openclaw-autoclaw\\workspace\\linknest\\backend\\batch_tools.jsonl';

let text = fs.readFileSync(path, 'utf8');
let lines = text.split('\n').filter(l => l.trim());

// Keep first 200
lines = lines.slice(0, 200);
fs.writeFileSync(path, lines.join('\n') + '\n', 'utf8');

// Final validation
text = fs.readFileSync(path, 'utf8');
lines = text.split('\n').filter(l => l.trim());
console.log('Final count:', lines.length);

// Check all valid JSON and no duplicates
const seen = new Set();
let valid = true;
for (let i = 0; i < lines.length; i++) {
  try {
    const obj = JSON.parse(lines[i]);
    if (seen.has(obj.url)) {
      console.log(`DUPE: ${obj.url} at line ${i+1}`);
      valid = false;
    }
    seen.add(obj.url);
    if (!obj.title || !obj.url || !obj.description || !obj.tags) {
      console.log(`MISSING FIELD at line ${i+1}`);
      valid = false;
    }
    if (obj.tags.some(t => !Array.isArray(t) || t.length !== 2)) {
      console.log(`BAD TAG at line ${i+1}`);
      valid = false;
    }
  } catch(e) {
    console.log(`INVALID JSON at line ${i+1}: ${e.message}`);
    valid = false;
  }
}
if (valid && lines.length === 200) {
  console.log('ALL GOOD - 200 valid unique entries');
}
