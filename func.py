import datetime
from datetime import timedelta


slovoform = {
    "завтра": "="+str((datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%d.%m.%Y')),
    "послезавтра" : "="+str((datetime.datetime.now() + datetime.timedelta(days=2)).strftime('%d.%m.%Y'))
}

def check_in_date(when): #функция проверки есть ли эта дата в словаре
    
    return False



def learn_notify(notify_msg):
    what = notify_msg[0]
    when = str(notify_msg[1])
    date = check_in_date(when)
    for i,j in slovoform.items():
            if when in i: 
                return j
    if "=" in date:
        return (date[1:])
    elif len(str(date)) <=10 and date!="f":
        return datetime.datetime.strptime(when, "%d.%m.%Y")
    elif date=="f":
        return (datetime.datetime.strptime(when, "%d.%m.%Y %H:%M"))
    


