const fs = require('fs');

async function run() {
  const response = await fetch('https://raw.githubusercontent.com/VoltAgent/awesome-openclaw-skills/main/README.md');
  const text = await response.text();
  
  // Regex to find skills and their descriptions
  // Format: - [slug](url) - description
  const regex = /- \[(.*?)\]\((.*?)\)(?: - (.*))?/g;
  const linkedinSkills = [];
  let match;
  
  while ((match = regex.exec(text)) !== null) {
    const slug = match[1];
    const url = match[2];
    const description = match[3] || "";
    
    if (slug.toLowerCase().includes('linkedin') || 
        slug.toLowerCase().includes('inkedin') || 
        description.toLowerCase().includes('linkedin') ||
        description.toLowerCase().includes('inkedin')) {
      linkedinSkills.push(slug);
    }
  }
  
  console.log(JSON.stringify([...new Set(linkedinSkills)]));
}

run();
