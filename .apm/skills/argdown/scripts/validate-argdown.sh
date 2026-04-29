#!/usr/bin/env bash
# validate-argdown.sh — Basic syntax validation for Argdown files
# Usage: bash scripts/validate-argdown.sh <file.argdown>

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

errors=0
warnings=0

error() { echo -e "${RED}ERROR:${NC} $1"; ((errors++)); }
warn()  { echo -e "${YELLOW}WARN:${NC} $1"; ((warnings++)); }
ok()    { echo -e "${GREEN}OK:${NC} $1"; }

if [ $# -eq 0 ]; then
    echo "Usage: bash validate-argdown.sh <file.argdown>"
    echo "Performs basic syntax validation on an Argdown file."
    exit 1
fi

FILE="$1"

if [ ! -f "$FILE" ]; then
    error "File not found: $FILE"
    exit 1
fi

# Check file extension
if [[ "$FILE" != *.argdown ]]; then
    warn "File does not have .argdown extension: $FILE"
fi

CONTENT=$(cat "$FILE")
LINE_COUNT=$(wc -l < "$FILE" | tr -d ' ')

echo "Validating: $FILE ($LINE_COUNT lines)"
echo "---"

# Check for frontmatter
if echo "$CONTENT" | head -1 | grep -q "^==="; then
    # Find closing ===
    CLOSE_LINE=$(echo "$CONTENT" | tail -n +2 | grep -n "^===" | head -1 | cut -d: -f1)
    if [ -z "$CLOSE_LINE" ]; then
        error "Frontmatter opened with === but never closed"
    else
        ok "Frontmatter block found (lines 1-$((CLOSE_LINE + 1)))"
    fi
fi

# Check for statements with titles
TITLED_STATEMENTS=$(grep -c '^\[' "$FILE" 2>/dev/null || true)
if [ "$TITLED_STATEMENTS" -gt 0 ]; then
    ok "Found $TITLED_STATEMENTS titled statement(s)"
else
    warn "No titled statements found (lines starting with [Title]:)"
fi

# Check for arguments
ARGUMENTS=$(grep -c '^<' "$FILE" 2>/dev/null || true)
if [ "$ARGUMENTS" -gt 0 ]; then
    ok "Found $ARGUMENTS argument reference(s)/definition(s)"
else
    warn "No arguments found (lines starting with <Title>)"
fi

# Check for relations
RELATIONS=$(grep -cE '^\s+((\+>)|(\->)|(\_>)|(<\+)|(<\-)|(<\_)|(><))' "$FILE" 2>/dev/null || true)
if [ "$RELATIONS" -gt 0 ]; then
    ok "Found $RELATIONS relation(s)"
fi

# Check for PCS (premise-conclusion structures)
PCS_PREMISES=$(grep -cE '^\s*\([0-9]+\)' "$FILE" 2>/dev/null || true)
PCS_INFERENCES=$(grep -cE '^\s*-{4,}' "$FILE" 2>/dev/null || true)
if [ "$PCS_PREMISES" -gt 0 ]; then
    ok "Found $PCS_PREMISES PCS premise(s) and $PCS_INFERENCES inference line(s)"
fi

# Check for common mistakes

# Titled statement without colon
while IFS= read -r line; do
    lineno=$(echo "$line" | cut -d: -f1)
    # Match lines that start with [Something] but don't have a colon after the bracket
    text=$(echo "$line" | cut -d: -f2-)
    if echo "$text" | grep -qE '^\[.+\][^:]' 2>/dev/null; then
        # Only warn if it's not a reference in a relation context
        if ! echo "$text" | grep -qE '^\s+((\+>)|(\->)|(\_>)|(<\+)|(<\-)|(<\_)|(><))' 2>/dev/null; then
            warn "Line $lineno: Titled statement may be missing colon after [Title]"
        fi
    fi
done < <(grep -nE '^\[.+\][^:\]]' "$FILE" 2>/dev/null || true)

# Argument definition without colon
while IFS= read -r line; do
    lineno=$(echo "$line" | cut -d: -f1)
    text=$(echo "$line" | cut -d: -f2-)
    if echo "$text" | grep -qE '^<.+>[^:]' 2>/dev/null; then
        if ! echo "$text" | grep -qE '^\s+((\+>)|(\->)|(\_>)|(<\+)|(<\-)|(<\_)|(><))' 2>/dev/null; then
            # This might be a reference, which is fine — only warn if it has trailing text
            trailing=$(echo "$text" | sed 's/^<[^>]*>//' | tr -d '[:space:]')
            if [ -n "$trailing" ]; then
                warn "Line $lineno: Argument may be missing colon after <Title>"
            fi
        fi
    fi
done < <(grep -nE '^<.+>[^:\>]' "$FILE" 2>/dev/null || true)

# Check for headings
HEADINGS=$(grep -cE '^#{1,6} ' "$FILE" 2>/dev/null || true)
if [ "$HEADINGS" -gt 0 ]; then
    ok "Found $HEADINGS heading(s)"
fi

# Check for tags
TAGS=$(grep -coE '#[a-z][a-z0-9-]*' "$FILE" 2>/dev/null || true)
if [ "$TAGS" -gt 0 ]; then
    ok "Found $TAGS tag usage(s)"
fi

# Summary
echo "---"
if [ "$errors" -eq 0 ] && [ "$warnings" -eq 0 ]; then
    echo -e "${GREEN}✓ Validation passed — no issues found${NC}"
elif [ "$errors" -eq 0 ]; then
    echo -e "${YELLOW}⚠ Validation passed with $warnings warning(s)${NC}"
else
    echo -e "${RED}✗ Validation failed — $errors error(s), $warnings warning(s)${NC}"
    exit 1
fi
