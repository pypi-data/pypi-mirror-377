"""
AgentSpec CLI entry point for module execution.

This allows running AgentSpec as a module:
    python -m agentspec [args]
"""

import sys

from .cli.main import main

if __name__ == "__main__":
    sys.exit(main())
