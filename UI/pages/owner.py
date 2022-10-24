import os
import json
from web3 import Web3
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
import streamlit as st
import numpy as np
from PIL import Image
import decimal


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

# Define and connect a new Web3 provider
w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URI")))

################################################################################
# The Load_Contract Function
################################################################################


@st.cache(allow_output_mutation=True)
def load_contract():

    # Load the contract ABI
    with open(Path('../Contracts/Compiled/ethbay_abi.json')) as f:
        ethbay_abi = json.load(f)

    contract_address = os.getenv("SMART_CONTRACT_ADDRESS")

    # Load the contract
    contract = w3.eth.contract(
        address=contract_address,
        abi=ethbay_abi
    )

    return contract

contract = load_contract()

st.title("Eth Bay")

owner_address = contract.functions.owner().call()
st.write(f"The Owner is {owner_address}")

owner_wei_balance = w3.eth.getBalance(owner_address); 
# Convert Wei value to ether
owner_eth_balalnce = w3.fromWei(owner_wei_balance, "ether")
st.write(f"The Owner wallet has  {owner_eth_balalnce} Eth.")

################################################################################
# Display Stores
################################################################################
st.title("Stores on EthBay")
st.write('')
total_stores = contract.functions.nextStoreId().call() - 1
st.write(f"Total Stores on EthBay :  {total_stores}")
stores = []
iterator = 0
for iterator in range(total_stores):   
    stores.append(contract.functions.stores(iterator).call())
df = pd.DataFrame(stores, columns=['StoreID', 'Store Name','Store Decsription', 'Seller', 'Is Active'])
df = df.drop(columns=['Is Active']) 
st.table(df)

total_products = contract.functions.nextProductId().call() - 1



################################################################################
# Display Products
################################################################################
st.title("Products on EthBay")
st.write('')
st.write(f"Total Products on EthBay :  {total_products}")
products = []
products_dict = {}
total_products = contract.functions.nextProductId().call() - 1
for iterator in range(total_products):
    product = contract.functions.products(iterator).call()
    products.append(product)
    products_dict[product[3]] = product

df = pd.DataFrame(products, columns=['StoreID', 'ProductID','Seller', 'Name', 'Description','Quantity', 'Price (in Wei)', 'Image'])
st.table(df)





################################################################################
# Register Selller
################################################################################
st.title("Register Seller")

accounts = w3.eth.accounts
seller_address = st.selectbox("Seller Account", options=accounts)

if st.button("Register Seller"):

    # Check if seller is already registered
    is_seller = contract.functions.isSeller(seller_address).call()
    if is_seller:
        st.write("Seller already registered.")
    else:
        # Use the contract to send a transaction to the registerArtwork function
        tx_hash = contract.functions.addSeller(
            seller_address,
        ).transact({'from': owner_address, 'gas': 1000000})
        receipt = w3.eth.waitForTransactionReceipt(tx_hash)
        st.write("Seller Registered")
        #st.write(dict(receipt))
        total_sellers = contract.functions.totalSellers().call()
        st.write(f"Total sellers on EthBay :  {total_sellers}")



################################################################################
# Get Contract Balance
################################################################################
st.title("Check EthBay Balance")


if st.button("Get Balance"):

    contract_balance = contract.functions.balance().call()  
    contract_balance = w3.fromWei(contract_balance, "ether") 
    st.write(f"Contract Balance :  {contract_balance} Eth")

################################################################################
# Withdraw Balance
################################################################################
st.title("Withdraw Balance")

if st.button("Withdraw Balance"):
    contract_balance = contract.functions.balance().call()
    if contract_balance > 0:
        try:
            contract.functions.withdrawEthBayFunds().transact({'from': owner_address, 'gas': 1000000})
            owner_wei_balance = w3. eth. getBalance(owner_address); 
            owner_eth_balalnce = w3.fromWei(owner_wei_balance, "ether")
            st.write(f"{contract_balance} Wei transferred to {owner_address} ")
            st.write(f"Owner balance : {owner_eth_balalnce}  Eth ")
        except:
            st.write('Error')
    else:
        st.write("Contract doesn't have enough ETH to withdraw")

