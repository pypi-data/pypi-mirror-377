"""Creative Frameworks Documentation MCP Server."""

import os
from pathlib import Path

from miamcpdoc.main import create_server
from miamcpdoc.splash import SPLASH

def main():
    """Creative Frameworks Documentation MCP Server."""
    # Search in __llms directory
    llms_dir = Path(__file__).parent.parent / "__llms"

    # Patterns to match creative framework documents
    creative_patterns = [
        "*creative*",
        "*narrative*",
        "*rise-framework*",
        "*structural-thinking*",
        "*structural-tension*",
        "*structural-distillation*",
        "*non-creative-orientation*"
    ]

    doc_sources = []

    if llms_dir.exists():
        for pattern in creative_patterns:
            # Find files matching each pattern
            matched_files = list(llms_dir.glob(pattern))

            for file_path in matched_files:
                # Skip directories and create clean names
                if file_path.is_file():
                    # Create a clean name from filename
                    clean_name = file_path.stem.replace("llms-", "").replace("-", " ").title()

                    doc_sources.append({
                        "name": clean_name,
                        "llms_txt": str(file_path)
                    })

    if not doc_sources:
        print("No creative framework documents found.")
        return

    print(SPLASH)
    print("Loading Creative Frameworks documentation...")
    for source in doc_sources:
        print(f"  - {source['name']}")

    server = create_server(doc_sources)
    server.run(transport="stdio")

if __name__ == "__main__":
    main()