import os
import gc
import argparse
import time
import logging  # Import logging module
from trello import TrelloClient
import pandas as pd
from dotenv import load_dotenv



# Configure logging
logging.basicConfig(
    filename="trello_integration_update.log",  # Log file name
    level=logging.INFO,  # Log level
    format="%(asctime)s - %(levelname)s - %(message)s"  # Log format
)

# Load environment variables
load_dotenv()

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Trello integration script.")
parser.add_argument("--board_name", required=True, help="Name of the Trello board.")
args = parser.parse_args()

# Name of elements of interest
board_name = args.board_name

# Initialize Trello client
cliente = TrelloClient(
    api_key=os.environ.get('TRELLO_API_KEY'),
    api_secret=os.environ.get('TRELLO_API_SECRET'),
    token=os.environ.get('TRELLO_TOKEN')
)

# Get the board
target_board = None
for b in cliente.list_boards():
    if b.name == board_name:
        target_board = b
        break

if not target_board:
    # Log an error if the board is not found
    logging.error(f"Board '{board_name}' not found.")
    raise ValueError(f"Board '{board_name}' not found.")

# Get the lists of the selected board
lists = cliente.get_board(board_name).list_lists()

# Create a dictionary to store the members