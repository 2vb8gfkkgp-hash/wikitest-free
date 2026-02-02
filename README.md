# wikitest-free

Consent-based Wikipedia-style search demo for stage mentalism. This project logs audience search
queries (with explicit permission) and lets the performer see them live.

## Features
- Audience search page that looks and feels like a mini Wikipedia viewer.
- Performer dashboard with a live feed of search terms.
- Optional push notifications via [ntfy.sh](https://ntfy.sh/) so you can receive alerts on phone,
  Apple Watch (via iOS notifications), or laptop.

## Getting started

```bash
npm install
npm start
```

Visit:
- `http://localhost:3000/` for the audience view.
- `http://localhost:3000/performer.html` for the performer dashboard.

## Optional push notifications

1. Create a topic name on ntfy.sh (e.g., `wikitest-demo-123`).
2. Subscribe to that topic in the ntfy mobile app or browser.
3. Start the server with the topic:

```bash
NTFY_TOPIC=wikitest-demo-123 npm start
```

Every logged search triggers a push notification.

## Responsible use
Only use this demo with explicit consent from participants, and follow Wikipedia's usage and
licensing guidelines when displaying its content.
