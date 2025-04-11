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
    filename="trello_integration.log",  # Log file name
    level=logging.INFO,  # Log level
    format="%(asctime)s - %(levelname)s - %(message)s"  # Log format
)

# Load environment variables
load_dotenv()

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Trello integration script.")
parser.add_argument("--board_name", required=True, help="Name of the Trello board.")
parser.add_argument("--list_name", required=True, help="Name of the Trello list.")
parser.add_argument("--input_folder", default="input", help="Path to the input folder.")
args = parser.parse_args()

# Name of elements of interest
board_name = args.board_name
list_name = args.list_name

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
    logging.error(f"Board '{board_name}' not found.")
    raise ValueError(f"Board '{board_name}' not found.")

# Get the list
target_list = None
for l in target_board.list_lists():
    if l.name == list_name:
        target_list = l
        break

if not target_list:
    logging.error(f"List '{list_name}' not found.")
    raise ValueError(f"List '{list_name}' not found.")

# Create a dictionary to store the members
member_dict = {member.full_name: member.id for member in target_board.get_members()}

# Dictionary to reclassify PL members
mmbr_reclass_dict = {'PS': 'Pedro J Sanchez', 'GG': 'Gema Gomez'}

# Get the labels
labels = target_board.get_labels()
label_dict = {label.name: label for label in labels}

# Dictionary to reclassify the status labels
reclass_dict = {'H': 'HOT', 'W': 'WON', 'L': 'LOST'}

# Find the Excel file in the input folder
input_path = args.input_folder
file_path = [os.path.join(input_path, f) for f in os.listdir(input_path) if f.endswith('xlsm')][0]

# Load the Excel file as a DataFrame
df = pd.read_excel(
    file_path,
    sheet_name='Angebotsliste',
    header=9,
    converters={'Umsatz': float, 'FIRMA': str, 'Offer Nummer': str}
)

# Subset columns of interest
c_interest = ['Status', 'FIRMA', 'Projektname', 'Offer Nummer', 'Leistungsumfang', 'Umsatz', 'Angebotsland', 'Aufstellungsland', 'PL', 'SOLL-Kontakt:']
df_subset = df[c_interest]

# Remove empty rows
df_clean = df_subset.loc[(df_subset['Offer Nummer'].notna()) & (df_subset['Offer Nummer'] != '0')]

# Replace NaN and 0 values in specific fields
df_clean.loc[df_clean['FIRMA'].isna(), 'FIRMA'] = 'BLANKO'
df_clean.loc[df_clean['FIRMA'] == '0', 'FIRMA'] = 'BLANKO'
df_clean.loc[df_clean['Projektname'].isna(), 'Projektname'] = 'BLANKO'
df_clean.loc[df_clean['Projektname'] == '0', 'Projektname'] = 'BLANKO'
df_clean.loc[df_clean['Umsatz'].isna(), 'Umsatz'] = 0

# Reclassify the status values and member names
df_clean = df_clean.replace({'Status': reclass_dict, 'PL': mmbr_reclass_dict})

# Split the DataFrame into subsets of 100 rows
subsets = [df_clean.iloc[i:i + 100] for i in range(0, len(df_clean), 100)]

# Process each subset with a delay
for subset_index, subset in enumerate(subsets):
    logging.info(f"Processing subset {subset_index + 1} of {len(subsets)}...")
    for index, row in subset.iterrows():
        miembro = row['PL']
        etiqueta_nombre = row['Status']
        name_card = f"{row['FIRMA']}_{row['Offer Nummer']}_{row['Projektname']}"
        leistung = row['Leistungsumfang']
        umsatz = row['Umsatz']
        angebots = row['Angebotsland']
        aufstell = row['Aufstellungsland']
        text_desc = f"""**Leistungsumfang**: {leistung} \n**Angebotsland**: {angebots} \n**Aufstellungsland**: {aufstell}"""
        due_date = None if pd.isna(row['SOLL-Kontakt:']) else str(row['SOLL-Kontakt:'])

        try:
            # Create the card
            card = target_list.add_card(
                name=name_card,
                desc=text_desc,
                due=due_date,
            )

            # Add label to the card
            if etiqueta_nombre in label_dict:
                card.add_label(label_dict[etiqueta_nombre])

            # Assign a member to the card
            if miembro in member_dict:
                card.assign(member_id=member_dict[miembro])

            # Fill the custom field 'Order Volume'
            cf = card.get_custom_field_by_name('Order Volume')
            if cf:
                cf.value = umsatz

            logging.info(f"Row {row['Offer Nummer']} added as a new card.")
        except Exception as e:
            logging.error(f"Error processing row {row['Offer Nummer']}: {e}")

        # Clear memory
        del miembro, etiqueta_nombre, name_card, leistung, umsatz, angebots, aufstell, due_date
        gc.collect()

    # Add a delay of 60 seconds between subsets
    if subset_index < len(subsets) - 1:
        logging.info("Waiting for 60 seconds before processing the next subset...")
        time.sleep(60)

# Print a message when the uploading process is finished
print("OLE OLE LOS CARACOLEEE \nUploading process completed successfully!")
logging.info("Uploading process completed successfully!")