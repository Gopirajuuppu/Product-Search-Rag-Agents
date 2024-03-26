
from llama_index import SQLDatabase
import tiktoken 
from llama_index.callbacks import CallbackManager, TokenCountingHandler 
from llama_index import ServiceContext, LLMPredictor, OpenAIEmbedding, PromptHelper 
from llama_index.llms import OpenAI 
from llama_index import ServiceContext 
from llama_index.indices.struct_store.sql_query import NLSQLTableQueryEngine 

from llama_index.objects import ObjectIndex
from llama_index.objects import SQLTableNodeMapping, SQLTableSchema 
import pandas as pd 

from llama_index.indices.struct_store import SQLTableRetrieverQueryEngine 
from llama_index import VectorStoreIndex 

table_details = { "product": "The product table stores various types of Flower bouquets, including Valentine's and anniversary Flower bouquets", 
                 "category": "The category table stores a list of product line categories", 
                 "item": "The item table stores a list of product line items with different Flower sizes", 
                 "seller": "The seller table stores seller data, including their associated zip code"
                 }

class LlamaIndexSqlEngine(object):
      
    def __init__(self,sql_engine,model_name,query):
        self.sql_database = SQLDatabase(sql_engine, sample_rows_in_table_info=2)
        self.llm_model_name = model_name
        self.query = query  
        self.token_counter = TokenCountingHandler( tokenizer=tiktoken.encoding_for_model(model_name).encode ) 
    
    def get_llm(self):
        llm = OpenAI(temperature=0.1, model=self.llm_model_name)
        return llm
    
    def get_service_context(self):
        callback_manager = CallbackManager([self.token_counter])
        service_context = ServiceContext.from_defaults( llm=self.get_llm(),
                                               callback_manager=callback_manager)
        return service_context
    
    def get_NLSQLTableQueryEngine_response(self):               
        query_engine = NLSQLTableQueryEngine( sql_database=self.sql_database(), 
                                             service_context=self.get_service_context())
        response = query_engine.query(self.query)
        sql_query_used = response.metadata['sql_query']
        final_result = response.response
        total_tokens_used = self.token_counter.total_llm_token_count
        self. token_counter.reset_counts()
        
        return sql_query_used,final_result,total_tokens_used
        
    def get_SQLTableRetrieverQueryEngine(self):        
        tables = list(self.sql_database._all_tables) 
        table_node_mapping = SQLTableNodeMapping(self.sql_database) 
        table_schema_objs = [] 
        for table in tables: 
            table_schema_objs.append((SQLTableSchema(table_name = table, context_str = table_details[table])))            
        obj_index = ObjectIndex.from_objects( table_schema_objs, table_node_mapping, VectorStoreIndex, service_context=self.get_service_context())
        query_engine = SQLTableRetrieverQueryEngine( self.sql_database, obj_index.as_retriever(similarity_top_k=2), service_context=self.get_service_context() )
        
        response = query_engine.query(self.query)
        sql_query_used = response.metadata['sql_query']
        final_result = response.response
        total_tokens_used = self.token_counter.total_llm_token_count
        self. token_counter.reset_counts()
        results = {"output":final_result,
                  "total_tokens":total_tokens_used,
                  "sql_query":sql_query_used}
        
        return results
        

         