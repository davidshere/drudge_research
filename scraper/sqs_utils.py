import json

import boto3

sqs = boto3.resource('sqs')

FETCH_QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/402878705062/drudge-fetch-queue'
PARSE_QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/402878705062/drudge-parse-queue'
fetch_queue = sqs.Queue(FETCH_QUEUE_URL)
parse_queue = sqs.Queue(PARSE_QUEUE_URL)

def post_to_queue(message, queue):
  if not isinstance(message, str):
    message = json.dumps(message, default=str)
  
  result = queue.send_message(
    MessageBody=message
  )
  return result

def fetch_from_queue(queue):
  result = queue.receive_messages()
  return result

if __name__ == "__main__":
  msg = fetch_from_queue(fetch_queue)[0]
  print(msg.body)
