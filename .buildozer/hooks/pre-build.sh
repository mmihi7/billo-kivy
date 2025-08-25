#!/bin/bash
echo "=== Running pre-build hook ==="

# Find and patch pyjnius_utils.pxi
find .buildozer -type f -path "*/pyjnius/jnius/jnius_utils.pxi" | while read -r pxi_file; do
    echo "Patching $pxi_file"
    # Replace long with int in isinstance checks
    sed -i 's/isinstance(\([^,]*\), *long)/isinstance(\1, int)/g' "$pxi_file"
    # Replace any remaining long with int
    sed -i 's/\([^a-zA-Z0-9_]\)long\([^a-zA-Z0-9_]\)/\1int\2/g' "$pxi_file"
done

exit 0
