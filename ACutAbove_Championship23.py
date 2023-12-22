import streamlit as st
import requests
import pandas as pd
import json
from functools import reduce
from time import strftime, localtime
from datetime import datetime
import numpy as np
import altair as alt
import IPython
import plotly.express as px
from pandas import json_normalize
import seaborn as sns
from sleeper_wrapper import League
from sleeper_wrapper import Players


####### setting some stuff up

st.set_page_config(page_title="A Cut Above Scoreboard")
st.title(":blue[A Cut Above - Championship Scoreboard]")

leagueid = "992211821861576704"

now = datetime.now()
now = now.strftime('%Y-%m-%d')


if  now > '2024-01-01': currentweek=18
elif now > '2023-12-25': currentweek=17
elif now > '2023-12-18': currentweek=16
elif now > '2023-12-11': currentweek=15
elif now > '2023-12-04': currentweek=14
elif now > '2023-11-27': currentweek=13
elif now > '2023-11-20': currentweek=12
elif now > '2023-11-13': currentweek=11
elif now > '2023-11-06': currentweek=10
elif now > '2023-10-30': currentweek=9
elif now > '2023-10-23': currentweek=8
elif now > '2023-10-16': currentweek=7
elif now > '2023-10-09': currentweek=6
elif now > '2023-10-02': currentweek=5
elif now > '2023-09-25': currentweek=4
elif now > '2023-09-18': currentweek=3
elif now > '2023-09-11': currentweek=2
else: currentweek=1

leagueid = "992211821861576704"

league = League(leagueid)

############################################# users

# get all users in a particular league
users = league.get_users()
users = pd.DataFrame(users)

userlist = users['user_id'].tolist() ## metadata has team name...maybe I can eventually get this to be fully automated

# initialize list of lists
data = [['Mat', 1], ['Jeff', 2], ['CJ', 3],['Leo', 4],['Kevin', 5],['Hunter', 6],['Kyle', 7], ['Nick', 8], \
['Jimmy', 9],['Jonathan', 10],['Jon', 11],['Harry J', 12],['Ian', 13],['Brandon', 14],['Myles', 15],['Harry G', 16],['Shea', 17],['Ed', 18]]
  
# Create the pandas DataFrame
users_df = pd.DataFrame(data, columns=['Manager', 'roster_id'])

df = users_df.loc[users_df.index.repeat(17)].reset_index(drop=True)
df['Week'] = df.groupby(['Manager'])['Manager'].transform("cumcount")
df['Week'] = df['Week']+1
df = df.loc[(df['Week'] <= currentweek)]

############################################# matchups

all_matchups1=pd.DataFrame()
for i in range(1,currentweek+1): #gotta automate!
    data = league.get_matchups(i)
    data1 = pd.DataFrame(data)
    data1['Week'] = i
    frames = [all_matchups1,data1]
    all_matchups1= pd.concat(frames)



all_matchups2 = pd.merge(all_matchups1, users_df, left_on='roster_id', right_on='roster_id')
all_matchups = pd.merge(df, all_matchups2, on=['Manager','Week'],how='left')


all_matchups.rename(columns={"points": "Points"}, inplace=True)

all_matchups = all_matchups[["Week","Manager","Points"]]
all_matchups['Week'] = all_matchups['Week'].astype('string')
all_matchups['Points'] = all_matchups['Points'].astype('string').astype('float')
all_matchups['Cumulative Points'] = all_matchups.groupby(['Manager'])['Points'].cumsum()
all_matchups['Week'] = all_matchups['Week'].astype(int)

## filter for championship weeks and managers
list_of_managers = ["Hunter","Jeff","Leo","Jonathan"]
all_matchups = all_matchups[all_matchups['Manager'].isin(list_of_managers)]
all_matchups = all_matchups[all_matchups['Week'] > 14]

### switch to wide table

all_matchups_wide = all_matchups.pivot(index='Manager', columns='Week', values='Points')

all_matchups_wide['Total'] = all_matchups_wide.sum(axis=1)
all_matchups_wide = all_matchups_wide.sort_values(by=['Total'], ascending=False)


#st.write("We're into Week {theweek} and {teamcount} teams are still alive. The remaining overall budget has gone from 18K to {thebudget}."\
#         .format(theweek=currentweek,teamcount=alive_text,thebudget=budget_left_text))
st.dataframe(all_matchups_wide)