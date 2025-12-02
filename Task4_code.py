import streamlit as st
import pandas as pd
from yaml import safe_load
import numpy as np
import pyarrow.parquet as pa
import matplotlib.pyplot as plt
import matplotlib

st.title("Task4 Trzeciak Agnieszka")
st.set_page_config(layout="wide")

path = str(st.selectbox("Data set", ['DATA1', 'DATA2', 'DATA3']))
st.write(path+r'/users.csv')

Users = pd.read_csv(path+r'/users.csv')

with open(path+r'/books.yaml','r') as books_yaml:
    Books = pd.json_normalize(safe_load(books_yaml))
Books.columns = [column[1:] for column in Books.columns]

Orders = pa.read_table(path+r'/orders.parquet').to_pandas()
output_formula = r'\g<d>/\g<m>/\g<y>'
Orders['date'] = pd.to_datetime(Orders['timestamp'].str.replace(r'[\d:]+(?: [APap]\.?[Mm]\.?)?[ ,;]+(?P<d>\d{1,2})-(?P<m>\w+)-\d{2}(?P<y>\d{2})',output_formula,regex=True).str.replace(
                                    r'(?P<m>\d{2})/(?P<d>\d{2})/(?P<y>\d{2})[ ,;]+[\d:]+(?: [APap]\.?[Mm]\.?)?',output_formula,regex=True).str.replace(
                                    r'[\d:]+,? \d{2}(?P<y>\d{2})-(?P<m>\d{2})-(?P<d>\d{2})',output_formula,regex=True).str.replace(
                                    r'\d{2}(?P<y>\d{2})-(?P<m>\d{2})-(?P<d>\d{2})[ ,;]+[\d:]+(?: [APap]\.?[Mm]\.?)?',output_formula,regex=True).str.replace(
                                    r' ?(?P<d>\d{1,2})[-.](?P<m>\w+)[-.]\d{2}(?P<y>\d{2})[, ;]+[\d:]+(?: [APap]\.?[Mm]\.?)?',output_formula,regex=True).str.replace(
                                    r'[\d:]+(?: [APap]\.?[Mm]\.?)?[,; ]+(?P<m>\d{2})/(?P<d>\d{2})/(?P<y>\d{2})',output_formula,regex=True).str.replace(
                                    r'\d{2}(?P<y>\d{2})-(?P<m>\d{2})-(?P<d>\d{2})T[\d:]+\.?\d*',output_formula,regex=True).str.replace(
                                    r'\w+ (?P<m>\w+) +(?P<d>\d{1,2}) [\d:]+ \d{2}(?P<y>\d{2})',output_formula,regex=True).str.replace(
                                    r'[\d:]+(?: [APap]\.?[Mm]\.?)?[,; ]+\d{2}(?P<y>\d{2})-(?P<m>\d{2})-(?P<d>\d{2})',output_formula,regex=True),
                                dayfirst = True)
Orders['paid_price'] = np.where(np.where(Orders['unit_price'].str.contains(r'\€|EUR',regex=True),'EUR','USD')=='EUR',
                                pd.to_numeric(Orders['unit_price'].str.replace(r'\D*(\d+)\D?(\d*)\D*',r'\1.\2',regex=True))*1.2*Orders['quantity'],
                                pd.to_numeric(Orders['unit_price'].str.replace(r'\D*(\d+)\D?(\d*)\D*',r'\1.\2',regex=True))*Orders['quantity'])


col1, col2 = st.columns(2)
col1.markdown("<h3 style='text-align: center;'>Top 5 days</h1>", unsafe_allow_html=True)
col1.write(pd.DataFrame(round(Orders.groupby(by='date')['paid_price'].sum().sort_values(ascending=False),2)[:5]))

Users['alias_id'] = Users['id']
for column in Users.loc[:, (Users.columns != 'id') & (Users.columns != 'alias_id')]:
    for duplicated_user in Users[Users.loc[:, ~Users.columns.isin(['id','alias_id',column])].duplicated()].iterrows():
        if len(Users[Users[column]==duplicated_user[1][column]]['alias_id'].unique()) != 1:
            new_id = duplicated_user[1]['alias_id']
            for alias_id in Users[Users[column]==duplicated_user[1][column]]['alias_id'].unique():
                Users.loc[Users['alias_id']==alias_id,'alias_id']=new_id
number_of_unique_users = Users.groupby(by='alias_id')['alias_id'].unique().count()

def sort_author_list(author_list):
    return sorted(author_list)
Books['author'] = Books['author'].str.split(', ').apply(sort_author_list).str.join(', ')
number_of_unique_authors = len(Books.groupby(by='author'))

author = pd.merge(Books,Orders,left_on='id',right_on='book_id',validate='1:m',how='inner').groupby(by='author')['quantity'].sum().sort_values(ascending=False)[:1].index[0]

top_buyer_alias = pd.merge(Users,Orders,left_on='id',right_on='user_id',validate='1:m',how='inner').groupby(by='alias_id')['paid_price'].sum().sort_values(ascending=False).head(1)
best_buyer = list(Users[Users['alias_id']==pd.DataFrame(top_buyer_alias).index[0]]['id'])

col2.markdown("<h4 style='text-align: center;'></h1>", unsafe_allow_html=True)
col2.metric(label="Unique users", value=f"{number_of_unique_users:}")
col2.divider()
col2.metric(label="Unique authors", value=f"{number_of_unique_authors:}",height='stretch')
st.divider()
st.metric(label='Most sucessful author', value=f"{author:}",height='stretch')
st.metric(label='Best buyer', value=f"{best_buyer:}")
st.divider()

col1, col2, col3 = st.columns([1,4,1])
with col2:
    fig,ax = plt.subplots()
    ax.plot(Orders.groupby(by='date')['paid_price'].sum())
    ax.set_title('Daily revenue')
    ax.set_xlabel('Date')
    ax.set_ylabel('Revenue')
    st.pyplot(fig)











