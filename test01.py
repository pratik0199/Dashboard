# -*- coding: utf-8 -*-
"""
Created on Tue May  7 11:31:56 2024

@author: Naina Sisodia
"""

import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings("ignore")


# ### Creating dataframe to store required data

# In[4]:
#testing
df1_config=pd.read_excel("excel_to_python.xlsx", sheet_name='config_data')
df2_proc_data=pd.read_excel("excel_to_python.xlsx", sheet_name='Data')
df_tag_list=pd.read_excel("excel_to_python.xlsx", sheet_name='tag_description')
df_final_cols=pd.read_excel("excel_to_python.xlsx", sheet_name='final_col_list')
df_coeff_summary=pd.read_excel("CoeffsLinearReg (1).xlsx")
dict_stg = {'Stage 1': {'tab1': [7, 368, 'table1_df'], 'tab2': [372, 733, 'table2_df'], 'tab3': [745, 1106, 'table3_df'], 'tab4': [1110, 1471,'table4_df']},
            'Stage 2': {'tab1': [7, 368, 'table1_df'], 'tab2': [372, 733, 'table2_df'], 'tab3': [745, 1106, 'table3_df'], 'tab4': [1110, 1471,'table4_df']}
           }

# ### Mapping our client's tag list to the new column name as per our convenience

# In[5]:
col_mapping=dict(zip(df_tag_list['client_tag_name'],df_tag_list['description']))#this will help us to use our column name for calculation irrespective of client's tag_name
df2_proc_data.rename(columns=col_mapping, inplace=True) #this will rename client_tag with our column_name, which we specified in df3

# In[6]:

df1_config.set_index('tag_name', inplace=True) #changing index so we can use loc function directly to locate values

# In[7]:

df_coeff_summary.set_index('Unnamed: 0', inplace=True) #changing index so we can use loc function directly to locate values

# ### Making a list of final columns which we've to calculate

# In[8]:

final_col_list=df_final_cols['new_name']

# In[9]:


### Defining a function to store our formulae for final_cols


# In[10]:


#df_res_stg1=calc(df1_config, df2_proc_data,'stg1')


# In[11]:


