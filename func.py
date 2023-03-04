from datetime import timedelta, datetime, date, time
from decouple import config
import sqlite3
import main
import asyncio


slovoform = {
    "завтра": str((datetime.now() + timedelta(days=1)).strftime('%d.%m.%Y 07:00')),
    "послезавтра" : str((datetime.now() + timedelta(days=2)).strftime('%d.%m.%Y 07:00')),
    "через неделю" : str((datetime.now() + timedelta(days=7)).strftime('%d.%m.%Y 07:00'))
}

weeks = {
    "пн" : datetime.strptime(str("02.01.2023 7:00 Monday"), "%d.%m.%Y %H:%M %A").strftime('%H:%M %A'),
    "вт" : datetime.strptime(str("03.01.2023 7:00 Tuesday"), "%d.%m.%Y %H:%M %A").strftime('%H:%M %A'),
    "ср" : datetime.strptime(str("04.01.2023 7:00 Wednesday"), "%d.%m.%Y %H:%M %A").strftime('%H:%M %A'),
    "чт" : datetime.strptime(str("05.01.2023 7:00 Thursday"), "%d.%m.%Y %H:%M %A").strftime('%H:%M %A'), 
    "пт" : datetime.strptime(str("06.01.2023 7:00 Friday"), "%d.%m.%Y %H:%M %A").strftime('%H:%M %A'),
    "сб" : datetime.strptime(str("07.01.2023 7:00 Saturday"), "%d.%m.%Y %H:%M %A").strftime('%H:%M %A'),
    "вс" : datetime.strptime(str("08.01.2023 7:00 Sunday"), "%d.%m.%Y %H:%M %A").strftime('%H:%M %A')
}

weeks2 = {
    "пн" : "Monday",
    "вт" : "Tuesday",
    "ср" : "Wednesday",
    "чт" : "Thursday",
    "пт" : "Friday",
    "сб" : "Saturday",
    "вс" : "Sunday"
}

def learn_notify(notify_msg): #функция получает строку из сообщения, и вычленяет дату и время
    when = str(notify_msg[1])
    if "каждый" in when or "каждую" in when or "каждое" in when:
        for i,j in weeks.items():
            if when.split(" ")[1] in i: 
                return j, "1"
    if " в " in when and when.split(" ")[0] in weeks2.keys():
        for i,j in weeks2.items():
            if when.split(" ")[0] in i:
                return str(datetime.strptime(str("01.01.2023 "+when.split(" ")[2]), "%d.%m.%Y %H:%M").strftime('%H:%M ')+j), "0"
    if when in weeks.keys():
        for i,j in weeks.items():
            if when in i: 
                return j, "0"
    if "в" in when and "ежедневно" not in when:
        return (datetime.strptime(str("01.01.2023 "+when.split(" ")[1]), "%d.%m.%Y %H:%M").strftime('%H:%M')), "0"
    if "др" in when:   
        return(datetime.strptime(str(when.split(" ")[1]+".2023"), "%d.%m.%Y").strftime('%d.%m 07:00')), 0
    if "ежедневно" in when:
        return (datetime.strptime(str("01.01.2023 "+when.split("в ")[1]), "%d.%m.%Y %H:%M").strftime('%H:%M')), "1"
    if when in slovoform.keys():
        for i,j in slovoform.items():
            if when in i: 
                return j, "0"
    if len(str(when)) <=10:
        return datetime.strptime(when, "%d.%m.%Y").strftime('%d.%m.%Y 07:00'), "0"
    else:
        return (datetime.strptime(when, "%d.%m.%Y %H:%M").strftime('%d.%m.%Y %H:%M')), "0"

def query_for_db(query): #укороченая отправка запросов к бд
    conn = sqlite3.connect(main.name_db)
    cur = conn.cursor()
    cur.execute(query)
    conn.commit()
    cur.close()

async def check_notify(): #функция для ежеминутной проверки бд на события о которых пора сообщить
    now_datetime = datetime.now().strftime("%d.%m.%Y %H:%M")
    now_shortdatetime = datetime.now().strftime("%d.%m %H:%M")
    now_time = datetime.now().strftime("%H:%M")
    day_week = datetime.now().strftime("%H:%M %A")
    conn = sqlite3.connect(main.name_db)
    cur = conn.cursor()
    cur.execute(f'SELECT * FROM notify WHERE (whens="{now_datetime}" or whens="{now_shortdatetime}" or whens="{now_time}" or whens="{day_week}") and statuses!=1;')
    one_result = cur.fetchall()
    cur.close()
    if one_result!=[]:
        for j in one_result:
            await main.send_notify(j)

