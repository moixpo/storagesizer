# Interactive battery simulator 
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
#import random as rnd

#home made import:
#from groupe_e_access_functions import *
#from meteo_access_functions import *
from solarsystem import *
from advanced_figures import *

#constants TODO: put them as variable in the menu
INVERTER_STANDBY_W = 50  #Watts
EFFICIENCY_BATT_ONE_WAY  =  0.95  #TODO make variable, transmit to the battery simulation
SOC_FOR_END_OF_DISCHARGE = 5.0  #for islanding case



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
    battery_size_kwh_usr_input = st.slider("Battery capacity (kWh): ", min_value=0.0, max_value=50.0, value=10.0, step=1.0)
    # On garde en state la dernière valeur courante
    st.session_state.battery_size_kwh_usr_input = battery_size_kwh_usr_input

 
    st.markdown("---")
    st.write("☀️ Solar used for simulation, scale from original data measured on each house")
    solar_scale_usr_input = st.slider("Solar installed (%): ", min_value=0.0, max_value=300.0, value=100.0, step=10.0)
    
    
    st.markdown("---")
    st.write("**Choose a dataset  🏠** ")

    options = ["House1.csv", "House2.csv", "House3.csv", "House4.csv", "House5.csv", "Building1.csv", "Community1.csv", "School1.csv","Industry1.csv" ]
    dataset_choice = st.selectbox("Choose one option:", options)
 
    st.write("your data set :", dataset_choice, " is measured on:")
    
    if dataset_choice == "House1.csv":
        st.write("Modern house 2020, heat pump, low consumption already optimized for solar, 9.5kWp")
    elif dataset_choice == "House2.csv":
        st.write("House of 2000's, heat pump, electric car charged at home, 14kWp")
    elif dataset_choice == "House3.csv":
        st.write("House 1990, heat pump, EV")
    elif dataset_choice == "House4.csv":
        st.write("Old house, electric heating for some parts")
    elif dataset_choice == "House5.csv":
        st.write("House of 2010, gaz heating, EV without charge synch with solar")
    elif dataset_choice == "Building1.csv":
        st.write("Building 1990 with one residential flat and a service entreprise in one floor")            
    elif dataset_choice == "Community1.csv":
        st.write("The consumption of Houses 1 to 5 + Building1, and solar of houses 2 and 5 that wanted to share their production in a local electricity community to value it")    
    elif dataset_choice == "School1.csv":
        st.write("Large school with a PV roof")            
    elif dataset_choice == "Industry1.csv":
        st.write("Industrial site with a PV roof")            


    st.markdown("---")
    st.write("⚡💸 **Electricity Prices**")
    
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
    st.write("🔋💸 **Battery Price** ")
    st.write("An linear regression is taken between the price for an 5kWh and 50kWh")

    batt_five_kWh_price_user_input = st.slider("Battery cost per kWh for 5 kWh (CHF): ", min_value=100.0, max_value=800.0, value=600.0, step=50.0, help="Variable price per kWh for a small battery")
    batt_fifty_kWh_price_user_input = st.slider("Battery cost per kWh for 50 kWh (CHF): ", min_value=100.0, max_value=800.0, value=350.0, step=50.0, help="Variable price per kWh for a large battery")
    batt_installation_price_user_input = st.slider("Battery fixed installation cost (CHF): ", min_value=0.0, max_value=5000.0, value=1000.0, step=100.0, help="That is for the electrician and the controller, you could also use this for other fixed components")
    price_slope = (batt_fifty_kWh_price_user_input-batt_five_kWh_price_user_input) / 45.0
    zero_crossing_value = batt_five_kWh_price_user_input - price_slope * 5.0
    if battery_size_kwh_usr_input == 0:
        kWh_cost = 0.0
        batt_total_cost = 0.0
    else:
        kWh_cost = zero_crossing_value + battery_size_kwh_usr_input * price_slope
        batt_total_cost = batt_installation_price_user_input + battery_size_kwh_usr_input * kWh_cost
    st.write(f"The {battery_size_kwh_usr_input :.0f} kWh battery is estimated at {kWh_cost :.0f} CHF/kWh and total system cost {batt_total_cost:.0f} CHF")


    st.markdown("---")
    st.write("🌃 🪫 **Backup settings** ")
    batt_soc_for_backup_user_input = st.slider("Battery SOC reserved for backup (%): ", min_value=10.0, max_value=100.0, value=20.0, step=1.0, help="Battery will not discharge below this SOC.")
    st.write(f"The battery stops to discharge at this level, note that real battery don't go under {SOC_FOR_END_OF_DISCHARGE}%")


    st.markdown("---")
    st.write("⚡🗻 **Peak shaving settings** ")

    opt_to_use_peak_shaving= st.checkbox("Use the peak power shaving and a price?")

    if opt_to_use_peak_shaving:
                
        peak_shaving_user_input = st.slider("🪓 Peak consumption shaving to (% of max load): ", min_value=0.0, max_value=100.0, value=70.0, step=1.0)
        batt_soc_for_peak_user_input = st.slider("Battery SOC level reserved for peak shaving (%): ", min_value=10.0, max_value=100.0, value=20.0, step=1.0, help="Battery will not discharge below this SOC except for peak shaving.")
        st.write(f"The battery stops to discharge at this level for self-consumption optimization and can go lower to SOC for backup for peak shaving")

        peak_price_usr_input = 12.0 * st.slider("Price for the peak power (CHF/kW max year/month): ", min_value=0.0, max_value=20.0, value=0.0, step=0.1) #TODO: adapt to the size of the dataset, here is the hypothesis of 12 months

        #st.markdown(  "<span style='color:red; font-size:18pt'><b> WARNING, this price is not used in the final result with a real batt simulation yet </b></span>",  unsafe_allow_html=True)
    else :
        peak_price_usr_input = 0.0
        peak_shaving_user_input = 100.0
        batt_soc_for_peak_user_input = 20.0


    st.markdown("---")
    st.write("**👷 More Advanced settings** ")

    batt_charge_power_rate_user_input = st.slider("Battery max charge power rate (C): ", min_value=0.1, max_value=2.0, value=1.0, step=0.05, help="C rate relates the battery capacity to the power it can give.")
    battery_charge_power_kw = batt_charge_power_rate_user_input * battery_size_kwh_usr_input
    st.write("The max charge/discharge power is set to " + f"{battery_charge_power_kw :.1f}"+" kW")
    st.write("C/2 would be a reasonable charge/discharge limit, note that this limit is applied all day")

    st.write(" ")
    soc_init_user_input = st.slider("Battery initial SOC for simulation (%): ", min_value=20.0, max_value=100.0, value=50.0, step=1.0)


    opt_to_limit_gridfeeding= st.checkbox("Use grid feeding limitation (curtailment) ?")
    if opt_to_limit_gridfeeding:
        pv_injection_curtailment_user_input = st.slider("🚫 PV max grid feeding power (% of peak prod): ", min_value=0.0, max_value=100.0, value=60.0, step=1.0)
        st.write("The power above this limit will be lost. " \
        "\n Note: normally this factor is applied to the installed power, here it is applied on the peak of production profile as the exact DC kWp is not known")
    else :
        pv_injection_curtailment_user_input = 100.0 #a large value to have no limitation
        
    opt_to_use_smart_charging= st.checkbox("Use Smart Charging?")
    st.write("Smart charging reduce grid peak injection by waiting to recharge at the proper time, minimize the time with high batteries if possible.")



    # st.markdown("---")

    # st.markdown("---")
    # st.write("⏱️📈 📊 Planification with simple charge and discharge setpoint")

    # threshold_discharge = st.slider("⚡ Discharge when energy is expensive above (CHF/kWh): ", min_value=0.0, max_value=0.5, value=0.25, step=0.01)
    # threshold_charge  = st.slider("⚡ Charge when energy is cheap below (CHF/kWh): ", min_value=0.0, max_value=0.5, value=0.17, step=0.01)
    # st.write("between those levels nothing happens")

    # st.markdown("---")



    st.markdown("---")
    st.write("Battery sizer, version 0.6")
    st.write("✌️ Moix P-O, 2025")
    st.write("Streamlit for interactive dashboards...")
    



