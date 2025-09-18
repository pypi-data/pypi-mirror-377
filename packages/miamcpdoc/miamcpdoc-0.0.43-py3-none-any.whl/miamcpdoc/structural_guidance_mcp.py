"""Structural Guidance Documentation MCP Server."""

from pathlib import Path

from miamcpdoc.main import create_server
from miamcpdoc.splash import SPLASH

def main():
    """Structural Guidance Documentation MCP Server."""
    # Search in __llms directory
    llms_dir = Path(__file__).parent.parent / "__llms"

    # Patterns to match structural guidance documents
    guidance_patterns = [
        "*digital-decision-making*",
        "*delayed-resolution-principle*",
        "*leadership*",
        "*managerial-moment-of-truth*"
    ]

    doc_sources = []

    if llms_dir.exists():
        for pattern in guidance_patterns:
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
        print("No structural guidance documents found.")
        return

    print(SPLASH)
    print("Loading Structural Guidance documentation...")
    for source in doc_sources:
        print(f"  - {source['name']}")

    server = create_server(doc_sources)
    server.run(transport="stdio")

if __name__ == "__main__":
    main()