# -*- coding: utf8 -*-

from random import randint
from time import sleep
import dataset
import requests
import config
import csv
import lib
import re
import sys
import os
import codecs
from bs4 import BeautifulSoup
from datetime import date, timedelta as td

if config.CRAWLERA_USER != "":
    CRAWLERA_USER = config.CRAWLERA_USER
    CRAWLERA_PASS = config.CRAWLERA_PASS
    proxies = {
            "http": "http://" + CRAWLERA_USER + ":" + CRAWLERA_PASS + "@proxy.crawlera.com:8010/",
    }
    crawlera = True

USER_AGENTS = [
	"Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; Crazy Browser 1.0.5)",
	"curl/7.7.2 (powerpc-apple-darwin6.0) libcurl 7.7.2 (OpenSSL 0.9.6b)",
	"Mozilla/5.0 (X11; U; Linux amd64; en-US; rv:5.0) Gecko/20110619 Firefox/5.0",
	"Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b8pre) Gecko/20101213 Firefox/4.0b8pre",
	"Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)",
	"Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 7.1; Trident/5.0)",
	"Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0) chromeframe/10.0.648.205",
	"Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; InfoPath.2; SLCC1; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET CLR 2.0.50727)",
	"Opera/9.80 (Windows NT 6.1; U; sv) Presto/2.7.62 Version/11.01",
	"Opera/9.80 (Windows NT 6.1; U; pl) Presto/2.7.62 Version/11.00",
	"Opera/9.80 (X11; Linux i686; U; pl) Presto/2.6.30 Version/10.61",
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/15.0.861.0 Safari/535.2",
	"Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/15.0.872.0 Safari/535.2",
	"Mozilla/5.0 (Windows NT 6.1) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.812.0 Safari/535.1",
	]


def html_to_csv(html):
    # taken from http://stackoverflow.com/a/14167916
    soup = BeautifulSoup(html)
    table = soup.find('table', attrs={'class': 'items'})
    headers = [header.text for header in table.find_all('th')]

    rows = []
    for row in table.find_all('tr'):
        rows.append([val.text for val in row.find_all('td')])

    filename = os.path.join(config.base_folder, "output.csv")
    f = codecs.open(filename, "a", "utf8")
    for i in rows:
        if len(i) > 1:
            out  = i[0] + "," + i[1] + "," + i[2] + "," + i[3] + ","
            out += i[4] + "," + i[5] + "," + i[6] + "," + i[7] + ","
            out += i[8] + "," + i[9] + "\n"
            f.write(out)
        else:
            print i
    f.close()

    #with codecs.open("output.csv", "a", "utf8") as f:
        #writer = csv.writer(f)
        #writer.writerow(headers)
        #writer.writerows(row for row in rows if row)

def get_number_of_page_results(html):
    soup = BeautifulSoup(html)
    res = soup.find_all(href=re.compile("lstVisitasResult_page=([0-9]+)"))
    pages = []
    for i in res:
        page = re.search("_page=([0-9]+)", str(i)).groups()[0]
        pages.append(int(page))
    pages = set(pages)
    print pages
    if len(pages) > 0:
        pages = sorted(pages)[-1]
    else:
        pages = False
    return pages


def buscar(fecha):
    sleep(randint(1,5))

    url = "http://geo.vivienda.gob.pe/Visitas/controlVisitas/index.php"
    url += "?r=consultas/visitaConsulta/index"

    payload = {
            "VisitaConsultaQueryForm[feConsulta]": fecha
            }
    headers = { "User-Agent": USER_AGENTS[randint(0, len(USER_AGENTS))-1]}

    if config.CRAWLERA_USER != "":
        r = requests.post(url, data=payload, headers=headers, proxies=proxies)
    else:
        r = requests.post(url, data=payload, headers=headers)
    r.encoding = "utf8"
    csv = html_to_csv(r.text)
    print url

    number_of_pages = get_number_of_page_results(r.text)

    if number_of_pages != False:
        for i in range(2, int(number_of_pages)+1):
            url = "http://geo.vivienda.gob.pe/Visitas/controlVisitas/index.php"
            url += "?r=consultas/visitaConsulta/index"
            url += "&lstVisitasResult_page="
            url += str(i)
            print url
            try:
                sleep(randint(1,5))
                if crawlera:
                    r = requests.post(url, data=payload, headers=headers, proxies=proxies)
                else:
                    r = requests.post(url, data=payload, headers=headers)
                r.encoding = "utf8"
                csv = html_to_csv(r.text)
            except:
                pass

def last_date_in_db():
    import lib
    lib.create_database()
    filename = os.path.join(config.base_folder, "visitas.db")
    db = dataset.connect("sqlite:///" + filename)
    res = db.query("select date from visitas")

    dates = []
    for i in res:
        i = i['date'].split("/")
        dates.append(date(int(i[2]), int(i[1]), int(i[0])))
    dates.sort()
    if dates:
        return dates[-1]
    else:
        return False




# clean our outfile
try:
    filename = os.path.join(config.base_folder, "output.csv")
    os.remove(filename)
except OSError:
    pass

# Use this format for dates
# fecha = "DD/MM/YYYY"

# Days between two dates
# taken from http://stackoverflow.com/a/7274316
#d1 = date(2012,12,1)
#d2 = date(2014,3,7)
if last_date_in_db():
    d1 = last_date_in_db() - td(days=3)
else:
    d1 = date(2011,7,28)

d2 = d1 + td(days=8)
delta = d2 - d1

#d1 = date(2014,3,26)
#d2 = date(2014,3,27)
#delta = d2 - d1
for i in range(delta.days + 1):
    my_date = d1 + td(days=i)
    fecha = my_date.strftime("%d/%m/%Y")
    print fecha

    buscar(fecha)


# upload data from our csv file
items = lib.get_data()
filename = os.path.join(config.base_folder, "visitas.db")
db = dataset.connect("sqlite:///" + filename)
table = db['visitas']

for i in items:
    if not table.find_one(sha1=i['sha1']):
        print i['sha1'], i['date']
        table.insert(i)

lib.recreate_website()