#**************
# MAIN PAGE
st.title(" 🔋 Storage Sizing for a Solar System")

if len(st.session_state.simulation_results_history)==0: 
    st.write(""" This simulation is based on the data of a full year of monitoring on real houses with PV production. 
            
    In the menu on the left, you can vary various setting (the size of the battery, the prices, the datasets...) and see the changes on the graphs below. 
    The reference case is always the house with solar and the addition of storage is compared to it. If you change the solar (per example 200% to see what happens if you had 2 times mores solar), it becomes the new reference for storage evaluation.
        
    The relevant indicators are calculated:
    - self-consumption rate
    - self-sufficiency rate ( also called autarky rate)
    - the electricity taken from the grid and its annual cost
    - the electricity injected into the grid and its annual cost
    - the final bill (ex fixed fees) and the gain compared to the case without storage
    - the cost of storage 

    
    Various interactive plots of the power fluxes are given to vizualize what happens exactly in the house. At the end of the page there is a table with all the results that can be downloaded in csv format to do your own charts (excel,...).
    
    It is possible to activate a peak shaving function and asses if the storage is able to make it. It is also possible to study the backup time available.
             
        """)
        

    st.markdown("---")





####################
# FIRST: LOAD DATA 
#********************


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


#take the data of the power profile in numpy (format for simulation)
pow_array_all = df_pow_profile["Consumption [kW]"].to_numpy()
solar_array_all = df_pow_profile["Solar power [kW]"].to_numpy()
solar_array_all_scaled = solar_array_all *solar_scale_usr_input / 100.0


#save in dataframe for easy display:
df_pow_profile["Solar power scaled"] = solar_array_all_scaled

#*********************
# Computations for the peak shaving and curtailment from the peak powers
peak_power_of_consumption = df_pow_profile["Consumption [kW]"].max()
clipping_level = peak_shaving_user_input*peak_power_of_consumption/100.0

peak_power_of_production = df_pow_profile["Solar power scaled"].max()
pv_injection_curtailment_power = pv_injection_curtailment_user_input *peak_power_of_production/100

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





#*********************
# Perform the simulation
#*********************


##########################################
#Let's simulate the solar system 
#########################################################################
# with the solarsystem.py object:

solar_system = SolarSystem("M-P-O","Rue du Solaire 6, 2050 Transition" )

# properties initialisation  
solar_system.batt_capacity_kWh = battery_size_kwh_usr_input #10*1 # in kWh
solar_system.soc_init = soc_init_user_input # in %
solar_system.soc_for_backup_user = batt_soc_for_backup_user_input
solar_system.soc_for_peak_shaving_user = batt_soc_for_peak_user_input
solar_system.peak_shaving_activated = opt_to_use_peak_shaving
solar_system.max_grid_injection_power = pv_injection_curtailment_power #kW  a high value in order not to have caping 


#For TEST, warning, TODO
solar_system.peak_shaving_limit = clipping_level #kW

solar_system.max_power_charge = battery_charge_power_kw #to update the max charge used by default independently of the battery size
solar_system.max_power_discharge = -battery_charge_power_kw #same rate applied
solar_system.max_inverter_power = 500 #kW  a high value in order not to have caping   # 15kW  for the next3

if battery_size_kwh_usr_input == 0.0:
    solar_system.selfpowerconsumption = 0.0
else:
    solar_system.selfpowerconsumption = INVERTER_STANDBY_W / 1000
solar_system.efficiency_batt_one_way = EFFICIENCY_BATT_ONE_WAY

# solar_system.gps_location = [46.208, 7.394] 
# solar_system.pv_kW_installed = 9.24 #power installed on the roof
# solar_system.roof_orientation = -10 # 0=S, 90°=W, -90°=E, -180°=N (or -180)
# solar_system.roof_slope = 25.0
# solar_system.comment = "installed in June 2022"


#load data in the module for simulation:
solar_system.load_data_for_simulation(pow_array_all, solar_array_all_scaled, timestep=0.25)


##########################################
#Let's simulate the solar system without battery for reference:
solar_system.run_simple_simulation(print_res=False)


#Take the results of the simple simulation:
grid_array_all = solar_system.net_grid_balance_profile
reference_curtailment_lost_energy_kwh = sum(solar_system.lostproduction_profile)/4.0

#All the series for the case with solar only and no storage will be the reference:
df_pow_profile["grid power reference"] = grid_array_all #all grid balance without storage with scaled solar

# Replace all positive values with 0 to have the injection only, note the injection is negative power on the grid
df_pow_profile["grid injection reference"] = df_pow_profile["grid power reference"].mask(df_pow_profile["grid power reference"] > 0, 0.0)
# Replace all negative values with 0 to have the consumption only
df_pow_profile["grid consumption reference"] = df_pow_profile["grid power reference"].mask(df_pow_profile["grid power reference"] < 0, 0.0)


