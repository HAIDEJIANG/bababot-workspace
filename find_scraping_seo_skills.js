const fs = require('fs');

async function run() {
  const response = await fetch('https://raw.githubusercontent.com/VoltAgent/awesome-openclaw-skills/main/README.md');
  const text = await response.text();
  
  const regex = /- \[(.*?)\]\((.*?)\)(?: - (.*))?/g;
  const targetSkills = [];
  let match;
  
  const keywords = [
    'browser', 'automation', 'scrape', 'crawl', 'scraping', 
    'data extraction', 'data capture', 'data grabbing',
    'seo', 'search engine optimization', 'keywords',
    'form', 'auto-fill', 'form filling'
  ];
  
  while ((match = regex.exec(text)) !== null) {
    const slug = match[1];
    const description = match[3] || "";
    const combinedText = (slug + " " + description).toLowerCase();
    
    if (keywords.some(k => combinedText.includes(k))) {
      targetSkills.push(slug);
    }
  }
  
  console.log(JSON.stringify([...new Set(targetSkills)]));
}

run();
