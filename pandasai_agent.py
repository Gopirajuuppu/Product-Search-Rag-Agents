import os
import re
import pandas as pd
import pandasai
from pandasai import SmartDatalake
from pandasai import SmartDataframe
from pandasai import Agent as PandasAiAgent
from pandasai.llm.openai import OpenAI

class PandasAI_DF_Agent(object):
      
    def __init__(self,dfs_list,model_name,query):
        self.dfs_list = dfs_list
        self.llm_model_name = model_name
        self.query = query  
        #self.token_counter = TokenCountingHandler( tokenizer=tiktoken.encoding_for_model(model_name).encode ) 
    
    def get_llm(self):
        
        llm = OpenAI(temperature=0.1, model=self.llm_model_name)
        #llm = OpenAI(temperature=0.1, model=self.llm_model_name)
        return llm  
    
    def get_smartDataLake_df(self):
        #smart_df_config = { "custom_instructions": "Here are the final instrcutions to follow :" + self.final_prompt }
        smart_data_lake_df = SmartDatalake(self.dfs_list, config={"llm": self.get_llm()} )
        #smart_data_lake_df = SmartDatalake(self.dfs_list)
        return smart_data_lake_df
#         smart_data_lake_df = SmartDataframe(self.log_df, 
#                                           config=smart_df_config,
#                                           name=battery_charge_events_df_name,
#                                           description=battery_description)
            
        
    def get_pandasAI_agent_response(self):
        panda_ai_agent = PandasAiAgent(self.dfs_list, 
                                       config={"llm": self.get_llm()}
                                       )
        PAI_agent_output = panda_ai_agent.chat(self.query)
        PAI_agent_last_code_generated = panda_ai_agent.last_code_generated
        PAI_agent_explain = panda_ai_agent.explain()
        PAI_agent_response = {'output':PAI_agent_output,
                             'code_generated':PAI_agent_last_code_generated,
                             'explanation':PAI_agent_explain}
        return PAI_agent_response
    