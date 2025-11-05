#!/bin/bash
# Script: clean_demo_filenames.sh
# Purpose: Clean filenames inside Lesson-32.Helm/Demos by removing special characters and spaces
# Usage: Run inside Lesson-32.Helm/Demos

echo "🔍 Starting filename cleanup in $(pwd)..."

for f in *; do
  # Skip if not a file
  [ -f "$f" ] || continue
  
  # Skip Readme.md
  if [[ "$f" == "Readme.md" ]]; then
    continue
  fi

  # Build sanitized filename:
  # 1. Replace ":" and "," with "-"
  # 2. Replace spaces with "-"
  # 3. Remove special characters except . _ -
  # 4. Replace multiple dashes with one
  newname=$(echo "$f" | \
    sed -E 's/[:|,]/-/g' | \
    sed -E 's/ /-/g' | \
    sed -E 's/[^A-Za-z0-9._-]//g' | \
    sed -E 's/-+/-/g')

  # Only rename if name changes
  if [ "$f" != "$newname" ]; then
    echo "➡️  Renaming: '$f' → '$newname'"
    mv "$f" "$newname"
  fi
done

echo "✅ All demo filenames cleaned successfully!"
