# Interactive battery simulator v0.1
# Moix P-O ✌️
# Albedo Engineering 2025
# MIT licence

#to run the app: streamlit run streamlit_battery_simulator.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import datetime
import random as rnd

#home made import:
#from groupe_e_access_functions import *
#from meteo_access_functions import *
from solarsystem import *
from advanced_figures import *

#constants
INVERTER_STANDBY_W = 50  #Watts
SOC_FOR_END_OF_DISCHARGE = 5.0  #for islanding case

#EFFICIENCY_BATT_ONE_WAY = 0.95  #TODO make variable



st.set_page_config(page_title="Battery Simulator", page_icon='🔋',layout="wide")

# --- Initialisation du state qui persiste pour tracer les résultats de plusieurs simules ---
if "battery_size_kwh_usr_input" not in st.session_state:
    st.session_state.battery_size_kwh_usr_input = 10.0  # valeur par défaut du slider

# Historique : liste de {timestamp, values}
if "simulation_results_history" not in st.session_state:
    st.session_state.simulation_results_history = []
    

#**************
# SIDEBAR
### Create sidebar with the options for simulation
with st.sidebar:

    st.title("⚙️ Simulation Settings ")

    st.write("🔋 Storage used for simulation")
    battery_size_kwh_usr_input = st.slider("Battery capacity (kWh): ", min_value=2.0, max_value=50.0, value=10.0, step=1.0)
    # On garde en state la dernière valeur courante
    st.session_state.battery_size_kwh_usr_input = battery_size_kwh_usr_input

 
    st.markdown("---")
    st.write("☀️ Solar used for simulation, scale from original data measured on each house")
    solar_scale_usr_input = st.slider("Solar installed (%): ", min_value=0.0, max_value=300.0, value=100.0, step=10.0)
    
    
    st.markdown("---")
    st.write("⚡💸 Electricity Prices ")
    
    price_type_usr_input = st.radio(
        "Select your tarif",
        ["**Fixed price**", "**Dynamic**"],
        captions=[
            "simple tarif for buy and sale",
            "Dynamic tarif of groupe-E.",
        ],
    )

    if price_type_usr_input == "**Fixed price**":
        st.write("You selected fixed price, enter them:")
        fixed_price_buy_usr_input = st.slider("Buy price (ct/kWh): ", min_value=5.0, max_value=40.0, value=25.6, step=0.1) / 100  # directly in CHF/kWh
        
    else:
        st.write("The stored groupe-E Vario price of 2024 are used for electrity buying.")
        fixed_price_buy_usr_input = 0.0
    #flat sell price is for both
    fixed_price_sell_usr_input = st.slider("Sell PV price (ct/kWh): ", min_value=5.0, max_value=40.0, value=11.2, step=0.1) / 100  # directly in CHF/kWh



    st.markdown("---")
    st.write("**Chose a dataset dataset 🏠** ")

    options = ["House1.csv", "House2.csv", "House3.csv", "House4.csv", "Building5.csv"]
    dataset_choice = st.selectbox("Choose one option:", options)

    st.write("your data set :", dataset_choice, " is measured on:")
    
    if dataset_choice == "House1.csv":
        st.write("villa moderne, PAC, conso faible et optimisee solaire")
    elif dataset_choice == "House2.csv":
        st.write("villa 2000, PAC, voiture électrique")
    elif dataset_choice == "House3.csv":
        st.write("villa 1990, plaine, PAC")
    elif dataset_choice == "House4.csv":
        st.write("ancienne grande maison, chauffage électrique")
    elif dataset_choice == "Building5.csv":
        st.write("logement 1990 + entreprise")            




    st.markdown("---")
    st.write("**👷 More Advanced settings** ")

    batt_charge_power_rate_user_input = st.slider("Battery max charge power rate (C): ", min_value=0.1, max_value=2.0, value=0.5, step=0.05, help="C rate relates the battery capacity to the power it can give.")
    battery_charge_power_kw = batt_charge_power_rate_user_input * battery_size_kwh_usr_input
    st.write("The max charge/discharge power is set to " + f"{battery_charge_power_kw :.1f}"+" kW")
    st.write("C/2 would be a reasonable charge/discharge limit, note that this limit is applied all day")
    batt_soc_for_backup_user_input = st.slider("Battery SOC reserved for backup (%): ", min_value=10.0, max_value=100.0, value=20.0, step=1.0, help="Battery will not discharge below this SOC.")
    st.write(f"The battery stops to discharge at this level, note that real battery don't go under {SOC_FOR_END_OF_DISCHARGE}%")

    st.write(" ")
    soc_init_user_input = st.slider("Battery initial SOC for simulation (%): ", min_value=20.0, max_value=100.0, value=50.0, step=1.0)



    # st.markdown("---")


    # st.markdown("---")
    # st.write("⏱️📈 📊 Planification with simple charge and discharge setpoint")

    # threshold_discharge = st.slider("⚡ Discharge when energy is expensive above (CHF/kWh): ", min_value=0.0, max_value=0.5, value=0.25, step=0.01)
    # threshold_charge  = st.slider("⚡ Charge when energy is cheap below (CHF/kWh): ", min_value=0.0, max_value=0.5, value=0.17, step=0.01)
    # st.write("between those levels nothing happens")

    # st.markdown("---")



    st.markdown("---")
    st.write("Battery sizer, version 0.1")
    st.write("✌️ Moix P-O, 2025")
    st.write("Streamlit for interactive dashboards...")
    



