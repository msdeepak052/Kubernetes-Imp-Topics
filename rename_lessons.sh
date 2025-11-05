#!/bin/bash
# Script: rename_lessons.sh
# Purpose: Rename directories like "1. k8s-Architecture" → "Lesson-1.k8s-Architecture"
# Usage: Run from inside the repo root (e.g., ~/Kubernetes-Imp-Topics)

echo "🔍 Starting rename process..."

for d in [0-9]*; do
  if [ -d "$d" ]; then
    # Transform folder name: replace leading number. → Lesson-number. and remove spaces
    newname=$(echo "$d" | sed -E 's/^([0-9]+)\. ?/Lesson-\1./' | tr -d ' ')
    
    if [ "$d" != "$newname" ]; then
      echo "➡️  Renaming: '$d' → '$newname'"
      mv "$d" "$newname"
    fi
  fi
done

echo "✅ All matching folders have been renamed successfully!"
