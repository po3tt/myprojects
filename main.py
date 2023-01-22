#подключение моих библиотек
from settings import *
#подключение библиотек

#конец библиотек

connect = sqlite3.connect('noty.db')
current = connect.cursor()
current.execute("""CREATE TABLE IF NOT EXISTS notify(data DATE, what TEXT, when DATE, status TEXT, status TEXT);""")
connect.commit()
current.close()


