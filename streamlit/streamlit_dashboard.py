import streamlit as st
import psycopg2
import pandas as pd
import numpy as np
import yaml
import matplotlib.pyplot as plt
import altair as alt
import seaborn as sns
import plotly.express as px


# import plotly.graph_objects as go

def load_config():
    stream = open('config.yaml')
    db_config = yaml.load(stream, Loader=yaml.FullLoader)
    return db_config

db_config = load_config()
connection = psycopg2.connect(
    database = db_config['database'],
    user = db_config['username'],
    password = db_config['password'],
    host = db_config['hostname']
)
cur = connection.cursor()

### KEYS
sql_windows = {'Fa-Open-2017': ['2017-07-01', '2017-10-01'],
            'Fa-Close-2017': ['2017-10-01', '2018-01-01'],
            'Sp-Open-2018': ['2018-01-01', '2018-04-01'],
            'Sp-Close-2018': ['2018-04-01', '2018-07-01'],
            'Fa-Open-2018': ['2018-07-01', '2018-10-01'],
            'Fa-Close-2018': ['2018-10-01', '2019-01-01'],
            'Sp-Open-2019': ['2019-01-01', '2019-04-01'],
            'Sp-Close-2019': ['2019-04-01', '2019-07-01'],
            'Fa-Open-2019': ['2019-07-01', '2019-10-01'], 
            'Fa-Close-2019': ['2019-10-01', '2020-01-01'], 
            'Sp-Open-2020': ['2020-01-01', '2020-04-01'],
            'Sp-Close-2020': ['2020-04-01', '2020-07-01'],
            'Fa-Open-2020': ['2020-07-01', '2020-10-01'],
            'Fa-Close-2020': ['2020-10-01', '2021-01-01'],
            'Sp-Open-2021': ['2021-01-01', '2021-04-01'],
            'Sp-Close-2021': ['2021-04-01', '2021-07-01'],
            'Fa-Open-2021': ['2021-07-01', '2021-10-01'],
            'Fa-Close-2021': ['2021-10-01', '2022-01-01'],
            'Sp-Open-2022': ['2022-01-01', '2022-04-01'],
            'Sp-Close-2022': ['2022-04-01', '2022-07-01'],
            }

uuid_name_dict = dict({'Brandeis University': '5d6afd8d-1184-4c7f-ba23-bee36a42f3d0',
        'University of Connecticut' : '7223e991-f17a-4238-8563-a25d2a8ef1a0',
        'Northeastern University' : '38f6eab1-0e9d-4014-b2c2-49664d750b6d',
        'The Ohio State University': 'e7e7d205-106f-4e18-879b-47d5b70f906b',
        'University of Oxford': '2f6051c4-08a3-4e9e-bf4d-0402b8a96a5b',
        'Tufts University' : '298ec884-3abc-435b-bbcc-ff84f4c88d08',
        'Wesleyan University' : 'b2f08514-ccb6-4663-843d-6dbb9b0c9a2f'})


st.set_page_config(page_title="TEN Analytics Dashboard", page_icon=":bar_chart:", layout="wide")
# @st.cache
# def get_image(path:str)->Image:
#     image = Image.open(path)
#     return image
# 
# image = get_image("dataSet/supermarket.jpeg") # path of the file
# st.sidebar.image(image, use_column_width=True)
st.title(":bar_chart: TEN Analytics Dashboard")
st.markdown("##")
st.sidebar.header("Filter Your Data")



university_option = st.sidebar.selectbox('University',('Tufts University', 'University of Connecticut', 'Wesleyan University'))
start_season = st.sidebar.selectbox('Season Start',
    ('Fa-Open-2017', 'Fa-Close-2017', 
    'Sp-Open-2018', 'Sp-Close-2018', 
    'Fa-Open-2018','Fa-Close-2018',
    'Sp-Open-2019', 'Sp-Close-2019',
    'Fa-Open-2019','Fa-Close-2019',
    'Sp-Open-2020', 'Sp-Close-2020',
    'Fa-Open-2020','Fa-Close-2020',
    'Sp-Open-2021', 'Sp-Close-2021',
    'Fa-Open-2021','Fa-Close-2021',
    'Sp-Open-2022', 'Sp-Close-2022'
     ))
     
end_season = st.sidebar.selectbox('Season End',
    ('Fa-Open-2017', 'Fa-Close-2017', 
    'Sp-Open-2018', 'Sp-Close-2018', 
    'Fa-Open-2018','Fa-Close-2018',
    'Sp-Open-2019', 'Sp-Close-2019',
    'Fa-Open-2019','Fa-Close-2019',
    'Sp-Open-2020', 'Sp-Close-2020',
    'Fa-Open-2020','Fa-Close-2020',
    'Sp-Open-2021', 'Sp-Close-2021',
    'Fa-Open-2021','Fa-Close-2021',
    'Sp-Open-2022', 'Sp-Close-2022'),
    index=19)
     
