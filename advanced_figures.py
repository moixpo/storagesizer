#advanced_figures.py
#visualisations of a solar system with storage
#Moix P-O
#Albedo Engineering 2025
#MIT license

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

#figsize=(FIGSIZE_WIDTH, FIGSIZE_HEIGHT)
FIGSIZE_WIDTH=14
FIGSIZE_HEIGHT=7

#colorset
PINK_COLOR='#FFB2C7'
RED_COLOR='#CC0000'
WHITE_COLOR='#FFFFFF'
A_RED_COLOR="#9A031E"
A_YELLOW_COLOR="#F7B53B"
A_BLUE_COLOR="#2E5266"
A_RAISINBLACK_COLOR="#272838"
A_BLUEGREY_COLOR="#7E7F9A"
A_GREY_COLOR_SLATE="#6E8898"
A_GREY_COLOR2_BLUED="#9FB1BC"
A_GREY_COLOR3_LIGHT="#F9F8F8"


#Stud
NX_LIGHT_BLUE="#F0F6F8"
NX_BLUE="#6BA3B8"
NX_BROWN="#A2A569"
NX_LIGHT_BROWN="#E3E4D2"
NX_PINK="#B06B96"
NX_GREEN="#78BE20"



#COLORS CHOICES FROM THE SETS ABOVE:
FIGURE_FACECOLOR=WHITE_COLOR #NX_LIGHT_BROWN
AXE_FACECOLOR=WHITE_COLOR
SOLAR_COLOR=A_YELLOW_COLOR
LOAD_COLOR=A_RED_COLOR
GENSET_COLOR=A_BLUE_COLOR


def build_SOC_heatmap_figure(hours_mean_df):
    
    all_channels_labels = list(hours_mean_df.columns)
    channel_number_SOC = [i for i, elem in enumerate(all_channels_labels) if ('SOC' in elem) ]
        
    #print(all_channels_labels)
    #print(channel_number_SOC)

    # Resample the data to hourly intervals and aggregate using the mean or sum
    #hourly_data = data.resample('H').mean()  # or data.resample('H').sum()
    energies_by_hours=hours_mean_df[all_channels_labels[channel_number_SOC[0]]]

    # Extract the values from the dataframe
    consumption_data = energies_by_hours.values
    #print(consumption_data)

    # Determine the shape of the reshaped array
    n_days = len(consumption_data) // (24)
    n_hours = 24
    
    # Reshape the data into a 2D array (days x hours)
    consumption_data = consumption_data.reshape(n_days, n_hours)

    #get the date of each day:
    date_of_consumption_data = energies_by_hours.index.date
    date_of_consumption_data= date_of_consumption_data.reshape(n_days, n_hours) #reshape to get one point each day
    date_only= date_of_consumption_data[:,0] #take the first column
    y_axis = np.arange(0,n_hours)
    
    
    # Create the heatmap
    fig_hours_heatmap, axe_hours_heatmap = plt.subplots(nrows=1, ncols=1, figsize=(FIGSIZE_WIDTH, FIGSIZE_HEIGHT))
    pos = axe_hours_heatmap.pcolormesh(date_only, y_axis, consumption_data.transpose(), shading='auto', cmap='turbo') #cmap='RdBu' cmap='hot' viridis, cmap = 'jet'
      
    #pos = axe_hours_heatmap.imshow(consumption_data.transpose(), cmap='jet', aspect='auto')  
    
    fig_hours_heatmap.suptitle('SOC state by hour [%]', fontweight = 'bold', fontsize = 12)
      
   
    axe_hours_heatmap.set_xlabel('Day of the Year', fontsize=12)
    axe_hours_heatmap.set_ylabel('Hour of the Day', fontsize=12)
    axe_hours_heatmap.set_ylim(-0.5,23.5)
    axe_hours_heatmap.set_yticks([0, 4, 8, 12, 16, 20])

    #axe_hours_heatmap.set_title("Profile by hour ", fontsize=12, weight="bold")
      
    # Display the colorbar
    fig_hours_heatmap.colorbar(pos, ax=axe_hours_heatmap)
    
    # #remove the frame
    # axe_hours_heatmap.spines['bottom'].set_color('white')
    # axe_hours_heatmap.spines['top'].set_color('white') 
    # axe_hours_heatmap.spines['right'].set_color('white')
    # axe_hours_heatmap.spines['left'].set_color('white')
    
    # axe_hours_heatmap.grid(True)
    
    # fig_hours_heatmap.figimage(im, 10, 10, zorder=3, alpha=.2)
    # fig_hours_heatmap.savefig("FigureExport/hours_soc_heatmap.png")

   
    return fig_hours_heatmap




