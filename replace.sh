#!/bin/bash
# Replace all "pyrogram" with "pyrogram" in the entire repo

echo "Replacing 'pyrogram' with 'pyrogram'..."
grep -rl "pyrogram" . | xargs sed -i 's/pyrogram/pyrogram/g'

echo "✅ Replacement complete!"