start_date = sql_windows[start_season][0]
end_date = sql_windows[end_season][1]


q = """
SELECT SUM(price)
FROM api_exchanges
WHERE date_sold >= '""" + start_date + """' and date_sold < '""" + end_date + """' and university_id = '""" + uuid_name_dict[university_option] + """'
"""

cur.execute(q)
res = cur.fetchall()

total = 0

if res[0][0] == None:
    total = 0
else:
    total = res[0][0]

st.header("Total Runnings")
col1, col2 = st.columns(2)

col1.metric(label="Total $ Sales", value="$" + str(total), delta=None)
col2.metric(label="Total Savings", value="$" + str(round(total * 1.895)), delta=None)


#Transaction Type Breakdown
q = """SELECT Seller_payment_type, Buyer_payment_type, COUNT(*) AS count_name
FROM api_exchanges
WHERE date_sold >= '""" + start_date + """' and date_sold < '""" + end_date + """' and university_id = '""" + uuid_name_dict[university_option] + """'
GROUP BY Seller_payment_type, Buyer_payment_type
ORDER BY count_name DESC;
"""

cur.execute(q)
res = cur.fetchall()
df = pd.DataFrame(res, columns=["seller payment type", "buyer payment type", "count"])
df['seller payment type'] = df['seller payment type'].apply(lambda x: "venmo" if x == 2 else "cash")
df['buyer payment type'] = df['buyer payment type'].apply(lambda x: "venmo" if x == 2 else "cash")
names = df['seller payment type'] + "-" + df['buyer payment type']
df['transaction_type'] = names
st.header(university_option + ' Transaction Type Breakdown')
# st.write(df)
fig = px.pie(df, values='count', names='transaction_type')
st.plotly_chart(fig)

st.caption('**Explanation:** This graph can be used to identify the most common types of payment for sellers and buyers.')
st.markdown('##')


st.header("Textbook Price Distribution")
# listings_col_hist, sales_col_hist = st.columns(2)
# with listings_col_hist:
q = """
SELECT price
FROM api_exchanges
WHERE date_added >= '""" + start_date + """' and date_added < '""" + end_date + """' and university_id = '""" + uuid_name_dict[university_option] + """'
AND (status = 1 or Status = 2)
"""
cur.execute(q)
res = cur.fetchall()
# 
# 

df_listings = pd.DataFrame(res, columns=["Listing Prices"])
df_listings = df_listings[df_listings['Listing Prices'] < 100]
q = """
SELECT price
FROM api_exchanges
WHERE date_sold >= '""" + start_date + """' and date_sold < '""" + end_date + """' and university_id = '""" + uuid_name_dict[university_option] + """'
AND (Status = 2)
"""
cur.execute(q)
res = cur.fetchall()

# 
# 
df_sales = pd.DataFrame(res, columns=["Sales Prices"])
df_sales = df_sales[df_sales['Sales Prices'] < 100]

prices_df = pd.concat([df_sales, df_listings], axis=1)
fig = px.histogram(prices_df, barmode='overlay', nbins=10)

# fig.show()
st.plotly_chart(fig)

st.caption('**Explanation:** This graph can be used to identify which price ranges books are most commonly listed and sold within. This allows TEN to work towards building a price recommendation model to help sellers find the most effective price for their books to ensure that they can spend the least amount of time in inventory.')
st.markdown('##')


#########################################
st.header("Popular Departments")
             
q = """
SELECT course_dept, count(course_dept), ROUND(avg(price), 2) AS avg_price FROM api_exchanges
LEFT JOIN api_courses ON api_exchanges.course_id = api_courses.uuid
WHERE date_sold >= '""" + start_date + """' and date_sold < '""" + end_date + """' and api_exchanges.university_id = '""" + uuid_name_dict[university_option] + """'
AND status = 2
GROUP BY(course_dept)
ORDER BY(count(course_dept)) DESC;
"""
cur.execute(q)
res = cur.fetchall()

df_department_sold = pd.DataFrame(res, columns=["course_dept", "count", "avg_price"])
df_department_sold["Status"] = "Sold"