def build_production_heatmap_figure(hours_mean_df):
    
    all_channels_labels = list(hours_mean_df.columns)
    channel_number_SOC = [i for i, elem in enumerate(all_channels_labels) if ('Solar power scaled' in elem) ]
        
    #print(all_channels_labels)
    #print(channel_number_SOC)

    # Resample the data to hourly intervals and aggregate using the mean or sum
    #hourly_data = data.resample('H').mean()  # or data.resample('H').sum()
    energies_by_hours=hours_mean_df[all_channels_labels[channel_number_SOC[0]]]

    # Extract the values from the dataframe
    consumption_data = energies_by_hours.values
    #print(consumption_data)

    # Determine the shape of the reshaped array
    n_days = len(consumption_data) // (24)
    n_hours = 24
    
    # Reshape the data into a 2D array (days x hours)
    consumption_data = consumption_data.reshape(n_days, n_hours)

    #get the date of each day:
    date_of_consumption_data = energies_by_hours.index.date
    date_of_consumption_data= date_of_consumption_data.reshape(n_days, n_hours) #reshape to get one point each day
    date_only= date_of_consumption_data[:,0] #take the first column
    y_axis = np.arange(0,n_hours)
    
    
    # Create the heatmap
    fig_hours_heatmap, axe_hours_heatmap = plt.subplots(nrows=1, ncols=1, figsize=(FIGSIZE_WIDTH, FIGSIZE_HEIGHT))
    pos = axe_hours_heatmap.pcolormesh(date_only, y_axis, consumption_data.transpose(), shading='auto', cmap='hot') #cmap='RdBu' cmap='hot' viridis, cmap = 'jet'
      
    #pos = axe_hours_heatmap.imshow(consumption_data.transpose(), cmap='jet', aspect='auto')  

    
    fig_hours_heatmap.suptitle('Solar production for each hour [kW] -[kWh]', fontweight = 'bold', fontsize = 12)  
    axe_hours_heatmap.set_xlabel('Day of the Year', fontsize=12)
    axe_hours_heatmap.set_ylabel('Hour of the Day', fontsize=12)
    axe_hours_heatmap.set_ylim(-0.5,23.5)
    axe_hours_heatmap.set_yticks([0, 4, 8, 12, 16, 20])

    #axe_hours_heatmap.set_title("Profile by hour ", fontsize=12, weight="bold")
      
    # Display the colorbar
    cbar = fig_hours_heatmap.colorbar(pos, ax=axe_hours_heatmap)
    cbar.set_label("kW  - kWh", rotation=270, labelpad=15)


    
    # fig_hours_heatmap.figimage(im, 10, 10, zorder=3, alpha=.2)
    # fig_hours_heatmap.savefig("FigureExport/hours_soc_heatmap.png")

   
    return fig_hours_heatmap



