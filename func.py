import datetime
from datetime import timedelta
slovoform = {
    "завтра": datetime.datetime.now() + timedelta(days=1)
}



def learn_notify(notify_msg):
    what = notify_msg[0]
    when = str(notify_msg[1])
    print(datetime.datetime.now() + timedelta(days=1).strftime("%Y.%d.%m %H:%M"))
    print(datetime.datetime.strptime(when, "%Y.%d.%m %H:%M"))
    