#**************
# MAIN PAGE
st.title(" 🔋 Storage Sizing for a Solar System")

if len(st.session_state.simulation_results_history)==0: 
    st.write(""" This simulation is based on the data of a full year of monitoring on real houses with PV production. 
            
    In the menu on the left, you can vary various setting (the size of the battery, the prices...) and see the changes on the graphs below. 
    The reference case is always the house with solar and the addition of storage is compared to it. If you change the solar (per example 200% to see what happens if you had 2 times mores solar), it becomes the new reference for storage evaluation.
        
    The relevant indicators are calculated:
    - self-consumption rate
    - self-sufficiency rate ( also called autarky rate)
    - the electricity taken from the grid and its annual cost
    - the electricity injected into the grid and its annual cost
    - the final bill (ex fixed fees) and the gain compared to the case without storage

    
    Various interactive plots of the power fluxes are given to vizualize what happens exactly in the house. 
    
        """)
        

    st.markdown("---")





####################
# FIRST: LOAD DATA AND PERFORM SIMULATION WITH USER ENTRIES
#********************************************************


# Current local datetime
now = datetime.datetime.now()
now_string_timestamp = now.strftime("%Y-%m-%d %H:%M:%S")


# Load Data
df_pow_profile = pd.read_csv(dataset_choice)

# Ensure 'Time' is a DateTime type#
df_pow_profile["Time"] = pd.to_datetime(df_pow_profile["Time"])

#Use Time  as index:
df_pow_profile = df_pow_profile.set_index("Time")



# # Show dataset preview
# st.write("📋 **Data Overview**")
# st.dataframe(df_pow_profile.head())


#take the data of the power profile un numpy (format for simulation)
pow_array_all = df_pow_profile["Consumption [kW]"].to_numpy()
solar_array_all = df_pow_profile["Solar power [kW]"].to_numpy()
solar_array_all_scaled = solar_array_all *solar_scale_usr_input / 100.0

#save in dataframe for easy display:
df_pow_profile["Solar power scaled"] = solar_array_all_scaled

#All the series for the case with solar only and no storage will be the reference:
df_pow_profile["grid power reference"] = pow_array_all-solar_array_all_scaled #all grid balance without storage with scaled solar

# Replace all positive values with 0 to have the injection only, note the injection is negative power on the grid
df_pow_profile["grid injection reference"] = df_pow_profile["grid power reference"].mask(df_pow_profile["grid power reference"] > 0, 0.0)
# Replace all negative values with 0 to have the consumption only
df_pow_profile["grid consumption reference"] = df_pow_profile["grid power reference"].mask(df_pow_profile["grid power reference"] < 0, 0.0)



#Add the column to the dataframe:
consumption_kWh = df_pow_profile["Consumption [kW]"].sum()/4.0
original_production_kWh = df_pow_profile["Solar power [kW]"].sum()/4.0 #from dataset
scaled_production_kWh = df_pow_profile["Solar power scaled"].sum()/4.0 #scaled and used

reference_grid_injection_kWh = -df_pow_profile["grid injection reference"].sum()/4.0
reference_grid_consumption_kWh = df_pow_profile["grid consumption reference"].sum()/4.0

reference_self_consumption_ratio = (scaled_production_kWh-reference_grid_injection_kWh) / scaled_production_kWh * 100
reference_autarky_ratio = (consumption_kWh-reference_grid_consumption_kWh) / consumption_kWh * 100.0  






#***********************
#Load the wanted prices
#***********************

length_profile = len(df_pow_profile.index)

#PV excess selling is same for both cases:
price_array_sell_pv = np.ones(length_profile) * fixed_price_sell_usr_input


if price_type_usr_input == "**Fixed price**":
    price_array_buy = np.ones(length_profile) * fixed_price_buy_usr_input

else:
    #here we load the buy price of groupe-e:

    # Load Data
    df_price_varioplus = pd.read_csv("vario_prices_2024.csv")
    #API to the electricity price:
    #df_price_varioplus = get_groupe_e_consumption_price(now, 1, 1)

    price_array_buy = df_price_varioplus["Varioplus"].values
    
    # Ensure 'Time' is a DateTime type#
    df_price_varioplus["Time"] = pd.to_datetime(df_price_varioplus["Time"])

    # #And plot the prices used:
    # fig_levels = px.line(df_price_varioplus, 
    #                             x=df_pow_profile.index, 
    #                             y=["Varioplus",  "Double Tarif"], 
    #                             title="⚡ Dynamic Electricity Price of Groupe-E 💸", 
    #                             labels={"value": "Energy price (CHF/kWh)", "variable": "Legend"})
    # st.plotly_chart(fig_levels)

#and put the prices in the dataframe:
df_pow_profile["price buy"] = price_array_buy
df_pow_profile["price sell PV"] = price_array_sell_pv



# compute the costs based on the selected price for the consumption only, it must be done for every quarters because 
df_pow_profile["CostForBuyingNoSolar"] = (df_pow_profile["Consumption [kW]"] * df_pow_profile["price buy"]/4.0)   
cost_buying_no_solar_chf = df_pow_profile["CostForBuyingNoSolar"].sum()
#print("Cost buying paid without solar and without storage:", cost_buying_no_solar_chf)

