#import necessary libraries
import pandas as pd
import os
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    ForeignKey,
    String,
    Integer,
    select,
    inspect,
    text,
)

from sqlalchemy.types import *
from sqlalchemy.types import TEXT

foriegn_key_off_query = """ PRAGMA foreign_keys = off; """ 
begin_transaction_query = """ BEGIN TRANSACTION; """

category_query_1 = """  
CREATE TABLE category_temp (
    id TEXT PRIMARY KEY,
    name TEXT,
    description TEXT
);
"""
category_query_2 = """  
INSERT INTO category_temp SELECT * FROM category;
"""
category_query_3 = """ DROP TABLE category; """
category_query_4 = """ALTER TABLE category_temp RENAME TO category; """

item_query_1 = """ 
CREATE TABLE item_temp (
    id TEXT PRIMARY KEY,
    size TEXT,
    description TEXT
);
"""
item_query_2 = """  
INSERT INTO item_temp SELECT * FROM item;
"""
item_query_3 = """ DROP TABLE item; """
item_query_4 = """ALTER TABLE item_temp RENAME TO item; """

seller_query_1 = """ 
CREATE TABLE seller_temp (
    id TEXT PRIMARY KEY,
    name TEXT,
    zipcode TEXT
);
"""
seller_query_2 = """  
INSERT INTO seller_temp SELECT * FROM seller;
"""
seller_query_3 = """ DROP TABLE seller; """
seller_query_4 = """ALTER TABLE seller_temp RENAME TO seller; """

commit_query = """ COMMIT; """


foriegn_key_on_query = """ PRAGMA foreign_keys = ON; """ 

#Create a temporary table with the desired schema and primary key constraint
product_query_1 = """ 
CREATE TABLE product_temp (
    product_id TEXT PRIMARY KEY,    
    name TEXT,
    price TEXT,
    category_id TEXT,
    FOREIGN KEY (category_id) REFERENCES category(id),
    item_id TEXT,
    FOREIGN KEY (item_id) REFERENCES item(id),
    type TEXT,
    image_url TEXT,
    seller_id TEXT,
    color TEXT,
    FOREIGN KEY (seller_id) REFERENCES seller(id)    
);
"""

product_query_1_v1 = """ 
CREATE TABLE product_temp (
    product_id TEXT PRIMARY KEY,    
    name TEXT,
    price TEXT,
    category_id TEXT,    
    item_id TEXT,    
    type TEXT,
    image_url TEXT,
    seller_id TEXT,
    color TEXT,
    FOREIGN KEY (category_id) REFERENCES category(id),
    FOREIGN KEY (item_id) REFERENCES item(id),
    FOREIGN KEY (seller_id) REFERENCES seller(id)    
);
"""



# Copy data from the original Table1 to the temporary table
product_query_2 = """
INSERT INTO product_temp SELECT * FROM product;
"""
#Drop the original Table1
product_query_3 = """ DROP TABLE product; """

#Rename the temporary table to Table1
product_query_4 = """
ALTER TABLE product_temp RENAME TO product;
"""

def get_sqlite_engine(product_data_df,category_data_df,item_data_df,seller_data_df):    
    sqlite_engine = create_engine("sqlite:///:memory:")    
    product_data_df.to_sql(name="product",con=sqlite_engine,index=False) 
    category_data_df.to_sql(name="category",con=sqlite_engine,index=False) 
    item_data_df.to_sql(name="item",con=sqlite_engine,index=False) 
    seller_data_df.to_sql(name="seller",con=sqlite_engine,index=False) 
    
    return sqlite_engine

def perform_sqlite_database_operations(sqlite_engine):
    #Updating tables with primary and forign key relationships    
    sqlite_connection = sqlite_engine.connect()
    sqlite_connection.execute(text(foriegn_key_off_query) )
    sqlite_connection.execute(text(begin_transaction_query) )

    #category table related changes
    sqlite_connection.execute(text(category_query_1) )
    sqlite_connection.execute(text(category_query_2) )
    sqlite_connection.execute(text(category_query_3) )
    sqlite_connection.execute(text(category_query_4) )

    #item table related changes
    sqlite_connection.execute(text(item_query_1) )
    sqlite_connection.execute(text(item_query_2) )
    sqlite_connection.execute(text(item_query_3) )
    sqlite_connection.execute(text(item_query_4) )

    #seller table related changes
    sqlite_connection.execute(text(seller_query_1) )
    sqlite_connection.execute(text(seller_query_2) )
    sqlite_connection.execute(text(seller_query_3) )
    sqlite_connection.execute(text(seller_query_4) )

    sqlite_connection.execute(text(commit_query) )
    sqlite_connection.execute(text(foriegn_key_on_query) )
    sqlite_connection.close()
    
    #product table related changes
    sqlite_connection.close()
    sqlite_connection = sqlite_engine.connect()
    sqlite_connection.execute(text(foriegn_key_off_query) )
    sqlite_connection.execute(text(begin_transaction_query) )

    sqlite_connection.execute(text(product_query_1_v1) )
    sqlite_connection.execute(text(product_query_2) )
    sqlite_connection.execute(text(product_query_3) )
    sqlite_connection.execute(text(product_query_4) )

    sqlite_connection.execute(text(commit_query) )
    sqlite_connection.execute(text(foriegn_key_on_query) )
    sqlite_connection.close()

    
    