consumption_kWh = df_pow_profile["Consumption [kW]"].sum()/4.0
original_production_kWh = df_pow_profile["Solar power [kW]"].sum()/4.0 #from dataset
scaled_production_kWh = df_pow_profile["Solar power scaled"].sum()/4.0 #scaled and used

reference_grid_injection_kWh = -df_pow_profile["grid injection reference"].sum()/4.0
reference_grid_consumption_kWh = df_pow_profile["grid consumption reference"].sum()/4.0

reference_self_consumption_ratio = (scaled_production_kWh - reference_grid_injection_kWh - reference_curtailment_lost_energy_kwh) / scaled_production_kWh * 100
reference_autarky_ratio = (consumption_kWh - reference_grid_consumption_kWh) / consumption_kWh * 100.0  



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








# load data in the module for simulation:

# # #Test of some control variable:
# charge_command_array= df_price_varioplus["ChargeCommand"].to_numpy()
# discharge_command_array= df_price_varioplus["DischargeCommand"].to_numpy()

# #force charging on the grid:
# solar_system.delta_p_on_ac_source_profile = charge_command_array * battery_charge_power_kw
# #let discharging only during this time:
# solar_system.battery_max_discharge_setpoint_profile = - discharge_command_array * battery_charge_power_kw


################################
# Optimized use of the battery for charging.
################################
#here an open loop setpoint profile is made to have something light to implement.

if opt_to_use_smart_charging: 

    #run the simulation an firt time with the loaded data to have an estimate of the SOC:
    solar_system.run_storage_simulation(print_res=False)
    df_pow_profile["SOC"] = solar_system.soc_profile 
    #Separate all the available data in subsets for each day of the year an timeseries and assess the smart charging:
    #Method 1: with an pd groupby 
    list_of_days = []
    full_plim_list = []
    full_day_max_charging_power_profile_list = []
    k = 0

    for day, day_df in df_pow_profile.groupby(df_pow_profile.index.date):
        day_df["cumsum conso"] = day_df["Consumption [kW]"].cumsum()* 0.25
        conso_of_the_day = (day_df["cumsum conso"].values[-1])
        day_df["cumsum sol"] = day_df["Solar power scaled"].cumsum()* 0.25
        solar_of_the_day = (day_df["cumsum sol"].values[-1])
        day_df["cumsum balance"] = day_df["grid power reference"].cumsum()* 0.25 #with the reference without storage
        balance_of_the_day = (day_df["cumsum balance"].values[-1]) #conso is positive
        
        #take the excess that could be stored to the battery, taking into account max charge power and efficiency
        excess_that_can_be_stored=-day_df["grid injection reference"].values * EFFICIENCY_BATT_ONE_WAY
        excess_that_can_be_stored[excess_that_can_be_stored > solar_system.max_power_charge] = solar_system.max_power_charge

        solar_excess_of_the_day = abs(excess_that_can_be_stored.sum() / 4.0)

        min_soc_day = day_df["SOC"].min()
        max_soc_day = day_df["SOC"].max()

        max_space_in_the_battery = (100.0-min_soc_day)/100.0 * battery_size_kwh_usr_input

        #the available space for energy is given in the min of SOC in the morning
        size_vector_morning=int( len(day_df) / 2 ) + 1
        min_soc_of_morning =day_df["SOC"].values[0:size_vector_morning].min()
        energy_to_fill = (100.0 - min_soc_of_morning) / 100.0 * battery_size_kwh_usr_input
        
        #print(day, f" space in the battery: {max_space_in_the_battery :.2f} kWh")

        #first evaluate if full recharge is possible or not: 
        #then take some margin to be sure the battery can be fully charged.
        MARGIN_FACTOR_ON_RECHARGE = 1.05 #5% margin to be sure to charge the batt 

        # if the solar excess is not sufficient to charge the battery, no need to limit charging 
        if solar_excess_of_the_day < energy_to_fill * MARGIN_FACTOR_ON_RECHARGE :
            
            #in a first simple algorithm, we can
            #simply say that there is no use to limit the charging 
            # TODO: compute intraday limitations if the battery could be charged fully at certain times and discharged again later (with max_soc_day)

            power_limitation_factor_profile = np.ones(len(day_df))
            day_max_charging_power_profile = np.ones(len(day_df)) * solar_system.max_power_charge
            scale_used = 1.0
            scaled_excess = excess_that_can_be_stored / scale_used
            peak_search_level = 0.0
            peak_array = scaled_excess
        else:
            #here we could limit charging at certain time of the day and be able to recharge the battery

            #######################################
            # the smart algo 2:
            # search in the peak solar power which level corresponds to the battery left room.
            # Warning, here it is done with the real measurements but in reality that should be done with the production and consumption forecast.

            #scaled available solar excess power:
            scale_used=abs(excess_that_can_be_stored.max())
            scaled_excess = excess_that_can_be_stored / scale_used
            e_to_fill_scaled = energy_to_fill / scale_used


            #15 iterations to find where the peak power corresponds to energy to be charged in the battery:
            #init:
            peak_search_level = 0.5
            step = 0.5
            direction = 1.0
            peak_search_level_array= [] #to track evolution
            energy_peak_prod_array= [] #to track evolution

            for i in range(15): 
                
                peak_array = scaled_excess - peak_search_level
                #remove negative value and compute energy of the peak
                peak_array[peak_array < 0] = 0.0
                energy_peak_prod = peak_array.sum()/4.0

                #tracking:
                energy_peak_prod_array.append(energy_peak_prod)
                peak_search_level_array.append(peak_search_level)

                #if energy is not enough, we can make an step smaller and increase the surface with negative direction
                if energy_peak_prod < e_to_fill_scaled :
                    step = step / 2.0
                    direction = -1
                else: 
                    direction = 1

                #search further
                peak_search_level = peak_search_level + step * direction

            
            #the exact match is found, use one with a margin; TODO: for days with not much energy in the afternoon take more margin, for days with a lot of afternoon sun that shoudl be sufficient: 
            peak_array = scaled_excess - peak_search_level * MARGIN_FACTOR_ON_RECHARGE
            #remove negative value and compute energy of the peak
            peak_array[peak_array < 0] = 0.0

            #and let recharge at the end of the afternon, that will give some margin for prediction errors:
            d = day_df["cumsum sol"].values / day_df["cumsum sol"].max()-0.75

            power_limitation_factor_profile = np.maximum(peak_array, d) # Element-wise  and rescaling to power in kW
            day_max_charging_power_profile = power_limitation_factor_profile * scale_used

            #print(day, f"Space in batt: {energy_to_fill :.2f} kWh for solar {solar_excess_of_the_day :.2f} and it is scaled to {e_to_fill_scaled :.2f} and {(solar_excess_of_the_day / scale_used): .2f}, found {energy_peak_prod : .2f}")
            #print(peak_search_level_array)

        # #For the visulisation of a single day for dev and debug:
        # k = k+1
        # if k == 160: 
            
        #     # #algo 1:
        #     # a = day_df["Solar power scaled"].values / day_df["Solar power scaled"].max()
        #     # b = (day_df["Solar power scaled"].values / day_df["Solar power scaled"].max() - 0.75 ) *4.0
        #     # c = b.copy()
        #     # c[c < 0] = 0
        #     # d = day_df["cumsum sol"].values / day_df["cumsum sol"].max()-0.5
        #     # e = np.maximum(c, d) # Element-wise maximum

        #     #algo 2:
        #     a = scaled_excess
        #     b = scaled_excess-peak_search_level
        #     c = peak_array
        #     d = day_df["cumsum sol"].values / day_df["cumsum sol"].max()-0.75
        #     e = power_limitation_factor_profile
        #     #Now transform this limit into the maximal charge power array of the battery: 
        #     #day_max_charging = e * solar_system.max_power_charge

        
        #     #display for tests:
        #     matrix = np.stack((a, b, c, d, e), axis=1)
        #     fig_smart1 =build_test_figure(matrix) #day_df["Solar power scaled"].values
        #     #fig_cumsum2 =build_test_figure(day_df["grid power reference"].values  ) #day_df["Solar power scaled"].values
        #     st.pyplot(fig_smart1)
            
        #     fig_smart2 =build_test_figure(day_df["SOC"].values) #power_limitation_factor_profile)
        #     st.pyplot(fig_smart2)

        #     fig_smart3 =build_test_figure(day_max_charging_power_profile ) # day_df["grid injection reference"].values / day_df["grid injection reference"].min())
        #     st.pyplot(fig_smart3)


        list_of_days.append(day_df)
        full_plim_list.append(power_limitation_factor_profile)
        full_day_max_charging_power_profile_list.append(day_max_charging_power_profile)



    # finally convert to np array:
    full_plim_array = np.concatenate(full_plim_list)
    full_day_max_charging_power_profile_array = np.concatenate(full_day_max_charging_power_profile_list)


    # fig_smart4 =build_test_figure(full_plim_array)
    # st.pyplot(fig_smart4)