df_pow_profile["CostForBuyingSolarOnly"] = (df_pow_profile["grid consumption reference"] * df_pow_profile["price buy"]/4.0)   
cost_buying_solar_only_chf = df_pow_profile["CostForBuyingSolarOnly"].sum()
#print("Cost buying paid witht solar only, no storage:", cost_buying_solar_only_chf)

df_pow_profile["SellSolarOnly"] = -(df_pow_profile["grid injection reference"] * df_pow_profile["price sell PV"]/4.0)   
sellings_solar_only_chf = df_pow_profile["SellSolarOnly"].sum()
#print("Sold PV electricity with with solar only, no storage:", sellings_solar_only_chf)

bill_with_solar_only = cost_buying_solar_only_chf -  sellings_solar_only_chf

#*********************
# Perform the battery simulation
#*********************



##########################################
#Let's simulate the solar system with a battery:
#########################################################################
# with the solarsystem.py object:

solar_system = SolarSystem("M-P-O","Rue du Solaire 6, 2050 Transition" )

# properties initialisation  
solar_system.batt_capacity_kWh = battery_size_kwh_usr_input #10*1 # in kWh
solar_system.soc_init = soc_init_user_input # in %
solar_system.soc_for_backup_user = batt_soc_for_backup_user_input
solar_system.max_power_charge = battery_charge_power_kw #to update the max charge used by default independently of the battery size
solar_system.max_power_discharge = -battery_charge_power_kw #same rate applied
solar_system.max_inverter_power = 150 #kW  a high value in order not to have caping   # 15kW  for the next3
solar_system.max_grid_injection_power = 150 #kW  a high value in order not to have caping 
solar_system.selfpowerconsumption = INVERTER_STANDBY_W / 1000




# solar_system.gps_location = [46.208, 7.394] 
# solar_system.pv_kW_installed = 9.24 #power installed on the roof
# solar_system.roof_orientation = -10 # 0=S, 90°=W, -90°=E, -180°=N (or -180)
# solar_system.roof_slope = 25.0
# solar_system.comment = "installed in June 2022"


#load data in the module for simulation:
solar_system.load_data_for_simulation(pow_array_all, solar_array_all_scaled, timestep=0.25)

# # #Test of some control variable:
# charge_command_array= df_price_varioplus["ChargeCommand"].to_numpy()
# discharge_command_array= df_price_varioplus["DischargeCommand"].to_numpy()

# #force charging on the grid:
# solar_system.delta_p_on_ac_source_profile = charge_command_array * battery_charge_power_kw
# #let discharging only during this time:
# solar_system.battery_max_discharge_setpoint_profile = - discharge_command_array * battery_charge_power_kw


#and run the simulation of the system with the loaded datas:
solar_system.run_storage_simulation(print_res=False)


#and retrieve the grid power and inject it in the dataframe:
grid_power_with_storage_array = solar_system.net_grid_balance_profile
df_pow_profile["Grid with storage"] = grid_power_with_storage_array 

battery_power_array = solar_system.clamped_batt_pow_profile
df_pow_profile["Battery power"] = battery_power_array 
#separate the positive and the negative power to compute charge and discharge energy:
df_pow_profile["Battery discharge power only"] = df_pow_profile["Battery power"].mask(df_pow_profile["Battery power"] > 0, 0.0)
df_pow_profile["Battery charge power only"] = df_pow_profile["Battery power"] .mask(df_pow_profile["Battery power"] < 0, 0.0)

# Replace all negative values with 0 to have the consumption only
df_pow_profile["Grid consumption with storage"] = df_pow_profile["Grid with storage"].mask(df_pow_profile["Grid with storage"] < 0, 0.0)
# Replace all positive values with 0 to have the injection only
df_pow_profile["Grid injection with storage"] = df_pow_profile["Grid with storage"].mask(df_pow_profile["Grid with storage"] > 0, 0.0)

soc_array = solar_system.soc_profile
df_pow_profile["SOC"] = soc_array 

#and compute the price with that power profile
df_pow_profile["CostForBuyingWithStorage"] = (df_pow_profile["Grid consumption with storage"] * df_pow_profile["price buy"]/4.0)   #note, result is true/false, and .astype(int) convert to 1/0
cost_buying_solar_storage_chf = df_pow_profile["CostForBuyingWithStorage"].sum()
#print("Price paid with storage:", cost_buying_solar_storage_chf)
consumption_kWh_with_storage = df_pow_profile["Grid consumption with storage"].sum()/4.0

df_pow_profile["SellSolarWithStorage"] = (-df_pow_profile["Grid injection with storage"] * df_pow_profile["price sell PV"]/4.0)   
sellings_solar_storage_chf = df_pow_profile["SellSolarWithStorage"].sum()
#print("Sold PV electricity with with solar only, no storage:", sellings_solar_storage_chf)
injection_kWh_with_storage = -df_pow_profile["Grid injection with storage"].sum()/4.0

bill_with_storage = cost_buying_solar_storage_chf -sellings_solar_storage_chf 

