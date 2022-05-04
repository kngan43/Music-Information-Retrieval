import numpy as np
import pandas as pd
import gensim 
from gensim.models import Word2Vec
from urllib import request
import warnings
warnings.filterwarnings('ignore')

import os
path = os.path.dirname(os.path.abspath(__file__))
os.chdir(path)
#print(os.getcwd())


data = request.urlopen('https://storage.googleapis.com/maps-premium/dataset/yes_complete/train.txt')
lines = data.read().decode("utf-8").split('\n')[2:] 

playlists = [s.rstrip().split() for s in lines if len(s.split()) > 1]
model = Word2Vec(playlists, vector_size=32, window=20, negative=50, min_count=1, workers=4)

songs_file = request.urlopen('https://storage.googleapis.com/maps-premium/dataset/yes_complete/song_hash.txt')
songs_file = songs_file.read().decode("utf-8").split('\n')
songs = [s.rstrip().split('\t') for s in songs_file]

songs_df = pd.DataFrame(data=songs, columns = ['id', 'title', 'artist'])

songs_df.drop(songs_df.tail(1).index,inplace=True)



tags = []
with open('dataset/yes_complete/tags.txt', 'r') as f:
    for line in f.readlines():
        tags.append(line.rstrip())


tags_df = pd.DataFrame(data=tags, columns = ['tags'])
songs_df['tags'] = tags_df

songs_df = songs_df.set_index('id')

#song_id = 135 
#query_song = songs_df.iloc[song_id]

def print_recommendations(song_id):

    similar_songs = np.array(model.wv.most_similar(positive=str(song_id)))[:,0]
    return  songs_df.iloc[similar_songs] 

queries = []
query_song_list = []
for i in range(100):
    rec = print_recommendations(i+1)
    rec_flat = rec.values.tolist() # [['-', '-', '#'], ['Turnaround', 'Michael Treni', '#']]
    queries.append(rec_flat)
    query_song_list.append(i+1)

#query_flat = query_song.values.tolist() # ex. ['Curry Tabanca', 'Mighty Trini', '#']
#print(query_flat)


def add_score(q_song, hits):
    #print('q_song',q_song)
    #print('hits', hits)
    arist = q_song[1]
    tags = q_song[2]
    tags = set(tags)

    for i in range(len(hits)):
        h_title, h_artist, h_tags = hits[i]
        scored = False
        if arist in h_artist:
            scored = True
            hits[i].append(1)
            continue

        for t in h_tags.split():
            if t in tags:
                scored = True
                hits[i].append(1)
                break
            
        if scored:
            continue
        else:
            hits[i].append(0)

    return hits

for i in range(len(queries)):
    song_id = query_song_list[i]
    query_song = songs_df.iloc[song_id]
    query_flat = query_song.values.tolist()
    queries[i] = add_score(query_flat, queries[i])

#print(queries)

average_ap = []
for query in queries:
  pr = []
  total_correct = 0
  for i in range(len(query)):
    index = i + 1
    h_title, h_artist, h_tags, h_score = query[i]
      
    if h_score >= 1:
      total_correct += 1
      pr.append(total_correct/index)
    else: 
      pr.append(0)
      
  ap = 0
  if total_correct > 0:
    ap = (1/total_correct) * sum(pr)
    
  average_ap.append(ap)

map = sum(average_ap)/len(average_ap)
print(map)