vsp_const=8314.4
time_conv=3600*1000
def calc(df1_config, df2_proc_data, stage):

    df2_proc_data['suction_pressure_flange_' + str(stage)] = df2_proc_data[str(stage)+'_suction_pressure'] + df1_config.loc['atmospheric_pressure', str(stage)]
    df2_proc_data['discharge_pressure_flange_' + str(stage)] = (df1_config.loc['dp_flange_discharge_line', str(stage)] + (df1_config.loc['atmospheric_pressure', str(stage)] + df2_proc_data[str(stage)+'_discharge_pressure']))
    df2_proc_data['compression_ratio_' + str(stage)] = df2_proc_data['discharge_pressure_flange_' + str(stage)] / df2_proc_data['suction_pressure_flange_' + str(stage)]
    df2_proc_data['total_swept_vol_' + str(stage)] = df1_config.loc['total_swept_volume', str(stage)]
    df2_proc_data['swept_vol_HE_' + str(stage)] = df1_config.loc['swept_volume_head_end', str(stage)]
    df2_proc_data['swept_vol_CE_' + str(stage)] = df1_config.loc['swept_volume_crank_end', str(stage)]
    df2_proc_data['HE_clearance_vol_Vs_' + str(stage)] = ((df1_config.loc['head_end_clearance', str(stage)] / 100) * df2_proc_data['swept_vol_HE_' + str(stage)])
    df2_proc_data['(V4) TDC' + str(stage)] = df2_proc_data['HE_clearance_vol_Vs_' + str(stage)]
    df2_proc_data['polymetric_expo_n_' + str(stage)] = 1 / (1 - ((np.log((df2_proc_data[str(stage)+'_discharge_temp'] + 273) / (df2_proc_data[str(stage)+'_suction_temp'] + 273))) / (np.log((df2_proc_data['discharge_pressure_flange_' + str(stage)] / df2_proc_data['suction_pressure_flange_' + str(stage)])))))
    df2_proc_data['head_end_V1' + str(stage)] = df2_proc_data['(V4) TDC' + str(stage)] * ((df2_proc_data['compression_ratio_' + str(stage)]) ** (1 / df2_proc_data['polymetric_expo_n_' + str(stage)]))
    df2_proc_data['BDC_V2' + str(stage)] = df2_proc_data['swept_vol_HE_' + str(stage)] + df2_proc_data['HE_clearance_vol_Vs_' + str(stage)]
    df2_proc_data['HE_V3' + str(stage)] = df2_proc_data['BDC_V2' + str(stage)] * ((1 / (df2_proc_data['compression_ratio_' + str(stage)])) ** (1 / df2_proc_data['polymetric_expo_n_' + str(stage)]))
    df2_proc_data['CE_clearance_vol_Vs' + str(stage)] = ((df1_config.loc['crank_end_clearance', str(stage)] / 100) * df2_proc_data['swept_vol_CE_' + str(stage)])
    df2_proc_data['TDC_V4' + str(stage)] = df2_proc_data['CE_clearance_vol_Vs' + str(stage)]
    df2_proc_data['CE_V1' + str(stage)] = df2_proc_data['CE_clearance_vol_Vs' + str(stage)] * ((df2_proc_data['compression_ratio_' + str(stage)]) ** (1 / df2_proc_data['polymetric_expo_n_' + str(stage)]))
    df2_proc_data['BDC_V2' + str(stage)] = df2_proc_data['swept_vol_CE_' + str(stage)] + df2_proc_data['CE_clearance_vol_Vs' + str(stage)]
    df2_proc_data['HE_V3(2)' + str(stage)] = df2_proc_data['BDC_V2' + str(stage)] * ((1 / (df2_proc_data['compression_ratio_' + str(stage)])) ** (1 / df2_proc_data['polymetric_expo_n_' + str(stage)]))
    df2_proc_data['HE_inlet_vol_eff %' + str(stage)] = ((df2_proc_data['swept_vol_HE_' + str(stage)] + df2_proc_data['HE_clearance_vol_Vs_' + str(stage)] - df2_proc_data['head_end_V1' + str(stage)]) * 100) / (df2_proc_data['swept_vol_HE_' + str(stage)] + df2_proc_data['HE_clearance_vol_Vs_' + str(stage)] - df2_proc_data['HE_clearance_vol_Vs_' + str(stage)])
    df2_proc_data['CE_inlet_vol_eff %' + str(stage)] = ((df2_proc_data['BDC_V2' + str(stage)] - df2_proc_data['CE_V1' + str(stage)]) * 100) / (df2_proc_data['BDC_V2' + str(stage)] - df2_proc_data['TDC_V4' + str(stage)])
    df2_proc_data['HE_discharge_vol_eff %' + str(stage)] = ((df2_proc_data['HE_V3' + str(stage)] - df2_proc_data['HE_clearance_vol_Vs_' + str(stage)]) * 100) / ((df2_proc_data['swept_vol_HE_' + str(stage)] + df2_proc_data['HE_clearance_vol_Vs_' + str(stage)]) - df2_proc_data['HE_clearance_vol_Vs_' + str(stage)])
    df2_proc_data['CE_discharge_vol_eff %' + str(stage)] = (((df2_proc_data['HE_V3(2)' + str(stage)] - df2_proc_data['TDC_V4' + str(stage)])) * 100) / (df2_proc_data['BDC_V2' + str(stage)] - df2_proc_data['TDC_V4' + str(stage)])
    df2_proc_data['cal_avg_inlet_vol_eff %' + str(stage)] = (df2_proc_data['HE_inlet_vol_eff %' + str(stage)] + df2_proc_data['CE_inlet_vol_eff %' + str(stage)]) / 2
    df2_proc_data['design_avg_inlet_vol_eff %' + str(stage)] = df1_config.loc['volumetric_efficiency', str(stage)]
    df2_proc_data['overall_vol_eff %' + str(stage)] = (df2_proc_data['HE_inlet_vol_eff %' + str(stage)] + df2_proc_data['CE_inlet_vol_eff %' + str(stage)] + df2_proc_data['HE_discharge_vol_eff %' + str(stage)] + df2_proc_data['CE_discharge_vol_eff %' + str(stage)]) / 4
    df2_proc_data['stage_inlet_capacity_Q ' + str(stage)] = df2_proc_data['cal_avg_inlet_vol_eff %' + str(stage)] * df2_proc_data['total_swept_vol_' + str(stage)] / 100
    df2_proc_data['stage_discharge_capacity_Q ' + str(stage)] = (df2_proc_data['HE_discharge_vol_eff %' + str(stage)] + df2_proc_data['CE_discharge_vol_eff %' + str(stage)]) / 2 * df2_proc_data['total_swept_vol_' + str(stage)] / 100
    df2_proc_data['actual_disc_temp_'+ str(stage)+str(stage)] = df2_proc_data[str(stage)+'_discharge_temp'] + 273
    df2_proc_data['rod_load_tension ' + str(stage)] = (((df1_config.loc['cross_sectional_area_of_piston', str(stage)] * (df2_proc_data['discharge_pressure_flange_' + str(stage)] - df2_proc_data['suction_pressure_flange_' + str(stage)])) - ((df1_config.loc['cross_sectional_area_of_piston_rod', str(stage)] * df2_proc_data['discharge_pressure_flange_' + str(stage)])) * 10 ** 5))
    df2_proc_data['rod_load_compression ' + str(stage)] = (((df1_config.loc['cross_sectional_area_of_piston', str(stage)] * (df2_proc_data['discharge_pressure_flange_' + str(stage)] - df2_proc_data['suction_pressure_flange_' + str(stage)])) + ((df1_config.loc['cross_sectional_area_of_piston_rod', str(stage)] * df2_proc_data['suction_pressure_flange_' + str(stage)])) * 10 ** 5))
    df2_proc_data['max_allowed_gas_load ' + str(stage)] = df1_config.loc['max_allowed_gas_rod_load', str(stage)]
    df2_proc_data['Zs_'+ str(stage)] = df_coeff_summary.loc['Intercept', 'z_suc_'+str(stage)] + (df_coeff_summary.loc['Temperature', 'z_suc_'+str(stage)] * df2_proc_data[str(stage)+'_suction_temp']) + (df_coeff_summary.loc['Pressure', 'z_suc_'+str(stage)] * df2_proc_data['suction_pressure_flange_' + str(stage)] * 100) + (df_coeff_summary.loc['Temperature^2', 'z_suc_'+str(stage)] * ((df2_proc_data[str(stage)+'_suction_temp'] ** 2))) + (df_coeff_summary.loc['Temperature Pressure', 'z_suc_'+str(stage)] * df2_proc_data[str(stage)+'_suction_temp'] * df2_proc_data['suction_pressure_flange_' + str(stage)] * 100) + (df_coeff_summary.loc['Pressure^2', 'z_suc_'+str(stage)] * ((df2_proc_data['suction_pressure_flange_' + str(stage)] * 100) ** 2))
    df2_proc_data['Zd_'+ str(stage)] = df_coeff_summary.loc['Intercept', 'z_disch_'+str(stage)] + (df_coeff_summary.loc['Temperature', 'z_disch_'+str(stage)] * df2_proc_data[str(stage)+'_discharge_temp']) + (df_coeff_summary.loc['Pressure', 'z_disch_'+str(stage)] * df2_proc_data['discharge_pressure_flange_' + str(stage)] * 100) + (df_coeff_summary.loc['Temperature^2', 'z_disch_'+str(stage)] * ((df2_proc_data[str(stage)+'_discharge_temp'] ** 2))) + (df_coeff_summary.loc['Temperature Pressure', 'z_disch_'+str(stage)] * df2_proc_data[str(stage)+'_discharge_temp'] * df2_proc_data['discharge_pressure_flange_' + str(stage)] * 100) + (df_coeff_summary.loc['Pressure^2', 'z_disch_'+str(stage)] * ((df2_proc_data['discharge_pressure_flange_' + str(stage)] * 100) ** 2))
    df2_proc_data['zavg ' + str(stage)] = (df2_proc_data['Zs_'+ str(stage)] + df2_proc_data['Zd_'+ str(stage)]) / 2
    df2_proc_data['Vsp_inlet_' + str(stage)] = df2_proc_data['Zs_'+ str(stage)] * vsp_const * (df2_proc_data[str(stage)+'_suction_temp'] + 273) / ((df1_config.loc['mol_wt', str(stage)] * df2_proc_data['suction_pressure_flange_' + str(stage)] * (10 ** 5)))
    df2_proc_data['Vsp_discharge_' + str(stage)] = df2_proc_data['Zd_'+ str(stage)] * vsp_const * (df2_proc_data[str(stage)+'_discharge_temp'] + 273) / ((df1_config.loc['mol_wt', str(stage)] * df2_proc_data['discharge_pressure_flange_' + str(stage)] * (10 ** 5)))
    df2_proc_data['stage_inlet_capacity_M ' + str(stage)] = df2_proc_data['stage_inlet_capacity_Q ' + str(stage)] / df2_proc_data['Vsp_inlet_' + str(stage)]
    df2_proc_data['stage_discharge_capacity_M ' + str(stage)] = df2_proc_data['stage_discharge_capacity_Q ' + str(stage)] / df2_proc_data['Vsp_discharge_' + str(stage)]
    df2_proc_data['k ' + str(stage)] = (((df_coeff_summary.loc['Intercept', 'cpcv_suc_'+str(stage)] + (df_coeff_summary.loc['Temperature', 'cpcv_suc_'+str(stage)] * df2_proc_data[str(stage)+'_suction_temp']) + (df_coeff_summary.loc['Pressure', 'cpcv_suc_'+str(stage)] * df2_proc_data['suction_pressure_flange_' + str(stage)] * 100) + (df_coeff_summary.loc['Temperature^2', 'cpcv_suc_'+str(stage)] * ((df2_proc_data[str(stage)+'_suction_temp'] ** 2))) + (df_coeff_summary.loc['Temperature Pressure', 'cpcv_suc_'+str(stage)] * df2_proc_data[str(stage)+'_suction_temp'] * df2_proc_data['suction_pressure_flange_' + str(stage)] * 100) + (df_coeff_summary.loc['Pressure^2', 'cpcv_suc_'+str(stage)] * ((df2_proc_data['suction_pressure_flange_' + str(stage)] * 100) ** 2))) + (df_coeff_summary.loc['Intercept', 'cpcv_disch_'+str(stage)] + (df_coeff_summary.loc['Temperature', 'cpcv_disch_'+str(stage)] * df2_proc_data[str(stage)+'_discharge_temp']) + (df_coeff_summary.loc['Pressure', 'cpcv_disch_'+str(stage)] * df2_proc_data['discharge_pressure_flange_' + str(stage)] * 100) + (df_coeff_summary.loc['Temperature^2', 'cpcv_disch_'+str(stage)] * ((df2_proc_data[str(stage)+'_discharge_temp'] ** 2))) + (df_coeff_summary.loc['Temperature Pressure', 'cpcv_disch_'+str(stage)] * df2_proc_data[str(stage)+'_discharge_temp'] * df2_proc_data['discharge_pressure_flange_' + str(stage)] * 100) + (df_coeff_summary.loc['Pressure^2', 'cpcv_disch_'+str(stage)] * ((df2_proc_data['discharge_pressure_flange_' + str(stage)] * 100) ** 2)))) / 2)
    df2_proc_data['k/k-1 ' + str(stage)] = df2_proc_data['k ' + str(stage)] / (df2_proc_data['k ' + str(stage)] - 1)
    df2_proc_data['Had ' + str(stage)] = df2_proc_data['zavg ' + str(stage)] * (vsp_const / (df1_config.loc['mol_wt', str(stage)]) * (df2_proc_data[str(stage)+'_suction_temp'] + 273) * df2_proc_data['k/k-1 ' + str(stage)] * (df2_proc_data['compression_ratio_' + str(stage)] ** (1 / df2_proc_data['k/k-1 ' + str(stage)]) - 1))
    df2_proc_data['adiabatic_disc_temp ' + str(stage)] = (df2_proc_data[str(stage)+'_suction_temp'] + 273) * (df2_proc_data['compression_ratio_' + str(stage)] ** (1 / df2_proc_data['k/k-1 ' + str(stage)]))
    df2_proc_data['adiabatic_eff%' + str(stage)] = (df2_proc_data['adiabatic_disc_temp ' + str(stage)]-273 - ((df2_proc_data[str(stage)+'_suction_temp']))) * 100 / ((df2_proc_data[str(stage)+'_discharge_temp']) - (df2_proc_data[str(stage)+'_suction_temp']))
    df2_proc_data['Pad ' + str(stage)] = df2_proc_data['stage_inlet_capacity_M ' + str(stage)] * df2_proc_data['Had ' + str(stage)] / (df2_proc_data['adiabatic_eff%' + str(stage)] / 100) * (1 / time_conv)
    df2_proc_data['zd_adiabatic_temp_disc_press ' + str(stage)] = df_coeff_summary.loc['Intercept', 'z_disch_'+str(stage)] + (df_coeff_summary.loc['Temperature', 'z_disch_'+str(stage)] * (df2_proc_data['adiabatic_disc_temp ' + str(stage)] + 273)) + (df_coeff_summary.loc['Pressure', 'z_disch_'+str(stage)] * df2_proc_data['discharge_pressure_flange_' + str(stage)] * 100) + (df_coeff_summary.loc['Temperature^2', 'z_disch_'+str(stage)] * (((df2_proc_data['adiabatic_disc_temp ' + str(stage)] - 273) ** 2))) + (df_coeff_summary.loc['Temperature Pressure', 'z_disch_'+str(stage)] * (df2_proc_data['adiabatic_disc_temp ' + str(stage)] - 273) * df2_proc_data['discharge_pressure_flange_' + str(stage)] * 100) + (df_coeff_summary.loc['Pressure^2', 'z_disch_'+str(stage)] * ((df2_proc_data['discharge_pressure_flange_' + str(stage)] * 100) ** 2))
    df2_proc_data['vsp_discharge ' + str(stage)] = df2_proc_data['Zd_'+ str(stage)] * vsp_const * (df2_proc_data[str(stage)+'_discharge_temp']+273) / ((df1_config.loc['mol_wt', str(stage)] * df2_proc_data['discharge_pressure_flange_' + str(stage)] * (10 ** 5)))
    df2_proc_data['stage_discharge_capacity_M adiabatic ' + str(stage)] = df2_proc_data['stage_discharge_capacity_M ' + str(stage)] * df2_proc_data['adiabatic_eff%' + str(stage)] / 100
    df2_proc_data['actual_disc_temp_' + str(stage)] = df2_proc_data[str(stage)+'_discharge_temp'] + 273
    df2_proc_data['Dish temp - Ad. Disch temp' +str(stage)]=df2_proc_data['actual_disc_temp_' + str(stage)]-df2_proc_data['adiabatic_disc_temp ' + str(stage)]
    df2_proc_data['Flow factor' +str(stage)]=(df2_proc_data['stage_inlet_capacity_M ' + str(stage)])/(df2_proc_data['stage_discharge_capacity_M ' + str(stage)])
    df2_proc_data['Inlet Capacity' +str(stage)]=df2_proc_data['stage_inlet_capacity_Q ' + str(stage)]*((df1_config.loc['reference_temperature', str(stage)]+273)/(df2_proc_data[str(stage)+'_suction_temp'] + 273))*(df2_proc_data['suction_pressure_flange_' + str(stage)]/df1_config.loc['reference_pressure', str(stage)])*(1/df2_proc_data['Zs_'+ str(stage)])*24*(10**-3)
    df2_proc_data['Discharge Capacity' +str(stage)]=df2_proc_data['stage_discharge_capacity_Q ' + str(stage)]*((df1_config.loc['reference_temperature', str(stage)]+273)/(df2_proc_data[str(stage)+'_discharge_temp'] + 273))*(df2_proc_data['discharge_pressure_flange_' + str(stage)]/df1_config.loc['reference_pressure', str(stage)])*(1/df2_proc_data['Zd_'+ str(stage)])*24*(10**-3)
    df2_proc_data['Sp. consumption' +str(stage)]=df2_proc_data['Pad ' + str(stage)]/((df2_proc_data['Inlet Capacity' +str(stage)]+df2_proc_data['Discharge Capacity' +str(stage)])/2)