else: 
    full_plim_array = np.ones(length_profile)
    full_day_max_charging_power_profile_array = np.ones(length_profile) * solar_system.max_power_charge

#and update the max charge profile for simulation:
solar_system.battery_max_charge_setpoint_profile = full_day_max_charging_power_profile_array #full_plim_array * solar_system.max_power_charge
#store it for later:
df_pow_profile["Smart Charging"] = full_day_max_charging_power_profile_array #full_plim_array



#and run the simulation of the system with the loaded datas:
solar_system.run_storage_simulation(print_res=False)


#and retrieve the grid power and inject it in the dataframe:
grid_power_with_storage_array = solar_system.net_grid_balance_profile
df_pow_profile["Grid with storage"] = grid_power_with_storage_array 

#The losses due to PV injection limitation is
df_pow_profile["PV curtailment"] = solar_system.lostproduction_profile
curtailment_lost_energy_kWh =df_pow_profile["PV curtailment"].sum()/4.0



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
grid_consumption_kWh_with_storage = df_pow_profile["Grid consumption with storage"].sum()/4.0

df_pow_profile["SellSolarWithStorage"] = (-df_pow_profile["Grid injection with storage"] * df_pow_profile["price sell PV"]/4.0)   
sellings_solar_storage_chf = df_pow_profile["SellSolarWithStorage"].sum()
#print("Sold PV electricity with with solar only, no storage:", sellings_solar_storage_chf)
grid_injection_kWh_with_storage = -df_pow_profile["Grid injection with storage"].sum()/4.0

#bilan batterie  
delta_e_batt=(soc_array[-1]-soc_array[0])/100.0*battery_size_kwh_usr_input  #last SOC - first SOC of the simulation
#valorisé au prix moyen de la journée:
mean_price_with_storage = cost_buying_solar_storage_chf/grid_consumption_kWh_with_storage
storage_value = delta_e_batt * mean_price_with_storage # np.mean(cost_normal_profile_with_vario_with_storage/consumption_kWh)




#*********************
# Computations for the peak power

peak_power_of_production = df_pow_profile["Solar power scaled"].max()

peak_grid_consumption_with_solar = df_pow_profile["grid consumption reference"].max()
peak_grid_injection_with_solar = df_pow_profile["grid injection reference"].min()

peak_grid_consumption_with_batteries = df_pow_profile["Grid consumption with storage"].max()
peak_grid_injection_with_batteries = df_pow_profile["Grid injection with storage"].min()




#*********************
# Computations of the bills
bill_of_peak_without_nothing = peak_power_of_consumption * peak_price_usr_input
bill_of_peak_solar_only = peak_grid_consumption_with_solar * peak_price_usr_input
bill_of_peak_with_storage = peak_grid_consumption_with_batteries*peak_price_usr_input

bill_without_nothing = cost_buying_no_solar_chf + bill_of_peak_without_nothing
bill_with_solar_only = cost_buying_solar_only_chf -  sellings_solar_only_chf + bill_of_peak_solar_only
bill_with_storage = cost_buying_solar_storage_chf - sellings_solar_storage_chf + bill_of_peak_with_storage


gain_of_storage = bill_with_solar_only - bill_with_storage
total_gain_of_solar_and_storage= bill_without_nothing - bill_with_storage



#*********************
# Computations for the blackout

#energy left to empty battery (5%)

df_pow_profile["Energy to empty batt"] = (df_pow_profile["SOC"]- SOC_FOR_END_OF_DISCHARGE ) /100 * battery_size_kwh_usr_input

#time to empty batt in hours
#for each 
#lets iterate that on the two in np:
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
        if energy <= sum_of_quarters:
            #how many minutes of the last quarters exactly? TODO
            #TODO
            break
        n = n + 1

    energy_to_go[k] = sum_of_quarters
    number_of_quarters[k] = n #+ 1

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

minimal_backup_time = df_pow_profile["Time of backup on battery"].min()



# #####################################################
# # Compute the time of backup with solar and storage: TODO
# #########
# energy_in_coming_consumption = np.zeros(length_profile)
# energy_to_go = np.zeros(length_profile)
# number_of_quarters = np.zeros(length_profile)
# k=0
# for energy in energy_in_batt_array:
#     #from that point, how many quarters of conso equals to energy? 
    
