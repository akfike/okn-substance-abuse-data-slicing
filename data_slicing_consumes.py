import pandas as pd

# Load the TSV file
data = pd.read_csv('NSDUH_2022_Tab 2.txt', delimiter='\t')

# Load the data dictionary
data_dictionary = pd.read_csv('Schare_DataDictionary_RawData_SAMHSA_NSDUH_2022.csv')

# Load the substances data
substances = pd.read_csv('substance.csv')


def apply_mapping(column_name, data_series):
    # Filter the data dictionary for the current column
    dict_subset = data_dictionary[data_dictionary['Question_code'] == column_name]
    if dict_subset.empty:
        return data_series  # If no mapping is found, return the original series

    # Initialize a result series with 'Unknown' to handle unmapped values
    result_series = pd.Series('Unknown', index=data_series.index)

    for index, row in dict_subset.iterrows():
        answer_type = row['Answer_type']
        if answer_type == 'direct':
            try:
                start_range = int(row['Answer_code'])
                end_range = int(row['Answer_name'])
                mask = data_series.between(start_range, end_range, inclusive='both')
                result_series[mask] = data_series[mask].apply(lambda x: str(int(x)))  # Convert directly to string of int
            except ValueError:
                continue
        elif answer_type == 'optional':
            # Convert and map only 'Unknown' values
            mapping_dict = {str(int(float(key))): val for key, val in zip(dict_subset['Answer_code'], dict_subset['Answer_name'])}
            unknown_mask = result_series == 'Unknown'
            mapped_values = data_series[unknown_mask].astype(str).map(mapping_dict)
            result_series[unknown_mask] = mapped_values.fillna('Unknown')

    return result_series

# Function to create data frames for each substance
def create_substance_data(substance_name, substance_code_column, days_column, avg_column=None):
    filtered_data = data[data[substance_code_column] == 1]
    substance_row = substances[substances['SubstanceName'] == substance_name]
    substance_id = substance_row['SubstanceID'].iloc[0]
    
    substance_data = pd.DataFrame()
    substance_data['PersonID'] = filtered_data['QUESTID2']
    substance_data['SubstanceID'] = substance_id
    substance_data['DaysConsumedPast30Days'] = apply_mapping(days_column, filtered_data[days_column])
    if avg_column:
        substance_data['AvgConsumedInPast30Days'] = apply_mapping(avg_column, filtered_data[avg_column])
    else:
        substance_data['AvgConsumedInPast30Days'] = ''
    
    return substance_data

# Create data frames for each substance
consumes_cigs_data = create_substance_data('Cigarettes', 'CIGEVER', 'CG30EST', 'CIG30AV')
consumes_alcohol_data = create_substance_data('Alcohol', 'ALCEVER', 'AL30EST', 'ALCUS30D')
consumes_mj_data = create_substance_data('Marijuana', 'MJEVER', 'MR30EST')

# Combine data frames
combined_data = pd.concat([consumes_cigs_data, consumes_alcohol_data, consumes_mj_data], ignore_index=True)

# Save the combined data to CSV
combined_data.to_csv('consumes.csv', header=True, index=False)

print("Data has been successfully appended to consumes.csv.")