gain_of_storage = bill_with_solar_only - bill_with_storage
total_gain_of_solar_and_storage= cost_buying_no_solar_chf - bill_with_storage

#bilan batterie  
delta_e_batt=(soc_array[-1]-soc_array[0])/100.0*battery_size_kwh_usr_input  #last SOC - first SOC of the simulation
#valorisé au prix moyen de la journée:
mean_price_with_storage = cost_buying_solar_storage_chf/consumption_kWh_with_storage
storage_value = delta_e_batt * mean_price_with_storage # np.mean(cost_normal_profile_with_vario_with_storage/consumption_kWh)




#*********************
# Computations for the peak power

peak_power_of_consumption = df_pow_profile["Consumption [kW]"].max()
peak_power_of_production = df_pow_profile["Solar power scaled"].max()

peak_grid_consumption_with_solar = df_pow_profile["grid consumption reference"].max()
peak_grid_injection_with_solar = df_pow_profile["grid injection reference"].min()

peak_grid_consumption_with_batteries = df_pow_profile["Grid consumption with storage"].max()
peak_grid_injection_with_batteries = df_pow_profile["Grid injection with storage"].min()


#*********************
# Computations for the blackout

#energy left to empty battery (5%)

df_pow_profile["Energy to empty batt"] = (df_pow_profile["SOC"]- SOC_FOR_END_OF_DISCHARGE ) /100 * battery_size_kwh_usr_input

#time to empty batt in hours
#for each 
#lets iterate that on the two in np:
#TODO  
energy_in_batt_array = df_pow_profile["Energy to empty batt"].values
energy_in_coming_consumption = np.zeros(length_profile)
energy_to_go = np.zeros(length_profile)
number_of_quarters = np.zeros(length_profile)

df_pow_profile["cumsum conso"]= df_pow_profile["Consumption [kW]"].cumsum()* 0.25
df_pow_profile["comm conso"]= consumption_kWh - df_pow_profile["cumsum conso"]
cumsum_conso = df_pow_profile["cumsum conso"].values
k=0
for energy in energy_in_batt_array:
    #from that point, how many quarters of conso equals to energy? 
    
    sum_of_quarters = 0.0
    n = 0
    for power in pow_array_all[k:length_profile-1]:
        sum_of_quarters = sum_of_quarters + power/4.0
        #compare energy 
        #TODO
        if energy < sum_of_quarters:
            #how many minutes of the last quarters exactly? TODO
            #TODO
            break
        n = n + 1

    energy_to_go[k] = sum_of_quarters
    number_of_quarters[k] = n + 1

    k=k+1

df_pow_profile["Energy in coming consumption"] = energy_to_go

#TODO  : correctif sur les dernières heures de l'année qui ont un time to go qui tombe à 0 à cause de la fin des données.
number_of_quarters[-8] = number_of_quarters[-9] 
number_of_quarters[-7] = number_of_quarters[-8] 
number_of_quarters[-6] = number_of_quarters[-7] 
number_of_quarters[-5] = number_of_quarters[-6] 
number_of_quarters[-4] = number_of_quarters[-5] 
number_of_quarters[-3] = number_of_quarters[-4] 
number_of_quarters[-2] = number_of_quarters[-3] 
number_of_quarters[-1] = number_of_quarters[-2] 
df_pow_profile["Time of backup on battery"] = number_of_quarters / 4.0
#TODO  : correctif sur les dernières heures de l'année qui ont un time to go qui tombe à 0 à cause de la fin des données.



#*********************
# Get the results

#TODO

sim_grid_injection_kWh = injection_kWh_with_storage
sim_grid_consumption = consumption_kWh_with_storage

sim_cost_buying_electricity_chf = cost_buying_solar_storage_chf
sim_sellings_solar_chf = sellings_solar_storage_chf
sim_bill = bill_with_storage

reference_self_consumption_ratio = (scaled_production_kWh-reference_grid_injection_kWh) / scaled_production_kWh * 100

sim_self_consumption_ratio = (scaled_production_kWh-injection_kWh_with_storage) / scaled_production_kWh * 100
sim_autarky_ratio = (consumption_kWh-consumption_kWh_with_storage) / consumption_kWh * 100.0  



# # Energy Consumption Plot using Plotly
# fig_simstorage_profile = px.line(df_pow_profile, 
#                         x=df_pow_profile.index, 
#                         y=[ "Consumption [kW]","Solar"], 
#                         title="⚡ Consumption and production", 
#                         labels={"value": "Power (kW)", "variable": "Legend"},
#                         color_discrete_sequence=["blue", "orange"]
# )
    
# # Move legend below the graph
# fig_simstorage_profile.update_layout(
#     legend=dict(
#         orientation="h",
#         yanchor="top",
#         y=-0.2,  # Position below the graph
#         xanchor="center",
#         x=0.1
#     )
# )
# st.plotly_chart(fig_simstorage_profile)






