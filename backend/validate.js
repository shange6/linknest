const fs = require('fs');
const lines = fs.readFileSync('C:/Users/shange/.openclaw-autoclaw/workspace/linknest/backend/batch_dev.jsonl', 'utf-8').split('\n').filter(l => l.trim());
let errors = 0;
lines.forEach((line, i) => {
  try { JSON.parse(line); } catch(e) { console.log(`Line ${i+1} FAIL: ${e.message}`); errors++; }
});
console.log(`Total: ${lines.length} lines, ${errors} errors`);
