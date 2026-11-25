import asyncio
import sys

from .team import run
from .tools.sandbox_tools import reset_sandbox


requirements = """
A simple account management system for a trading simulation platform.
The system should allow users to create an account, deposit funds, and withdraw funds.
The system should allow users to record that they have bought or sold shares, providing a quantity.
The system should calculate the total value of the user's portfolio, and the profit or loss from the initial deposit.
The system should be able to report the holdings of the user at any point in time.
The system should be able to report the profit or loss of the user at any point in time.
The system should be able to list the transactions that the user has made over time.
The system should prevent the user from withdrawing funds that would leave them with a negative balance, or
 from buying more shares than they can afford, or selling shares that they don't have.
 The system has access to a function get_share_price(symbol) which returns the current price of a share, and includes a test implementation that returns fixed prices for AAPL, TSLA, GOOGL.
"""


def main():
    try:
        print("=== Engineering Team ===")
        print(f"Requirements:\n{requirements.strip()}\n")
        reset_sandbox()
        result = asyncio.run(run(requirements))
        print("\n" + "=" * 60)
        print("=== DESIGN ===")
        print("=" * 60)
        print(result["design"])
        print("\n" + "=" * 60)
        print("=== CODE ===")
        print("=" * 60)
        print(result["code"])
        print("\n" + "=" * 60)
        print("=== FRONTEND ===")
        print("=" * 60)
        print(result["frontend"])
        print("\n" + "=" * 60)
        print("=== TEST ===")
        print("=" * 60)
        print(result["test"])
    except Exception as e:
        print(f"An error occurred while running the team: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
