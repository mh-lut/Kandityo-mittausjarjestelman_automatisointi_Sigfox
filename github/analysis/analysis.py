import sqlite3
import datetime
import matplotlib.pyplot as plt
import numpy
import folium

def check_pairs(database1, database2):
    # Connect to the first SQLite databases
    conn1 = sqlite3.connect(database1)  # Replace with your first database name
    cursor1 = conn1.cursor()
    conn2 = sqlite3.connect(database2)  # Replace with your second database name
    cursor2 = conn2.cursor()

    # Execute SELECT queries to fetch all data from both databases
    query1 = "SELECT message, time_start, time_finished, time_difference, answer, lat, lon, speed FROM sending_side"
    cursor1.execute(query1)
    query2 = "SELECT device, time, seqNumber, data, deviceTypeId, serverTime FROM serverInfo"
    cursor2.execute(query2)

    # Fetch
    rows1 = cursor1.fetchall()
    rows2 = cursor2.fetchall()

    # Close database connections
    cursor1.close()
    conn1.close()
    cursor2.close()
    conn2.close()

    # Lists
    matching_pairs_list = []
    unmatched_rows_list = []

    # Find pairs in sent and received messages
    for row1 in rows1:
        message, time_start, time_finished, time_difference, answer, lat, lon, speed = row1
        timestamp1 = round(float(time_start), 3)  # Round to time
        datetime_obj1 = datetime.datetime.fromtimestamp(timestamp1)# Make time object
        matched = False
        
        for row2 in rows2:
            device, time, seqNumber, data, deviceTypeId, serverTime = row2
            timestamp2 = round(float(serverTime)/1000, 3)  # Round to time
            datetime_obj2 = datetime.datetime.fromtimestamp(timestamp2) # Make time object
            delay = (datetime_obj2 - datetime_obj1).total_seconds() # Delay between messages
            
            if delay <= 30 and message == data and delay > 0:
                # Pair found!
                matching_pairs_list.append([row1, row2])
                matched = True
                break
        
        if not matched:
            unmatched_rows_list.append(row1)

    # Print the results
    """
    print("Matched Rows from Databases:")
    for pair in matching_pairs_list:
        print(pair)    

    print("Unmatched Rows from Databases:")
    for row in unmatched_rows_list:
        print(row)
    """
    
    return matching_pairs_list, unmatched_rows_list

# Count the delays per message size
def calculate_delay(matching_pairs_list):
    delay_list_1 = []
    delay_list_4 = []
    delay_list_8 = []
    delay_list_12 = []
    
    
    for pair in matching_pairs_list:
        # Calculate delay
        device, time, seqNumber, data, deviceTypeId, serverTime = pair[1]
        message, time_start, time_finished, time_difference, answer, lat, lon, speed = pair[0]
        
        timestamp2 = round(float(serverTime)/1000, 3)  # Make it right format
        datetime_obj2 = datetime.datetime.fromtimestamp(timestamp2) # Make time object
        
        timestamp1 = round(float(time_start), 3)  # Make it right format
        datetime_obj1 = datetime.datetime.fromtimestamp(timestamp1)# Make time object
        
        delay = (datetime_obj2 - datetime_obj1).total_seconds() # Delay between messages
        
        # Append to right list
        if len(message) == 1*2:
            delay_list_1.append([delay, lat, lon, speed])
        if len(message) == 4*2:
            delay_list_4.append([delay, lat, lon, speed])
        if len(message) == 8*2:
            delay_list_8.append([delay, lat, lon, speed])
        if len(message) == 12*2:
            delay_list_12.append([delay, lat, lon, speed])
    
    delay_lists = []
    delay_lists.append(delay_list_1)
    delay_lists.append(delay_list_4)
    delay_lists.append(delay_list_8)
    delay_lists.append(delay_list_12)
    
    return delay_lists

# For lost_message_graph
def calculate_percentage(unmatched_range, total_range, lower_bound, upper_bound):
    matched_range = [num for num in total_range if lower_bound <= float(num) <= upper_bound]
    if not matched_range:
        return 0
    return (len([num for num in unmatched_range if lower_bound <= float(num) <= upper_bound]) / 
            len(matched_range)) * 100

