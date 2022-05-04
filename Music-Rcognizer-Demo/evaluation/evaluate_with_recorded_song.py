from pydub import AudioSegment
from pydub.utils import make_chunks
import os
import random
import Listen
import numpy as np
from tqdm import tqdm
from tqdm import tqdm
from io import StringIO,BytesIO
import pandas as pd
MUSICS_FOLDER_PATH = 'recorded_song/'
QUERY_FOLDER = 'querys/'
SAMPLE_SONGS = 14
# pydub use miliseconds
TEN_SECONDS = 10 * 1000
QUERY_SAMPLE_EACH_SONG = 5

def evaluate_with_recorded_song():
    '''
    apply recognizer on the recorded song's clip
    :return acurracy

    '''

    # performence logger
    logger = []
    song_list = os.listdir('recorded_song')
    song_not_in_database = [i for i in song_list if 'NOTINLIST' in i]
    song_in_database = [i for i in song_list if 'NOTINLIST' not in i]
    # go over all song from our folder
    random_songs_list = random.sample(song_not_in_database,SAMPLE_SONGS) + random.sample(song_in_database,SAMPLE_SONGS)
    print('The following song list will be evaluated')
    print(random_songs_list)

    for song_name in tqdm(random_songs_list):
        if song_name.endswith('.mp3'):
            # read mp3 file and make chunks to ten seconds each
            print('processing ', song_name)
            log = {'Song Name': song_name}
            song_name_without_extension = song_name.split('.')[0]

            song = AudioSegment.from_file(MUSICS_FOLDER_PATH + song_name)
            song = np.fromstring(song._data, np.int16)

            # get one channel for matching
            song = song[::2]

            # sample query start after 20 secon, before 90% length of the song
            sample_start_range_from = 200000
            sample_start_range_to = int(len(song) * 0.85)

            for i in range(QUERY_SAMPLE_EACH_SONG):

                #  random 10 sec clip
                query_start_point = np.random.randint(sample_start_range_from, sample_start_range_to)
                song_clip = song[query_start_point:query_start_point + 100000]

                # matching
                matched_song_name = Listen.match_song([song_clip.tolist()], mode='eval')

                if matched_song_name == song_name:
                    print('Succesfully matched!!!')
                    log['Query_' + str(i)] = 1
                else:
                    log['Query_' + str(i)] = 0
            logger.append(log)
    df = pd.DataFrame.from_dict(logger, orient='columns')
    print(df)

    df.to_csv('result_recorded_song.csv', index=False)
    print('finish!!')

if __name__ == '__main__':
    evaluate_with_recorded_song()