def build_consumption_heatmap_figure(hours_mean_df):
    
    all_channels_labels = list(hours_mean_df.columns)
    channel_number_SOC = [i for i, elem in enumerate(all_channels_labels) if ('Consumption [kW]' in elem) ]
        
    #print(all_channels_labels)
    #print(channel_number_SOC)

    # Resample the data to hourly intervals and aggregate using the mean or sum
    #hourly_data = data.resample('H').mean()  # or data.resample('H').sum()
    energies_by_hours = hours_mean_df[all_channels_labels[channel_number_SOC[0]]]

    # Extract the values from the dataframe
    consumption_data = energies_by_hours.values
    #print(consumption_data)

    # Determine the shape of the reshaped array
    n_days = len(consumption_data) // (24)
    n_hours = 24
    
    # Reshape the data into a 2D array (days x hours)
    consumption_data = consumption_data.reshape(n_days, n_hours)

    #get the date of each day:
    date_of_consumption_data = energies_by_hours.index.date
    date_of_consumption_data= date_of_consumption_data.reshape(n_days, n_hours) #reshape to get one point each day
    date_only= date_of_consumption_data[:,0] #take the first column
    y_axis = np.arange(0,n_hours)
    
    
    # Create the heatmap
    fig_hours_heatmap, axe_hours_heatmap = plt.subplots(nrows=1, ncols=1, figsize=(FIGSIZE_WIDTH, FIGSIZE_HEIGHT))
    pos = axe_hours_heatmap.pcolormesh(date_only, y_axis, consumption_data.transpose(), shading='auto', cmap='jet') #cmap='RdBu' cmap='hot' viridis, cmap = 'jet'
      
    #pos = axe_hours_heatmap.imshow(consumption_data.transpose(), cmap='jet', aspect='auto')  
    
    fig_hours_heatmap.suptitle('Consumption for each hour [kW] -[kWh]', fontweight = 'bold', fontsize = 12)
      
   
    axe_hours_heatmap.set_xlabel('Day of the Year', fontsize=12)
    axe_hours_heatmap.set_ylabel('Hour of the Day', fontsize=12)
    axe_hours_heatmap.set_ylim(-0.5,23.5)
    axe_hours_heatmap.set_yticks([0, 4, 8, 12, 16, 20])

    #axe_hours_heatmap.set_title("Profile by hour ", fontsize=12, weight="bold")
      
    # Display the colorbar
    cbar = fig_hours_heatmap.colorbar(pos, ax=axe_hours_heatmap)
    cbar.set_label("kW  - kWh", rotation=270, labelpad=15)


    
    # fig_hours_heatmap.figimage(im, 10, 10, zorder=3, alpha=.2)
    # fig_hours_heatmap.savefig("FigureExport/hours_soc_heatmap.png")

   
    return fig_hours_heatmap



def build_hours_grid_heatmap_figure(hours_mean_df):
    fig_acsource_hours_heatmap, axe_hours_heatmap_acsource = plt.subplots(nrows=1, ncols=1, figsize=(FIGSIZE_WIDTH, FIGSIZE_HEIGHT))

    # Assuming 'data' is your original Pandas timeseries with minute-level data
    # You can replace it with your actual timeseries data
    #data = hours_mean_df
    
    
    
    all_channels_labels = list(hours_mean_df.columns)
    channel_number_Pin_actif_Tot = [i for i, elem in enumerate(all_channels_labels) if "Grid with storage" in elem]        
    energies_by_hours=hours_mean_df[hours_mean_df.columns[channel_number_Pin_actif_Tot]]
    
    # Resample the data to hourly intervals and aggregate using the mean or sum
    #hourly_data = data.resample('H').mean()  # or data.resample('H').sum()
    
    # Extract the values from the Series
    consumption_data = energies_by_hours.values #/1000 already in kW
    
    # Determine the shape of the reshaped array
    n_days = len(consumption_data) // (24)
    n_hours = 24
    
    # Reshape the data into a 2D array (days x hours)
    consumption_data = consumption_data.reshape(n_days, n_hours)

    #get the date of each day:
    date_of_consumption_data = energies_by_hours.index.date
    date_of_consumption_data= date_of_consumption_data.reshape(n_days, n_hours) #reshape to get one point each day
    date_only= date_of_consumption_data[:,0] #take the first column
    y_axis = np.arange(0,n_hours)
    
    pos = axe_hours_heatmap_acsource.pcolormesh(date_only, y_axis, consumption_data.transpose(), shading='auto', cmap='terrain') #gist_ncar gist_stern
      
    
      
        
    # Create the heatmap
    #pos = axe_hours_heatmap_acloads.imshow(consumption_data.transpose(), cmap='jet', aspect='auto')  #cmap='RdBu' cmap='hot' viridis, cmap = 'jet'
    
    fig_acsource_hours_heatmap.suptitle('Energy consumption profile by hour on grid [kW - kWh]', fontweight = 'bold', fontsize = 12)
      
   
    
    axe_hours_heatmap_acsource.set_xlabel('Day of the Year', fontsize=12)
    axe_hours_heatmap_acsource.set_ylabel('Hour of the Day', fontsize=12)
    axe_hours_heatmap_acsource.set_ylim(-0.5,23.5)
    axe_hours_heatmap_acsource.set_yticks([0, 4, 8, 12, 16, 20])

    #axe_hours_heatmap.set_title("Profile by hour ", fontsize=12, weight="bold")
      
    # Display the colorbar
    fig_acsource_hours_heatmap.colorbar(pos, ax=axe_hours_heatmap_acsource)
    
  

    return fig_acsource_hours_heatmap




