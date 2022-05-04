import pandas as pd
from termcolor import colored

# read result csv
df = pd.read_csv('result_recorded_song.csv', encoding= 'unicode_escape')
# df = pd.read_csv('result.csv')

query_number = len(df.columns) - 1
song_number = len(df)
total_query_amout = song_number * query_number

# how many query sucessful match the answer?
result_column = df.columns[1:]
correct = df[result_column].sum().sum()
accuracy = correct / total_query_amout
print(correct)

print('There are ' + str(song_number) + ' songs in total')
print('Each song will have ' + str(query_number) + ' random querys')
print('The music recognizer have an accuracy of ',accuracy * 100,'%',' in all querys')

# How many song's queries are fully recognized?
full_recognized_song_count = 0
full_recognized_song_name = []
for i,row in df.iterrows():
    if sum(row[1:]) == query_number:
        full_recognized_song_count += 1
        full_recognized_song_name.append(row[0])
print('The proportion of song that being fully recogized: ',full_recognized_song_count/song_number * 100,' %')

# How many song's queries are fully recognized?
not_recognized_song_count = 0
not_recognized_song_name = []
for i,row in df.iterrows():
    if sum(row[1:]) == 0:
        not_recognized_song_count += 1
        not_recognized_song_name.append(row[0])
print('The proportion of song that non of the query is recogized: ',not_recognized_song_count/song_number * 100,' %')