#     sum_of_quarters = 0.0
#     n = 0
#     for power in grid_array_all[k:length_profile-1]:
#         sum_of_quarters = sum_of_quarters + power/4.0
#         #the sum of quarters must be capped by the battery size in negative to avoid to integrate too big solar charging.
#         #compare energy 
#         #TODO
#         if sum_of_quarters < -battery_size_kwh_usr_input : #* 0.95 + energy :
#             sum_of_quarters = -battery_size_kwh_usr_input #* 0.95 + energy

#         if energy <= sum_of_quarters:
#             #how many minutes of the last quarters exactly? TODO
#             #TODO
#             break
#         n = n + 1

#     energy_to_go[k] = sum_of_quarters
#     number_of_quarters[k] = n #+ 1

#     k=k+1

# df_pow_profile["Energy in coming consumption and solar"] = energy_to_go

# df_pow_profile["Time of backup on battery and solar"] = number_of_quarters / 4.0




#*********************
# Analyse the results

self_consumption_ratio_with_storage = (scaled_production_kWh-grid_injection_kWh_with_storage-curtailment_lost_energy_kWh) / scaled_production_kWh * 100
autarky_ratio_with_storage = (consumption_kWh-grid_consumption_kWh_with_storage) / consumption_kWh * 100.0  



#save hours sampling for heatmap display:
hours_mean_df = df_pow_profile.resample('h', label="right", closed="right").mean() 
day_kwh_df = hours_mean_df.resample('d').sum() 
month_kwh_df = day_kwh_df.resample('ME').sum() 

batt_throughput_energy = -month_kwh_df['Battery discharge power only'].sum()
if battery_size_kwh_usr_input == 0.0:
    equivalent_80percent_cycles = 0.0
    cost_of_stored_kWh_over_15_years = 0.0
else :
    equivalent_80percent_cycles =  batt_throughput_energy / battery_size_kwh_usr_input / 0.8

    #assuming the data are always for 1 full year: TODO make it in function of the data size
    cost_of_stored_kWh_over_15_years = batt_total_cost / 15.0 / batt_throughput_energy





# --- Enregistrement dans l'historique ---
st.session_state.simulation_results_history.append({
    "timestamp": datetime.datetime.now(),  # horodatage 
    "Battery size (kWh)": battery_size_kwh_usr_input,
    "Solar scaling (%)": solar_scale_usr_input,
    "Buy Electricity price (CHF/kWh)": fixed_price_buy_usr_input,
    "Sell PV price (CHF/kWh)": fixed_price_sell_usr_input,
    "Price type selection": price_type_usr_input, 
    "Price peak power (CHF/kW max year/year)": peak_price_usr_input,
    "Battery C rate (-)": batt_charge_power_rate_user_input,
    "Battery SOC for backup (%)" : batt_soc_for_backup_user_input, 
    "Level of peak shaving (%)" : peak_shaving_user_input, 
    "Battery SOC for peak shaving (%)" : batt_soc_for_peak_user_input,
    "Dataset choice": dataset_choice,
    "PV injection curtailment (%)": pv_injection_curtailment_user_input,
    "PV injection curtailment (kW)": pv_injection_curtailment_power,
    "Use of SmartCharging": opt_to_use_smart_charging,
    "Self-consumption ratio with storage (%)": self_consumption_ratio_with_storage,
    "Autarky ratio with storage (%)": autarky_ratio_with_storage, 
    "PV sell revenue with storage (CHF)": sellings_solar_storage_chf,
    "Cost Buying Electricity with storage(CHF)": cost_buying_solar_storage_chf,
    "Bill with storage (CHF)": bill_with_storage, 
    "Gain of storage (CHF)": gain_of_storage, 
    "Total gain of solar and storage (CHF)": total_gain_of_solar_and_storage, 
    "Grid consumption (kWh)":grid_consumption_kWh_with_storage,
    "Grid injection (kWh)":grid_injection_kWh_with_storage,
    "Battery throughput Energy (kWh)": batt_throughput_energy,
    "Number of equivalent 80% DOD cycles": equivalent_80percent_cycles,
    "Battery total price (CHF)": batt_total_cost,
    "Battery variable price (CHF/kWh)": kWh_cost,
    "Cost of storage over 15 years (ct/kWh)": cost_of_stored_kWh_over_15_years*100.0,
    "Peak grid consumption with batt (kW)": peak_grid_consumption_with_batteries,
    "Lost energy due to curtailment (kWh)" : curtailment_lost_energy_kWh,
    "Reference grid injection (kWh)": reference_grid_injection_kWh,
    "Reference grid consumption (kWh)": reference_grid_consumption_kWh,
    "Reference total bill (CHF)": bill_with_solar_only,
    "Reference self-consumption (%)":reference_self_consumption_ratio, 
    "Reference autarky (%)": reference_autarky_ratio,
    "Reference lost energy due to curtailment (kWh)" : reference_curtailment_lost_energy_kwh,
    "Reference peak grid consumption (kW)": peak_grid_consumption_with_solar,

    })




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
col1.metric("Grid consumption", str(int(reference_grid_consumption_kWh)) + " kWh")
col2.metric("Grid-feeding", str(int(reference_grid_injection_kWh)) + " kWh")
col3.metric("Self-consumption", f"{reference_self_consumption_ratio :.1f}" + "%")
col4.metric("Autarky", f"{reference_autarky_ratio :.1f}" + "%")
col5.metric("Bill", f"{bill_with_solar_only :.0f}" + "CHF")

