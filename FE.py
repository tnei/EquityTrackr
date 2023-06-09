import streamlit as st
import snowflake.connector
import pandas as pd
import matplotlib.pyplot as plt

# Streamlit configuration
st.set_page_config(page_title='EquityTrackr')

# Page layout
st.title('EquityTrackr')

# Function to create the capitalization table
def create_cap_table(conn, table_name):
    query = f"CREATE TABLE IF NOT EXISTS {table_name} (id INTEGER, name STRING, ownership FLOAT)"
    conn.cursor().execute(query)
    conn.commit()

# Function to insert ownership details
def insert_ownership(conn, table_name, id, name, ownership):
    query = f"INSERT INTO {table_name} (id, name, ownership) VALUES ({id}, '{name}', {ownership})"
    conn.cursor().execute(query)
    conn.commit()

# Function to retrieve ownership details
def get_ownership(conn, table_name):
    query = f"SELECT * FROM {table_name}"
    cursor = conn.cursor().execute(query)
    results = cursor.fetchall()
    return results

# Function to delete ownership details
def delete_ownership(conn, table_name, id):
    query = f"DELETE FROM {table_name} WHERE id = {id}"
    conn.cursor().execute(query)
    conn.commit()

# User inputs for Snowflake connection details
snowflake_user = st.text_input('Snowflake Username')
snowflake_password = st.text_input('Snowflake Password', type='password')
snowflake_account = st.text_input('Snowflake Account')
snowflake_warehouse = st.text_input('Snowflake Warehouse')
snowflake_database = st.text_input('Snowflake Database')
tenant_id = st.text_input('Tenant ID')  # Prompt for tenant identifier
snowflake_table = st.text_input('Snowflake Table')

# Connect to Snowflake
if st.button('Connect'):
    try:
        conn = snowflake.connector.connect(
            user=snowflake_user,
            password=snowflake_password,
            account=snowflake_account,
            warehouse=snowflake_warehouse,
            database=snowflake_database,
            schema=tenant_id  # Use tenant identifier as the schema name
        )
        st.success('Snowflake connection successful!')
        create_cap_table(conn, snowflake_table)
    except Exception as e:
        st.error(f"Error connecting to Snowflake: {str(e)}")

# Main menu
menu = st.sidebar.selectbox('Menu', ['Add Ownership', 'Manage Ownership', 'Visualize Ownership'])

if menu == 'Add Ownership':
    st.header('Add Ownership')
    id = st.number_input('ID')
    name = st.text_input('Name')
    ownership = st.number_input('Ownership')
    
    if st.button('Submit'):
        insert_ownership(conn, snowflake_table, id, name, ownership)
        st.success('Ownership added successfully!')

elif menu == 'Manage Ownership':
    st.header('Manage Ownership')
    ownership_data = get_ownership(conn, snowflake_table)
    
    if ownership_data:
        st.table(ownership_data)
        
        delete_id = st.number_input('Enter the ID to delete')
        
        if st.button('Delete'):
            delete_ownership(conn, snowflake_table, delete_id)
            st.success('Ownership deleted successfully!')
    else:
        st.info('No ownership data available.')
        
elif menu == 'Visualize Ownership':
    st.header('Visualize Ownership')
    ownership_data = get_ownership(conn, snowflake_table)
    
    if ownership_data:
        df = pd.DataFrame(ownership_data, columns=['ID', 'Name', 'Ownership'])
        fig, ax = plt.subplots()
        ax.bar(df['Name'], df['Ownership'])
        ax.set_xlabel('Name')
        ax.set_ylabel('Ownership')
        ax.set_title('Ownership Distribution')
        st.pyplot(fig)
else:
    st.info('No ownership data available.')

elif menu == 'Shares and Options':
    st.header('Shares and Options owned by the Founders of the Company')

    founders = st.text_area('Founders (separated by comma)')
    founders = [founder.strip() for founder in founders.split(',')]

    common_shares = []
    options = []
    series_a_shares = []
    series_a_investment = []
    total_ownership = []
    percentage_fully_diluted = []

    for founder in founders:
        st.subheader(founder)

        common_share = st.number_input('Common Shares')
        option = st.number_input('Options')
        series_a_share = st.number_input('Series A Preferred Shares')
        series_a_inv = st.number_input('Series A Investment')

        total_ownership.append(common_share + series_a_share)
        percentage_fully_diluted.append(total_ownership[-1] / (pre_money + invested) * 100)

        common_shares.append(common_share)
        options.append(option)
        series_a_shares.append(series_a_share)
        series_a_investment.append(series_a_inv)

    data = {
        'Shareholders': founders,
        'Common Shares': common_shares,
        'Options': options,
        'Series A Preferred Shares': series_a_shares,
        'Series A Investment': series_a_investment,
        'Total Share Ownership': total_ownership,
        'Percentage of Fully Diluted Shares': percentage_fully_diluted
    }

    df = pd.DataFrame(data)
    st.table(df)

else:
    st.info('No ownership data available.')

