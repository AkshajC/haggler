# Demo script

Fill this in as you build. The demo is the whole game — plan it as carefully as the code.

## Pitch (memorize, 30 seconds)

> "We built Haggler — an AI agent that does what nobody wants to do: haggle with strangers online. You give it an item, it scouts Craigslist, eBay, and Facebook Marketplace, then messages five sellers in parallel and negotiates each one down. Here's what happened when we asked it to find a couch."

## Live demo flow (3 minutes)

1. **Setup shot** — show the dashboard, empty. Mention the architecture: scout + negotiator + messaging.
2. **Type the search** — "black mid-sized couch under $400 near San Ramon"
3. **Scout populates** — within 10 seconds, cards appear. Highlight the ranking ("we picked the 5 best").
4. **Negotiations start** — status badges flip from "pending" to "opening" to "offering". Open one card.
5. **Money shot** — pull up the full conversation transcript. Read 2-3 of the agent's messages aloud. The casual tone is the whole point — emphasize it.
6. **Result** — show final price next to asking price. "$280 from a $350 listing. Multiplied across five conversations."

## Backup plan

- If live demo breaks: have a saved transcript ready to screen-share.
- If the LLM API is slow: pre-run the search, replay the timeline.
- If the dashboard breaks: have a video recording at hand.

## What to emphasize

- The negotiation transcripts. Real people, real haggling, real savings.
- The parallelism. Five conversations at once is something humans can't do.
- The platform-agnostic design. Adding a new marketplace is one file.

## What to downplay

- It's a hackathon project, not a product. Don't oversell scale.
- ToS considerations are real but a conversation for later.

## Things to print/screenshot ahead of time

- [ ] Best conversation transcript, printed full-page
- [ ] Architecture diagram
- [ ] One-line pitch on a slide