st.write("📋 **Results of simulation with solar and storage 🔋** ")
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Grid consumption", str(int(grid_consumption_kWh_with_storage))+" kWh", f"{(grid_consumption_kWh_with_storage-reference_grid_consumption_kWh)/reference_grid_consumption_kWh*100 :.1f}" + "%", delta_color="off")
col2.metric("Grid-feeding", str(int(grid_injection_kWh_with_storage))+" kWh", f"{(grid_injection_kWh_with_storage-reference_grid_injection_kWh)/reference_grid_injection_kWh*100 :.1f}" + "%", delta_color="off")
col3.metric("Self-consumption", f"{self_consumption_ratio_with_storage :.1f}"+"%", f"{(self_consumption_ratio_with_storage-reference_self_consumption_ratio) :.1f}" + "%" )
#col3.metric("Self-consumption", f"{(self_consumption_ratio_with_storage) :.1f, }"+"%", f"{(self_consumption_ratio_with_storage-reference_self_consumption_ratio) :.1f}"+"%")
col4.metric("Autarky", f"{(autarky_ratio_with_storage) :.1f}" + "%", f"{(autarky_ratio_with_storage-reference_autarky_ratio) :.1f}"+"%")
col5.metric("Bill", f" {bill_with_storage :.0f}"+"CHF", f" { bill_with_storage-bill_with_solar_only :.0f}"+"CHF", delta_color="off" )

    


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
        list_of_channels_x = list(df_results.columns)[0:14]
        list_of_channels_y = list(df_results.columns)[14:-1]    
    
        dataresults_x_axis = st.selectbox("Choose X axis:", list_of_channels_x, index=0)
        dataresults_y_axis = st.selectbox("Choose Y axis:", list_of_channels_y, index=5)

        if st.button("🔁 Reset (empty tracking)"):
            st.session_state.simulation_results_history = []
            st.success("History cleared")
            st.rerun()


    with cols[1]:

        #st.line_chart(df_results["battery_size_kwh_usr_input"])  # trace simple de la valeur dans le temps
        #st.scatter_chart(ddf_resultsf, x=dataresults_x_axis, y=dataresults_y_axis)

        df_sorted = df_results.sort_values(dataresults_x_axis)
        # st.line_chart(df_sorted, 
        #             x=dataresults_x_axis, 
        #             y=dataresults_y_axis,
        #             x_label=dataresults_x_axis,
        #             y_label=dataresults_y_axis)
        
        
        fig_analysis = px.line(
            df_sorted,
            x=dataresults_x_axis,
            y=dataresults_y_axis,
            markers=True,  
            labels={
                dataresults_x_axis: dataresults_x_axis,
                dataresults_y_axis: dataresults_y_axis,
            },
            title="Results analysis"
        )

        st.plotly_chart(fig_analysis, use_container_width=True)

else:
    st.info("No data, move one setting on the left.")





#st.markdown("---")



