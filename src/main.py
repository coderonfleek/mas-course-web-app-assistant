import argparse

from src.cli import run_cli

def main():
    """Main entry point with argument parsing"""

    parser = argparse.ArgumentParser(
        description="Web App Troubleshooting Assistant - Debug web apps with AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m src.main              Start interactive CLI
  python -m src.main --help       Show this help message

Environment Variables:
  OPENAI_API_KEY          Your OpenAI API key
  ANTHROPIC_API_KEY       Your Anthropic API key (optional)
  LLM_PROVIDER            Choose "openai" or "anthropic" (default: openai)
  OPENAI_MODEL            OpenAI model to use (default: gpt-4o)
  ANTHROPIC_MODEL         Anthropic model to use (default: claude-sonnet-4-20250514)

For more information, see README.md
        """
    )

    parser.add_argument(
        "--version",
        action="version",
        version="Web App Troubleshooting Assistant v1.0.0"
    )

    args = parser.parse_args()

    run_cli()

if __name__ == "__main__":
    main()