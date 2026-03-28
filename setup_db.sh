#!/bin/bash

# Script to set up PostgreSQL for CUROVA development
# This script creates the database and user for local development

echo "=========================================="
echo "PostgreSQL Setup for CUROVA"
echo "=========================================="
echo ""

# Create database
echo "Creating database 'curova_db'..."
sudo -u postgres psql << EOF
CREATE DATABASE IF NOT EXISTS curova_db;
\q
EOF

echo ""
echo "Creating user 'curova_user' with password 'postgres'..."
sudo -u postgres psql << EOF
CREATE USER IF NOT EXISTS curova_user WITH PASSWORD 'postgres';
\q
EOF

echo ""
echo "Granting privileges..."
sudo -u postgres psql << EOF
GRANT ALL PRIVILEGES ON DATABASE curova_db TO curova_user;
\q
EOF

echo ""
echo "=========================================="
echo "Verifying setup..."
echo "=========================================="
echo ""

# Test connection
echo "Testing connection as curova_user..."
PGPASSWORD=postgres psql -U curova_user -h 127.0.0.1 -d curova_db -c "SELECT version();"

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ SUCCESS: Database and user are set up correctly!"
else
    echo ""
    echo "✗ FAILED: Could not connect to database"
    echo "  Check that PostgreSQL is running and credentials are correct"
fi

echo ""
echo "=========================================="
