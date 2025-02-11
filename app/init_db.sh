#!/bin/bash

# Database configuration
DB_NAME="ecommerce_db"
SQL_FILE="schema.sql"

# Check if PostgreSQL is running
if ! command -v psql &> /dev/null; then
    echo "PostgreSQL could not be found. Please install PostgreSQL first."
    exit 1
fi

# Create database
echo "Creating database '$DB_NAME'..."
createdb "$DB_NAME"

# Execute schema script
echo "Initializing schema..."
psql -d "$DB_NAME" -f "$SQL_FILE"

echo "Database initialization complete!"