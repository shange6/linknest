const fs = require('fs');
const lines = fs.readFileSync('C:\\Users\\shange\\.openclaw-autoclaw\\workspace\\linknest\\backend\\batch_tools.jsonl', 'utf8').split('\n').filter(l => l.trim());
const seen = new Map();
const dupes = [];
lines.forEach((line, i) => {
  try {
    const obj = JSON.parse(line);
    if (seen.has(obj.url)) {
      dupes.push({ url: obj.url, line: i+1, first: seen.get(obj.url) });
    } else {
      seen.set(obj.url, i+1);
    }
  } catch(e) { console.log('Invalid JSON at line', i+1); }
});
if (dupes.length > 0) {
  dupes.forEach(d => console.log(`Duplicate: "${d.url}" at line ${d.line} (first at line ${d.first})`));
} else {
  console.log('No duplicates');
}
console.log('Total lines:', lines.length);
