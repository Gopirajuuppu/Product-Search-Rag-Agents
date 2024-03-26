#Importing Necessary libraries
import os
import pandas as pd

def process_data(file_name):
    product_data = pd.read_excel(file_name,sheet_name="product")
    category_data = pd.read_excel(file_name,sheet_name="category")
    seller_data = pd.read_excel(file_name,sheet_name="seller") 
    item_data = pd.read_excel(file_name,sheet_name="item")
    return product_data,category_data,item_data,seller_data