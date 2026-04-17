# Wiki Log

Append-only chronological record of every wiki operation. Entry prefix is
`## [YYYY-MM-DD HH:MM] <op> | <title>` so the log stays `grep`-parseable:

```
grep "^## \[" research/wiki/log.md | tail -10
```

Valid `<op>` values: `ingest`, `query`, `lint`, `resolve`, `refactor`.
