import argparse
from agents.orchestrator import build_intelsync_workflow

def main():
    parser = argparse.ArgumentParser(
        description="Run the IntelSync multi-agent market intelligence pipeline."
    )
    parser.add_argument(
        "--config-dir", type=str, default="config/",
        help="Path to your agents' YAML configuration files."
    )
    args = parser.parse_args()

    # Build and run the workflow
    workflow = build_intelsync_workflow()
    workflow.run(config_dir=args.config_dir)

if __name__ == "__main__":
    main()