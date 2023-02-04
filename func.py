import datetime

def learn_notify(notify_msg):
    what = notify_msg[0]
    when = notify_msg[1]
    dt=datetime.datetime.now()
    dt.strptime(when, "%d.%m.%Y %H:%M")
    print(what)
    print(when)