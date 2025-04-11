# Trello Integration Project

This script automates the process of uploading cards to a Trello board from an Excel file.

## Requirements
- Python 3.8 or higher
- A Trello account
- Trello API credentials (API key, API secret, and token)

## Installation

1. **Download the Script**:
   - Go to the [GitHub repository](https://github.com/your-username/trello-integration).
   - Click the green **Code** button and select **Download ZIP**.
   - Extract the ZIP file to a folder on your computer.

2. **Install Python**:
   - Download and install Python from [python.org](https://www.python.org/).


3. **Install Dependencies**:
   - Open a terminal or command prompt.
   - Navigate to the folder where you extracted the script.
   - Run the following command to install the required libraries:
     ```bash
     pip install -r requirements.txt
     ```

4. **Set Up Trello API Credentials**:
   - Create a `.env` file in the same folder as `main.py`.
   - Add the following lines to the `.env` file:
     ```
     TRELLO_API_KEY=your_api_key
     TRELLO_API_SECRET=your_api_secret
     TRELLO_TOKEN=your_token
     ```

5. **Prepare the Input File**:
   - Place your Excel file in a folder named `input` in the same directory as `main.py`.

## Usage

1. Open a terminal or command prompt.
2. Navigate to the folder where the script is located.
3. Run the script with the following command:
   ```bash
   python [main.py](http://_vscodecontentref_/1) --board_name "Your Board Name" --list_name "Your List Name"

## License

This project is licensed under the MIT License. See the LICENSE file for more details.