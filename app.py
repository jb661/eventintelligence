import json
import time
import datetime as dt
from pathlib import Path
import streamlit as st

import requests
import pandas as pd

# NOTE: rotate this key in the Ticketmaster developer console before submitting.
# Better practice: API_KEY = os.environ["TM_API_KEY"]
load_dotenv()
API_KEY = os.getenv("API_KEY")

COUNTRY = "GB"
SEGMENT = "Music"
N_WEEKS = 26          # analysis horizon; check the retrieval plot before trusting the tail

st.title(