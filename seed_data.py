"""
Root wrapper script to execute backend/seed_data.py.
AgentCare — Type-2 Diabetes Decision Support System.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend"))

from backend.seed_data import seed_database

if __name__ == "__main__":
    seed_database()
