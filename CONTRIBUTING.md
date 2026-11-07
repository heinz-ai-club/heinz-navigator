# How we work in this repo

## The one rule

**Never push straight to `main`.** Every change goes through a pull request.

```bash
git checkout main
git pull
git checkout -b your-name/short-description   # e.g. minwoo/retrieval-v1
# ...make your changes...
git add .
git commit -m "Add first retrieval version"
git push -u origin your-name/short-description
```

Then open a pull request on GitHub and ask one teammate to review it. Once approved, merge it.

On the public repos, GitHub enforces this. On the private repos, it is a team rule.

## Keys and secrets

- Your project's AI key lives only in `.env`, which git ignores.
- Never put a key in code, notebooks, screenshots, Slack, or a pull request.
- If a key leaks, tell your project lead right away. It can be disabled in seconds.

## AI usage

- Use `from haic import ask`. It only allows GPT-6 Luna (`"luna"`) and Claude Haiku 5.5 (`"haiku"`).
- Your project has a monthly spending cap. Test with small inputs first.
- Keep reasoning effort at the default (`"low"`) unless a task truly needs more.

## Getting help

Ask your project lead first. They bring anything that needs a decision to Trav.
