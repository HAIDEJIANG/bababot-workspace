# Reactive Resume Schema Reference
The complete JSON Schema is available at: https://rxresu.me/schema.json

This reference provides key structural information for generating valid resume data.

## Top-Level Structure
```json
{
 "picture": { ... },
 "basics": { ... },
 "summary": { ... },
 "sections": { ... },
 "customSections": [ ... ],
 "metadata": { ... }
}
```

## Picture Configuration
"hidden": false,
 "url": "https://example.com/photo.jpg",
 "size": 80,
 "rotation": 0,
 "aspectRatio": 1,
 "borderRadius": 0,
 "borderColor": "rgba(0, 0, 0, 0.5)",
 "borderWidth": 0,
 "shadowColor": "rgba(0, 0, 0, 0.5)",
 "shadowWidth": 0

## Basics
"name": "John Doe",
 "headline": "Senior Software Engineer",
 "email": "john@example.com",
 "phone": "+1 (555) 123-4567",
 "location": "San Francisco, CA",
 "website": { "url": "https://johndoe.com", "label": "Portfolio" },
 "customFields": []

## Summary
"title": "Summary",
 "columns": 1,
 "content": "<p>HTML-formatted summary content here.</p>"

## Sections
All sections share a common structure:

 "title": "Section Title",
 "items": [ ... ]

### Experience Items
"id": "uuid-here",
 "company": "Acme Corp",
 "position": "Software Engineer",
 "period": "Jan 2020 - Present",
 "website": { "url": "https://acme.com", "label": "" },
 "description": "<ul><li>Built scalable microservices</li><li>Led team of 5 engineers</li></ul>"

### Education Items
"school": "Stanford University",
 "degree": "Bachelor of Science",
 "area": "Computer Science",
 "grade": "3.8 GPA",
 "location": "Stanford, CA",
 "period": "2012 - 2016",
 "website": { "url": "", "label": "" },
 "description": ""

### Skills Items
"icon": "",
 "name": "JavaScript",
 "proficiency": "Expert",
 "level": 5,
 "keywords": ["React", "Node.js", "TypeScript"]

Level: 0-5 (0 hides the visual indicator)

### Project Items
"name": "Open Source Project",
 "period": "2023 - Present",
 "website": { "url": "https://github.com/user/project", "label": "GitHub" },
 "description": "<p>Description of the project and your contributions.</p>"

### Language Items
"language": "English",
 "fluency": "Native",
 "level": 5

Fluency examples: Native, Fluent, Conversational, Basic, or CEFR levels (A1-C2)

### Certification Items
"title": "AWS Solutions Architect",
 "issuer": "Amazon Web Services",
 "date": "March 2023",
 "website": { "url": "https://aws.amazon.com/certification/", "label": "Verify" },

### Award Items
"title": "Employee of the Year",
 "awarder": "Acme Corp",
 "date": "2022",

### Publication Items
"title": "Research Paper Title",
 "publisher": "IEEE",
 "date": "2021",
 "website": { "url": "https://doi.org/...", "label": "DOI" },

### Volunteer Items
"organization": "Local Food Bank",
 "period": "2020 - Present",
 "description": "<p>Volunteer activities and impact.</p>"

### Interest Items
"name": "Photography",
 "keywords": ["Landscape", "Portrait", "Street"]

### Reference Items
"name": "Jane Smith",
 "position": "Engineering Manager at Acme Corp",
 "website": { "url": "https://linkedin.com/in/janesmith", "label": "LinkedIn" },
 "phone": "+1 (555) 987-6543",
 "description": "<p>Optional testimonial or quote.</p>"

### Profile Items (Social Links)
"icon": "linkedin-logo",
 "network": "LinkedIn",
 "username": "johndoe",
 "website": { "url": "https://linkedin.com/in/johndoe", "label": "" }

Icons use @phosphor-icons/web names. Common icons: `linkedin-logo`, `github-logo`, `twitter-logo`, `globe`

## Metadata

### Template Options
Available templates: `azurill`, `bronzor`, `chikorita`, `ditto`, `ditgar`, `gengar`, `glalie`, `kakuna`, `lapras`, `leafish`, `onyx`, `pikachu`, `rhyhorn`

### Layout Configuration
"sidebarWidth": 35,
 "pages": [
 "fullWidth": false,
 "main": ["profiles", "summary", "experience", "education", "projects"],
 "sidebar": ["skills", "languages", "certifications", "interests"]
 ]

Section IDs for layout: `profiles`, `experience`, `education`, `projects`, `skills`, `languages`, `interests`, `awards`, `certifications`, `publications`, `volunteer`, `references`, `summary`

### Page Settings
"gapX": 4,
 "gapY": 6,
 "marginX": 14,
 "marginY": 12,
 "format": "a4",
 "locale": "en-US",
 "hideIcons": false

Format options: `a4`, `letter`

### Design Settings
"colors": {
 "primary": "rgba(220, 38, 38, 1)",
 "text": "rgba(0, 0, 0, 1)",
 "background": "rgba(255, 255, 255, 1)"
 },
 "level": {
 "icon": "star",
 "type": "circle"

Level types: `hidden`, `circle`, `square`, `rectangle`, `rectangle-full`, `progress-bar`, `icon`

### Typography
"body": {
 "fontFamily": "IBM Plex Serif",
 "fontWeights": ["400", "500"],
 "fontSize": 10,
 "lineHeight": 1.5
 "heading": {
 "fontWeights": ["600"],
 "fontSize": 14,

Font family must be available on Google Fonts. Font weights: 100-900.

### CSS Customization
"enabled": false,
 "value": ""

## Custom Sections
Custom sections extend the base section structure with additional fields:

 "title": "Custom Section Title",
 "type": "experience",

The `type` field determines the item schema. Valid types: `profiles`, `experience`, `education`, `projects`, `skills`, `languages`, `interests`, `awards`, `certifications`, `publications`, `volunteer`, `references`

## UUID Generation
All `id` fields require valid UUIDs version 7. If available, use 'v7()' from the 'uuid' package to generate a valid UUID. Otherwise, fallback to generating a valid UUID v4 using crypto.randomUUID() from 'node' or the equivalent.

## HTML Content
Fields marked as "HTML-formatted string" accept basic HTML:
- `<p>` for paragraphs
- `<ul><li>` for bullet lists
- `<ol><li>` for numbered lists
- `<strong>` for bold
- `<em>` for italic
- `<a href="...">` for links

Keep formatting minimal for best rendering across templates.