def process_stages(df1_config, df2_proc_data, num_stages):
    for i in range(num_stages):
        stage = f'S{i + 1}'
        calc(df1_config, df2_proc_data, stage)
num_stages = 2
process_stages(df1_config, df2_proc_data, num_stages)
print(df2_proc_data.head())


# In[ ]:
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
st.set_page_config(layout="wide")

col1, col2, col3 = st.columns([1, 4, 1])  # Adjust the ratios as needed

# Place the left image in the first column
with col1:
    st.image("DresserRandSiemensLogo.jpeg", width=200)
with col2:
    st.markdown("<h1 style='text-align: center;'>Compressor Health Monitoring</h1>", unsafe_allow_html=True)

with col3:
    st.image("IngeneroLogo.jpeg", width=200)


# Side by Side Display for S1 and S2
excel_file = pd.ExcelFile("GERC_A_PARA_GUI_rev4.xlsm")
dict_stg = {'Stage 1': {'tab1': [7, 368, 'table1_df'], 'tab2': [372, 733, 'table2_df'], 'tab3': [745, 1106, 'table3_df'], 'tab4': [1110, 1471,'table4_df']},
            'Stage 2': {'tab1': [7, 368, 'table1_df'], 'tab2': [372, 733, 'table2_df'], 'tab3': [745, 1106, 'table3_df'], 'tab4': [1110, 1471,'table4_df']}
           }
