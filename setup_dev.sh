#!/bin/bash
# Setup dev environment with Keycloak OIDC support.
# Prerequisites: Docker (for Keycloak), Python venv at .venv (via uv)

set -e

SETTINGS_FILE="src/shiftings/local_settings.py"
DEV_SETTINGS="src/shiftings/local_settings.dev.py"

if [ ! -f "$SETTINGS_FILE" ]; then
    cp "$DEV_SETTINGS" "$SETTINGS_FILE"
    echo "Created local_settings.py from dev template (OIDC enabled)"
else
    echo "local_settings.py already exists, skipping copy"
fi

./setup_db.sh

echo ""
echo "=========================================="
echo "  Dev setup complete!"
echo "=========================================="
echo ""
echo "Start Keycloak:  docker compose -f docker-compose.dev.yml up -d"
echo "Start Django:    .venv/bin/python src/manage.py runserver"
echo ""
echo "Keycloak admin:  http://localhost:8080       (admin / admin)"
echo "Shiftings:       http://127.0.0.1:8000       (SSO + local login)"
echo ""
echo "Keycloak users all have password: password"
echo ""
