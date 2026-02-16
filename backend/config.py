import os

# Mets ton token ici OU via variable d'environnement ADMIN_TOKEN
# PowerShell:
#   $env:ADMIN_TOKEN="BCZ-2026-SECRET"
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "BCZ-2026-SECRET")
