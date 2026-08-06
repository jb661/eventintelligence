import json
import time
import datetime as dt
from pathlib import Path
import streamlit as st

import requests
import pandas as pd


load_dotenv()
API_KEY = os.getenv("API_KEY")

COUNTRY = "GB"
SEGMENT = "Music"
N_WEEKS = 26          

st.title("Welcome!")