# Draw lost message graph %
def lost_message_graph(matching_pairs_list, unmatched_rows_list):
 
    unmatched_1 = []
    unmatched_4 = []
    unmatched_8 = []
    unmatched_12 = []

    matched_1 = []
    matched_4 = []
    matched_8 = []
    matched_12 = []
    
    # Separate the data into four lists based on the message lenght
    for message, _, _, _, _, _, _, speed in unmatched_rows_list:
        if len(message)/2 == 1:
            unmatched_1.append(speed)
        elif len(message)/2 == 4:
            unmatched_4.append(speed)
        elif len(message)/2 == 8:
            unmatched_8.append(speed)
        elif len(message)/2 == 12:
            unmatched_12.append(speed)
    
    for pair in matching_pairs_list:
        message, _, _, _, _, _, _, speed = pair[0]
        if len(message)/2 == 1:
            matched_1.append(speed)
        elif len(message)/2 == 4:
            matched_4.append(speed)
        elif len(message)/2 == 8:
            matched_8.append(speed)
        elif len(message)/2 == 12:
            matched_12.append(speed)

    total_messages_1 = unmatched_1 + matched_1  # Total number of messages message lenght = 1
    total_messages_4 = unmatched_4 + matched_4  # Total number of messages message lenght = 4
    total_messages_8 = unmatched_8 + matched_8  # Total number of messages message lenght = 8
    total_messages_12 = unmatched_12 + matched_12  # Total number of messages message lenght = 12

    
    # Calculate the percentage of unmatched messages for each size
    ranges = [(i, i+10) for i in range(0, 91, 10)]  # Generate ranges from 0 to 100 with step 10

    percent_unmatched_1 = [calculate_percentage(unmatched_1, total_messages_1, lower, upper) for lower, upper in ranges]
    percent_unmatched_4 = [calculate_percentage(unmatched_4, total_messages_4, lower, upper) for lower, upper in ranges]
    percent_unmatched_8 = [calculate_percentage(unmatched_8, total_messages_8, lower, upper) for lower, upper in ranges]
    percent_unmatched_12 = [calculate_percentage(unmatched_12, total_messages_12, lower, upper) for lower, upper in ranges]
    
    range_labels = [f'{lower}-{upper}' for lower, upper in ranges]
    
    # Create a plot
    x = numpy.arange(len(range_labels))  # x-coordinates for the bars
    width = 0.2  # Width of the bars

    fig, ax = plt.subplots()
    bar_1 = ax.bar(x - 1.5*width, percent_unmatched_1, width, label='Message lenght 1')
    bar_4 = ax.bar(x - 0.5*width, percent_unmatched_4, width, label='Message lenght 4')
    bar_8 = ax.bar(x + 0.5*width, percent_unmatched_8, width, label='Message lenght 8')
    bar_12 = ax.bar(x + 1.5*width, percent_unmatched_12, width, label='Message lenght 12')

    ax.set_xlabel('Speed')
    ax.set_ylabel('Percentage Unmatched')
    ax.set_title('Percentage of Unmatched Messages')
    ax.set_xticks(x)
    ax.set_xticklabels(range_labels)
    ax.legend()
    
    # Add labels
    add_value_labels(bar_1, ax)
    add_value_labels(bar_4, ax)
    add_value_labels(bar_8, ax)
    add_value_labels(bar_12, ax)

    plt.xticks(rotation=45)
    plt.tight_layout()

    plt.show()

    return None

#Count how many messages of that size are in the list
def calculate_length(rows, x):
    amount = 0
    for row in rows:
        message, time_start, time_finished, time_difference, answer, lat, lon, speed = row
        if len(message) == x:
            amount += 1
    return amount

# Accumulation of delays graph
def delay_graph(delay_lists):

    delay_only_list_1 = [innerlist[0] for innerlist in delay_lists[0]]
    delay_only_list_4 = [innerlist[0] for innerlist in delay_lists[1]]
    delay_only_list_8 = [innerlist[0] for innerlist in delay_lists[2]]
    delay_only_list_12 = [innerlist[0] for innerlist in delay_lists[3]]
    
    # Create a cumulative distribution plot for each dataset
    plt.hist(delay_only_list_1, bins=1000, density=True, histtype='step', color='blue', cumulative=True, alpha=0.5, label='Message lenght 1')
    plt.hist(delay_only_list_4, bins=1000, density=True, histtype='step', color='green', cumulative=True, alpha=0.5, label='Message lenght 4')
    plt.hist(delay_only_list_8, bins=1000, density=True, histtype='step', color='red',cumulative=True, alpha=0.5, label='Message lenght 8')
    plt.hist(delay_only_list_12, bins=1000, density=True, histtype='step', color='black',cumulative=True, alpha=0.5, label='Message lenght 12')

    # Add labels and title
    plt.xlabel('Time')
    plt.ylabel('Cumulative Probability')
    plt.title('Cumulative Distribution Plot')

    # Add a legend
    plt.legend()

    # Show the plot
    plt.grid()
    plt.show()

    return None

