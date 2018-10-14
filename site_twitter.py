
# Importing libraries
import pandas as pd
import numpy as np
from textblob import TextBlob
from matplotlib import pyplot as plt
import seaborn as sns
from tweepy import Cursor,OAuthHandler

# For using twitter api, below i used essential information of my app.
key="key"
secret="secret"
token="token"
token_secret="token_secret"
auth = OAuthHandler(key, secret)
auth.set_access_token(token, token_secret)
api = API(auth)

# Adding twitter account names and DataFrame column names
accounts=['BBCWorld','NHKWORLD_News','trtworld','cnni','foxnews','dwnews','ajenglish','FRANCE24','rt_com','cgtnofficial']
names=['bbc','nhk','trt','cnn','foxnews','dw','aj','fr24','rt','cgtn']
accounts = accounts + names
tw=pd.DataFrame()
lists=[bbc,nhk,trt,cnn,foxnews,dw,aj,fr24,rt,cgtn]
accounts = accounts + lists

# Here, I requested for tweets by qursor object and recieved necessary information, number of favorites, retweets and texts of specific tweets
# This code may not work well since so many queries
tw['fav_' + i]=[k.favorite_count for i in accounts for j in Cursor(api.user_timeline, screen_name=i).pages() for k in j]
tw['rt_' + i]=[k.retweet_count for i in accounts for j in Cursor(api.user_timeline, screen_name=i).pages() for k in j]
tw[ i]=[k.text for i in accounts for j in Cursor(api.user_timeline, screen_name=i).pages() for k in j]
        

# Then i reduced the number of rows of dataframe to 3000
tw=tw.iloc[:3000,:]

# To manipulate text data, i set their column index numbers to a variable
text_places = [2,5,8,11,14,17,20,23,26,29]
# I deleted urls from texts
for i in tw.iloc[:,text_places].columns:
    tw[i] =  re.sub(r"http\S+", "", tw[i])

# I have saved specific data to csv, in order to further usage	
# The last dataset is added, you can check it out there.
tw.to_csv('tw.csv',index=False)

# Reading dataset which is created by me and uploaded, since tweets are changing constantly, I saved them to freeze the tweets
tw=pd.read_csv('tw.csv')

# Here, I created three dataframes to add sentiments and objectivities of tweets
sentiment_numeric=pd.DataFrame()
sentiment_class=pd.DataFrame()
objectivity_class=pd.DataFrame()

# Only text consisting dataframe creation
text=tw.iloc[:,text_places]
text.columns=['Al Jazeera','Trt World','CNN', 'Deutsche Welle','Fox News', 'France 24', 'NHK Japan', 'RT Russia', 'CGTN China','BBC']
for i in text.columns:
    for j in text.index:
        if type(text.loc[j,i])!=str:
            text=text.drop(j,axis=0)
			
# This is the place where i made sentiment and objectivity analysis, I have used TextBlob's features to extract these labels and numerics
# Thresholds are 
# For sentiments zero sentiment labelled as neutral, greater than zero is positive negatives are labelled as negative sentiment
# For objectivity categorization, I made up a threshold at 0.5 more than threshold labelled as objective, others are labelled as subjective
for i in text.columns:
    sentiment_numeric[i]=[TextBlob(text.loc[j,i]).sentiment.polarity for j in text.index]
    sentiment_class[i]=['positive' if TextBlob(text.loc[j,i]).sentiment.polarity>0 else 'neutral' if TextBlob(text.loc[j,i]).sentiment.polarity==0  else 'negative' for j in text.index]
    objectivity_class[i]=['objective' if TextBlob(text.loc[j,i]).sentiment.subjectivity<0.5 else 'subjective' for j in text.index]

# Now i started to make descriptive analysis of the results
# First i counted the labels then to plot I melted the dataframe of counts	
sent=[]
for i in sentiment_class.columns:
    sent.append(sentiment_class[i].value_counts())

sent=pd.concat(sent,axis=1).reset_index()
sent=pd.melt(sent,id_vars='index')    
sent.columns=['Sentiments','Broadcaster Corporations','Counts']

# First plotting is labels of the sentiments' counts
sns.set_style('whitegrid')
sns.set_palette('Spectral')
sns.barplot(x='Broadcaster Corporations',y='Counts',hue='Sentiments',data=sent)
plt.title("Broadcaster Corporations' Last 3000 Tweets with Labelled Emotions")

# Same process of objectivity classes is made here
obj=[]
for i in objectivity_class.columns:
    obj.append(objectivity_class[i].value_counts())

obj=pd.concat(obj,axis=1).reset_index()
obj=pd.melt(obj,id_vars='index')
obj.columns=['Objectivity','Broadcaster Corporations','Counts']

sns.set_style('whitegrid')
sns.set_palette('rainbow')
sns.barplot(x='Broadcaster Corporations',y='Counts',hue='Objectivity',data=obj)
plt.title("Broadcaster Corporations' Last 3000 Tweets with Labelled Objectivity")

# Describing positive and negative tweets' means
sns.set_style('whitegrid')
sns.set_palette('Spectral')

sentiment_numeric.columns=['Al Jazeera','Trt World','CNN', 'Deutsche Welle','Fox News', 'France 24', 'NHK Japan', 'RT Russia', 'CGTN China','BBC']
pos=pd.melt(sentiment_numeric)
pos=pos[pos['value']>0]
pos=pos.groupby('variable')['value'].mean().reset_index()
pos.columns=['Broadcaster Corporations','Average Score of Sentiment']
neg=pd.melt(sentiment_numeric)
neg=neg[neg['value']<0]
neg=neg.groupby('variable')['value'].mean().reset_index()
neg.columns=['Broadcaster Corporations','Average Score of Sentiment']

pos['Average Score of Sentiment'], neg['Average Score of Sentiment'] = pos['Average Score of Sentiment']*100 ,neg['Average Score of Sentiment']*100
pos=pos.sort_values(by='Average Score of Sentiment',ascending=False)


plt.title('Positive and Negative Tweets Score Averages out of 100')
sns.barplot(x='Broadcaster Corporations',y='Average Score of Sentiment',data=pos,color='Yellow')
sns.barplot(x='Broadcaster Corporations',y='Average Score of Sentiment',data=neg,color='DarkGrey')
plt.axhline(y=0, color='k')
plt.legend()
plt.show()