def read_tables_from_excel(excel_file, dict_stg):
    for stg in dict_stg:
        
        sheet_name = stg
        print('Sheet Name: ', sheet_name)

        for tab in dict_stg[stg]:
            
            print ('Tab: ',dict_stg[stg][tab]) 

            skip_rows = dict_stg[stg][tab][0]-1
            n_rows = dict_stg[stg][tab][1] - dict_stg[stg][tab][0] + 1
            
            print('Skip rows: ', skip_rows)
            print('N rows: ', n_rows)
            
            table_name = f"{stg}_{tab}"
            table_df = pd.read_excel(excel_file, sheet_name, header=0, skiprows=skip_rows, nrows=n_rows)
            print(f"{table_name} DataFrame: \n",table_df.head(2))
            
            dict_stg[stg][tab][2] = table_df
            print(f"{table_name} DataFrame: \n",dict_stg[stg][tab][2])
read_tables_from_excel(excel_file, dict_stg)
#min_gas_load_stage1 = min(dict_stg['Stage 1']['tab3'][2]['Gas load, KN'])
# %%
import streamlit as st
import pandas as pd

# Assuming df2_proc_data and dict_stg are defined
# Define the width ratios for each column
# Create columns with adjustable width ratios
col1, col2, col3 = st.columns([0.75, 1, 1])

