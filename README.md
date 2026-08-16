# Rashik Lab

`lab.rashik.org` is the public technology and capability archive for **Rashik — The Awakening**. It documents selected organisation-level projects, engineering decisions, and verified public evidence links in Bengali.

The current founder and author profile is [G. K. M. Jarif Ur Rahim](https://jarifurrahim.one/). This archive is a supporting project surface, not a replacement for the primary portfolio or an active control system for any other website.

## Publishing

GitHub Pages deploys the repository root from the `main` branch to `lab.rashik.org`. Before committing a change, build the static CSS and run:

```bash
bash scripts/validate-static-site.sh
```

The public archive must preserve the following rules:

1. Every material project claim must have a first-party live, GitHub, DOI, or official verification destination where one exists.
2. Historical projects must be labeled as historical; they must not imply active access to other systems.
3. Founder attribution must remain factual and restrained.
4. `robots.txt`, `sitemap.xml`, canonical metadata, and organisation schema must remain aligned with `https://lab.rashik.org/`.