# --- Enregistrement dans l'historique ---
st.session_state.simulation_results_history.append({
    "timestamp": datetime.datetime.now(),  # horodatage 
    "Battery size (kWh)": battery_size_kwh_usr_input,
    "Solar scaling (%)": solar_scale_usr_input,
    "Buy Electricity price (CHF/kWh)": fixed_price_buy_usr_input,
    "Sell PV price (CHF/kWh)": fixed_price_sell_usr_input,
    "Battery C rate (-)": batt_charge_power_rate_user_input,
    "Battery SOC for backup (%)" : batt_soc_for_backup_user_input, 
    "Price type selection": price_type_usr_input, 
    "Dataset choice": dataset_choice,
    "Self-consumption ratio with storage (%)": sim_self_consumption_ratio,
    "Autarky ratio with storage (%)": sim_autarky_ratio, 
    "PV sell revenue with storage (CHF)": sim_sellings_solar_chf,
    "Cost Buying Electricity with storage(CHF)": sim_cost_buying_electricity_chf,
    "Bill with storage (CHF)": sim_bill, 
    "Gain of Storage (CHF)": gain_of_storage, 
    "Total gain of Solar and storage (CHF)": total_gain_of_solar_and_storage, 
    "Reference grid injection (kWh)": reference_grid_injection_kWh,
    "Reference grid consumption (kWh)": reference_grid_consumption_kWh,
    "Reference self-consumption (%)":reference_self_consumption_ratio, 
    "Reference autarky (%)": reference_autarky_ratio
    })



#save hours sampling for heatmap display:
hours_mean_df = df_pow_profile.resample('h', label="right", closed="right").mean() 
day_kwh_df = hours_mean_df.resample('d').sum() 
month_kwh_df = day_kwh_df.resample('ME').sum() 



####################
# SECOND: DISPLAY THE RESULTS ON THE APP 
#********************************************************
####################


#st.markdown("---")


st.write("📋 **Reference without storage, ☀️ only**")

col1, col2 = st.columns(2)
col1.metric("Consumption", str(int(consumption_kWh))+" kWh")
col2.metric("Production", str(int(scaled_production_kWh))+" kWh")

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Grid-feeding", str(int(reference_grid_injection_kWh)) + " kWh")
col2.metric("Grid consumption", str(int(reference_grid_consumption_kWh)) + " kWh")
col3.metric("Self-consumption", f"{reference_self_consumption_ratio :.1f}" + "%")
col4.metric("Autarky", f"{reference_autarky_ratio :.1f}" + "%")
col5.metric("Bill", f"{bill_with_solar_only :.1f}" + "CHF")

st.write("📋 **Results of simulation with solar and storage 🔋** ")
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Grid-feeding", str(int(sim_grid_injection_kWh))+" kWh", f"{(sim_grid_injection_kWh-reference_grid_injection_kWh)/reference_grid_injection_kWh*100 :.1f}" + "%")
col2.metric("Grid consumption", str(int(sim_grid_consumption))+" kWh", f"{(sim_grid_consumption-reference_grid_consumption_kWh)/reference_grid_consumption_kWh*100 :.1f}" + "%")
col3.metric("Self-consumption", f"{sim_self_consumption_ratio :.1f}"+"%", f"{(sim_self_consumption_ratio-reference_self_consumption_ratio) :.1f}" + "%" )
#col3.metric("Self-consumption", f"{(sim_self_consumption_ratio) :.1f, }"+"%", f"{(sim_self_consumption_ratio-reference_self_consumption_ratio) :.1f}"+"%")
col4.metric("Autarky", f"{(sim_autarky_ratio) :.1f}" + "%", f"{(sim_autarky_ratio-reference_autarky_ratio) :.1f}"+"%")
col5.metric("Bill", f" {sim_bill :.1f}"+"CHF", f" { sim_bill-bill_with_solar_only :.1f}"+"CHF" )

    


# --- Simulation results graphique ---
if st.session_state.simulation_results_history:
    df_results = pd.DataFrame(st.session_state.simulation_results_history)
    df_results = df_results.set_index("timestamp")
    
    st.subheader("Simulations results display")

        
    # --- Actions ---
    cols = st.columns(2)
    with cols[0]:
        #st.metric("Valeur actuelle (kWh)", f"{battery_size_kwh_usr_input:.1f}")
        st.write("Swipe one settings at a time and choose what you want to display accordingly to perform sensitivity analysis. Advice: reset when you want to explore another input.")
        list_of_channels_x = list(df_results.columns)[0:7]
        list_of_channels_y = list(df_results.columns)[7:-1]    
    
        dataresults_x_axis = st.selectbox("Choose X axis:", list_of_channels_x, index=0)
        dataresults_y_axis = st.selectbox("Choose Y axis:", list_of_channels_y, index=6)

        if st.button("🔁 Reset (empty tracking)"):
            st.session_state.simulation_results_history = []
            st.success("History cleared")
            st.rerun()


    with cols[1]:

        #st.line_chart(df_results["battery_size_kwh_usr_input"])  # trace simple de la valeur dans le temps
        #st.scatter_chart(ddf_resultsf, x=dataresults_x_axis, y=dataresults_y_axis)

        df_sorted = df_results.sort_values(dataresults_x_axis)
        st.line_chart(df_sorted, 
                    x=dataresults_x_axis, 
                    y=dataresults_y_axis,
                    x_label=dataresults_x_axis,
                    y_label=dataresults_y_axis)
else:
    st.info("No data, move one setting on the left.")