# Data for Stage 1
with col1:
    excel_file1 = pd.read_excel("GERC_A_PARA_GUI_rev4.xlsm", sheet_name='cur_data')

    @st.cache_data(ttl=60)  # Cache with a timeout of 1 min
    def load_data():
        return pd.read_excel("GERC_A_PARA_GUI_rev4.xlsm", sheet_name='cur_data')

    # Main Streamlit app
    def main():

        # Load data
        data = load_data()

        # Function to check valve leakage status
        def check_valve_leakage(data):
            suction_valve_leak_stage1 = any(df2_proc_data['Flow factor' +'S1'] > 1.04)
            suction_valve_leak_stage2 = any(df2_proc_data['Flow factor' + 'S2'] > 1.04)
            disch_valve_leak_stage1 = any(df2_proc_data['Flow factor' +'S1'] < 0.98)
            disch_valve_leak_stage2 = any(df2_proc_data['Flow factor' + 'S2'] < 0.98)
            cylinder_leak_stage1 = any(df2_proc_data['Dish temp - Ad. Disch temp' + 'S1'] > 8.5)
            cylinder_leak_stage2 = any(df2_proc_data['Dish temp - Ad. Disch temp' + 'S2'] > 8.5)
            return suction_valve_leak_stage1, suction_valve_leak_stage2, disch_valve_leak_stage1, disch_valve_leak_stage2, cylinder_leak_stage1, cylinder_leak_stage2

        # Check valve leakage status
        suction_valve_leak_stage1, suction_valve_leak_stage2, disch_valve_leak_stage1, disch_valve_leak_stage2, cylinder_leak_stage1, cylinder_leak_stage2 = check_valve_leakage(data)
        
        # CSS styles
        red_checkbox_style = """<style>input[type="checkbox"].red {color:red !important;} </style>"""
        green_checkbox_style = """<style>input[type="checkbox"].green {color:green !important;} </style>"""

        # Display valve leakage status
        st.write("Valve Health Status", fontsize=12, fontweight='bold')
        col1, col2 = st.columns([30,1.5])
        with col1:
            st.text("suction valve leak - stage 1 :")
        with col2:
            if suction_valve_leak_stage1:
                st.markdown('<div style="display: inline-block; width: 20px; height: 20px; background-color: red;"></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div style="display: inline-block; width: 20px; height: 20px; background-color: green;"></div>', unsafe_allow_html=True)

        col1, col2 = st.columns([60, 3])

        with col1:
            st.text("suction valve leak - stage 2:")
        with col2:
            if suction_valve_leak_stage2:
                st.markdown('<div style="display: inline-block; width: 20px; height: 20px; background-color: red;"></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div style="display: inline-block; width: 20px; height: 20px; background-color: green;"></div>', unsafe_allow_html=True)

        col1, col2 = st.columns([90, 4.5])

        with col1:
            st.text("Discharge valve leak - stage 1:")
        with col2:
            if disch_valve_leak_stage1:
                st.markdown('<div style="display: inline-block; width: 20px; height: 20px; background-color: red;"></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div style="display: inline-block; width: 20px; height: 20px; background-color: green;"></div>', unsafe_allow_html=True)
        col1, col2 = st.columns([120,7])
        with col1:
            st.text("Discharge valve leak - stage 2:")
        with col2:
            if disch_valve_leak_stage2:
                st.markdown('<div style="display: inline-block; width: 20px; height: 20px; background-color: red;"></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div style="display: inline-block; width: 20px; height: 20px; background-color: green;"></div>', unsafe_allow_html=True)
        col1, col2 = st.columns([150, 8])
        with col1:
            st.text("Cylinder leak - stage 1:")
        with col2:
            if cylinder_leak_stage1:
                st.markdown('<div style="display: inline-block; width: 20px; height: 20px; background-color: red;"></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div style="display: inline-block; width: 20px; height: 20px; background-color: green;"></div>', unsafe_allow_html=True)

        col1, col2 = st.columns([180, 9])
        with col1:
            st.text("Cylinder leak - stage 2:")
        with col2:
            if cylinder_leak_stage2:
                st.markdown('<div style="display: inline-block; width: 20px; height: 20px; background-color: red;"></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div style="display: inline-block; width: 20px; height: 20px; background-color: green;"></div>', unsafe_allow_html=True)

    if __name__ == "__main__":
        main()

# Image in the middle
with col2:
    st.image("Recip crosssection.jpg", caption='Compressor Image')

