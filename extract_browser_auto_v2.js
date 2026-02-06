const fs = require('fs');

async function run() {
  const response = await fetch('https://raw.githubusercontent.com/VoltAgent/awesome-openclaw-skills/main/README.md');
  const text = await response.text();
  
  // Try to find the section by the anchor link or the text
  const sectionName = 'Browser & Automation';
  const regexSection = new RegExp('### ' + sectionName.replace('&', '.'), 'i');
  const matchSection = text.match(regexSection);
  
  if (!matchSection) {
    console.error('Category not found with regex');
    // Print a bit of text to see what's wrong
    console.log('Sample text:', text.substring(0, 500));
    return;
  }
  
  const startIdx = matchSection.index;
  let endIdx = text.indexOf('### ', startIdx + 10);
  if (endIdx === -1) endIdx = text.length;
  
  const section = text.substring(startIdx, endIdx);
  const regexSlug = /- \[(.*?)\]\(https:\/\/github\.com\/openclaw\/skills\/tree\/main\/skills\/(.*?)\)/g;
  
  const results = [];
  let match;
  while ((match = regexSlug.exec(section)) !== null) {
    results.push(match[1]);
  }
  
  console.log(JSON.stringify(results));
}

run();
