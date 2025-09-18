"""Creative Orientation Documentation MCP Server."""

from miamcpdoc.main import create_server
from miamcpdoc.splash import SPLASH
from pathlib import Path

def main():
    """Creative Orientation Documentation MCP Server."""
    # Dynamically find the llms.txt file for creative orientation
    creative_frameworks_dir = Path(__file__).parent / "creative_frameworks"
    if not creative_frameworks_dir.exists():
        creative_frameworks_dir = Path(__file__).parent.parent / "__llms"

    # Find a suitable llms.txt or use a default
    llms_txt_path = next(creative_frameworks_dir.glob("*creative*.txt"), None)

    if not llms_txt_path:
        llms_txt_path = Path(__file__).parent.parent / "__llms" / "llms-creative-orientation.txt"

    doc_sources = [
        {
            "name": "CreativeOrientation",
            "llms_txt": str(llms_txt_path)
        }
    ]

    print(SPLASH)
    print("Loading Creative Orientation documentation...")
    server = create_server(doc_sources)
    server.run(transport="stdio")

if __name__ == "__main__":
    main()