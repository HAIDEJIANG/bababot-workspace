const fs = require('fs');

async function run() {
  const response = await fetch('https://raw.githubusercontent.com/VoltAgent/awesome-openclaw-skills/main/README.md');
  const text = await response.text();
  
  const categories = [
    'Web & Frontend Development',
    'Browser & Automation',
    'Self-Hosted & Automation'
  ];
  
  const results = {};
  
  categories.forEach(cat => {
    const startIdx = text.indexOf('### ' + cat);
    if (startIdx === -1) return;
    
    // Find the next category or end of file
    let endIdx = text.indexOf('### ', startIdx + 1);
    if (endIdx === -1) endIdx = text.length;
    
    const section = text.substring(startIdx, endIdx);
    const regex = /- \[(.*?)\]\(https:\/\/github\.com\/openclaw\/skills\/tree\/main\/skills\/(.*?)\)/g;
    const slugs = [];
    let match;
    while ((match = regex.exec(section)) !== null) {
      slugs.push(match[1]);
    }
    results[cat] = slugs;
  });
  
  console.log(JSON.stringify(results));
}

run();
