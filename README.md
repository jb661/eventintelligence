# Eventintelligence
This project is a small streamlit webapp to display music genre data obtained from the Ticketmaster API

The architecture goes as follows:
```
Ticketmaster API -> get_data.py -> data/processed -> Streamlit app
```

## Setup instructions

```
git clone https://github.com/jb661/eventintelligence.git
cd eventintelligence
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
You must obtain an API key to access the information from Ticketmaster.
To do this you must create an account.
More information can be found [here](https://developer-account.ticketmaster.com/)
Then, save the API key in your local `.env` file:
```
API_KEY = # add it here
```

Then finally run
```
python get_data.py
streamlit run Home.py
```