q = """
SELECT course_dept, count(course_dept) FROM api_exchanges
LEFT JOIN api_courses ON api_exchanges.course_id = api_courses.uuid
WHERE date_added >= '""" + start_date + """' and date_added< '""" + end_date + """' and api_exchanges.university_id = '""" + uuid_name_dict[university_option] + """'
AND (status = 1 or status = 2)
GROUP BY(course_dept)
ORDER BY(count(course_dept)) DESC;
"""

cur.execute(q)
res = cur.fetchall()

df_department_added = pd.DataFrame(res, columns=["course_dept", "count"])
df_department_added["Status"] = "Listed"

# creating new dataframe by joining both dataframes on course_dept column
df_sl_percentage = df_department_sold.join(
                          df_department_added.set_index('course_dept'), 
                          on='course_dept', lsuffix='_sold', rsuffix='_listed')

df_sl_percentage = df_sl_percentage[df_sl_percentage['count_sold'] > 4]

# adding column for sales:listing percent on new dataframe
df_sl_percentage['Sales to Listings Ratio'] = (df_sl_percentage['count_sold'] / 
                                            df_sl_percentage['count_listed']) 

                                
sl_percentage = st.selectbox('Select the range of listed books that were sold', ('Show all', 
                            '0-25%', '25-50%', '50-75%', '75-100%'), index=0)
             
st.caption('After selecting a percentage range, hover over the displayed depts to see the average price of a textbook sold in that dept.')

### KEYS
percentage_windows = {'Show all': [0.0, 1.0],
                    '0-25%': [0.0, 0.25],
                    '25-50%': [0.25, 0.5],
                    '50-75%': [0.5, 0.75],
                    '75-100%': [0.75, 1.0],
                    }
percent_lower_limit = percentage_windows[sl_percentage][0]
percent_upper_limit = percentage_windows[sl_percentage][1]


# filtering based on sales:listings percent    
df_sl_percentage = df_sl_percentage[df_sl_percentage['Sales to Listings Ratio'] >= percent_lower_limit] 
df_sl_percentage = df_sl_percentage[df_sl_percentage['Sales to Listings Ratio'] < percent_upper_limit]

if sl_percentage == 'Show all':
    df_department = df_department_added.append(df_department_sold, ignore_index=True)
    df_department = df_department[df_department['count'] > 4]
    df_department = df_department[df_department.duplicated(subset=['course_dept'], keep=False)]
    
    fig = px.bar(df_department, x='course_dept', y='count', color='Status', barmode='group')

else:
    fig = px.bar(df_sl_percentage, x='course_dept', y='count_sold', color='Status_sold', barmode='group', hover_data=['avg_price'])

st.plotly_chart(fig)

st.caption('**Example Interpretation:** At Tufts University, between Fall 2017 Opening and Spring 2022 Closing, between 75-100% of the books listed in the Chemistry department were sold. The average price for a book sold was $35.39.')
st.caption('**Explanation:** This graph can be used to identify which departments have the highest yield for textbook sales. This gives TEN insight into which departments to focus advertising on, which can include reaching out to professors, department chairs, department newsletters, and clubs that cater to students majoring in relevant subjects.')
st.markdown('##')

#########################################
st.header("Total Sales and Listings by Season")
seasons = []
num_sales, num_listings = [], []
val_sales, val_listings = [], []

for key, value in sql_windows.items() :
    season = key;
    seasons.append(season)
    q = """
    SELECT COUNT(*), SUM(price)
    FROM api_exchanges
    WHERE api_exchanges.date_sold >= '""" + value[0] + """' AND api_exchanges.date_sold < '""" + value[1] + """'
    AND api_exchanges.university_id = '""" + uuid_name_dict[university_option] + """'
    AND status = 2
    UNION ALL
    SELECT COUNT(*), SUM(price)
    FROM api_exchanges
    WHERE api_exchanges.date_added >= '""" + value[0] + """' AND api_exchanges.date_added < '""" + value[1] + """'
    AND (Status = 1 or Status = 2 or status = 3 or status = 5)
    AND api_exchanges.university_id = '""" + uuid_name_dict[university_option] + """'
    """
    cur.execute(q)
    res = cur.fetchall()
    
    for i, label in enumerate(["Sales", "Listings"]):
#        
        try:
            if(label == 'Sales'):
                num_sales.append(res[i][0])
                val_sales.append(res[i][1])
            if(label == 'Listings'):
                num_listings.append(res[i][0])
                val_listings.append(res[i][1])
        except:
            if(label == 'Sales'):
                num_sales.append(0)
                val_sales.append(0)
            if(label == 'Listings'):
                num_listings.append(0)
                val_listings.append(0)

num_sales = [x if x != None else 0 for x in num_sales]
num_listings = [x if x != None else 0 for x in num_listings]