def build_battery_SOC_min_max_analysis_figure(quarters_mean_df):
    #all_channels_labels = list(total_datalog_df.columns)
    quarters_channels_labels=list(quarters_mean_df.columns)
    
    ####
    # channel recorded:
    channels_number_bat_soc = [i for i, elem in enumerate(quarters_channels_labels) if ('SOC' in elem)]
    
    #####
    # resample the day min and the day max
    day_max_df = quarters_mean_df.resample("1d").max()
    day_min_df = quarters_mean_df.resample("1d").min()

    delta_soc_df=day_max_df-day_min_df
    
    fig_batt_soc, axes_batt_soc = plt.subplots(nrows=2, 
                               ncols=1,
                               figsize=(FIGSIZE_WIDTH, FIGSIZE_HEIGHT))
    #axes4_2 = axes4.twinx()
    
    day_max_df.plot(y=day_max_df.columns[channels_number_bat_soc],
                          grid=True,
                          legend="max",
                          ax=axes_batt_soc[0])
    day_min_df.plot(y=day_min_df.columns[channels_number_bat_soc],
                          grid=True,
                          legend="min",
                          ax=axes_batt_soc[0]) 
    
    axes_batt_soc[0].legend(['max', 'min'])
    axes_batt_soc[0].set_ylabel('SOC [%]', fontsize=12)
    axes_batt_soc[0].grid(True) 
    axes_batt_soc[0].set_title('Daily battery SOC min-max analysis', fontsize=12, weight="bold")
   
    
    mean_delta=np.nanmean(delta_soc_df[day_max_df.columns[channels_number_bat_soc]].values) #mean value dropping NaN to avoid error
    
    
    delta_soc_df.plot(y=day_max_df.columns[channels_number_bat_soc],
                      grid=True,
                      legend="delta",
                      ax=axes_batt_soc[1])
    
    plt.axhline(mean_delta, color='r', linestyle='dashed', linewidth=2, alpha=0.5)

    axes_batt_soc[1].grid(True) 
    
    axes_batt_soc[1].set_ylabel('$\Delta$ SOC [%]', fontsize=12)
    axes_batt_soc[1].legend(['$\Delta$ SOC', 'mean'])


    # fig_batt_soc.figimage(im, 10, 10, zorder=3, alpha=.2)
    # fig_batt_soc.savefig("FigureExport/bat_SOC_min_max.png")

    return fig_batt_soc



    return fig_hist

def build_power_histogram_figure(quarters_mean_df):
    all_channels_labels = list(quarters_mean_df.columns)
    channels_number_Pin_actif = [i for i, elem in enumerate(all_channels_labels) if ("Grid with storage" in elem) ]
    channels_number_Pout_actif = [i for i, elem in enumerate(all_channels_labels) if ("Consumption [kW]" in elem) ]


    #take out the 0kW power (when genset/grid is not connected):    
    #chanel_number=channels_number_Pin_actif[0]


    channel_number = channels_number_Pin_actif[0]
    values_for_Pin_hist = quarters_mean_df[all_channels_labels[channel_number]]
    
    channel_number=channels_number_Pout_actif[0]
    values_for_Pout_hist= quarters_mean_df[all_channels_labels[channel_number]]

    fig_hist, axes_hist = plt.subplots(figsize=(FIGSIZE_WIDTH, FIGSIZE_HEIGHT))
    
    values_for_Pout_hist.hist( bins=80, alpha=0.5, label="Consumption",density=True)
    values_for_Pin_hist.hist( bins=80, alpha=0.5, label="Grid power", density=True)
    plt.axvline(values_for_Pout_hist.mean(), color='b', alpha=0.5, linestyle='dashed', linewidth=2)
    plt.axvline(values_for_Pin_hist.mean(), color='r', alpha=0.5, linestyle='dashed', linewidth=2)

    axes_hist.set_title("Histogram of Powers, consumption and grid exchange", fontsize=12, weight="bold")
    axes_hist.set_xlabel("Power [kW]", fontsize=12)
    axes_hist.set_ylabel("Frequency density", fontsize=12)
    axes_hist.legend(loc='upper right')


    axes_hist.grid(True)
    


    return fig_hist






