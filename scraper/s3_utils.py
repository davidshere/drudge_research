import io

import boto3

BUCKET_NAME = 'drudge-archive'

def bytes_to_s3(io_buffer, s3_path):
  # we want to start writing from the beginning of the object
  io_buffer.seek(0)

  s3 = boto3.resource('s3')
  success = s3.Object(BUCKET_NAME, s3_path).put(Body=io_buffer)
  if success:
    return True

if __name__ == "__main__":

  text = b'this is some text in bytes'
  buff = io.BytesIO(text)
  bytes_to_s3(buff, 'test/path/text.bytes')
