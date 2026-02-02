# wikitest-free

Consent-based Wikipedia-style search demo for stage mentalism. This project generates temporary
audience links that display a Wikipedia-style mock page; audience searches are logged (with explicit
permission) so the performer can see them live.

## Features
- Temporary audience links that open a Wikipedia-style mock page.
- Performer dashboard with a live feed of search terms.
- Optional push notifications via [ntfy.sh](https://ntfy.sh/) so you can receive alerts on phone,
  Apple Watch (via iOS notifications), or laptop.

## Getting started

```bash
npm install
npm start
```

Visit:
- `http://localhost:3000/` to create a temporary audience link.
- `http://localhost:3000/performer.html` for the performer dashboard and live feed.

Share the generated link with a participant. The mock Wikipedia page posts searches back to the
performer feed.

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
