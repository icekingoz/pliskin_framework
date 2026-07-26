#!/usr/bin/env bash
#
# Assemble the GitHub Pages site from a freshly generated Allure report.
#
#   assemble_allure_site.sh <report_dir> <gh_pages_dir> <site_dir> <run_number> [keep]
#
# Produces:
#   <site>/index.html      redirect to the newest report
#   <site>/latest/         newest report
#   <site>/<run_number>/   this run, archived
#   <site>/last-history/   history the *next* run reads to build trend graphs
#
# Older numbered runs are carried forward from the existing site and pruned to
# the newest `keep`. Everything is plain POSIX-ish shell so it runs identically
# on the CI runner and on a Mac.

set -euo pipefail

REPORT="${1:?report dir required}"
GH_PAGES="${2:?gh-pages checkout dir required}"
SITE="${3:?output site dir required}"
RUN="${4:?run number required}"
KEEP="${5:-30}"

rm -rf "$SITE"
mkdir -p "$SITE"

# --- carry forward previous runs --------------------------------------------
# Only numeric directories. Copying `latest/` forward would double the site
# size every run, and copying `.git` would confuse the publish step.
if [ -d "$GH_PAGES" ]; then
    for dir in "$GH_PAGES"/*/; do
        [ -d "$dir" ] || continue
        name="$(basename "$dir")"
        case "$name" in
            '' | *[!0-9]*) continue ;;
        esac
        cp -r "$dir" "$SITE/$name"
    done
fi

# --- add this run ------------------------------------------------------------
cp -r "$REPORT" "$SITE/$RUN"

# --- prune to the newest $KEEP ----------------------------------------------
# `head -n -N` would be shorter but it is a GNU extension; this works anywhere.
count="$(find "$SITE" -maxdepth 1 -type d -exec basename {} \; | grep -Ec '^[0-9]+$' || true)"
if [ "$count" -gt "$KEEP" ]; then
    remove=$((count - KEEP))
    find "$SITE" -maxdepth 1 -type d -exec basename {} \; \
        | grep -E '^[0-9]+$' \
        | sort -n \
        | sed -n "1,${remove}p" \
        | while IFS= read -r old; do
            rm -rf "${SITE:?}/${old:?}"
        done
fi

# --- latest ------------------------------------------------------------------
rm -rf "$SITE/latest"
cp -r "$REPORT" "$SITE/latest"

# --- history for the next run ------------------------------------------------
# This is the bit that makes trend graphs work: the next run copies this back
# into allure-results/ before generating, so Allure can see prior outcomes.
rm -rf "$SITE/last-history"
if [ -d "$REPORT/history" ]; then
    cp -r "$REPORT/history" "$SITE/last-history"
fi

# --- root redirect -----------------------------------------------------------
# Without this, the Pages root is a directory listing (or a 404).
cat > "$SITE/index.html" <<'HTML'
<!doctype html>
<meta charset="utf-8">
<meta http-equiv="refresh" content="0; url=./latest/">
<title>Test report</title>
<p><a href="./latest/">Latest test report</a></p>
HTML

echo "Site assembled at $SITE:"
ls -1 "$SITE"
