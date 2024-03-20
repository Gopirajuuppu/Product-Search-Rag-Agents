import os
import re

import pandas as pd
import numpy as np

def extract_timestamp(value):
    try:
        obj = re.search(r"\[\s*([^\[\]]+?)\s*(?:\([^)]*\))?\s*\]", value).group(1)
        return obj.replace(" UTC", "")
    except:
        return None


def convert_hexa_to_decimal(value):
    if not value:
        return None
    value = value.strip()
    value_list = value.split("-")
    value_list.reverse()
    hex_value = "".join(value_list)
    integer_value = int(hex_value, 16)
    return integer_value


class IPGLogsDataPreProcessing(object):
    def __init__(self,log_file):
        self.log_file = log_file
    
    def preprocess(self):
        battery_charge_events_df = BatteryChargeEventsProcessor(self.log_file).process()
        daily_current_change_df = DailyCurrentChangeProcessor(self.log_file).process()
        program_on_off_df = ProgramOnOffProcessor(self.log_file).process()
        temp_df = TemperatureProcessor(self.log_file).process()
        
        ipg_logs_dfs_dict = {
                             'Battery and Charge events':battery_charge_events_df,
                             'Daily Current Change':daily_current_change_df,
                             'Program On Off':program_on_off_df,
                             'Temperature':temp_df
                            }                             
        
        #ipg_logs_df_list = [battery_charge_events_df,daily_current_change_df,program_on_off_df,temp_df]
        return ipg_logs_dfs_dict
    
class TemperatureProcessor(object):
    def __init__(self,log_file):
        self.temp_df = pd.read_excel(log_file,
                   sheet_name="Temperature",
                   usecols=["Time Stamp", "Temperature"],
                   index_col=None)
        self.temp_df.dropna(how="any", inplace=True)
        self.EVENTS_COLS = ["Time Stamp", "Temperature"]
    
    def convert_to_processed_temp_data(self,df):
        data_list = list()
        for i in range(df.shape[0]):
            temperature_val = df["Temperature"].iloc[i].strip()
            temperature_val = re.search(r"\[(.*?)\]", temperature_val)
            temperature_val = temperature_val.groups()[0].replace("℃", "")
            data_list.append([df["Time Stamp"].iloc[i], temperature_val])
        processed_df = pd.DataFrame(data_list, columns=list(map(lambda x: x.capitalize(), self.EVENTS_COLS)))
        return processed_df
    
    def process(self):
        self.temp_df["Time Stamp"] = self.temp_df["Time Stamp"].map(extract_timestamp)
        #self.temp_df["Time Stamp"] = pd.to_datetime(self.temp_df["Time Stamp"], format='%m/%d/%Y %I:%M:%S %p') 
        self.temp_df["Time Stamp"] = pd.to_datetime(self.temp_df["Time Stamp"], format='%m/%d/%Y %I:%M %p')
        self.temp_df.dropna(how="any", inplace=True)
        temp_df = self.convert_to_processed_temp_data(self.temp_df)
        temp_df.to_csv("processed_log_Temparature.csv", index=False)
        return temp_df    

# program on of sheet
class ProgramOnOffProcessor(object):
    def __init__(self,log_file):
        self.poo_df = pd.read_excel(log_file,
                   sheet_name="Program On Off",
                   usecols=["Record ID", "Time Stamp", "Data"],
                   index_col=None)
        self.poo_df.dropna(how="any", inplace=True)       
        self.USE_COLUMNS = ["PRG ID", "CYCLE_ON", "CYCLE_OFF", "THPY ERR"]
        self.EVENTS_COLUMNS_DICT = {"END_STORAGE": "Ready to implant",
                       "END_PROGRAM_SWAP": "Active program swapped",
                       "START_EXTERNAL": "Program started from external command",
                       "END_EXTERNAL": "Program ended from external command"}
    
    def extract_events_and_values(self,event_string):
        events_list = re.findall(r"\[.*?\]", event_string)
        events_hex = re.findall(r'\b(?:[0-9A-F]{2}-?)+\b', event_string)
        events_name = re.findall(r'\[(.*?)\]', event_string)
        events_name_hex_dict = dict(zip(events_name, events_hex))
        for name, _hex in events_name_hex_dict.items():
            if name in ["CYCLE_ON", "CYCLE_OFF", "PRG ID"]:
                events_name_hex_dict[name] = convert_hexa_to_decimal(_hex)
            else:
                events_name_hex_dict[name] = _hex
        
        return events_name_hex_dict
    
    def process(self):
        self.poo_df["Time Stamp"] = self.poo_df["Time Stamp"].map(extract_timestamp)
        self.poo_df.dropna(how="any", inplace=True)
        
        data_list = list()
        previous_program_id = None
        for i in range(self.poo_df.shape[0]):
            temp_list = list()
            try:
                temp_list.append(self.poo_df["Time Stamp"].iloc[i])
                found_event = False
                events_name_hex_dict = self.extract_events_and_values(self.poo_df["Data"].iloc[i])
                for col in self.USE_COLUMNS:
                    if events_name_hex_dict.get(col, "NA") == "NA":
                        if col == "PRG ID":
                            temp_list.append(previous_program_id)
                        else:
                            temp_list.append(None)
                    else:
                        if col != "THPY ERR":
                            if col == "PRG ID":
                                previous_program_id = events_name_hex_dict.get(col)
                            temp_list.append(events_name_hex_dict.get(col))
                        else:
                            temp_list.append("Yes")
                for evt_name, evt_hex in events_name_hex_dict.items():
                    if evt_name in self.EVENTS_COLUMNS_DICT:
                        found_event = True
                        temp_list.append(self.EVENTS_COLUMNS_DICT[evt_name])
                if not found_event:
                    temp_list.append(None)
                data_list.append(temp_list)
            except:
                pass
        
        processed_df = pd.DataFrame(data_list, columns=["Time Stamp", "Program ID", "Cycle On Time", "Cycle Off                                                          Time", "Therapy Error", "Events"])
        processed_df.to_csv("processed_log_program_on_off.csv", index=False)
        return processed_df

