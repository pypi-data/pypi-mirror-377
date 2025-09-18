"""Creative Frameworks Documentation MCP Server."""

import os
import fnmatch
from pathlib import Path
try:
    from importlib.resources import files
except ImportError:
    from importlib_resources import files

from miamcpdoc.main import create_server
from miamcpdoc.splash import SPLASH

def main():
    """Creative Frameworks Documentation MCP Server."""
    # Access package resources
    try:
        # Try to access bundled resources first
        llms_resources = files('miamcpdoc') / '__llms'

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

        if llms_resources.is_dir():
            # List all files in the __llms directory
            for resource_path in llms_resources.iterdir():
                if resource_path.is_file():
                    filename = resource_path.name

                    # Check if file matches any of our patterns
                    for pattern in creative_patterns:
                        if fnmatch.fnmatch(filename, pattern):
                            # Create a clean name from filename
                            clean_name = resource_path.stem.replace("llms-", "").replace("-", " ").title()

                            doc_sources.append({
                                "name": clean_name,
                                "llms_txt": str(resource_path)
                            })
                            break

    except Exception:
        # Fallback to filesystem path for development
        llms_dir = Path(__file__).parent.parent / "__llms"

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
                matched_files = list(llms_dir.glob(pattern))

                for file_path in matched_files:
                    if file_path.is_file():
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