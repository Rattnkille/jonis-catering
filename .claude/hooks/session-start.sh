#!/bin/bash
set -euo pipefail

# SessionStart-Hook für Jonis Catering
# Installiert die Dev-Abhängigkeiten (htmlhint), damit der HTML-Linter
# in Claude-Code-Web-Sessions sofort einsatzbereit ist.

# Nur in der Remote-/Web-Umgebung ausführen, lokale Sessions nicht beeinflussen.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "$CLAUDE_PROJECT_DIR"

# npm install (nicht ci): nutzt den gecachten Container-State und ist idempotent.
npm install
