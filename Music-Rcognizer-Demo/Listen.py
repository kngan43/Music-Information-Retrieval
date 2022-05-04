import src.analyzer as analyzer
from itertools import zip_longest
from termcolor import colored
from src.listener import Listener
from src.db import SQLiteDatabase

# found hashes have to be more than this to be return
HASH_COUNT_THRESHOLD = 15

db = SQLiteDatabase()

# return false if we have very low confident for the retrieved song
def results_filter(largest_count):
  return True if largest_count > HASH_COUNT_THRESHOLD else False

def find_matches(samples, Fs=analyzer.DEFAULT_FS):
  hashes = analyzer.fingerprint(samples, Fs=Fs)
  return return_matches(hashes)


def return_matches(hashes):
  mapper = {}
  for hash, offset in hashes:
    mapper[hash.upper()] = offset
  values = mapper.keys()

  for split_values in grouper(values, 1000):
    query = """
      SELECT upper(hash), song_fk, offset
      FROM fingerprints
      WHERE upper(hash) IN (%s)
    """
    vals = list(split_values).copy()
    length = len(vals)
    query = query % ', '.join('?' * length)
    x = db.executeAll(query, values=vals)
    matches_found = len(x)
    if matches_found > 0:
      msg = 'I found %d hash in db'
      print(colored(msg, 'green') % (matches_found))

    for hash, sid, offset in x:
      yield (sid, mapper[hash])

def grouper(values, n, fillvalue=None):
  args = [iter(values)] * n
  return (filter(None, values) for values in zip_longest(fillvalue=fillvalue, *args))

def align_matches(matches):
  diff_counter = {}
  largest = 0
  largest_count = 0
  song_id = -1
  filtered = True

  for tup in matches:
    sid, diff = tup

    if diff not in diff_counter:
      diff_counter[diff] = {}

    if sid not in diff_counter[diff]:
      diff_counter[diff][sid] = 0

    diff_counter[diff][sid] += 1

    if diff_counter[diff][sid] > largest_count:
      largest = diff
      largest_count = diff_counter[diff][sid]
      song_id = sid
  print(diff_counter)
  print("largest_count",largest_count)
  songM = db.get_song_by_id(song_id)

  # the matching hashes have to surpass the thereshold
  if not results_filter(largest_count):
    print("No exact result are found since there are really few matches.")
    print("The one with most hashes are ",songM[1])
    filtered = False

  nseconds = round(float(largest) / analyzer.DEFAULT_FS *
                   analyzer.DEFAULT_WINDOW_SIZE *
                   analyzer.DEFAULT_OVERLAP_RATIO, 5)

  return {
    "FILTERED_ANSWER":filtered,
    "SONG_ID": song_id,
    "SONG_NAME": songM[1],
    "CONFIDENCE": largest_count,
    "OFFSET": int(largest),
    "OFFSET_SECS": nseconds
  }

def match_song(data = None,mode = 'listen'):
  seconds = int(10)
  chunksize = 2 ** 12
  channels = 1

  if mode == 'listen':
    print(colored("Default listen will be 10 seconds !", "yellow"))

    # start recording
    listener = Listener()
    listener.start_recording(seconds=seconds,
                             chunksize=chunksize,
                             channels=channels)
    while True:
      bufferSize = int(listener.rate / listener.chunksize * seconds)
      print(colored("Listening....", "green"))

      for i in range(0, bufferSize):
        listener.process_recording()
      break
    listener.stop_recording()
    print(colored('That\'s enough!! Stop listening~', "green"))
    # Recorded data
    data = listener.get_recorded_data()
    print(colored('%d samples in total', attrs=['dark']) % len(data[0]))

  matches = []
  for channeln, channel in enumerate(data):
    matches.extend(find_matches(channel))

  total_matches_found = len(matches)

  if total_matches_found > 0:

    msg = 'Totally found %d hash'
    print(colored(msg, 'green') % total_matches_found)

    song = align_matches(matches)

    msg = ' => song: %s (id=%d)\n'
    msg += '    offset: %d (%d secs)\n'

    print(colored(msg, 'green') % (
      song['SONG_NAME'], song['SONG_ID'],
      song['OFFSET'], song['OFFSET_SECS']
    ))

    return song['SONG_NAME']
  else:
    msg = 'Not anything matching'
    print(colored(msg, 'red'))


if __name__ == '__main__':
  match_song()
