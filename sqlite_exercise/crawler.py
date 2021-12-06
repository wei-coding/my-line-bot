import requests
from bs4 import BeautifulSoup
import sqlite3
from opencc import OpenCC

r = requests.get('https://wiki.biligame.com/ys/%E6%AD%A6%E5%99%A8%E5%9B%BE%E9%89%B4')
cc = OpenCC('s2t')
conn = sqlite3.connect('weapon.db')
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS `weapons` (
    `name` TEXT NOT NULL PRIMARY KEY,
    `type` TEXT,
    `stars` INT
)
""")
conn.commit()

if r.status_code == 200:
    soup = BeautifulSoup(r.text, 'html.parser')

    r = soup.select("#CardSelectTr > tbody > tr")

    for row in r[1:]:
        data = (cc.convert(row.find_all("td")[1].find('a').text.strip()), cc.convert(row.find_all("td")[2].text.strip()), int(row.find_all("td")[3].find('img').attrs['alt'].split("星")[0]))
        c.execute("INSERT INTO `weapons` VALUES (?, ?, ?)", data)

    conn.commit()
    c.close()
    conn.close()