# Function to add value labels on top of the bars
def add_value_labels(bars, ax):
    for bar in bars:
        yval = bar.get_height() # Bar height
        if yval != 0:    
            ax.annotate(f'{yval:.2f}',
                        xy=(bar.get_x() + bar.get_width() / 2, yval),
                        xytext=(0, 0),  # text 
                        textcoords='offset points',
                        ha='center', va='bottom')

# Delay graph 2 (min/average/max)
def delay_graph_2(delay_lists):
    # Calculate min, average, and max for each list
    derlay_only_list_1 = []
    for sublist in delay_lists[0]:
        derlay_only_list_1.append(sublist[0])
        
    derlay_only_list_4 = []
    for sublist in delay_lists[1]:
        derlay_only_list_4.append(sublist[0])
        
    derlay_only_list_8 = []
    for sublist in delay_lists[2]:
        derlay_only_list_8.append(sublist[0])
    derlay_only_list_12 = []
    
    for sublist in delay_lists[3]:
        derlay_only_list_12.append(sublist[0])
    

    min_values = [min(sublist) if sublist else float('inf') for sublist in [derlay_only_list_1, derlay_only_list_4, derlay_only_list_8, derlay_only_list_12]]
    average_values = [numpy.mean(derlay_only_list_1), numpy.mean(derlay_only_list_4), numpy.mean(derlay_only_list_8), numpy.mean(derlay_only_list_12)]
    max_values = [max(sublist) if sublist else float('inf') for sublist in [derlay_only_list_1, derlay_only_list_4, derlay_only_list_8, derlay_only_list_12]]

    # Create bar positions
    x = numpy.arange(4)

    # Bar width
    width = 0.25

    # Create the bar chart
    fig, ax = plt.subplots()
    min_bars = ax.bar(x - width, min_values, width, label='Min')
    avg_bars = ax.bar(x, average_values, width, label='Average')
    max_bars = ax.bar(x + width, max_values, width, label='Max')

    # Add labels, title, and legend...
    ax.set_xlabel('Message lenght')
    ax.set_ylabel('Time')
    ax.set_title('Delay')
    ax.set_xticks(x)
    ax.set_xticklabels(['1', '4', '8', '12'])
    ax.legend()
    ax.grid(axis='y', linestyle='-', alpha=0.8) # Add grid - only across

    # Call the function to add value labels
    add_value_labels(min_bars, ax)
    add_value_labels(avg_bars, ax)
    add_value_labels(max_bars, ax)

    # Display the plot
    plt.tight_layout()
    plt.show()

    return None

# Location map html
def location_map(matching_pairs_list, unmatched_rows_list):
    

    
    # Create map
    m = folium.Map(location=[61.065724644380076, 28.094349045916406], zoom_start=10)
    for message, time_start, time_finished, time_difference, answer, lat, lon, speed in unmatched_rows_list:
        # Add markers
        folium.Marker([lat, lon], icon=folium.Icon(color="red")).add_to(m)
        
        
    # Add successful messages
    for pair in matching_pairs_list:
        message, time_start, time_finished, time_difference, answer, lat, lon, speed = pair[0]
        # Add markers
        folium.Marker([lat, lon], icon=folium.Icon(color="blue")).add_to(m)
        
        
    # Save the map
    m.save('sigfox_message_location_map.html')
    

    return None
    

def main():
    # Find pairs
    matching_pairs_list, unmatched_rows_list = check_pairs('./database.db', './database2.db')

    # Print amount
    print("Matching pairs: " + str(len(matching_pairs_list)))
    print("Unmatched: " + str(len(unmatched_rows_list)))

    # Calculate delay
    delay_lists = calculate_delay(matching_pairs_list)
    
    # Graphs...
    
    # Lost message percentage graph
    lost_message_graph(matching_pairs_list, unmatched_rows_list)
    
    # Delay graph
    delay_graph(delay_lists)
    
    # Delay graph 2 (min/average/max)
    delay_graph_2(delay_lists)

    # Map
    location_map(matching_pairs_list, unmatched_rows_list)
    
    


if __name__ == "__main__":
    main()