# Dataframe for the sheet `Daily Current Usage`
class DailyCurrentChangeProcessor(object):
    def __init__(self,log_file):        
        self.dcu_df = pd.read_excel(log_file,
                   sheet_name="Daily Current Usage",
                   usecols=["Record ID", "Time Stamp", "Data"],
                   index_col=None)
        self.dcu_df.dropna(how="any", inplace=True)
        self.EVENTS_COLS = ["PRG ID", "STIM ON TIME", "USAGE"]
        self.NON_EVENTS_COLS = ["Time Stamp", "Record ID"]
            
    def convert_dcu_data_decomposition(self,list1):
        list2 = []
        temp_list = []
    
        for item in list1:
            if item[0] == 'PRG ID':
                if temp_list:
                    list2.append(temp_list)
                temp_list = []
            temp_list.append(item)
    
        if temp_list:
            list2.append(temp_list)
        return list2

    def convert_to_processed_dcu_data(self,df):
        data_list = list()
        for i in range(df.shape[0]):
            events_hex = re.findall(r'\b(?:[0-9A-F]{2}-?)+\b', df["Data"].iloc[i].strip())
            events_name = re.findall(r'\[(.*?)\]', df["Data"].iloc[i].strip())
            interim_data_list = self.convert_dcu_data_decomposition(list(zip(events_name, events_hex)))
            for grouped_list in interim_data_list:
                temp_list = list()
                grouped_dict = dict(grouped_list)
                for col in self.NON_EVENTS_COLS:
                    temp_list.append(df[col].iloc[i])
                for col in self.EVENTS_COLS:
                    temp_list.append(convert_hexa_to_decimal(grouped_dict.get(col, None)))
                data_list.append(temp_list)
        processed_df = pd.DataFrame(data_list, columns=list(map(lambda x: x.capitalize(), self.NON_EVENTS_COLS + self.EVENTS_COLS)))
        return processed_df
    
    def process(self):
        self.dcu_df["Time Stamp"] = self.dcu_df["Time Stamp"].map(extract_timestamp)
        #self.dcu_df["Time Stamp"] = pd.to_datetime(self.dcu_df["Time Stamp"], format='%m/%d/%Y %I:%M:%S %p')
        self.dcu_df["Time Stamp"] = pd.to_datetime(self.dcu_df["Time Stamp"], format='%m/%d/%Y %I:%M %p') 
        self.dcu_df["Record ID"] = self.dcu_df["Record ID"].map(convert_hexa_to_decimal)
        self.dcu_df.dropna(how="any", inplace=True)
        self.dcu_df = self.convert_to_processed_dcu_data(self.dcu_df)        
        dcu_df = self.dcu_df.sort_values(by='Time stamp').reset_index(drop=True)
        
        dcu_df.to_csv("processed_log_DailyCurrentUsage.csv", index=False)
        return dcu_df        

