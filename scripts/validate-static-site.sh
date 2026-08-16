#!/usr/bin/env bash
set -euo pipefail

test -f index.html
test -f robots.txt
test -f sitemap.xml
test -f assets/styles.css
test -f assets/lucide.min.js

grep -q '<link rel="canonical" href="https://lab.rashik.org/">' index.html
grep -q 'Rashik - The Awakening' index.html
grep -q 'https://lab.rashik.org/sitemap.xml' robots.txt
grep -q 'https://lab.rashik.org/' sitemap.xml
grep -q 'https://github.com/JarifUrRahim/AgentOS' index.html
grep -q 'https://github.com/JarifUrRahim/NaBaB_AI' index.html

echo "Static showcase validation passed."
