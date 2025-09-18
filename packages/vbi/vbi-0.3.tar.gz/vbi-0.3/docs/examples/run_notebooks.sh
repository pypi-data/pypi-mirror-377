#!/usr/bin/env bash
set -euo pipefail

# Simple runner: execute *.ipynb in current directory, optionally filtered by name substrings.

OUTPUT_DIR="executed_notebooks"
LOG_FILE="notebook_execution_log.txt"

print_help() {
  cat <<EOF
Usage: ./run_notebooks.sh [patterns]

Run all Jupyter notebooks (*.ipynb) in the current directory,
saving executed copies into $OUTPUT_DIR/ (originals remain untouched).

Arguments:
  patterns    Optional substrings to filter notebook names.
              You can separate multiple patterns by space or comma.
              Matching is case-insensitive.

Examples:
  ./run_notebooks.sh           # run all notebooks
  ./run_notebooks.sh numba     # run only notebooks with "numba" in name
  ./run_notebooks.sh numba,cpp # run notebooks with "numba" OR "cpp"
  ./run_notebooks.sh numba cpp torch  # same, with spaces

Options:
  -h, --help   Show this help and exit
EOF
}

# ---------------- CLI parsing ----------------
if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  print_help
  exit 0
fi

# Collect patterns from args (comma- or space-separated)
patterns_csv="${*:-}"
patterns_csv="${patterns_csv//,/ }"
read -r -a PATTERNS <<< "$patterns_csv"

# ---------------- Notebook discovery ----------------
mapfile -t ALL_NBS < <(find . -maxdepth 1 -type f -name '*.ipynb' -printf '%f\n' | sort)

TARGETS=()
for nb in "${ALL_NBS[@]}"; do
  if ((${#PATTERNS[@]} == 0)); then
    TARGETS+=("$nb")
  else
    nb_lc="${nb,,}"
    for p in "${PATTERNS[@]}"; do
      [[ -z "$p" ]] && continue
      if [[ "$nb_lc" == *"${p,,}"* ]]; then
        TARGETS+=("$nb")
        break
      fi
    done
  fi
done

if ((${#TARGETS[@]} == 0)); then
  echo "No notebooks matched."
  if ((${#PATTERNS[@]} > 0)); then
    echo "Patterns: ${PATTERNS[*]}"
  fi
  exit 1
fi

# ---------------- Execution ----------------
mkdir -p "$OUTPUT_DIR"
echo "Notebook Execution Log - $(date)" > "$LOG_FILE"
echo "Output directory: $OUTPUT_DIR" >> "$LOG_FILE"
echo "Patterns: ${patterns_csv:-<none>} " >> "$LOG_FILE"
echo >> "$LOG_FILE"

echo "Starting notebook execution..."
echo "================================"
echo "Selected notebooks (${#TARGETS[@]}):"
for t in "${TARGETS[@]}"; do
  echo "  - $t"
done
echo "================================"

successful=0
failed=0
total_notebooks=${#TARGETS[@]}

for notebook in "${TARGETS[@]}"; do
  echo "Running: $notebook"
  echo "Running: $notebook" >> "$LOG_FILE"

  base="${notebook%.ipynb}"
  output_file="${base}_executed"

  if jupyter nbconvert --to notebook --execute --output-dir "$OUTPUT_DIR" --output "$output_file" "$notebook" 2>>"$LOG_FILE"; then
    echo "✓ SUCCESS: $notebook"
    echo "✓ SUCCESS: $notebook" >> "$LOG_FILE"
    successful=$((successful+1))
  else
    echo "✗ FAILED:  $notebook"
    echo "✗ FAILED:  $notebook" >> "$LOG_FILE"
    failed=$((failed+1))
  fi
  echo "---" >> "$LOG_FILE"
  echo
done

echo "================================"
echo "Execution Summary:"
echo "Total notebooks: $total_notebooks"
echo "Successful: $successful"
echo "Failed: $failed"
echo "Executed notebooks saved to: $OUTPUT_DIR/"
echo "Log saved to: $LOG_FILE"

{
  echo
  echo "SUMMARY:"
  echo "Total notebooks: $total_notebooks"
  echo "Successful: $successful"
  echo "Failed: $failed"
} >> "$LOG_FILE"

echo "Done!"
