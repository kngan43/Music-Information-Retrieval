from pydub import AudioSegment
from pydub.utils import make_chunks
import os
import random
import Listen
import numpy as np
from tqdm import tqdm
from io import StringIO,BytesIO
import pandas as pd
MUSICS_FOLDER_PATH = '../mp3/'
QUERY_FOLDER = 'querys/'
SAMPLE_SONGS = 10
# pydub use miliseconds
TEN_SECONDS = 10 * 1000
QUERY_SAMPLE_EACH_SONG = 3

def evaluate_with_original_song():
    '''
    apply recognizer on the original song's clip
    :return acurracy
    '''
    # performence logger
    logger = []

    # go over all song from our folder
    for song_name in tqdm(os.listdir('../mp3')):
        if song_name.endswith('.mp3'):
            # read mp3 file and make chunks to ten seconds each
            print('processing ', song_name)
            log = {'Song Name': song_name}
            song_name_without_extension = song_name.split('.')[0]

            song = AudioSegment.from_file(MUSICS_FOLDER_PATH + song_name)
            song = np.fromstring(song._data, np.int16)

            # get one channel for matching
            song = song[::2]

            # sample query start after 1 secon, before 90% length of the song
            sample_start_range_from = 10000
            sample_start_range_to = int(len(song) * 0.9)

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

    df.to_csv('result.csv', index=False)
    print('finish!!')




if __name__ == '__main__':
    evaluate_with_original_song()
    # # performence logger
    # logger = []
    #
    # # random sample songs
    # random_songs_list = random.sample(os.listdir('../../mp3'),SAMPLE_SONGS)
    # for song_name in random_songs_list:
    #     if song_name.endswith('.mp3'):
    #         # read mp3 file and make chunks to ten seconds each
    #         print('processing ',song_name)
    #         log = {'Song Name':song_name}
    #         song_name_without_extension = song_name.split('.')[0]
    #
    #         song = AudioSegment.from_mp3(MUSICS_FOLDER_PATH + song_name)
    #         song = np.fromstring(song._data, np.int16)
    #
    #         # get one channel for matching
    #         song = song[::2]
    #
    #         # sample query start after 1 secon, before 90% length of the song
    #         sample_start_range_from = 10000
    #         sample_start_range_to = int(len(song) * 0.9)
    #
    #         for i in range(QUERY_SAMPLE_EACH_SONG):
    #
    #             #  random 10 sec clip
    #             query_start_point = np.random.randint(sample_start_range_from,sample_start_range_to)
    #             song_clip = song[query_start_point:query_start_point + 100000]
    #
    #             # matching
    #             matched_song_name = listen.match_song([song_clip.tolist()],mode='eval')
    #
    #             if matched_song_name == song_name:
    #                 print('Succesfully matched!!!')
    #                 log['Query' + str(i)] = 1
    #             else:
    #                 log['Query' + str(i)] = 0
    #         logger.append(log)
    # df = pd.DataFrame.from_dict(logger, orient='columns')
    # print(df)
    #
    # df.to_csv('result.csv',index=False)
    # print('finish!!')

            # ch.export(file_name, format='mp3')
        # chunks = make_chunks(song, TEN_SECONDS)
        # print('processing {}, which have {} chunks'.format(song_name,len(chunks)))
        #
        # for i, ch in enumerate(chunks):
        #     # leave the 1st and last chunk out
        #     if i == 0 or i == (len(chunks) - 1):
        #         continue
        #     song_name_without_extension = song_name.split('.')[0]
        #     #export file
        #     file_name = './querys/query_chunks/' + song_name_without_extension + '_' + str(i) + '.mp3'
        #     ch.export(file_name, format='mp3')
        # break

    # first_10_seconds = song[:10000]
    # first_10_seconds.export(QUERY_FOLDER + "test.mp3", format="mp3")

    # make_chunks