#The original data set
# Combined Solar Power and Energy Consumption Plot using Plotly
if "Consumption [kW]" in df_pow_profile.columns:
    fig_combined = px.line(df_pow_profile, x=df_pow_profile.index, 
                            y=["Solar power scaled", "Consumption [kW]"], 
                            title="🌞 Solar Production vs ⚡ Energy Consumption", 
                            labels={"value": "Power [kW]", "variable": "Legend"},
                            color_discrete_sequence=["orange", "lightblue"] )
    
    # Move legend below the graph
    fig_combined.update_layout(
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.2,  # Position below the graph
            xanchor="center",
            x=0.1
        )
    )
    st.plotly_chart(fig_combined)





#st.markdown("---")



#st.subheader(" The battery simulation")
st.write("In this simulation the battery control is done like what most of the inverters do: charge as soon as there is solar excess and discharge as soon as there is not enough solar. " \
        "This is not very intelligent and doesn't optimize special cases like peak shaving, dynamic prices, ...")
    
            

         
# Energy Consumption Plot using Plotly
fig_soc_profile = px.area(df_pow_profile, 
                        x=df_pow_profile.index, 
                        y=[ "SOC"], 
                        title=" 🔋 State of charge of the battery", 
                        labels={"value": "State of charge (%)", "variable": "SOC"}
)
    
# Move legend below the graph
fig_soc_profile.update_layout(
    legend=dict(
        orientation="h",
        yanchor="top",
        y=-0.2,  # Position below the graph
        xanchor="center",
        x=0.1
    )
)
st.plotly_chart(fig_soc_profile)







st.write(f" Note: the selfconsumption power of storage system of {INVERTER_STANDBY_W: .1f} Watt, that is {INVERTER_STANDBY_W*24/1000} kWh/day. Plus there is an efficiency of 0.95 counted.")





#st.dataframe(df_pow_profile.head())



#**********************************
st.markdown("---")
st.subheader(" More plots to see  📈 📊 ")
#**********************************
opt_to_display_plots = st.checkbox("Show it, but that adds time to each simulation to create and display it")

if opt_to_display_plots:

    #Plot the prices used:
    fig_levels = px.line(df_pow_profile, 
                                x=df_pow_profile.index, 
                                y=["price buy",  "price sell PV"], 
                                title="⚡ Electricity price used 💸 ", 
                                labels={"value": "Energy price (CHF/kWh)", "variable": "Legend"})
    st.plotly_chart(fig_levels)



    # Energy Consumption Plot using Plotly
    fig_simstorage_profile = px.line(df_pow_profile, 
                            x=df_pow_profile.index, 
                            y=[ "Consumption [kW]","Grid consumption with storage","Grid injection with storage"], 
                            title="⚡🔌 Consumption from the grid with solar and storage", 
                            labels={"value": "Power (kW)", "variable": "Legend"},
    )
        
    # Move legend below the graph
    fig_simstorage_profile.update_layout(
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.2,  # Position below the graph
            xanchor="center",
            x=0.1
        )
    )
    st.plotly_chart(fig_simstorage_profile)





    st.write(" \n ")



    # Energy Consumption Plot using Plotly
    fig_batt_profile = px.area(df_pow_profile, 
                            x=df_pow_profile.index, 
                            y=[ "Battery power"], 
                            title=" 🔋 Power of the battery", 
                            labels={"value": "Battery power [kW]", "variable": "Legend"}
    )


    # Move legend below the graph
    fig_batt_profile.update_layout(
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.2,  # Position below the graph
            xanchor="center",
            x=0.1
        )
    )
    st.plotly_chart(fig_batt_profile)



    fig_hours_heatmap =  build_SOC_heatmap_figure(hours_mean_df)
    st.pyplot(fig_hours_heatmap)

    fig_batt_soc = build_battery_SOC_min_max_analysis_figure(df_pow_profile)
    st.pyplot(fig_batt_soc)

    fig_bat_inout = build_bat_inout_figure(day_kwh_df, month_kwh_df)
    st.pyplot(fig_bat_inout)


    st.write(" **Some results**")



    st.markdown(f""" ***Reference***
    - The consumption of electricity for this period is {consumption_kWh:.2f} kWh 🔌
    - The cost of grid electricity if there was no solar would have been {cost_buying_no_solar_chf:.2f} CHF , mean price is {cost_buying_no_solar_chf/consumption_kWh:.3f} CHF/kWh
    - The consumption of electricity on the grid for this period is {reference_grid_consumption_kWh:.2f} kWh with solar only
    - The cost of grid electricity is {cost_buying_solar_only_chf:.2f} CHF with solar only, mean price is {cost_buying_solar_only_chf/reference_grid_consumption_kWh:.3f} CHF/kWh
    - The sale of PV electricity is {sellings_solar_only_chf:.2f} CHF with solar only, mean price is {sellings_solar_only_chf/reference_grid_injection_kWh:.3f} CHF/kWh
    - The total bill is {bill_with_solar_only:.2f} CHF with solar only, a gain of {cost_buying_no_solar_chf-bill_with_solar_only:.1f} CHF due to solar""")


    st.markdown(f""" ***🔋 With storage***
    - The consumption of electricity on the grid for this period is {consumption_kWh_with_storage:.2f} kWh with storage
    - The value of the stored energy left in the battery with mean price is {storage_value:.2f} CHF
    - The cost of grid electricity is {cost_buying_solar_storage_chf:.2f} CHF with storage, mean price is {cost_buying_solar_storage_chf/consumption_kWh_with_storage:.3f} CHF/kWh
    - The sale of PV electricity is {sellings_solar_storage_chf:.2f} CHF with solar only, mean price is {sellings_solar_storage_chf/injection_kWh_with_storage:.3f} CHF/kWh
    - The total bill is {bill_with_storage:.2f} CHF with solar + storage, a gain of {bill_with_solar_only - bill_with_storage :.1f} CHF due to storage
    - **TOTAL gain** with solar + storage is {cost_buying_no_solar_chf - bill_with_storage :.2f} CHF """)


    st.markdown(f""" ***🔎 Some details***
    - The states of charge of the battery at beggining ({soc_array[0]:.0f} %) and end of the period ({soc_array[-1]:.0f} %) are not the same, that is {delta_e_batt:.1f} kWh and must be counted in the final price. 
    - The value of the stored energy left in the battery with mean price is {storage_value:.2f} CHF
        """)
    

    #st.metric(label="gain with storage", value=4, delta=-0.5, delta_color="inverse")