def build_time_to_go_heatmap_figure(hours_mean_df):
    
    all_channels_labels = list(hours_mean_df.columns)
    channel_number_SOC = [i for i, elem in enumerate(all_channels_labels) if ('Time of backup on battery' in elem) ]
        
    #print(all_channels_labels)
    #print(channel_number_SOC)

    # Resample the data to hourly intervals and aggregate using the mean or sum
    #hourly_data = data.resample('H').mean()  # or data.resample('H').sum()
    energies_by_hours=hours_mean_df[all_channels_labels[channel_number_SOC[0]]]

    # Extract the values from the dataframe to an array:
    consumption_data = energies_by_hours.values
    #print(consumption_data)

    # Determine the shape of the reshaped array
    n_days = len(consumption_data) // (24)
    n_hours = 24
    
    # Reshape the data into a 2D array (days x hours)
    consumption_data = consumption_data.reshape(n_days, n_hours)

    #get the date of each day:
    date_of_consumption_data = energies_by_hours.index.date
    date_of_consumption_data= date_of_consumption_data.reshape(n_days, n_hours) #reshape to get one point each day
    date_only= date_of_consumption_data[:,0] #take the first column
    y_axis = np.arange(0,n_hours)
    
    
    # Create the heatmap
    fig_hours_heatmap, axe_hours_heatmap = plt.subplots(nrows=1, ncols=1, figsize=(FIGSIZE_WIDTH, FIGSIZE_HEIGHT))
    pos = axe_hours_heatmap.pcolormesh(date_only, y_axis, consumption_data.transpose(), shading='auto', cmap='turbo') #cmap='RdBu' cmap='hot' viridis, cmap = 'jet'
      
    #pos = axe_hours_heatmap.imshow(consumption_data.transpose(), cmap='jet', aspect='auto')  
    
    fig_hours_heatmap.suptitle('Time to go by hour [h]', fontweight = 'bold', fontsize = 12)
      
   
    axe_hours_heatmap.set_xlabel('Day of the Year', fontsize=12)
    axe_hours_heatmap.set_ylabel('Hour of the Day', fontsize=12)
    axe_hours_heatmap.set_ylim(-0.5,23.5)
    axe_hours_heatmap.set_yticks([0, 4, 8, 12, 16, 20])

    #axe_hours_heatmap.set_title("Profile by hour ", fontsize=12, weight="bold")
      
    # Display the colorbar
    fig_hours_heatmap.colorbar(pos, ax=axe_hours_heatmap)
    


   
    return fig_hours_heatmap





