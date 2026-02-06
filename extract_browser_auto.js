const fs = require('fs');

async function run() {
  const response = await fetch('https://raw.githubusercontent.com/VoltAgent/awesome-openclaw-skills/main/README.md');
  const text = await response.text();
  
  const results = [];
  const startMarker = '### Browser & Automation';
  const endMarker = '### '; // Next category
  
  const startIdx = text.indexOf(startMarker);
  if (startIdx === -1) {
    console.error('Category not found');
    return;
  }
  
  let endIdx = text.indexOf(endMarker, startIdx + startMarker.length);
  if (endIdx === -1) endIdx = text.length;
  
  const section = text.substring(startIdx, endIdx);
  const regex = /- \[(.*?)\]\(https:\/\/github\.com\/openclaw\/skills\/tree\/main\/skills\/(.*?)\)/g;
  
  let match;
  while ((match = regex.exec(section)) !== null) {
    results.push(match[1]);
  }
  
  console.log(JSON.stringify(results));
}

run();
