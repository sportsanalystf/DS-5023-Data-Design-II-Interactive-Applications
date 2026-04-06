#!/bin/bash
# LaxIQ — Push updates to GitHub
# Run this script from the folder where you cloned the repo:
#   cd path/to/DS-5023-Data-Design-II-Interactive-Applications
#   bash laxiq/push_to_github.sh

set -e

# Check we're in the right repo
if [ ! -d "laxiq" ] || [ ! -d ".git" ]; then
    echo "❌ Please run this from the root of your DS-5023-Data-Design-II-Interactive-Applications repo."
    echo "   cd path/to/DS-5023-Data-Design-II-Interactive-Applications"
    echo "   bash laxiq/push_to_github.sh"
    exit 1
fi

echo "📦 Staging all laxiq changes..."
git add laxiq/Home.py laxiq/analytics.py laxiq/style.py laxiq/pages/1_Game_Analysis.py laxiq/pages/2_Player_Intelligence.py

# Add new assets folder
mkdir -p laxiq/assets
git add laxiq/assets/va_logo.png

echo "📝 Creating commit..."
git commit -m "Update LaxIQ dashboard: redesigned Game Analysis, sidebar logo, clickable schedule

- Redesigned Tab 2 (Players & Team Stats) with butterfly chart, dark quarter cards,
  player WPA influence chart, and stat cards with green/red highlight logic
- Fixed WPA calculation: goals now use real logistic WP shift instead of 0.0
- Fixed Game Comparison tab NaN crash with consistent metrics across all 156 combos
- Fixed white text on light backgrounds across all charts and tabs
- Added Virginia Lacrosse helmet logo to sidebar (transparent background, 180px)
- Removed duplicate sidebar navigation, kept custom page_link nav
- Made schedule game rows clickable - navigates directly to Game Analysis
- Synthesized PBP data for Maryland (142 events) and Florida State (135 events)
- Added CSS fixes for selectbox visibility and tab styling

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"

echo "🚀 Pushing to GitHub..."
git push origin main

echo "✅ Done! Changes are live at:"
echo "   https://github.com/sportsanalystf/DS-5023-Data-Design-II-Interactive-Applications/tree/main/laxiq"
