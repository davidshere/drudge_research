import datetime

import sqs_utils
import drudge_data_classes

if __name__ == "__main__":

  start = datetime.datetime.now().date() - datetime.timedelta(days=30)

  day_pages = [
    drudge_data_classes.DayPage(start + datetime.timedelta(x))
    for x in range(20)
  ]
  
  to_enqueue = [day_page.to_json() for day_page in day_pages]
  print(to_enqueue)
  sqs_utils.post_to_queue(to_enqueue, sqs_utils.fetch_queue)
    
