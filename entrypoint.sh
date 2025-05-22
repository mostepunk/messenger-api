#!/bin/bash
set -e

python -c "
from manage import logo
print('\n')
print(logo())
"

echo "-> Run migrations and init DB..."
echo "-> Alebmbic upgrade head..."
alembic upgrade head

if [ "$ENVIRONMENT" = "LOCAL" ]; then
    echo "-> ENVIRONMENT= $ENVIRONMENT. Fill DB with fake data..."
    python manage.py db --fill
else
    echo "-> Do not fill DB with fake data..."
fi

echo "-> Run server..."
exec python main.py
