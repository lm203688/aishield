#!/bin/bash
set -e

echo "=== Publishing @aishield/mcp-server to npm ==="

# Check login
if ! npm whoami 2>/dev/null; then
    echo "ERROR: Not logged in to npm. Run: npm login"
    exit 1
fi

# Build
echo "Building TypeScript..."
cd mcp-server
npm install
npm run build

# Dry run
echo "Dry run publish..."
npm publish --dry-run

# Publish
echo "Publishing..."
npm publish --access public

echo "Done! Install with: npx @aishield/mcp-server"