# Data for Stage 1 and Stage 2 dropdown
with col3:
    # Dropdown for selecting Stage 1 or Stage 2
    stage_selection = st.selectbox("Select Stage", ["Stage 1", "Stage 2"])

    # Data for Stage 1
    if stage_selection == "Stage 1":
        data_s1 = {
            "Stage 1": [
                "Suction Vol. Efficiency",
                "Discharge Vol. Efficiency",
                "Indicated Powe",
                "Adiabatic Discharge Temperature",
                "Discharge Temperature",
                "Suction Capacity",
                "Discharge Capacity",
                "Average Capacity",
                "Flow Balance",
                "Power/Avg Capacity Ratio",
                "Peak Rod Load (Gas), Tension",
                "Peak Rod Load (Gas), Compression",
                "Peak Combined Rod load, Tension",
                "Peak Combined Rod load, Compression"
            ],
            "Values": [
                df2_proc_data['cal_avg_inlet_vol_eff %' + str('S1')].iloc[0],
                (df2_proc_data['HE_discharge_vol_eff %' + str('S1')].iloc[0] + df2_proc_data['CE_discharge_vol_eff %' + str('S1')].iloc[0]) / 2,
                df2_proc_data['Pad ' + str('S1')].iloc[0],
                df2_proc_data['adiabatic_disc_temp ' + str('S1')].iloc[0] - 273,
                df2_proc_data['actual_disc_temp_' + str('S1')].iloc[0] - 273,
                df2_proc_data['Inlet Capacity' + str('S1')].iloc[0],
                df2_proc_data['Discharge Capacity' + str('S1')].iloc[0],
                (df2_proc_data['Inlet Capacity' + str('S1')].iloc[0] + df2_proc_data['Discharge Capacity' + str('S1')].iloc[0]) / 2,
                df2_proc_data['Flow factor' + str('S1')].iloc[0],
                df2_proc_data['Sp. consumption' + str('S1')].iloc[0],
                max(dict_stg['Stage 1']['tab3'][2]['Gas load, KN']),
                min(dict_stg['Stage 1']['tab3'][2]['Gas load, KN']),
                max(dict_stg['Stage 1']['tab3'][2]['Combined rod load, KN']),
                min(dict_stg['Stage 1']['tab3'][2]['Combined rod load, KN'])
            ]
        }
        df_s1 = pd.DataFrame(data_s1)
        st.dataframe(df_s1, height=200)

    # Data for Stage 2
    elif stage_selection == "Stage 2":
        data_s2 = {
            "Stage 2": [
                "Suction Vol. Efficiency",
                "Discharge Vol. Efficiency",
                "Indicated Powe",
                "Adiabatic Discharge Temperature",
                "Discharge Temperature",
                "Suction Capacity",
                "Discharge Capacity",
                "Average Capacity",
                "Flow Balance",
                "Power/Avg Capacity Ratio",
                "Peak Rod Load (Gas), Tension",
                "Peak Rod Load (Gas), Compression",
                "Peak Combined Rod load, Tension",
                "Peak Combined Rod load, Compression"
            ],
            "Values": [
                df2_proc_data['cal_avg_inlet_vol_eff %' + str('S2')].iloc[0],
                (df2_proc_data['HE_discharge_vol_eff %' + str('S2')].iloc[0] + df2_proc_data['CE_discharge_vol_eff %' + str('S2')].iloc[0]) / 2,
                df2_proc_data['Pad ' + str('S2')].iloc[0],
                df2_proc_data['adiabatic_disc_temp ' + str('S2')].iloc[0] - 273,
                df2_proc_data['actual_disc_temp_' + str('S2')].iloc[0] - 273,
                df2_proc_data['Inlet Capacity' + str('S2')].iloc[0],
                df2_proc_data['Discharge Capacity' + str('S2')].iloc[0],
                (df2_proc_data['Inlet Capacity' + str('S2')].iloc[0] + df2_proc_data['Discharge Capacity' + str('S2')].iloc[0]) / 2,
                df2_proc_data['Flow factor' + str('S2')].iloc[0],
                df2_proc_data['Sp. consumption' + str('S2')].iloc[0],
                max(dict_stg['Stage 2']['tab3'][2]['Gas load, KN']),
                min(dict_stg['Stage 2']['tab3'][2]['Gas load, KN']),
                max(dict_stg['Stage 2']['tab3'][2]['Combined rod load, KN']),
                min(dict_stg['Stage 2']['tab3'][2]['Combined rod load, KN'])
            ]
        }
        df_s2 = pd.DataFrame(data_s2)
        st.dataframe(df_s2, height=200)


from matplotlib.animation import FuncAnimation


# Function to plot pressure vs time for Stage 1
def plot_stage1():
    fig, ax = plt.subplots()
    ax.plot(dict_stg['Stage 1']['tab3'][2]['Crank angle'], dict_stg['Stage 1']['tab3'][2]['HE, Press'], color='red', label='HE')
    ax.plot(dict_stg['Stage 1']['tab3'][2]['Crank angle'], dict_stg['Stage 1']['tab4'][2]['CE'], color='orange', label='CE')
    
    ax.grid(color='white', linestyle='--', linewidth=0.25)
    ax.set_xlabel('Crank angle, deg')
    ax.set_ylabel('Pressure, bar, abs')
    ax.set_title('Stage I - Pressure vs. time', fontsize=12, fontweight='bold')
    ax.legend()
    ax.set_facecolor('black')
    return fig

# Function to plot pressure vs time for Stage 2
def plot_stage2():
    fig, ax = plt.subplots()
    ax.plot(dict_stg['Stage 2']['tab3'][2]['Crank angle'], dict_stg['Stage 2']['tab3'][2]['Pressure, Head end, bar abs'], color='red', label='HE')
    ax.plot(dict_stg['Stage 2']['tab3'][2]['Crank angle'], dict_stg['Stage 2']['tab4'][2]['Pressure, Crank end, bar abs'], color='orange', label='CE')
    
    ax.grid(color='white', linestyle='--', linewidth=0.25)
    ax.set_xlabel('Crank angle, deg')
    ax.set_ylabel('Pressure, bar, abs')
    ax.set_title('Stage II - Pressure vs. time', fontsize=12, fontweight='bold')
    ax.legend()
    ax.set_facecolor('black')
    return fig

# Function to plot HE-PV plot for Stage 1
def plot_stage1_he_pv():
    fig, ax = plt.subplots()
    ax.plot(dict_stg['Stage 1']['tab3'][2]['Swept vol, HE, %'], dict_stg['Stage 1']['tab3'][2]['HE, Press'], color='orange', label='HE')
    
    ax.grid(color='white', linestyle='--', linewidth=0.25)
    ax.set_xlabel('Swept vol, %')
    ax.set_ylabel('Pressure, bar, abs')
    ax.set_title('Stage I - HE PV Plot', fontsize=12, fontweight='bold')
    ax.legend()
    ax.set_facecolor('black')
    return fig

# Function to plot HE-PV plot for Stage 2
def plot_stage2_he_pv():
    fig, ax = plt.subplots()
    ax.plot(dict_stg['Stage 2']['tab3'][2]['Swept vol, HE, %'], dict_stg['Stage 2']['tab3'][2]['Pressure, Head end, bar abs'], color='orange', label='HE')
    ax.grid(color='white', linestyle='--', linewidth=0.25)
    ax.set_xlabel('Swept vol, %')
    ax.set_ylabel('Pressure, bar, abs')
    ax.set_title('Stage II - HE PV Plot', fontsize=12, fontweight='bold')
    ax.legend()
    ax.set_facecolor('black')
    return fig


