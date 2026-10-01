# Abhinav Nair — Portfolio

Static single-page portfolio (`index.html`, no build step). Open the file in a browser or deploy the folder to Netlify.

## Features
- Project case-study modals (problem, approach, architecture, results, stack)
- Skills linked to the projects that prove them
- Interactive terminal (`help`, `ls`, `cat meme`, `sudo hire me`…)
- Command palette: `Ctrl/Cmd + K` or `/`
- Rotating role line in the hero
- Chatbot with a recruiter-mode summary; optional AWS Lambda + Bedrock backend (see `backend/`)
- Live GitHub repos via the public API
- Contact form (Netlify Forms)

## Editing content
Project case studies live in the `PROJECTS` object inside `index.html`. To add a project link, add it to that project's `links` array.

Resume: `Abhinav_EY_resume.pdf`
