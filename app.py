print("======================= Product Search Enahancement =========================")
#Importing Necessary libraries
import os
import pandas as pd
import logging 
import sys 
logging.basicConfig(stream=sys.stdout, level=logging.INFO, force=True) 
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout)) 
from IPython.display import Markdown, display

#streamlit libraries
import streamlit as st
import streamlit as st
from audiorecorder import audiorecorder
#from utils import get_answer, text_to_speech, autoplay_audio, speech_to_text
from audio_recorder_streamlit import audio_recorder
from streamlit_float import *
from speech_text_utils import speech_to_text

import openai
from IPython.display import Markdown, display
from data_preprocessing import process_data
from utils import get_sqlite_engine,perform_sqlite_database_operations
from llamaIndex_agent import LlamaIndexSqlEngine
from langchain_agent import LangChainSqlEngine,LangChainPandasAgent
from pandasai_agent import PandasAI_DF_Agent
from text_classification import get_text_clasification_details


openAI__api_key = "apikey"
os.environ["OPENAI_API_KEY"] = openAI__api_key
openai.api_key = os.environ["OPENAI_API_KEY"]
model_name = "gpt-3.5-turbo"


# App related functions

def clear_submit():
    """
    Clear the Submit Button State
    Returns:

    """
    st.session_state["submit"] = False   


# Application interface
if __name__ == '__main__':
    # Streamlit Application Starts
    st.title("NLQ Diven Product Search Enahancement")
    uploaded_file = st.file_uploader("Upload Your data",
                                     type=["xlsx"],
                                     on_change=clear_submit)

    if uploaded_file:
        # Process excel work book
        product_data_df,category_data_df,item_data_df,seller_data_df = process_data(uploaded_file)
        dfs_list = [product_data_df,category_data_df,item_data_df,seller_data_df]
        if dfs_list is None:
            st.error("Error in data processing! See logs in terminal", icon="🚨")
        else:
            st.success("Your data Processed Successfully!", icon="✅")

        #dataBase operations
        sqlite_db_engine = get_sqlite_engine(product_data_df,category_data_df,item_data_df,seller_data_df)
        perform_sqlite_database_operations(sqlite_db_engine)
        st.success("Your data base operations have been done Successfully!", icon="✅") 
        
        st.title("Audio Recorder")        
        audio = audiorecorder("Click to record", "Click to stop recording")
        if len(audio) > 0:
            # To play audio in frontend:
            st.audio(audio.export().read())  

            # To save audio to a file, use pydub export method:
            audio.export("audio.wav", format="wav")

            # To get audio properties, use pydub AudioSegment properties:
            st.write(f"Frame rate: {audio.frame_rate}, Frame width: {audio.frame_width}, Duration: {audio.duration_seconds} seconds")
        
#         with st.spinner("Transcribing..."):
#             # Write the audio bytes to a temporary file
#             webm_file_path = "temp_audio.mp3"
#             with open(webm_file_path, "wb") as f:
#                 f.write(audio)

#             # Convert the audio to text using the speech_to_text function
#             transcript = speech_to_text(webm_file_path)
#             if transcript:
#                 st.write("------ Audio To Text -----")
#                 st.write(transcript)
#         print("########################")
        
        # Initialize floating features for the interface
        
#         #float_init()
#         print("----------Intializing Float -----")
#         footer_container = st.container()
#         #print(footer_container)
#         with footer_container:
#             #audio_bytes = audio_recorder()
#             audio_bytes = audio_recorder("Click to record", "Click to stop recording")
#             print("-- Audio Bytes -----")
#             print(audio_bytes)
#         if audio:
#             print("########################")
#             with st.spinner("Transcribing..."):
#                 # Write the audio bytes to a temporary file
#                 webm_file_path = "temp_audio.mp3"
#                 with open(webm_file_path, "wb") as f:
#                     f.write(audio_bytes)

#                 # Convert the audio to text using the speech_to_text function
#                 transcript = speech_to_text(webm_file_path)
#                 if transcript:
#                     st.write("------ Audio To Text -----")
#                     st.write(transcript)
         
        
        
        # React to user input
        if user_query := st.chat_input("Query..?"): 
            st.write("Your Query :: ", user_query)
            
            #Using Sql Agents from LlamaIndex and Langchain
            st.header('========== Sql Agents ===========', divider='rainbow')  
            col1, col2 = st.columns(2)            
            with col1:
                st.header('Llama-Index', divider='rainbow')           
                llamaIndex_object = LlamaIndexSqlEngine(sqlite_db_engine,model_name,user_query)
                llamaIndex_response = llamaIndex_object.get_SQLTableRetrieverQueryEngine()                
                st.write("Response: ",llamaIndex_response['output'])                
                st.write("Sql Query Used: ",llamaIndex_response['sql_query'])                
                st.write("Total Tokens Consumed:", llamaIndex_response['total_tokens'])               
            
            with col2:
                st.header('LangChain', divider='rainbow')
                lanhgChain_object = LangChainSqlEngine(sqlite_db_engine,model_name,user_query)
                LangChain_response = lanhgChain_object.get_langchain_sql_engine_response()                
                st.write("Response: ",LangChain_response)
            
            st.header('========= Pandas Agents =========', divider='rainbow') 
            st.header('LangChain', divider='rainbow') 
            lanhgChain_pandas_object = LangChainPandasAgent(dfs_list,model_name,user_query)
            LangChain_pandas_response = lanhgChain_pandas_object.get_langchain_pandas_agent_response()  
            st.write("Response: ",LangChain_pandas_response)          
            
            
            #Using PandasAI Agent by passing list of dataFrames
            st.header('PandasAI', divider='rainbow')
            pandasai_obj = PandasAI_DF_Agent(dfs_list,model_name,user_query)
            pandasai_agent_response = pandasai_obj.get_pandasAI_agent_response()
            st.write("Response: ",pandasai_agent_response['output'])
            #st.write("Explanation:", pandasai_agent_response['explanation']) 
            #st.write("Code Generated: ",pandasai_agent_response['code_generated']) 
            
            
            #Using Text Classification
            st.header('======== LLM- Text Classification =======', divider='rainbow') 
            print("----------------- Text Classification -----------")
            text_classification_results = get_text_clasification_details(model_name,user_query)
            st.write("text_classification_results: ",text_classification_results)
        
       
            

            

            