# Function to plot rod load for Stage 1 and Stage 2
def plot_stage1_rod_load():
    fig, ax = plt.subplots()
    ax.plot(dict_stg['Stage 1']['tab3'][2]['Crank angle'], dict_stg['Stage 1']['tab3'][2]['Gas load, KN'], color='cyan', label='Gas Load')
    ax.plot(dict_stg['Stage 1']['tab3'][2]['Crank angle'], dict_stg['Stage 1']['tab3'][2]['Finertia  = mrecip*r*omega^2[cos(omega*t) + r/l*cos(2*omega*t)]'], color='red', label='HE')
    ax.plot(dict_stg['Stage 1']['tab3'][2]['Crank angle'], dict_stg['Stage 1']['tab3'][2]['Combined rod load, KN'], color='yellow', label='Combined Load')
    ax.plot(dict_stg['Stage 1']['tab3'][2]['Crank angle'], dict_stg['Stage 1']['tab3'][2]['Max rod load, compression, KN'], color='orange', linestyle='--')
    ax.plot(dict_stg['Stage 1']['tab3'][2]['Crank angle'], dict_stg['Stage 1']['tab3'][2]['Max rod load, Tension, KN'], color='red', linestyle='--')
    
    ax.grid(color='white', linestyle='--', linewidth=0.25)
    ax.set_facecolor('black')
    ax.set_xlabel('Crank angle, deg')
    ax.set_ylabel('Rod load, KN')
    ax.set_title('Stage I - Rod Load', fontsize=12, fontweight='bold')
    ax.legend()
    return fig

def plot_stage2_rod_load():
    fig, ax = plt.subplots()
    ax.plot(dict_stg['Stage 2']['tab3'][2]['Crank angle'], dict_stg['Stage 2']['tab3'][2]['Gas load, KN'], color='cyan', label='Gas Load')
    ax.plot(dict_stg['Stage 2']['tab3'][2]['Crank angle'], dict_stg['Stage 2']['tab3'][2]['Finertia  = mrecip*r*omega^2[cos(omega*t) + r/l*cos(2*omega*t)]'], color='red', label='HE')
    ax.plot(dict_stg['Stage 2']['tab3'][2]['Crank angle'], dict_stg['Stage 2']['tab3'][2]['Combined rod load, KN'], color='yellow', label='Combined Load')
    ax.plot(dict_stg['Stage 2']['tab3'][2]['Crank angle'], dict_stg['Stage 2']['tab3'][2]['Max rod load, compression, KN'], color='orange', linestyle='--')
    ax.plot(dict_stg['Stage 2']['tab3'][2]['Crank angle'], dict_stg['Stage 2']['tab3'][2]['Max rod load, Tension, KN'], color='red', linestyle='--')
       
    ax.grid(color='white', linestyle='--', linewidth=0.25)
    ax.set_facecolor('black')
    ax.set_xlabel('Crank angle, deg')
    ax.set_ylabel('Rod load, KN')
    ax.set_title('Stage II - Rod Load', fontsize=12, fontweight='bold')
    ax.legend()
    return fig

# Function to plot CE-PV plot for Stage 1
def plot_stage1_ce_pv():
    fig, ax = plt.subplots()
    ax.plot(dict_stg['Stage 1']['tab3'][2]['Swept vol, HE, %'], dict_stg['Stage 1']['tab4'][2]['CE'], color='orange', label='CE')
    
    ax.grid(color='white', linestyle='--', linewidth=0.25)
    ax.set_xlabel('Swept vol, %')
    ax.set_ylabel('Pressure, bar, abs')
    ax.set_title('Stage I - CE PV Plot', fontsize=7)
    ax.legend()
    ax.set_facecolor('black')
    ax.set_xlim(0, 100)
    ax.set_ylim(20, 30)
    return fig

# Function to plot CE-PV plot for Stage 2
def plot_stage2_ce_pv():
    fig, ax = plt.subplots()
    ax.plot(dict_stg['Stage 2']['tab3'][2]['Swept vol, HE, %'], dict_stg['Stage 2']['tab4'][2]['Pressure, Crank end, bar abs'], color='orange', label='CE')
    
    ax.grid(color='white', linestyle='--', linewidth=0.25)
    ax.set_xlabel('Swept vol, %')
    ax.set_ylabel('Pressure, bar, abs')
    ax.set_title('Stage II - CE PV Plot', fontsize=7)
    ax.legend()
    ax.set_facecolor('black')
    ax.set_xlim(0, 100)
    ax.set_ylim(20, 40)
    return fig


# Function to plot Stage 1 Flow Balance
def plot_stage1_flow_balance():
    fig, ax = plt.subplots()
        
    ax.plot(database_df['Date'].iloc[1:26], database_df[' Stg I Flow factor'].iloc[1:26], marker='o', linestyle='-', color='orange')
    
    ax.grid(color='white', linestyle='--', linewidth=0.25)
    ax.set_xlabel('Swept vol, %')
    ax.set_ylabel('Pressure, bar, abs')
    ax.set_title('Stage I - Flow Balance', fontsize=7)
    ax.legend()
    ax.set_facecolor('black')
    ax.tick_params(axis='x', rotation=45)
    return fig
    

    
    plt.show()

# Function to plot Stage 2 Flow Balance
def plot_stage2_flow_balance():
    fig, ax = plt.subplots()
    
    # Stage II Flow Balance
    ax.plot(database_df['Date'].iloc[1:26], database_df[' Stg II Flow factor'].iloc[1:26], marker='o', linestyle='-', color='orange')
    ax.grid(color='white', linestyle='--', linewidth=0.25)
    ax.set_ylabel('Flow factor')
    ax.set_title('Stage II - Flow Balance', fontsize=7)
    ax.tick_params(axis='x', rotation=45)
    ax.set_facecolor('black')
    return fig
    
    plt.show()

