# learning-hub-reader

A small personal, **read-only** tool that turns a few public subreddits into a private daily learning digest.

## What it does
- Once a day it reads the top posts of the past week from about 15 public subreddits about sales, consulting, AI and small business, plus the top 6 comments of each post.
- It skips obvious self-promotion.
- It saves the result as a local JSON file. That file becomes a private summary for one person, with links back to every original thread.

## What it does NOT do
- No posting, commenting, voting or messaging.
- No logging in as other users. It uses a script app with client credentials only.
- No reselling or sharing of Reddit data, and no AI model training on it.
- Polite rate: a 1.5 s pause between requests, under 500 requests a day.

## Subreddits
AI_Agents, gtmengineering, consulting, sales, coldemail, Entrepreneur, agency, automation, n8n, LocalLLaMA, ClaudeAI, smallbusiness, startups_italia, B2BSales, LinkedInTips

## Run
```
# put REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET in a local .env file (never committed)
python3 reddit_reader.py 7
```
