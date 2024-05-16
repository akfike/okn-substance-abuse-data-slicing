import pandas as pd

# Load the TSV file
data = pd.read_csv('NSDUH_2022_Tab.txt', delimiter='\t')

# Load the data dictionary
data_dictionary = pd.read_csv('Schare_DataDictionary_RawData_SAMHSA_NSDUH_2022.csv')

# Load the substances data
substances = pd.read_csv('substance.csv')

# Create the 'consumes_in_combination_with.csv' file
def create_combination_data(data, alcohol_id, substance_mappings):
    combination_list = []
    for col, substance_name in substance_mappings:
        filtered_data = data[(data['CADRKDRUG'] == 1) & (data[col] == 1)]
        substance_id = substances[substances['SubstanceName'] == substance_name]['SubstanceID'].iloc[0]
        for _, row in filtered_data.iterrows():
            combination_list.append({
                'PersonID': row['QUESTID2'],
                'SubstanceID1': alcohol_id,
                'SubstanceID2': substance_id
            })
    combination_data = pd.DataFrame(combination_list)
    return combination_data

# Get the alcohol substance ID
alcohol_id = substances[substances['SubstanceName'] == 'Alcohol']['SubstanceID'].iloc[0]

# Define the substance mappings to check for combination
substance_mappings = [
    ('CADRKMARJ2', 'Marijuana')
]

# Create the combination data
combination_data = create_combination_data(data, alcohol_id, substance_mappings)

# Save the combination data to CSV
combination_data.to_csv('consumes_in_combination_with.csv', header=True, index=False)