#**********************************
st.markdown("---")
st.subheader(" More about the peak power 🗻 ")
#**********************************
opt_to_display_peak = st.checkbox("Show this part of analysis about peak if necessary. That adds time to each simulation to display it")

if opt_to_display_peak:
    st.write("Here we compute the time peak power on the grid.")


    st.write(""" For special cases, where this is relevant, the following indicators are also computed:      
    - the peak power taken from the grid
    - the peak injection power
    - the reserve time in case of blackout (how long is it possible to supply the coming consumption with the battery in islanding 🏝)

    But note that to optimize those points, an special control of the battery should be implemented 
    (per example not to charge the battery in the morning to avoid to be full at midday and give a high peak injection)    
    The optimal sizing of the battery cannot be decoupled from the way it is controlled.
    
    """)

    #st.markdown("<span style='color:red ; font-size:25pt'><b> TODO: Complete this part </b></span>", unsafe_allow_html=True)


    st.write("📋 **Reference without storage, ☀️ only**")


    # peak_power_of_consumption = df_pow_profile["Consumption [kW]"].max()
    # peak_power_of_production = df_pow_profile["Solar power [kW]"].max()


    # peak_grid_consumption_with_solar = df_pow_profile["grid consumption reference"].max()
    # peak_grid_injection_with_solar = df_pow_profile["grid consumption reference"].min()

    # peak_grid_consumption_with_batteries = df_pow_profile["Consumption [kW]"].max()
    # peak_grid_injection_with_batteries = df_pow_profile["grid consumption reference"].min()

    # print(peak_power_of_consumption)
    # print(peak_power_of_production)
    # print(peak_grid_consumption_with_solar)
    # print(peak_grid_injection_with_solar)


    col1, col2 = st.columns(2)
    col1.metric("Consumption peak", f"{peak_power_of_consumption :.1f}" + " kW")
    col2.metric("Production peak", f"{peak_power_of_production :.1f}" + " kW")  

    col1, col2, col3 = st.columns(3)
    col1.metric("Grid-consumption peak", f"{peak_grid_consumption_with_solar :.1f}" + " kW")  
    col2.metric("Grid Production peak", f"{peak_grid_injection_with_solar :.1f}" + " kW")   
    col3.metric("Bill", " TODO CHF" )


    st.write("📋 **Results of simulation with solar and storage 🔋** ")
    col1, col2, col3= st.columns(3)
    col1.metric("Grid-consumption peak", f"{peak_grid_consumption_with_batteries :.1f}" + " kW")
    col2.metric("Grid Production peak", f"{peak_grid_injection_with_batteries :.1f}" + " kW")
    col3.metric("Bill", " TODO CHF" )



    fig_hist = build_power_histogram_figure(df_pow_profile)
    st.pyplot(fig_hist)

    fig_acsource_hours_heatmap = build_hours_grid_heatmap_figure(hours_mean_df)
    st.pyplot(fig_acsource_hours_heatmap)


#**********************************
st.markdown("---")
st.subheader(" More about the backup time 🪫 ")
#**********************************
opt_to_display_bkup = st.checkbox("Show this part of analysis about backup if necessary. That adds time to each simulation to display it")

