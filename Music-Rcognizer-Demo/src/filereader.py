import os
from pydub import AudioSegment
from pydub.utils import audioop
import numpy as np
from hashlib import sha1

class FileReader():
  def __init__(self, filename):
    self.filename = filename

  def parse_audio(self):
    songname, extension = os.path.splitext(os.path.basename(self.filename))
    try:
      # 读取音频文件
      audiofile = AudioSegment.from_file(self.filename)

      data = np.fromstring(audiofile._data, np.int16)

      channels = []
      # 将左右声道存入list中
      for chn in range(audiofile.channels):
        channels.append(data[chn::audiofile.channels])

    except audioop.error:
      print('audioop.error')
      pass

    return {
      "songname": songname,
      "extension": extension,
      "channels": channels,
      "Fs": audiofile.frame_rate,
      "file_hash": self.parse_file_hash()
    }

  def parse_file_hash(self, blocksize=2**20):
    s = sha1()
    # 加密算法，让一个文件拥有unique hash
    # update method is for reading big file by block, which will yield the same hash by directly hash the whole file
    with open(self.filename , "rb") as f:
      while True:
        buf = f.read(blocksize)
        if not buf:
          break
        s.update(buf)
    # 返回哈希值
    return s.hexdigest().upper()
