"""CLI entry point for the paper-to-notebook tool (Azure Only)."""
import argparse
import sys
from pathlib import Path
from paper_to_notebook.core.pipeline import run_pipeline
from paper_to_notebook.config import DEFAULT_MODEL


def main():
    parser = argparse.ArgumentParser(description="Convert a research paper PDF to a Jupyter Notebook using Azure OpenAI.")
    parser.add_argument("pdf", help="Path to the research paper PDF file")
    parser.add_argument("-o", "--output", help="Output path for the .ipynb file", default="generated_notebook.ipynb")
    parser.add_argument("-m", "--model", help=f"Azure deployment name (default: {DEFAULT_MODEL})", default=DEFAULT_MODEL)
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        print(f"Error: PDF file not found: {args.pdf}")
        sys.exit(1)

    print(f"Propelling conversion for {pdf_path.name} using Azure OpenAI...")
    
    try:
        nb_bytes = run_pipeline(
            pdf_source=str(pdf_path),
            model=args.model,
            verbose=args.verbose
        )
        
        output_path = Path(args.output)
        output_path.write_bytes(nb_bytes)
        print(f"\nSuccess! Notebook saved to {output_path}")
        
    except Exception as e:
        print(f"\nError during pipeline: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Add src to path if running locally
    src_path = str(Path(__file__).parent / "src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    main()
