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

accounts = w3.eth.accounts

buyer_address = st.selectbox("Select buyer address", options=accounts)

buyer_wei_balance = w3.eth.getBalance(buyer_address); 
buyer_eth_balalnce = w3.fromWei(buyer_wei_balance, "ether")
st.header(f"Your wallet have  {buyer_eth_balalnce} Eth.")




################################################################################
# Display Products
################################################################################
products = []
products_dict = {}
total_products = contract.functions.nextProductId().call() - 1
for iterator in range(total_products):
    product = contract.functions.products(iterator).call()
    products.append(product)
    products_dict[product[3]] = product

product_list = products_dict.keys()


buyer_product = st.selectbox("Select Product", options=product_list)

try:
    df = pd.DataFrame({
                        'Seller': products_dict[buyer_product][2],
                        'Description': products_dict[buyer_product][4],
                        'Items Available': products_dict[buyer_product][5],
                        #'Price(in Eth)': w3.fromWei(products_dict[buyer_product][6], "ether") ,
                        #'Price(in Wei)': products_dict[buyer_product][6] ,
                        #'Image': products_dict[buyer_product][7]
            },
            index=[products_dict[buyer_product][1]])
    st.table(df)


    product_code = products_dict[buyer_product][1]
    product_price = products_dict[buyer_product][6]
    st.write("Price(in Eth) : ", float(w3.fromWei(product_price, "ether")))

except:
    ''

try:
    # Display  Image
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(' ')
    with col2:
        st.image(products_dict[buyer_product][7])
    with col3:
        st.write(' ')
    
except:
    ''

input_quantity = st.number_input('Quantity',min_value=1,step=1)

if st.button("Buy"):
    try:
        value = input_quantity * product_price
        st.write("value in Wei ", value)
        tx_hash = contract.functions.buyProduct(
                        product_code,
                        input_quantity                       
                        ).transact({'from': buyer_address,'value':value, 'gas': 1000000})
                        
        receipt = w3.eth.waitForTransactionReceipt(tx_hash)
        st.write("Payment Succesful")
        st.write(dict(receipt))
    except:
        st.write("Function not available currently.")