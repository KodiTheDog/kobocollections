#!/usr/bin/env python3
import subprocess, json, sys, re

LIB = "Put a path in here"      # Your library path
COL_LOOKUP = "collections"                     # Your custom column (lookup name, not label)
PROCESSED_COL = "processed"                    # Yes/No column to mark processed books
TITLE_PREFIX_ON_DEVICE = True                  # True: update Calibre title with series number

def run_db(args):
    cmd = ["calibredb", "--with-library", LIB] + args
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        print(f"ERROR: {' '.join(cmd)}\n{p.stderr.strip() or p.stdout.strip()}", file=sys.stderr)
        sys.exit(1)
    return p.stdout

def get_collection_path(tags):
    """
    Returns the collection path from tags. Supports:
      - #KB Something/Path  (single tag)
      - #KB, Tag1, Tag2, ..., #KB  (delimited group)
    """
    collecting = False
    parts = []
    for t in tags:
        if t == "#KB":
            if collecting:
                break   # stop collecting at second #KB
            else:
                collecting = True
                continue
        if t.startswith("#KB "):
            # single tag style: use the string after '#KB '
            return t[4:].strip()
        if collecting:
            # Split on commas in tag and collect parts
            parts.extend(p.strip() for p in t.split(",") if p.strip())
    if parts:
        return "/".join(parts)
    return ""

def get_series_info(book):
    """Return (series_name, series_index) or (None, None) if not in series."""
    s = book.get("series")
    idx = book.get("series_index")
    # Only return if both are non-empty and idx is a number
    if s and idx not in (None, "", "None"):
        try:
            idxnum = int(float(idx))
            return s, f"{idxnum:02d}"
        except Exception:
            pass
    return None, None

def fix_title_prefix(title, sidx):
    """
    Remove any leading NN - from title, then prefix with correct sidx.
    If sidx is None or empty, returns title as-is.
    """
    if not sidx:
        # Not in series, return unmodified (strip any leftover prefix)
        return re.sub(r"^\d+\s*-\s*", "", title)
    prefix = f"{sidx} - "
    # Remove existing prefix like NN - (only once)
    stripped_title = re.sub(r"^\d+\s*-\s*", "", title)
    return f"{prefix}{stripped_title}"

def main():
    # Add 'custom_column:processed' to field list for Yes/No marker
    fields = f"id,title,tags,series,series_index,custom_column:{PROCESSED_COL}"
    data = run_db([
        "list", "--fields", fields,
        "--for-machine"
    ])
    books = json.loads(data)
    for book in books:
        bid = str(book["id"])
        processed = book.get(f"custom_column:{PROCESSED_COL}", "")
        if processed.lower() == "yes":
            print(f"Book {bid}: already processed, skipping.")
            continue

        tags = book.get("tags", [])
        path = get_collection_path(tags)
        orig_title = book.get("title", "")
        series, sidx = get_series_info(book)

        # Default: no collection, no title change
        collections = []
        new_title = orig_title

        # Build the collection column
        if path:
            # Path from #KB tags, possibly with series
            if series:
                collection = f"{path}/{series}"
                collections = [collection]
            else:
                collections = [path]
        else:
            collections = []

        # Title renaming: only if book is in a series
        if TITLE_PREFIX_ON_DEVICE:
            expected_title = orig_title
            if series and sidx:
                # Ensure only a single correct prefix
                new_title = fix_title_prefix(orig_title, sidx)
                if orig_title != new_title:
                    run_db([
                        "set_metadata", bid, "--field", f"title:{new_title}"
                    ])
                    print(f"Book {bid}: title changed to '{new_title}'")
                else:
                    print(f"Book {bid}: title prefix OK")
            else:
                # Not in series: strip any prefix accidentally left
                new_title = fix_title_prefix(orig_title, None)
                if orig_title != new_title:
                    run_db([
                        "set_metadata", bid, "--field", f"title:{new_title}"
                    ])
                    print(f"Book {bid}: title cleaned to '{new_title}'")

        # Write to custom column
        value = ";".join(collections) if collections else ""
        print(f"Book {bid}: writing {COL_LOOKUP} → {value!r}")
        run_db([
            "set_custom", COL_LOOKUP, bid, value
        ])

        # Mark as processed
        run_db([
            "set_custom", PROCESSED_COL, bid, "Yes"
        ])

if __name__ == "__main__":
    main()

