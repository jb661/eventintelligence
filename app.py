import json
import time
import datetime as dt
from pathlib import Path
import streamlit as st

import requests
import pandas as pd

# NOTE: rotate this key in the Ticketmaster developer console before submitting.
# Better practice: API_KEY = os.environ["TM_API_KEY"]
#API_KEY = "VfYN2NrqqGt6XPpj4ssMPfWhKGmvzSKR"
API_KEY = "FzFv4eG7sbAcDA0R2aIpRrseLHStWetk" #This is James'

COUNTRY = "GB"
SEGMENT = "Music"
N_WEEKS = 26          # analysis horizon; check the retrieval plot before trusting the tail

st.title(