# Function to plot Stage 1 Adiabatic Flow Balance
def plot_stage1_adiabatic_flow_balance():
    fig, ax = plt.subplots()
    
    # Stage I Adiabatic Flow Balance
    ax.plot(database_df['Date'].iloc[1:26], database_df['Stg I Ad. Flow Factor'].iloc[1:26], marker='o', linestyle='-', color='orange')
    ax.grid(color='white', linestyle='--', linewidth=0.25)
    ax.set_ylabel('Ad. Flow factor')
    ax.set_title('Stage I - Adiabatic Flow Balance', fontsize=7)
    ax.tick_params(axis='x', rotation=45)
    ax.set_facecolor('black')
    return fig
    plt.show()

# Function to plot Stage 2 Adiabatic Flow Balance
database_df = excel_file.parse('database')
def plot_stage2_adiabatic_flow_balance():
    fig, ax = plt.subplots()
    
    # Stage II Adiabatic Flow Balance
    ax.plot(database_df['Date'].iloc[1:26], database_df['Stg II Ad. Flow Factor'].iloc[1:26], marker='o', linestyle='-', color='orange')
    ax.grid(color='white', linestyle='--', linewidth=0.25)
    ax.set_ylabel('Ad. Flow factor')
    ax.set_title('Stage II - Adiabatic Flow Balance', fontsize=7)
    ax.tick_params(axis='x', rotation=45)
    ax.set_facecolor('black')
    return fig
    plt.show()

# Function to plot Stage 1 Delta Temp
def plot_stage1_delta_temp():
    fig, ax = plt.subplots()
    
    # Stage I Delta Temp
    ax.plot(database_df['Date'].iloc[1:26], database_df['Stg I Act. Disc. Temp - Ad. Disch Temp'].iloc[1:26], marker='o', linestyle='-', color='orange')
    ax.grid(color='white', linestyle='--', linewidth=0.25)
    ax.set_ylabel('Act. - Ad. disch. temp')
    ax.set_title('Stage I - Disch temp', fontsize=7)
    ax.tick_params(axis='x', rotation=45)
    ax.set_facecolor('black')
    return fig
    plt.show()

# Function to plot Stage 2 Delta Temp
def plot_stage2_delta_temp():
    fig, ax = plt.subplots()
    
    # Stage II Delta Temp
    ax.plot(database_df['Date'].iloc[1:26], database_df['Stg II Act. Disc. Temp - Ad. Disch Temp'].iloc[1:26], marker='o', linestyle='-', color='orange')
    ax.grid(color='white', linestyle='--', linewidth=0.25)
    ax.set_ylabel('Act. - Ad. disch. temp')
    ax.set_title('Stage II - Disch Temp', fontsize=7)
    ax.tick_params(axis='x', rotation=45)
    ax.set_facecolor('black')
    return fig
    plt.show()

    plt.tight_layout()
 




# Main Streamlit appimport streamlit as st

import streamlit as st

def main():
    # Create the layout with two columns
    outer_col1, outer_col2 = st.columns(2)

    with outer_col1:
        # List widget to select the plot
        plot_options = ['Pressure vs Time', 'HE-PV Plot', 'Rod Load', 'CE PV']
        plot_choice = st.selectbox('Time Independent Plots', plot_options, key='time_dependent_plots')

        # Display the selected plot
        if plot_choice == 'Pressure vs Time':
            # Plot for Stage 1
            fig1 = plot_stage1()
            # Plot for Stage 2
            fig2 = plot_stage2()

        elif plot_choice == 'HE-PV Plot':
            # Plot for Stage 1 HE-PV
            fig1 = plot_stage1_he_pv()
            # Plot for Stage 2 HE-PV
            fig2 = plot_stage2_he_pv()

        elif plot_choice == 'Rod Load':
            # Plot for Stage 1 Rod Load
            fig1 = plot_stage1_rod_load()
            # Plot for Stage 2 Rod Load
            fig2 = plot_stage2_rod_load()

        elif plot_choice == 'CE PV':
            # Plot for Stage 1 CE PV
            fig1 = plot_stage1_ce_pv()
            # Plot for Stage 2 CE PV
            fig2 = plot_stage2_ce_pv()

        # Display plots side by side using columns layout
        inner_col1, inner_col2 = st.columns(2)
        with inner_col1:
            st.pyplot(fig1)
        with inner_col2:
            st.pyplot(fig2)

    with outer_col2:
        # List widget to select the plot for the second column
        plot_options = ['Flow Balance', 'Adiabatic Flow Balance', 'Delta Temp']
        plot_choice = st.selectbox('Time Dependent Plots', plot_options, key='time_independent_plots')

        # Display the selected plot for the second column
        if plot_choice == 'Flow Balance':
            # Plot for Stage 1 Flow Balance
            fig1 = plot_stage1_flow_balance()
            # Plot for Stage 2 Flow Balance
            fig2 = plot_stage2_flow_balance()

        elif plot_choice == 'Adiabatic Flow Balance':
            # Plot for Stage 1 Adiabatic Flow Balance
            fig1 = plot_stage1_adiabatic_flow_balance()
            # Plot for Stage 2 Adiabatic Flow Balance
            fig2 = plot_stage2_adiabatic_flow_balance()

        elif plot_choice == 'Delta Temp':
            # Plot for Stage 1 Delta Temp
            fig1 = plot_stage1_delta_temp()
            # Plot for Stage 2 Delta Temp
            fig2 = plot_stage2_delta_temp()

        # Display plots side by side using columns layout
        inner_col1, inner_col2 = st.columns(2)
        with inner_col1:
            st.pyplot(fig1)
        with inner_col2:
            st.pyplot(fig2)

if __name__ == "__main__":
    main()


from PIL import Image

# Add buttons with values in front of different parts of the compressor
st.button(label='Value 1', key='part1')
st.button(label='Value 2', key='part2')
st.button(label='Value 3', key='part3')