#for Battery and charge event sheets
class BatteryChargeEventsProcessor(object):
    def __init__(self, log_file):
        self.battery_df = pd.read_excel(log_file,
                                   sheet_name="Battery",
                                   usecols=["Time Stamp", "Type", "Status", "Battery Voltage"],
                                   index_col=None)
        self.battery_df.dropna(how="any", inplace=True)
        self.charge_event_df = pd.read_excel(log_file,
                                        sheet_name="Charge Events",
                                        usecols=["Time Stamp", "Data"],
                                        index_col=None)
        self.charge_event_df.dropna(how="any", inplace=True)
        
    def process_battery(self):
        # Process Time Stamp
        self.battery_df["Time Stamp"] = self.battery_df["Time Stamp"].map(extract_timestamp)
        self.battery_df["Time Stamp"] = pd.to_datetime(self.battery_df["Time Stamp"], format='%m/%d/%Y %I:%M %p')
        self.battery_df.dropna(how="any", inplace=True)
        
        # Process Type
        type_pattern = r"\[\s*([^\[\]]+?)\s*(?:\([^)]*\))?\s*\]"
        extract_type = lambda type_raw: re.search(type_pattern, type_raw).group(1) if re.search(type_pattern, type_raw) else None
        self.battery_df["Type"] = self.battery_df["Type"].map(extract_type)
        self.battery_df.dropna(how="any", inplace=True)
        
        # Process Status
        status_pattern = r"\[([A-Z.]+)\]"
        extract_status = lambda status_str: re.search(status_pattern, status_str).group(1) if re.search(status_pattern, status_str) else None
        self.battery_df["Status"] = self.battery_df["Status"].map(extract_status)
        self.battery_df.dropna(how="any", inplace=True)
        
        # Process Battery Voltage
        battery_voltage_pattern = r"\[([\d.]+)V\]"
        extract_battery_voltage = lambda battery_voltage_str: float(re.search(battery_voltage_pattern, battery_voltage_str).group(1)) if re.search(battery_voltage_pattern, battery_voltage_str) else None
        self.battery_df["Battery Voltage"] = self.battery_df["Battery Voltage"].map(extract_battery_voltage)
        self.battery_df.dropna(how="any", inplace=True)
        
        
    def process_charge_events(self):
        charge_event_flag_dict = {
                "00" : "PARTIALLY CHARGED",
                "01" : "FULLY CHARGED",
                "02" : "SOFTWARE OVER TEMPERATURE",
                "03" : "HARDWARE OVER TEMPERATURE"
            }

        # Process Time Stamp
        self.charge_event_df["Time Stamp"] = self.charge_event_df["Time Stamp"].map(extract_timestamp)
        self.charge_event_df["Time Stamp"] = pd.to_datetime(self.charge_event_df["Time Stamp"], format='%m/%d/%Y %I:%M %p')
        self.charge_event_df.dropna(how="any", inplace=True)
        
        # Process Data
        info_dict = {}
        temp_data_list = self.charge_event_df["Data"].tolist()
        
        end_voltage_pattern = r"\[END VOLT:([\d.]+)V\]"
        extract_end_voltage = lambda input_str: float(re.search(end_voltage_pattern, input_str).group(1)) if re.search(end_voltage_pattern, input_str) else None
        info_dict["Type"] = ["CHARGING ENDED" if voltage is not None else "CHARGING STARTED" for voltage in list(map(extract_end_voltage, temp_data_list))]
        
        voltage_pattern = r"\[(?:END|START) VOLT:([\d.]+)V\]"
        extract_voltage = lambda input_str: float(re.search(voltage_pattern, input_str).group(1)) if re.search(voltage_pattern, input_str) else None
        info_dict["Battery Voltage"] = list(map(extract_voltage, temp_data_list))
        
        flag_pattern = r"(\d{2})\s*\[FLAGS: .*\]"
        extract_flag_value = lambda flag_str: charge_event_flag_dict.get(re.search(flag_pattern, flag_str).group(1)) if re.search(flag_pattern, flag_str) else None
        info_dict["Status"] = [flag if flag is not None else "SUCCESS" for flag in list(map(extract_flag_value, temp_data_list))]
        
        self.charge_event_df = self.charge_event_df.drop('Data', axis=1)
        self.charge_event_df["Type"] = info_dict["Type"]
        self.charge_event_df["Status"] = info_dict["Status"]
        self.charge_event_df["Battery Voltage"] = info_dict["Battery Voltage"]
        self.charge_event_df.dropna(how="any", inplace=True)
        
    def process(self):
        self.process_battery()
        self.process_charge_events()

        # Merge dataframes
        merged_df = pd.concat([self.battery_df, self.charge_event_df])
        # Drop the individual "Value_df1" and "Value_df2" columns
        merged_df = merged_df.sort_values(by='Time Stamp').reset_index(drop=True)
        merged_df.to_csv("processed_log_Battery_Charge_events.csv", index=False)
        return merged_df