val_sales = [x if x != None else 0 for x in val_sales]
val_listings = [x if x != None else 0 for x in val_listings]

total_type = st.selectbox('Measurement Type',('Value of Books ($)', 'Number of Books'))


if(total_type == 'Value of Books ($)'):
    data = {
            'Period': seasons,
            'Sales': val_sales,
            'Listings': val_listings,
            }
else:
    data = {
            'Period': seasons,
            'Sales': num_sales,
            'Listings': num_listings,
            }
# 
# 
sales_df = pd.DataFrame(data)
fig = px.histogram(sales_df, x="Period", y=['Sales', 'Listings'], barmode='group')
st.plotly_chart(fig)


#########################################
st.header("Summary")

q = """
SELECT count(DISTINCT(buyer_id)) AS num_buyers, count(DISTINCT(seller_id)) AS num_sellers,
CASE
    WHEN count(DISTINCT(buyer_id)) > 0 THEN count(date_sold)/count(DISTINCT(buyer_id)) 
    WHEN count(DISTINCT(buyer_id)) = 0 THEN 0
    END AS avg_bought,
CASE
    WHEN count(DISTINCT(seller_id)) > 0 THEN count(date_sold)/count(DISTINCT(seller_id)) 
    WHEN count(DISTINCT(seller_id)) = 0 THEN 0
    END AS avg_sold,
CASE
    WHEN count(DISTINCT(seller_id)) > 0 THEN count(date_added)/count(DISTINCT(seller_id)) 
    WHEN count(DISTINCT(seller_id)) = 0 THEN 0
    END AS avg_listed
FROM api_exchanges
WHERE date_added >= '""" + start_date + """' and date_added< '""" + end_date + """' and date_sold >= '""" + start_date + """' AND date_sold < '""" + end_date + """' and university_id = '""" + uuid_name_dict[university_option] + """'
AND (status = 1 or status = 2);
"""
cur.execute(q)
res = cur.fetchall()
df_summary = pd.DataFrame(res, columns=["num_buyers", "num_sellers", "avg_bought", "avg_sold", "avg_listed"])
    
st.write('- In total, there were ', df_summary.iloc[0]["num_buyers"], 'buyers and ', 
        df_summary.iloc[0]["num_sellers"], ' sellers over this period of time.')
        
st.write('- On average, a single buyer bought ', df_summary.iloc[0]["avg_bought"], 
        'book(s) while a single seller listed ', df_summary.iloc[0]["avg_listed"], 
        'books and sold', df_summary.iloc[0]["avg_sold"], ' book(s) over this period of time.')
    


q = """
WITH num_added_sold AS (
SELECT count(transaction_id) AS books_added_sold
FROM api_exchanges
WHERE date_added >= '""" + start_date + """' and date_added< '""" + end_date + """' and date_sold >= '""" + start_date + """' AND date_sold < '""" + end_date + """' and university_id = '""" + uuid_name_dict[university_option] + """'
AND status = 2
),
 
num_added AS (
SELECT count(transaction_id) AS books_added
FROM api_exchanges
WHERE (date_added >= '""" + start_date + """' and date_added < '""" + end_date + """' and university_id = '""" + uuid_name_dict[university_option] + """')
AND (status = 1 or status = 2)
)

SELECT
CASE
    WHEN books_added = 0 THEN 0
    WHEN books_added > 0 THEN ROUND(((books_added_sold * 100.0)/ books_added), 1) 
    END AS turnover_rate
FROM num_added_sold, num_added
"""


cur.execute(q)
res = cur.fetchall()
df_summary["turnover_rate"] = pd.DataFrame(res, columns=["turnover_rate"])

st.write("- Approximately ", df_summary.iloc[0]["turnover_rate"], "% of books listed during this period of time were sold.")


# ind = np.arange(len(sales_df))  # the x locations for the groups
# width = 0.35       # the width of the bars
# 
# fig = plt.figure()
# ax = fig.add_subplot(111)
# rects1 = ax.bar(ind, sales_df["Listings"], width, color='blue')
# 
# rects2 = ax.bar(ind+width, sales_df["Sales"], width, color='orange')
# 
# # add some
# ax.set_ylabel(total_type)
# ax.set_title('Sales and Listings')
# ax.set_xticks(ind + width / 2)
# ax.set_xticklabels(sales_df['Period'], rotation=90)
# 
# ax.legend( (rects1[0], rects2[0]), ('Listings', 'Sales') )
# st.pyplot(fig)

# department level data


# number of buyers, number of sellers, average books for buyer, average book for seller

