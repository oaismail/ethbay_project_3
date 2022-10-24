import os
import json
from web3 import Web3
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
import streamlit as st
from PIL import Image

load_dotenv()

st.set_page_config(layout="wide",initial_sidebar_state='collapsed')

# Display  Image
col1, col2, col3 = st.columns(3)
with col1:
    st.write(' ')
with col2:
    image = Image.open('../Images/UI.webp')
    st.image(image)
with col3:
    st.write(' ')

contract_address = (os.getenv("SMART_CONTRACT_ADDRESS"))
st.write(f"Contract Address {contract_address}")