def build_bat_inout_figure(day_kwh_df, month_kwh_df):

    ##############################
    #CHARGE/DISCHARGE ENERGY OF THE BATTERY AND TRHOUGHPUT
    ################
    
    fig_bat_inout, axes_bat_inout = plt.subplots(nrows=2, ncols=1,figsize=(FIGSIZE_WIDTH, FIGSIZE_HEIGHT))
    
    
    day_kwh_df['Abs Discharge']=-day_kwh_df['Battery discharge power only']
    
    
    
    day_kwh_df[['Battery charge power only','Abs Discharge']].plot(ax=axes_bat_inout[0],
                          kind='line',
                          marker='o',
                          color=['g', 'r'])
    
    axes_bat_inout[0].legend(["CHARGE", "DISCHARGE"])
    axes_bat_inout[0].grid(True)
    #plt.xticks(np.arange(len(list(day_kwh_df.index))), labels=list(day_kwh_df.index.date), rotation=30, ha = 'center')        
    axes_bat_inout[0].set_ylabel("Energy per day [kWh]", fontsize=12)
    axes_bat_inout[0].set_title("How is the battery used? Daily and monthly cycling", fontsize=12, weight="bold")
    
    
    
    #to see both positive on the graph for better comparison:
    dischargeEm=-month_kwh_df['Battery discharge power only']
    chargeEm=month_kwh_df['Battery charge power only']
    ind = np.arange(len(list(month_kwh_df.index.month_name())))
    
    
    width = 0.35  # the width of the bars
    b1=axes_bat_inout[1].bar(ind- width/2, chargeEm.values, width, color='g', label='CHARGE')
    b2=axes_bat_inout[1].bar(ind+ width/2, dischargeEm.values, width, color='r', label='DISCHARGE')
    
    
    
    axes_bat_inout[1].set_ylabel("Energy per month [kWh]", fontsize=12)
    #axes_bat_inout.legend(["CHARGE", "DISCHARGE"])
    axes_bat_inout[1].legend()
    axes_bat_inout[1].grid(True)
    #plt.xticks(ind, labels=list(month_kwh_df.index.month_name()), rotation=30, ha = 'right')        
    labels_month=list(month_kwh_df.index.month_name())
    labels_year=list(month_kwh_df.index.year)
    loc, label= plt.xticks()

    for k,elem in enumerate(labels_month):
        if elem=='January':
            labels_month[k]=str(labels_year[k]) + ' January'
            
    
    #TODO: remove comment: change the ticks first to units
    #loc=[0, 1, 2]
    loc=np.arange(len(labels_month))
    plt.xticks(loc,labels=labels_month,rotation=35)


    return fig_bat_inout




def build_power_profile(quarters_mean_df, label_of_channel):
    #for tests:
    #start_date = dt.date(2018, 7, 1)
    #end_date = dt.date(2018, 8, 30) 
    
    # temp1 = total_datalog_df[total_datalog_df.index.date >= start_date]
    # temp2 = temp1[temp1.index.date <= end_date]

    temp2 = quarters_mean_df

    all_channels_labels = list(quarters_mean_df.columns)
    channel_number = [i for i, elem in enumerate(all_channels_labels) if label_of_channel in elem]
   
    #channel_number=channel_number_Pout_conso_Tot
    time_of_day_in_hours=list(temp2.index.hour+temp2.index.minute/60)
    time_of_day_in_minutes=list(temp2.index.hour*60+temp2.index.minute)
    
    #add a channels to the dataframe with minutes of the day to be able to sort data on it: 
    #Create a new entry in the dataframe:
    temp2['Time of day in minutes']=time_of_day_in_minutes
        
        
    fig_pow_by_min_of_day, axes_pow_by_min_of_day = plt.subplots(nrows=1, ncols=1, figsize=(FIGSIZE_WIDTH, FIGSIZE_HEIGHT))
    
    
    #maybe it is empty if there is no inverter:
    if channel_number:
        
        channel_label=all_channels_labels[channel_number[0]]
        
        axes_pow_by_min_of_day.plot(time_of_day_in_hours,
                          temp2[channel_label].values, 
                          marker='+',
                          alpha=0.25,
                          color='b',
                          linestyle='None')
       
        
    
        #faire la moyenne de tous les points qui sont à la même quart d'heure du jour:
        mean_by_minute=np.zeros(24*4)
        x1=np.array(range(0,24*4))
        for k in x1:
            tem_min_pow1=temp2[temp2['Time of day in minutes'].values == k*15]
            mean_by_minute[k]=np.nanmean(tem_min_pow1[channel_label].values)
            
    
        axes_pow_by_min_of_day.plot(x1/4, mean_by_minute,
                          color='r',
                          linestyle ='-',
                          linewidth=2,
                          drawstyle='steps-post')
    
        #faire la moyenne de tous les points qui sont à la même heure:
        mean_by_hour=np.zeros(24)
        x2=np.array(range(0,24))
        for k in x2:
            tem_min_pow2=temp2[temp2.index.hour == k]
            mean_by_hour[k]=np.nanmean(tem_min_pow2[channel_label].values)
            
    
        axes_pow_by_min_of_day.plot(x2, mean_by_hour,
                          color='g',
                          linestyle ='-',
                          linewidth=2,
                          drawstyle='steps-post')
        
        #mean power:
        #axes_pow_by_min_of_day.axhline(np.nanmean(total_datalog_df[channel_label].values), color='k', linestyle='dashed', linewidth=2)
        axes_pow_by_min_of_day.axhline(mean_by_minute.mean(), color='k', linestyle='dashed', linewidth=2)
        text_to_disp='Mean = ' + str(round(mean_by_minute.mean(), 2)) + ' '
        axes_pow_by_min_of_day.text(0.1,mean_by_minute.mean()+0.1,  text_to_disp, horizontalalignment='left',verticalalignment='bottom')
        axes_pow_by_min_of_day.legend(["All points", "quarter mean profile" ,"hour mean profile"])
        #axes_pow_by_min_of_day.set_ylabel("Power [kW]", fontsize=12)
        axes_pow_by_min_of_day.set_xlabel("Time [h]", fontsize=12)
        axes_pow_by_min_of_day.set_xlim(0,24)
        axes_pow_by_min_of_day.set_title("Profile by hour of the day " + label_of_channel, fontsize=12, weight="bold")
        axes_pow_by_min_of_day.grid(True)
        
    
    else:
        #axes_pow_by_min_of_day.text(0.0, 0.0, "There is no Studer inverter!", horizontalalignment='left',verticalalignment='bottom')
        axes_pow_by_min_of_day.set_title("There is no data with this lable!", fontsize=12, weight="bold")
        
    
    # fig_pow_by_min_of_day.figimage(im, 10, 10, zorder=3, alpha=.2)
    # fig_pow_by_min_of_day.savefig("FigureExport/typical_power_profile_figure.png")

    return fig_pow_by_min_of_day




