#!/usr/bin/env python
# coding: utf-8

# In[2]:


### Importing required libraries


# In[3]:


import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings("ignore")


# ### Creating dataframe to store required data

# In[4]:


df1_config=pd.read_excel(r"C:\Users\Naina Sisodia\Desktop\excel_to_python.xlsx", sheet_name='config_data')
df2_proc_data=pd.read_excel(r"C:\Users\Naina Sisodia\Desktop\excel_to_python.xlsx", sheet_name='Data')
df_tag_list=pd.read_excel(r"C:\Users\Naina Sisodia\Desktop\excel_to_python.xlsx", sheet_name='tag_description')
df_final_cols=pd.read_excel(r"C:\Users\Naina Sisodia\Desktop\excel_to_python.xlsx", sheet_name='final_col_list')
df_coeff_summary=pd.read_excel(r"C:\Users\Naina Sisodia\Desktop\CoeffsLinearReg (1).xlsx")


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
    df2_proc_data['HE_inlet_vol_eff %' + str(stage)] = ((df2_proc_data['BDC_V2' + str(stage)] - df2_proc_data['head_end_V1' + str(stage)]) * 100) / (df2_proc_data['BDC_V2' + str(stage)] - df2_proc_data['(V4) TDC' + str(stage)])
    df2_proc_data['CE_inlet_vol_eff %' + str(stage)] = ((df2_proc_data['BDC_V2' + str(stage)] - df2_proc_data['CE_V1' + str(stage)]) * 100) / (df2_proc_data['BDC_V2' + str(stage)] - df2_proc_data['TDC_V4' + str(stage)])
    df2_proc_data['HE_discharge_vol_eff %' + str(stage)] = ((df2_proc_data['HE_V3' + str(stage)] - df2_proc_data['(V4) TDC' + str(stage)]) * 100) / (df2_proc_data['BDC_V2' + str(stage)] - df2_proc_data['(V4) TDC' + str(stage)])
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
def process_stages(df1_config, df2_proc_data, num_stages):
    for i in range(num_stages):
        stage = f'S{i + 1}'
        calc(df1_config, df2_proc_data, stage)
num_stages = 2
process_stages(df1_config, df2_proc_data, num_stages)
print(df2_proc_data.head())


# In[ ]:




