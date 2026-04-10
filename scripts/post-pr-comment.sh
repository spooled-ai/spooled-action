#!/usr/bin/env bash
# Idempotent PR comment posting for Spooled AI Baseline Check.
# Searches for an existing comment with the marker, updates it if found,
# otherwise creates a new one. Prevents comment spam on repeated pushes.

set -euo pipefail

MARKER="<!-- spooled-baseline-check -->"
REPORT_FILE="ci-report/report.md"

if [ ! -f "$REPORT_FILE" ]; then
  echo "No report file found at $REPORT_FILE — skipping PR comment"
  exit 0
fi

BODY="${MARKER}
$(cat "$REPORT_FILE")"

# Find existing comment with our marker
EXISTING_COMMENT_ID=$(gh api \
  "repos/${REPO}/issues/${PR_NUMBER}/comments" \
  --paginate \
  --jq ".[] | select(.body | contains(\"${MARKER}\")) | .id" \
  2>/dev/null | head -1 || true)

if [ -n "$EXISTING_COMMENT_ID" ]; then
  echo "Updating existing comment $EXISTING_COMMENT_ID"
  gh api \
    "repos/${REPO}/issues/comments/${EXISTING_COMMENT_ID}" \
    --method PATCH \
    --field body="$BODY"
else
  echo "Creating new PR comment"
  gh pr comment "$PR_NUMBER" --repo "$REPO" --body "$BODY"
fi
