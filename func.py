from datetime import timedelta, datetime, date, time


slovoform = {
    "завтра": str((datetime.now() + timedelta(days=1)).strftime('%d.%m.%Y')),
    "послезавтра" : str((datetime.now() + timedelta(days=2)).strftime('%d.%m.%Y')),
    "через" : "ввввввввввввввввв"
}

slovoform2 = {
    "день": str((datetime.now() + timedelta(days=1)).strftime('%d.%m.%Y')),
    "неделя" : str((datetime.now() + timedelta(days=2)).strftime('%d.%m.%Y')),
    "месяц" : "ввввввввввввввввв"
}

def learn_notify(notify_msg):
    what = notify_msg[0]
    when = str(notify_msg[1])
    if "через" in when:
        data = when.split()
        print(data)
        return 

    for i,j in slovoform.items():
            if when in i: 
                return j
    if len(str(when)) <=10:
        return datetime.strptime(when, "%d.%m.%Y").date().strftime('%d.%m.%Y')
    else:
        return (datetime.strptime(when, "%d.%m.%Y %H:%M").strftime('%d.%m.%Y %H:%M'))


text = ("""sdfsdfsd-20.03.2022 12:55
11ййййййй-завтра
4343453453-послезавтра
выаываыва-через 1 день
sdfsdfsd-20.02.2022""")

add_noty = [i.split("-") for i in text.split("\n")]
db=[]
for i in add_noty:
    print(str(learn_notify(i)))
    #db.append([datetime.now().strftime("%d.%m.%Y %H:%M"),i[0],,"",""])
#print(db)
