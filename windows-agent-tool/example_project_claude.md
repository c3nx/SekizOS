# Project: Example Web App

## Available Tools

### Windows Agent
This project can interact with Windows desktop:
- Screenshot: `win screenshot`
- Browser testing: `win ps "start chrome http://localhost:3000"`
- UI automation: `win click`, `win type`

### Testing Workflow
1. Start dev server: `npm run dev`
2. Open in Windows: `win ps "start chrome http://localhost:3000"`
3. Take screenshot: `win screenshot`
4. Interact with UI: `win click 500 300`

### Quick Actions
- Refresh browser: `win key F5`
- Open DevTools: `win key F12`
- Close window: `win key alt+F4`