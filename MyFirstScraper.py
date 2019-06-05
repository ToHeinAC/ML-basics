import time, datetime
import random
from requests import get
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3 as lite


def scrape_write(site_url,number_of_points,write_dbname, fillDB=True):
    i = 0
    while i < number_of_points:
        t0 = time.time()
        n = datetime.datetime.now()
        now = n.strftime('%d.%m.%Y %H:%M:%S')
        response = get(url)
        html_soup = BeautifulSoup(response.text, 'html.parser')
        #type(html_soup)
        dax30_containers = html_soup.find_all('div', class_='Tllc Tbd')
        target = dax30_containers[1]
        firma = []
        isin = []
        kurs = []
        for item in target.tbody.find_all('td', class_='Tleft'):
            if item.find('b') is not None:
                firma.append(item.b.a.text)

        for item in target.tbody.find_all('td'):
            if item.find('a') is not None:
                isin.append(item.a.text)
            if item.find('b') is not None:
                kurs.append(item.b.text)

        kurs_n = [x[:-2].replace(',', '.') for x in kurs if x not in firma]
        isin_n = [x for x in isin if x not in firma]

        if fillDB:
            sheet = 'Daten'
            print ("Filling DB... ")
            conn = lite.connect(db_name)
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
            DB_status = cur.fetchall()

            if (i == 0 and DB_status == []):
                test_df = pd.DataFrame([isin_n, kurs_n], columns=firma)
                test_df['01_Zeitstempel'] = [now, now]
                # print(test_df)

                cur.execute('DROP TABLE IF EXISTS ' + sheet)
                test_df.to_sql(sheet, conn, if_exists='append', index=False)  # - writes the pd.df to SQLIte DB

                conn.commit()
            else:
                stuff = pd.DataFrame([kurs_n], columns=firma)
                stuff['01_Zeitstempel'] = now
                stuff.to_sql(sheet, conn, if_exists='append', index=False)  # - writes the pd.df to SQLIte DB

                # cur.execute("ALTER TABLE "+sheet+" ADD COLUMN '"+now+"'")
                # for l in range(len(stuff[now].values)):
                #    cur.execute("INSERT INTO "+sheet+" ('"+now+"') VALUES ({})".format(stuff[now].values[l]))

                conn.commit()

        conn.close()

        time.sleep(random.randint(6, 10))
        i += 1

if __name__ == '__main__':
    number_of_points = 3
    url = 'https://www.t-online.de/finanzen/boerse/indizes/id_51947152/isin_DE0008469008/indizes.html'
    db_name = 'Aktienkurse_DB.db'
    print('Scraping ...')
    scrape_write(url, number_of_points, db_name, fillDB=True)
    print('Done!')

