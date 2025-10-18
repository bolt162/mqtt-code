# mqtt-code
MQTT Data from California Reservoirs and Report

## Setup:

Start the docker daemon
Clone this repository and open the folder in a terminal and paste the following command to run docker:

<img width="437" height="25" alt="Screenshot 2025-10-18 at 2 40 36 PM" src="https://github.com/user-attachments/assets/c7c259b8-c25c-4850-baa7-946b79e99fe0" />

Then open a python virtual environment using:

source .venv/bin/activate
python3 -m venv .venv

Install the requirements:

pip install -r requirements.txt

Then in one terminal run the subscriber.py:

python subscriber.py --broker localhost --out daily_reservoir_report.csv

The publisher files convert the given CSV data to JSON in memory with this line:

<img width="515" height="150" alt="Screenshot 2025-10-18 at 2 47 26 PM" src="https://github.com/user-attachments/assets/c655d997-50f6-4128-a984-9c107ec7df80" />


And in the other terminal run the below commands one by one:

python publisher.py --broker localhost --topic SHASTA/WML --csv Shasta_WML.csv --rate_hz 5
python publisher.py --broker localhost --topic OROVILLE/WML --csv Oroville_WML.csv --rate_hz 5
python publisher.py --broker localhost --topic SONOMA/WML --csv Sonoma_WML.csv --rate_hz 5

Here is the output that the subscriber will generate:

<img width="548" height="744" alt="Screenshot 2025-10-18 at 2 45 48 PM" src="https://github.com/user-attachments/assets/0edd292d-b2b2-4ad7-b84f-495f5c1a6323" />