if opt_to_display_bkup:

    st.write(""" Here the following indicator is also computed:      

    - the reserve time on battery in case of blackout (how long is it possible to supply the coming consumption with the battery in islanding 🏝 🏭)

    """)
    #st.markdown("<span style='color:red ; font-size:25pt'><b> TODO: Complete this part </b></span>", unsafe_allow_html=True)

    # #Use Time  as index:
    # df_pow_profile = df_pow_profile.set_index("Time")
    # hours_mean_df = df_pow_profile.resample('H', label="right", closed="right").mean() 
    

    # Energy Consumption Plot using Plotly
    fig_batt_energy_left = px.area(df_pow_profile, 
                            x=df_pow_profile.index, 
                            y=[ "Energy to empty batt"], 
                            title=" Energy left in the battery to empty 🪫", 
                            labels={"value": "Battery Energy [kWh]", "variable": "Legend"},
                            color_discrete_sequence=["green"] 
    )


    # Move legend below the graph
    fig_batt_energy_left.update_layout(
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.2,  # Position below the graph
            xanchor="center",
            x=0.1
        )
    )
    st.plotly_chart(fig_batt_energy_left)




    # #For DEBUG: on the counted 
    # # Energy Consumption Plot using Plotly
    # fig_conso_coming = px.line(df_pow_profile, 
    #                         x=df_pow_profile.index, 
    #                         y=["Energy in coming consumption on the counted quarters", "Energy to empty batt"], 
    #                         title=" Coming consumption", 
    #                         labels={"value": "Com. Cons [kWh]", "variable": "Legend"},
    #                         color_discrete_sequence=["red", "yellow"] 
    # )


    # # Move legend below the graph
    # fig_conso_coming.update_layout(
    #     legend=dict(
    #         orientation="h",
    #         yanchor="top",
    #         y=-0.2,  # Position below the graph
    #         xanchor="center",
    #         x=0.1
    #     )
    # )
    # st.plotly_chart(fig_conso_coming)


    # Energy Consumption Plot using Plotly
    fig_batt_time_to_go = px.area(df_pow_profile, 
                            x=df_pow_profile.index, 
                            y=["Time of backup on battery"], 
                            title=" Time of backup on batteries only 🌃  🪫 🏴", 
                            labels={"value": "Backup time [h]", "variable": "Legend"},
                            color_discrete_sequence=["red"] 
    )


    # Move legend below the graph
    fig_batt_time_to_go.update_layout(
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.2,  # Position below the graph
            xanchor="center",
            x=0.1
        )
    )
    st.plotly_chart(fig_batt_time_to_go)

 
    # df_pow_profile = df_pow_profile.set_index("Time")
    # hours_mean_df = df_pow_profile.resample('H', label="right", closed="right").mean() 
    
    fig_timetogo_heatmap = build_time_to_go_heatmap_figure(hours_mean_df)
    st.pyplot(fig_timetogo_heatmap)



    st.write("This indicate for every moment how much time could be spend on the battery with the coming load and the SOC at that precise time. This is not the possible islanding time as the production is not taken into account, this is the next graph")




# #**********************************
# st.markdown("---")
# st.subheader(" Special visualizations  🌈  ")
# #**********************************
# opt_to_display_visu = st.checkbox("Show if necessary. That adds time to each simulation to display it")

# if opt_to_display_visu:
#     st.write("Heatmaps and more to enlight the understanding of what happens 💡  and because some are beautiful 💅")

#     # st.write("📋 **Data Overview head**")
#     # st.dataframe(df_pow_profile.head())
#     # len(df_pow_profile)
#     # st.write("📋 **Data Overview tail**")
#     # st.dataframe(df_pow_profile.tail())

#     #Use Time  as index:
#     # df_pow_profile = df_pow_profile.set_index("Time")
#     # hours_mean_df = df_pow_profile.resample('H', label="right", closed="right").mean() 
    
#     # #hours_mean_df = hours_mean_df.drop(hours_mean_df.index[-1])
#     # st.write("📋 **Data Overview tail**")
#     # st.dataframe(hours_mean_df.tail())
#     # len(hours_mean_df)
#     # st.write("📋 **Data Overview head**")
#     # st.dataframe(hours_mean_df.head())


#     # fig_storage_sim=solar_system.display_storage_simulation()
#     # # Show in Streamlit
#     # st.pyplot(fig_storage_sim)






#**********************************
st.markdown("---")
#The results that can be exported:
st.subheader("Raw results")
st.write("for your own analysis in excel or others, ...")
#**********************************

st.dataframe(df_results) #(df.rename(columns={"value": "Battery kWh"}))

st.download_button(
    " 💾 Download results (CSV)",
    data=df_results.to_csv(index=False),
    file_name="battery_sim_results.csv",
    mime="text/csv"
)




#**********************************
st.markdown("---")
st.title("Next steps 👨‍💻")
#**********************************



st.write(""" Solar, storage and optimization: the smart control 🏆
         
         The system sizing cannot be decoupled of the way it is operated, especially when there are multiple objectives like peakshaving, islanding, self-consumption and variable price optimization ...
         This daily energy management optimization is yet to come. It will be perfomed with day by day optimization.
         That is where the different objectives are maried. It's less obvious, but not rocket science ;-) 
         
         Then there will be real world control: to apply this strategy to the inverter (next3 of Studer-Innotec of course...), 
         transmit the orders with the API or locally with Modbus... 
         - Without solar: give directly the power setpoint on the grid input (AC-Source) 
            to force charging and set discharge current to 0 when you want to avoid discharge 
         - With solar: choose the time when to charge, discharge and force charge from the grid
         - That was already tested here for the nx3: https://github.com/moixpo/nxcontrol
         - a good control sould take the weather forcast into account, that was tested with Openmeteo API
             but now all the pieces of the puzzle must be put together...  
         
         ...see you later """)





#st.markdown("---")

# st.markdown("<span style='color:red'><b> TODO </b></span>", unsafe_allow_html=True)


# st.markdown("---")
# st.markdown("---")

# # Show dataset preview
# st.title("📋 **Data Overview, for debug purpose**")
# st.dataframe(df_pow_profile.head())

# st.dataframe(df_pow_profile.tail())


