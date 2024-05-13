import pandas as pd

# Load the TSV file
data = pd.read_csv('NSDUH_2022_Tab 2.txt', delimiter='\t')

# Load the data dictionary
data_dictionary = pd.read_csv('Schare_DataDictionary_RawData_SAMHSA_NSDUH_2022 - Sheet1 (1).csv')

# Create a new DataFrame for the output
person_data = pd.DataFrame()

# Map PersonID directly from QUESTID2
person_data['PersonID'] = data['QUESTID2']

# Define a function to apply the mapping from the data dictionary
def apply_mapping(column_name, data_series):
    # Filter the data dictionary for the current column
    dict_subset = data_dictionary[data_dictionary['Question_code'] == column_name]

    if dict_subset.empty:
        return data_series  # If no mapping is found, return the original series

    # Check the answer type from the filtered subset (assuming consistency within each column)
    answer_type = dict_subset.iloc[0]['Answer_type']

    # Process each type of answer
    if answer_type == 'direct':
        return data_series
    elif answer_type == 'optional':
        # Convert Answer_code to integer, then to string to remove any decimals
        mapping_dict = dict(zip(dict_subset['Answer_code'].astype(float).astype(int).astype(str), dict_subset['Answer_name']))
        print(f"Mapping for {column_name}: {mapping_dict}")

        # Apply the mapping to the data series, ensure conversion for matching
        return data_series.astype(str).map(mapping_dict).fillna('Unknown')  # Fill with 'Unknown' if no match found

# Apply the mappings for each relevant column
person_data['Age'] = apply_mapping('AGE3', data['AGE3'])
person_data['Sex'] = apply_mapping('IRSEX', data['IRSEX'])
person_data['RuralStatus'] = apply_mapping('COUTYP4', data['COUTYP4'])

# Save the processed data to CSV
person_data.to_csv('person.csv', index=False)

print("person.csv has been successfully created with the mapped values.")