#st.subheader(" The battery simulation")
st.write("In this simulation the battery control is done like what most of the inverters do: charge as soon as there is solar excess and discharge as soon as there is not enough solar. " \
        "This is not very intelligent and doesn't optimize special cases like dynamic prices, ... yet")
    
            

         
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


    #The original data set
    # Combined Solar Power and Energy Consumption Plot using Plotly
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



    fig_hours_heatmap =  build_SOC_heatmap_figure(hours_mean_df)
    st.pyplot(fig_hours_heatmap)

    fig_batt_soc = build_battery_SOC_min_max_analysis_figure(df_pow_profile)
    st.pyplot(fig_batt_soc)

    st.write(f"The energy throughtput is {batt_throughput_energy :.0f} kWh and this is equivalent to {equivalent_80percent_cycles :.0f}  cycles at 80% DOD")

    st.write(f"Over 15 years, that gives an cost of storage of {cost_of_stored_kWh_over_15_years*100.0 :.1f} ct/kWh, plus the value of the solar energy (with grid selling price here), the cost of stored energy is {(cost_of_stored_kWh_over_15_years*100.0 + fixed_price_sell_usr_input*100.0 ) :.0f}  ct/kWh")


    fig_bat_inout = build_bat_inout_figure(day_kwh_df, month_kwh_df)
    st.pyplot(fig_bat_inout)



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

    # df_pow_profile["testpoint1"] = solar_system.test_profile
    # df_pow_profile["testpoint2"] = solar_system.test2_profile
    # df_pow_profile["testpoint3"] = solar_system.test3_profile
    # df_pow_profile["testpoint4"] = solar_system.test4_profile

    # # Energy Consumption Plot using Plotly
    # fig_maxinject_profile = px.line(df_pow_profile, 
    #                         x=df_pow_profile.index, 
    #                         y=[ "testpoint1","testpoint2","testpoint3","testpoint4"], 
    #                         title="  Powers for the max inject", 
    #                         labels={"value": "testpoint [kW]", "variable": "Legend"}
    # )


    # # Move legend below the graph
    # fig_maxinject_profile.update_layout(
    #     legend=dict(
    #         orientation="h",
    #         yanchor="top",
    #         y=-0.2,  # Position below the graph
    #         xanchor="center",
    #         x=0.1
    #     )
    # )
    # st.plotly_chart(fig_maxinject_profile)




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
    st.write(" \n ")




    st.write("The consumption and production seen differently as heatmaps")


    fig_consumption_heatmap = build_consumption_heatmap_figure(hours_mean_df)
    st.pyplot(fig_consumption_heatmap)

    fig_production_heatmap = build_production_heatmap_figure(hours_mean_df)
    st.pyplot(fig_production_heatmap)


    st.write(" **Some results**")



    st.markdown(f""" ***Reference***
    - The consumption of electricity for this period is {consumption_kWh:.2f} kWh 🔌
    - The cost of grid electricity if there was no solar would have been {cost_buying_no_solar_chf:.2f} CHF , mean price is {cost_buying_no_solar_chf/consumption_kWh:.3f} CHF/kWh
    - The consumption of electricity on the grid for this period is {reference_grid_consumption_kWh:.2f} kWh with solar only
    - The cost of grid electricity is {cost_buying_solar_only_chf:.2f} CHF with solar only, mean price is {cost_buying_solar_only_chf/reference_grid_consumption_kWh:.3f} CHF/kWh
    - The lost energy due to grid-feeding limitation is {reference_curtailment_lost_energy_kwh :.0f} kWh and curtailment level is {pv_injection_curtailment_power:.2f} kW
    - The sale of PV electricity is {sellings_solar_only_chf:.2f} CHF with solar only, mean price is {sellings_solar_only_chf/reference_grid_injection_kWh:.3f} CHF/kWh
    - The total bill is {bill_with_solar_only:.2f} CHF with solar only, a gain of {cost_buying_no_solar_chf-bill_with_solar_only:.1f} CHF due to solar""")


    st.markdown(f""" ***🔋 With storage***
    - The consumption of electricity on the grid for this period is {grid_consumption_kWh_with_storage:.2f} kWh with storage
    - The energy lost due to grid feeding limitation is {curtailment_lost_energy_kWh :.0f} kWh
    - The value of the stored energy left in the battery with mean price is {storage_value:.2f} CHF
    - The cost of grid electricity is {cost_buying_solar_storage_chf:.2f} CHF with storage, mean price is {cost_buying_solar_storage_chf/grid_consumption_kWh_with_storage:.3f} CHF/kWh
    - The sale of PV electricity is {sellings_solar_storage_chf:.2f} CHF with solar only, mean price is {sellings_solar_storage_chf/grid_injection_kWh_with_storage:.3f} CHF/kWh
    - The total bill is {bill_with_storage:.2f} CHF with solar + storage, a gain of {bill_with_solar_only - bill_with_storage :.1f} CHF due to storage
    - **TOTAL gain** with solar + storage is {cost_buying_no_solar_chf - bill_with_storage :.2f} CHF """)


    st.markdown(f""" ***🔎 Some details***
    - The states of charge of the battery at beggining ({soc_array[0]:.0f} %) and end of the period ({soc_array[-1]:.0f} %) are not the same, that is {delta_e_batt:.1f} kWh and must be counted in the final price. 
    - The value of the stored energy left in the battery with mean price is {storage_value:.2f} CHF
        """)
    

    #st.metric(label="gain with storage", value=4, delta=-0.5, delta_color="inverse")
    
    st.write(" Figure to see the effect of the Smartcharging algorithm ")

    fig_scat2 = build_power_profile(df_pow_profile, "Grid with storage")
    st.pyplot(fig_scat2)

    fig_scat3 = build_power_profile(df_pow_profile, "SOC")
    st.pyplot(fig_scat3)

    fig_scat4 = build_power_profile(df_pow_profile, "Smart Charging")
    st.pyplot(fig_scat4)



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
    - the cost of the peaks
    - the fraction of the total energy that the peaks represents
    - the size of the battery to have peak shaving at a wanted level

    But note that to optimize those points, an special control of the battery should be implemented 
    (per example not to charge the battery in the morning to avoid to be full at midday and give a high peak injection)    
    The optimal sizing of the battery cannot be decoupled from the way it is controlled. This is to come in future work.
    
    """)

    #st.markdown("<span style='color:red ; font-size:25pt'><b> TODO: Complete this part </b></span>", unsafe_allow_html=True)


    st.write("📋 **Reference without storage, ☀️ only**")

    col1, col2, col3 = st.columns(3)
    col1.metric("Consumption peak", f"{peak_power_of_consumption :.1f}" + " kW")
    col2.metric("Production peak", f"{peak_power_of_production :.1f}" + " kW")  
    col3.metric("Peak bill Consump", f"{peak_power_of_consumption * peak_price_usr_input :.0f} CHF" )

    col1, col2, col3 = st.columns(3) 
    col1.metric("Grid-consumption peak", f"{peak_grid_consumption_with_solar :.1f}" + " kW")  
    col2.metric("Grid Production peak", f"{-peak_grid_injection_with_solar :.1f}" + " kW")   
    col3.metric("Peak bill sol", f"{bill_of_peak_solar_only :.0f} CHF" )

    st.markdown("---")
    st.subheader(" 🪓 Peak shaving: " + f"The consumption is shaved at  {clipping_level :.1f} kW ")

    st.write("📋 **Results of simulation with solar and storage 🔋** ")
    col1, col2, col3= st.columns(3)
    col1.metric("Grid-consumption peak", f"{peak_grid_consumption_with_batteries :.1f}" + " kW")
    col2.metric("Grid Production peak", f"{-peak_grid_injection_with_batteries :.1f}" + " kW")
    col3.metric("Peak bill sol+sto", f"{bill_of_peak_with_storage :.0f} CHF" , 
                                     f"{(bill_of_peak_with_storage - bill_of_peak_solar_only) :.0f} CHF ", delta_color="off" )



    fig_acsource_hours_heatmap = build_hours_grid_heatmap_figure(hours_mean_df)
    st.pyplot(fig_acsource_hours_heatmap)

    fig_hist = build_power_histogram_figure(df_pow_profile)
    st.pyplot(fig_hist)



    st.markdown("---")
    st.subheader("Assessement of the energy in the peaks, cut down from the peak recorded")
    st.write("This part is a pure study of the peaks, there is no simulation of the system with the battery")


    length_profile = len(df_pow_profile.index)
    #clipping_level = peak_shaving_user_input*peak_power_of_consumption/100.0
    clipping_level_profile = np.ones(length_profile)* clipping_level
    df_pow_profile["Clipping level"] = clipping_level_profile

    #Make the clipping:
    df_pow_profile["Clipped consumption"] = pow_array_all
    df_pow_profile["Clipped consumption"] = df_pow_profile["Clipped consumption"].clip(upper=clipping_level)
    df_pow_profile["peaks over limit"] = df_pow_profile["Consumption [kW]"]-df_pow_profile["Clipped consumption"]
    df_pow_profile["margin under limit"] = clipping_level - df_pow_profile["Clipped consumption"]

    clipped_consumption_kWh = df_pow_profile["Clipped consumption"].sum()/4.0
    clipped_peaks_kWh = df_pow_profile["peaks over limit"].sum()/4.0

    peak_e_ratio = (clipped_peaks_kWh)/consumption_kWh
    clipping_losses2 = df_pow_profile["peaks over limit"].sum()/4.0/consumption_kWh


    #Counting of peaks and integrating their energy:
    number_of_peaks = 0
    largest_peak_kWh = 0.0 

    integration_of_single_peaks = np.zeros(length_profile)
    integration_of_recovery = np.zeros(length_profile)
    integration_of_peaks_with_recovery = np.zeros(length_profile) #in this one we have to recover the energy with a factor EFFICIENCY_BATT_ONE_WAY^2
    margin_to_recharge = df_pow_profile["margin under limit"].values

    k = 0
    n = 0

    back_to_zero = False

    for value in df_pow_profile["peaks over limit"].values:
        if value == 0.0 :
            
            integration_of_single_peaks[k] = 0.0
            integration_of_recovery[k]  =  margin_to_recharge[k]/4 + integration_of_recovery[k-1]
            integration_of_peaks_with_recovery[k] = integration_of_peaks_with_recovery[k-1] - margin_to_recharge[k] /4.0 * EFFICIENCY_BATT_ONE_WAY*EFFICIENCY_BATT_ONE_WAY
            
            if integration_of_peaks_with_recovery[k] < 0.0 :
                integration_of_peaks_with_recovery[k] = 0.0

            if back_to_zero: 
                number_of_peaks = number_of_peaks + 1
                back_to_zero = False
        else: 
            integration_of_single_peaks[k] = value /4.0 + integration_of_single_peaks[k-1]
            integration_of_peaks_with_recovery[k] = value /4.0 + integration_of_peaks_with_recovery[k-1]

            integration_of_recovery[k] = 0.0
            back_to_zero = True

        k = k + 1

    df_pow_profile["integ of peaks"] = integration_of_single_peaks
    df_pow_profile["integ of recovery"] = integration_of_recovery
    df_pow_profile["integ of peaks and recovery"] = integration_of_peaks_with_recovery

    largest_peak_kWh = integration_of_single_peaks.max()
    battery_for_peak_shaving_kWh = integration_of_peaks_with_recovery.max()

    #largest_peak_kWh = df_pow_profile["integ of peaks"].max()







    #Visualization:
    col1, col2, col3= st.columns(3)
    col1.metric("Peak shaving level ", f" {clipping_level :.1f} kW ", f"{peak_shaving_user_input - 100.0 :.0f} % reduction", delta_color="off")
    col2.metric("Number of peaks ", f" {number_of_peaks :.0f} peaks")
    col3.metric("Peak Bill", f"{clipping_level * peak_price_usr_input :.1f} CHF" , f"{peak_shaving_user_input - 100.0 :.0f} % reduction", delta_color="off")

    fig_combined = px.line(df_pow_profile, x=df_pow_profile.index, 
                            y=["Consumption [kW]", "Clipping level", "Clipped consumption"], 
                            title="Consumption and clipping level", 
                            labels={"value": "Power (kW)", "variable": "Legend"},
                            color_discrete_sequence=["lightcoral", "lightblue", "lightgreen"] )
    
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


    # #############   
    # test_array = solar_system.peak_shaving_profile
    # df_pow_profile["test"] = test_array 

    # fig_test = px.line(df_pow_profile, x=df_pow_profile.index, 
    #                         y=["Consumption [kW]", "Clipping level", "test"], 
    #                         title="TEST", 
    #                         labels={"value": "Power (kW)", "variable": "Legend"},
    #                         color_discrete_sequence=["lightcoral", "lightblue", "lightgreen"] )
    # st.plotly_chart(fig_test)
    # #################

    st.write("How much energy is in each of those peaks? That is an indication of the battery size for this task. To really perfor this peak shaving with a battery, we must be sure that the battery can recharge between two peaks, that is why the battery size may be bigger that the peak size.")


    col1, col2, col3= st.columns(3)
    col1.metric("The largest peak is", f" {largest_peak_kWh :.1f} kWh")
    col2.metric("Battery energy reserved needed", f" {battery_for_peak_shaving_kWh :.1f} kWh " , f"{battery_for_peak_shaving_kWh / battery_size_kwh_usr_input *100 :.0f} % of total")
    col3.metric("Energy of all peaks shaved", str(int(clipped_peaks_kWh))+" kWh", f"{-peak_e_ratio*100 :.1f}"+"% of total energy", delta_color="off")



    fig_integ = px.line(df_pow_profile, x=df_pow_profile.index, 
                            y=["peaks over limit", "integ of peaks", "integ of peaks and recovery"], 
                            title="Peaks and their energy", 
                            labels={"value": "Power (kW / kWh)", "variable": "Legend"},
                            color_discrete_sequence=["lightcoral", "lightblue", "lightgreen"] )

    # Move legend below the graph
    fig_integ.update_layout(
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.2,  # Position below the graph
            xanchor="center",
            x=0.1
        )
    )
    st.plotly_chart(fig_integ)


#**********************************
st.markdown("---")
st.subheader(" More about the backup time 🪫 ")
#**********************************
opt_to_display_bkup = st.checkbox("Show this part of analysis about backup if necessary. That adds time to each simulation to display it")

if opt_to_display_bkup:

    st.write(""" Here the reserve time on battery in case of blackout (how long is it possible to supply the coming consumption with the battery in islanding 🏝 🏭)

    """)
    #st.markdown("<span style='color:red ; font-size:25pt'><b> TODO: Complete this part </b></span>", unsafe_allow_html=True)



    col1, col2 = st.columns(2)
    col1.metric("Minimal time of backup on battery", f" {minimal_backup_time} hours")
    col2.metric("Minimal time of backup on battery and solar", "TO DO")

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



    # ###########################
    # #For DEBUG: on the counted 
    # # Energy Consumption Plot using Plotly
    # fig_conso_coming = px.line(df_pow_profile, 
    #                         x=df_pow_profile.index, 
    #                         y=["Energy in coming consumption", "Energy to empty batt", "Energy in coming consumption and solar"], 
    #                         title=" Coming consumption on quarters", 
    #                         labels={"value": "Com. Cons [kWh]", "variable": "Legend"},
    #                         color_discrete_sequence=["red", "green", "yellow"] 
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
    # ###############################



    # Energy Consumption Plot using Plotly    #, "Time of backup on battery and solar"  , and on battery and solar "yellow"
    fig_batt_time_to_go = px.area(df_pow_profile, 
                            x=df_pow_profile.index, 
                            y=["Time of backup on battery"], 
                            title=" Time of backup on batteries only  🌃  🪫 🏴", 
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



    st.write("This indicate for every moment how much time could be spend on the battery only with the coming load and the SOC at that precise time. This is not the possible islanding time as the solar production is not taken into account, this is for an future graph. The goal here is to have an idea of the reserve independently of the enventual solar")




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
         
         The system sizing cannot be decoupled of the way it is operated, especially when there are multiple objectives 
         like peakshaving, islanding, self-consumption and variable price optimization ...
         Here an standard inverter behaviour was implemented.
         This daily energy management optimization is yet to come. It will be perfomed with day by day optimization.
         That is where the different objectives are married. It's less obvious, but not rocket science ;-) 
         
         Then there will be real world control: to apply this strategy to the inverter (next3 of Studer-Innotec of course...), 
         transmit the orders with the API or locally with Modbus... 
         - Without solar: give directly the power setpoint on the grid input (AC-Source) 
            to force charging and set discharge current to 0 when you want to avoid discharge 
         - With solar: choose the time when to charge, discharge and force charge from the grid
         - That was already tested here for the nx3: https://github.com/moixpo/nxcontrol
         - a good control sould take the weather forcast into account, that was tested with Openmeteo API
             but now all the pieces of the puzzle must be put together...  
         
         ...see you later """)

st.write("This part will be developped soon... ⏳️ ")





    
# st.write("📋 **Data Overview head**")
# st.dataframe(list_of_days[0].head())
# st.dataframe(list_of_days[1].head())
# st.dataframe(list_of_days[-1].head())



# fig_scat1 = build_power_profile(df_pow_profile, "Solar power scaled")
# st.pyplot(fig_scat1)



#st.plotly_chart(fig_scat2)



#st.markdown("---")

#st.markdown("<span style='color:red'><b> Smart Charging TODO </b></span>", unsafe_allow_html=True)



################################
# Optimized use of the battery for discharging:
# -discharge at the best price time
################################

# st.markdown("---")
# st.markdown("---")

# # Show dataset preview
# st.title("📋 **Data Overview, for debug purpose**")
# st.dataframe(df_pow_profile.head())

# st.dataframe(df_pow_profile.tail())


