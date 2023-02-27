from datetime import timedelta, datetime, date, time
from decouple import config
import sqlite3
import main
import asyncio


slovoform = {
    "завтра": str((datetime.now() + timedelta(days=1)).strftime('%d.%m.%Y 7:00')),
    "послезавтра" : str((datetime.now() + timedelta(days=2)).strftime('%d.%m.%Y 7:00')),
    "через неделю" : str((datetime.now() + timedelta(days=7)).strftime('%d.%m.%Y 7:00'))
}

def learn_notify(notify_msg): #функция получает строку из сообщения, и вычленяет дату и время
    when = str(notify_msg[1])
    if "др" in when:   
        return(datetime.strptime(str(when.split(" ")[1]+".2023"), "%d.%m.%Y").strftime('%d.%m 7:00'))
    if "ежедневно" in when:
        return when.split("в ")[1]
    for i,j in slovoform.items():
            if when in i: 
                return j
    if len(str(when)) <=10:
        return datetime.strptime(when, "%d.%m.%Y").strftime('%d.%m.%Y 7:00')
    else:
        return (datetime.strptime(when, "%d.%m.%Y %H:%M").strftime('%d.%m.%Y %H:%M'))

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
    conn = sqlite3.connect(main.name_db)
    cur = conn.cursor()
    cur.execute(f'SELECT * FROM notify WHERE (whens="{now_datetime}" or whens="{now_shortdatetime}" or whens="{now_time}") and statuses!=1;')
    one_result = cur.fetchall()
    cur.close()
    if one_result!=[]:
        for j in one_result:
            await main.send_notify(j)
            