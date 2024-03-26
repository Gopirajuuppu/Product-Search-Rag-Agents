import langchain_openai
from langchain_openai import OpenAI,ChatOpenAI
from langchain.sql_database import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent


class LangChainSqlEngine(object):
      
    def __init__(self,sql_engine,model_name,query):
        self.sql_database = SQLDatabase(sql_engine, sample_rows_in_table_info=2)
        self.llm_model_name = model_name
        self.query = query  
        #self.token_counter = TokenCountingHandler( tokenizer=tiktoken.encoding_for_model(model_name).encode ) 
    
    def get_llm(self):
        llm = ChatOpenAI(temperature=0.1, model=self.llm_model_name)
        return llm 
    
    def get_langchain_sql_engine_response(self):
        #sql_agent = create_sql_agent(self.get_llm(), db=self.sql_database, agent_type="openai-tools", verbose=True)
        sql_agent = create_sql_agent(self.get_llm(), db=self.sql_database, agent_type="openai-tools", verbose=True)
        response = sql_agent.invoke(self.query)     
        result = response['output']
        return result 

class LangChainPandasAgent(object):
      
    def __init__(self,dfs_list,model_name,query):
        self.dfs_list = dfs_list
        self.llm_model_name = model_name
        self.query = query  
        #self.token_counter = TokenCountingHandler( tokenizer=tiktoken.encoding_for_model(model_name).encode ) 
    
    def get_llm(self):
        llm = ChatOpenAI(temperature=0.1, model=self.llm_model_name)
        #llm = OpenAI(temperature=0.1, model=self.llm_model_name)
        return llm 
    
    def get_langchain_pandas_agent_response(self):
        agent_executor_args = {"handle_parsing_errors" : True,}
        LC_Pandas_Agent = create_pandas_dataframe_agent(self.get_llm(),
                                                        self.dfs_list,
                                                        agent_type="openai-tools", 
                                                        agent_executor_kwargs=agent_executor_args,
                                                        verbose=True)        
        response = LC_Pandas_Agent.run(self.query) 
        print("--------------- LangChain Pandas Agent Response ---------------")
        print(response)
        print("--------------- LangChain Pandas Agent Response ---------------")       
        return response 
        
    
    
