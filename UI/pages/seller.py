from asyncore import write
import os
import json
from tkinter.tix import INTEGER
from web3 import Web3
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
import streamlit as st
from PIL import Image
import requests

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
store = []
accounts = w3.eth.accounts

seller_address = st.selectbox("Seller Account", options=accounts)
skip_add_store = False

if st.button("Proceed"):
    try:
        store_ids = contract.functions.getStoreForSeller(seller_address).call()
        #st.write('Store ID : ', store_ids)
        for store_iterator in range(len(store_ids)):
            store_info= contract.functions.stores((store_ids[store_iterator])-1).call()
            #st.write(store_info)          
            store.append(store_info)
        df = pd.DataFrame(store, columns=['StoreID', 'Store Name','Store Description', 'Seller', 'Is Active'])
        df = df.drop(columns=['Seller', 'Is Active']) 
        st.header("Your Stores") 
        st.table(df)

        store_products = []
        for store in store_ids:   
            store_products.append(contract.functions.getProductsForStore(store).call())
        
        
    
        products = []
        for iterator in range(len(store_products)):
            for inner_iterator in range(len(store_products[iterator])):
                product_id = store_products[iterator][inner_iterator]
                products.append(contract.functions.products(product_id - 1).call())
        df = pd.DataFrame(products, columns=['StoreID', 'ProductID','Seller','Name', 'Description', 'Inventory','Price','Image'])
        df = df.drop(columns=['Seller'])   
        st.header("Your Products")    
        st.write(df)


        
    except:
        skip_add_store = True
        st.write("You don't have a store yet. Add a store to continue.")
        

################################################################################
        # Add Store
################################################################################
st.title("Add Store")
store_name = st.text_input("Store Name")
store_description = st.text_input("Store Description")


if st.button("Add Store"):
    # Check if seller is already registered
    is_seller = contract.functions.isSeller(seller_address).call()
    if is_seller:
        try:
            tx_hash = contract.functions.addStore(
                        store_name,
                        store_description
                        ).transact({'from': seller_address, 'gas': 1000000})
            receipt = w3.eth.waitForTransactionReceipt(tx_hash)
            st.write("Store Added")
            st.write(dict(receipt))
            total_stores = contract.functions.nextStoreId().call() - 1
            st.write(f"Total Stores on EthBay :  {total_stores}")
        except:
            st.write("Function not available currently.")
    else:
        st.write("You are not registered as a seller. Only seller can add a store")

################################################################################
# Add Product
################################################################################
st.title("Add Product")
product_name = st.text_input("Name")
product_description = st.text_input("Description")
product_inventory = st.number_input('Inventory',min_value=1,step=1)
product_price = st.number_input(label="Price ( in ETH)",step=1.,format="%.2f")
product_price_wei = w3.toWei(product_price, "ether")
store_id = st.number_input('Store ID',min_value=1,step=1)
product_id = contract.functions.nextProductId().call()
image_name = str(product_id) + '.jpg'
url = ''

image_local_url = '../Images/' + image_name





auth = 'Bearer ' + os.getenv("PINATA_KEY")


uploaded_file = st.file_uploader("Upload Product Image",type="jpg")
if uploaded_file is not None:
    # To write file as bytes:

    content = uploaded_file.getvalue()

    with open(image_local_url, 'wb') as f:
        f.write(content)
        url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
        files=[
                ('file',(image_name,open(image_local_url,'rb'),'application/octet-stream'))
              ]
        headers = {
                    'Authorization': auth
                 }
        response = requests.request("POST", url, headers=headers, files=files)
        url = 'https://gateway.pinata.cloud/ipfs/' + response.json()['IpfsHash']



store_seller = contract.functions.stores(store_id - 1).call()[3]
if st.button("Add Product"):
    if store_seller == seller_address:
        try:
            st.write("price in wei ", product_price_wei)
            tx_hash = contract.functions.addProduct(
                        store_id,
                        product_name,
                        product_description,
                        product_inventory,
                        product_price_wei,
                        url
                        ).transact({'from': seller_address, 'gas': 1000000})
            receipt = w3.eth.waitForTransactionReceipt(tx_hash)
            st.write("Product Added")
            st.write(dict(receipt))
        except:
            st.write("Function not available currently.")
    else:
        st.write("You are not store owner.")


################################################################################
# Edit Product
################################################################################
st.title("Edit Product")
product_inventory = st.number_input('Updated Inventory',min_value=1,step=1)
product_price = st.number_input(label="Updated Price( in Eth)",step=1.,format="%.2f")
product_price_wei = w3.toWei(product_price, "ether")
product_id = st.number_input('Product ID',min_value=1,step=1)

st.write("price in wei ", product_price_wei)
store_seller = contract.functions.products(product_id - 1).call()[2]

if st.button("Edit Product"):
    if store_seller == seller_address:
        try:
            tx_hash = contract.functions.editProduct(
                        product_id,
                        product_inventory,
                        product_price_wei
                        ).transact({'from': seller_address, 'gas': 1000000})
            receipt = w3.eth.waitForTransactionReceipt(tx_hash)
            st.write("Product Edited")
            st.write(dict(receipt)) 
        except:
            st.write("Function not available currently.")
    else:
        st.write("You are not Product owner.")
    
################################################################################
# Check Balance
################################################################################
st.title("Check Balance")

if st.button("Check Balance"):
    # Check if seller is already registered
    st.write(f"Checking Balance for  :  {seller_address}")
    seller = contract.functions.sellers(seller_address).call()
    st.write(f"Seller Balance :  {seller[2]} Wei")

################################################################################
# Withdraw Balance
################################################################################
st.title("Withdraw Balance")
if st.button("Withdraw Balance"):
    seller_balance = contract.functions.sellers(seller_address).call()[2]
    if seller_balance > 0:
        try:
            balance = contract.functions.sellers(seller_address).call()[2]
            tx_hash = contract.functions.sellerWithdraw().transact({'from': seller_address, 'gas': 1000000})
            receipt = w3.eth.waitForTransactionReceipt(tx_hash)
            st.write(f"{balance} Wei transferred to {seller_address}")
            st.write(dict(receipt))
        except:
            st.write("Function not available currently.")
    else:
        st.write("You don't have enough ETH to withdraw")