def build_test_figure(array):
    #for tests:

    test_figure, axes_test = plt.subplots(nrows=1, ncols=1, figsize=(FIGSIZE_WIDTH, FIGSIZE_HEIGHT))
    
    
    #maybe it is empty if there is no inverter:            
    axes_test.plot(array)
    
    axes_test.set_title("Test figure", fontsize=12, weight="bold")
    axes_test.grid(True)
        
    return test_figure



def build_daily_indicators_polar_fraction_figure(day_kwh_df):


    
    all_channels_labels=list(day_kwh_df.columns)
    
    #####################################
    # the channels with SYSTEM Power 
    
    channels_number_Psolar_Tot = [i for i, elem in enumerate(all_channels_labels) if 'Solar power scaled' in elem]
    #channel_number_Pin_actif_Tot = [i for i, elem in enumerate(all_channels_labels) if "Pin power (ALL)" in elem]
    
    channel_number_Pin_Consumption_Tot = [i for i, elem in enumerate(all_channels_labels) if "Grid consumption with storage" in elem]
    channel_number_Pin_Injection_Tot = [i for i, elem in enumerate(all_channels_labels) if "Grid injection with storage" in elem]


    #channel_number_Pout_actif_Tot = [i for i, elem in enumerate(all_channels_labels) if "Pout power (ALL)" in elem]
    
    
     
    #utilisation directe du label plutot que les indexs des columns: 
    #chanel_label_Pout_actif_tot=all_channels_labels[channel_number_Pout_actif_Tot[0]]
    chanel_label_Pin_Consumption_tot=all_channels_labels[channel_number_Pin_Consumption_Tot[0]]

    chanel_label_Psolar_tot=all_channels_labels[channels_number_Psolar_Tot[0]]
    chanel_label_Pin_Injection=all_channels_labels[channel_number_Pin_Injection_Tot[0]]
    
    fig_indicators_polar, [axes_autarky, axes_selfcon],  = plt.subplots(nrows=1, ncols=2, 
                                                        figsize=(FIGSIZE_WIDTH, FIGSIZE_HEIGHT), 
                                                        subplot_kw={'projection': 'polar'})
    
    
    ############################
    #Daily Energies Fractions:
    #############
    #normalized energy production
    normed_solar=day_kwh_df[chanel_label_Psolar_tot]/(day_kwh_df[chanel_label_Psolar_tot]+abs(day_kwh_df[chanel_label_Pin_Consumption_tot])+1e-9)*100
    #normed_solar_reinjected=month_kwh_df[chanel_label_Psolar_tot]/(month_kwh_df[chanel_label_Psolar_tot]+abs(month_kwh_df[chanel_label_Pin_Consumption_tot])+1e-9)*100
    normed_grid=abs(day_kwh_df[chanel_label_Pin_Consumption_tot])/(day_kwh_df[chanel_label_Psolar_tot]+abs(day_kwh_df[chanel_label_Pin_Consumption_tot])+1e-9)*100
    
    normed_selfconsumption=(1-abs(day_kwh_df[chanel_label_Pin_Injection])/(day_kwh_df[chanel_label_Psolar_tot]+1e-9))*100

    
    ind = day_kwh_df.index.dayofyear/365
    theta = 2 * np.pi * ind

    p1=axes_autarky.plot(theta, normed_solar.values, color=SOLAR_COLOR,  linewidth=3)
    p1_s=axes_autarky.fill_between(theta, normed_solar.values, color=SOLAR_COLOR,  alpha=0.5)
    
    p2=axes_selfcon.plot(theta, normed_selfconsumption.values, color=GENSET_COLOR,  linewidth=3)
    p2_s=axes_selfcon.fill_between(theta, normed_selfconsumption.values, color=GENSET_COLOR,  alpha=0.5)
    
    axes_autarky.set_ylim([0, 100])
    axes_selfcon.set_ylim([0, 100])

    #plt.xticks(ind, labels=list(day_kwh_df.index.month_name()), rotation=30, ha = 'right')        
    labels_month=["January", "March", "June", "September"]
    labels_month_full=["January", "\nFebruary",  "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    

            
    loc, label = plt.xticks()
    loc = [0, np.pi/2, np.pi, np.pi*3/2]
    loc_full = np.arange(12)*np.pi/6
    axes_autarky.set_xticks(loc_full,labels=labels_month_full) #,rotation=35)
    #axes_selfcon.set_xticks(loc[0:3],labels=labels_month[0:3]) #,rotation=35)
    #axes_selfcon.set_xticks(loc_full[0:9],labels=labels_month_full[0:9]) #,rotation=35)
    axes_selfcon.set_xticks(loc_full,labels=labels_month_full) #,rotation=35)

    loc_y=[20, 40, 60, 80, 100]
    label_y=["20%", "40%", "60%", "80%", "100%"]
    axes_autarky.set_yticks(loc_y,labels=label_y) #,rotation=35)
    axes_selfcon.set_yticks(loc_y,labels=label_y) #,rotation=35)


    axes_autarky.set_theta_zero_location("N")  # theta=0 at the top
    axes_autarky.set_theta_direction(-1)  # theta increasing clockwise
    axes_selfcon.set_theta_zero_location("N")  # theta=0 at the top
    axes_selfcon.set_theta_direction(-1)  # theta increasing clockwise

    #axes_indicator.set_ylabel("Energy fraction [%]", fontsize=12)
    
    # Add a title to the entire figure
    fig_indicators_polar.suptitle("Daily solar indicators", fontsize=14, weight="bold")
    axes_autarky.set_title("Self-sufficiency", fontsize=12, weight="bold")
    #axes_autarky.legend(["Self-sufficiency"]) 
    axes_autarky.grid(True)

    axes_selfcon.set_title("Self-consumption", fontsize=12, weight="bold")
    #axes_selfcon.legend(["Self-consumption"]) 
    axes_selfcon.grid(True)

    #fig_indicators_polar.figimage(im, 10, 10, zorder=3, alpha=.2)
    #fig_indicators_polar.savefig("FigureExport/energy_indicators_polar.png")

    return fig_indicators_polar

