# https://www.ferc.gov/power-sales-and-markets/rtos-and-isos
# https://www.spp.org/documents/62914/rto%20and%20western%20rc%20footprint%20w%20planned%20expansion.png

# RTO/ISO regions manage regional electricity markets and transmission planning overseen by the Federal Energy Regulatory Commission (FERC).
# RTO/ISO regions do not cover all states nor adhere to state geographic boundaries, and some states are covered by multiple RTO/ISO regions.
# For simplicity, a best fit for an RTO/ISO region was determined for each state, but the actual RTO/ISO region may vary.

def get_iso_rto(state_abbr):
    if state_abbr in state_iso_rto:
        iso_rto = state_iso_rto[state_abbr]['iso_rto']
        if iso_rto == 'Non-RTO/ISO_Region':
            print("You are in a non-RTO/ISO region.")
        return iso_rto
    else:
        return "State abbreviation not found in the dictionary."

state_iso_rto = {
    'AL': {'name': 'Alabama', 'iso_rto': 'Non-RTO/ISO_Region'},'},
    'AK': {'name': 'Alaska', 'iso_rto': 'Non-RTO/ISO_Region'},
    'AZ': {'name': 'Arizona', 'iso_rto': 'Non-RTO/ISO_Region'},
    'AR': {'name': 'Arkansas', 'iso_rto': 'MISO'},
    'CA': {'name': 'California', 'iso_rto': 'CAISO'},
    'CO': {'name': 'Colorado', 'iso_rto': 'Non-RTO/ISO_Region'},
    'CT': {'name': 'Connecticut', 'iso_rto': 'ISO-NE'},
    'DE': {'name': 'Delaware', 'iso_rto': 'PJM'},
    'FL': {'name': 'Florida', 'iso_rto': 'Non-RTO/ISO_Region'},
    'GA': {'name': 'Georgia', 'iso_rto': 'Non-RTO/ISO_Region'},
    'HI': {'name': 'Hawaii', 'iso_rto': 'HICC'},
    'ID': {'name': 'Idaho', 'iso_rto': 'Non-RTO/ISO_Region'},
    'IL': {'name': 'Illinois', 'iso_rto': 'MISO'},
    'IN': {'name': 'Indiana', 'iso_rto': 'MISO'},
    'IA': {'name': 'Iowa', 'iso_rto': 'MISO'},
    'KS': {'name': 'Kansas', 'iso_rto': 'SPP'},
    'KY': {'name': 'Kentucky', 'iso_rto': 'PJM'},
    'LA': {'name': 'Louisiana', 'iso_rto': 'MISO'},
    'ME': {'name': 'Maine', 'iso_rto': 'ISO-NE'},
    'MD': {'name': 'Maryland', 'iso_rto': 'PJM'},
    'MA': {'name': 'Massachusetts', 'iso_rto': 'ISO-NE'},
    'MI': {'name': 'Michigan', 'iso_rto': 'MISO'},
    'MN': {'name': 'Minnesota', 'iso_rto': 'MISO'},
    'MS': {'name': 'Mississippi', 'iso_rto': 'MISO'},
    'MO': {'name': 'Missouri', 'iso_rto': 'MISO'},
    'MT': {'name': 'Montana', 'iso_rto': 'SPP'},
    'NE': {'name': 'Nebraska', 'iso_rto': 'SPP'},
    'NV': {'name': 'Nevada', 'iso_rto': 'Non-RTO/ISO_Region'},
    'NH': {'name': 'New Hampshire', 'iso_rto': 'ISO-NE'},
    'NJ': {'name': 'New Jersey', 'iso_rto': 'PJM'},
    'NM': {'name': 'New Mexico', 'iso_rto': 'Non-RTO/ISO_Region'},
    'NY': {'name': 'New York', 'iso_rto': 'NYISO'},
    'NC': {'name': 'North Carolina', 'iso_rto': 'Non-RTO/ISO_Region'},
    'ND': {'name': 'North Dakota', 'iso_rto': 'MISO'},
    'OH': {'name': 'Ohio', 'iso_rto': 'PJM'},
    'OK': {'name': 'Oklahoma', 'iso_rto': 'SPP'},
    'OR': {'name': 'Oregon', 'iso_rto': 'Non-RTO/ISO_Region'},
    'PA': {'name': 'Pennsylvania', 'iso_rto': 'PJM'},
    'RI': {'name': 'Rhode Island', 'iso_rto': 'ISO-NE'},
    'SC': {'name': 'South Carolina', 'iso_rto': 'Non-RTO/ISO_Region'},
    'SD': {'name': 'South Dakota', 'iso_rto': 'SPP'},
    'TN': {'name': 'Tennessee', 'iso_rto': 'Non-RTO/ISO_Region'},
    'TX': {'name': 'Texas', 'iso_rto': 'ERCOT'},
    'UT': {'name': 'Utah', 'iso_rto': 'Non-RTO/ISO_Region'},
    'VT': {'name': 'Vermont', 'iso_rto': 'ISO-NE'},
    'VA': {'name': 'Virginia', 'iso_rto': 'PJM'},
    'WA': {'name': 'Washington', 'iso_rto': 'Non-RTO/ISO_Region'},
    'WV': {'name': 'West Virginia', 'iso_rto': 'PJM'},
    'WI': {'name': 'Wisconsin', 'iso_rto': 'MISO'},
    'WY': {'name': 'Wyoming', 'iso_rto': 'Non-RTO/ISO_Region'},
    'DC': {'name': 'District of Columbia', 'iso_rto': 'PJM'}
}

