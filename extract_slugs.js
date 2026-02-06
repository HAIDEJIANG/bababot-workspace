const fs = require('fs');

async function run() {
  const response = await fetch('https://raw.githubusercontent.com/VoltAgent/awesome-openclaw-skills/main/README.md');
  const text = await response.text();
  const regex = /- \[(.*?)\]\(https:\/\/github\.com\/openclaw\/skills\/tree\/main\/skills\/(.*?)\)/g;
  const slugs = [];
  let match;
  while ((match = regex.exec(text)) !== null) {
    // The slug for installation is actually the directory name in many cases, 
    // but the README says <skill-slug>. In ClawHub, the slug is usually the name in brackets or the path.
    // Let's assume the name in brackets is the slug.
    slugs.push(match[1]);
  }
  console.log(JSON.stringify(slugs));
}

run();
