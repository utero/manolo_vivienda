# -*- coding: utf8 -*-

import codecs
import hashlib
import json
import os
import re
import shutil

from bs4 import BeautifulSoup
import dataset

import config


def recreate_website():
    orig = config.base_folder
    dest = config.www_folder

    shutil.copy2(os.path.join(orig,"jumbotron-narrow.css"), os.path.join(dest,"jumbotron-narrow.css"))
    shutil.copy2(os.path.join(orig,"config.py"), os.path.join(dest,"config.py"))
    shutil.copy2(os.path.join(orig,"lib.py"), os.path.join(dest,"lib.py"))
    shutil.copy2(os.path.join(orig,"visitas.db"), os.path.join(dest,"visitas.db"))
    shutil.copy2(os.path.join(orig,"bootstrap.min.css"), os.path.join(dest,"bootstrap.min.css"))
    shutil.copy2(os.path.join(orig,"highlighter.js"), os.path.join(dest,"highlighter.js"))
    shutil.copy2(os.path.join(orig,"index.html"), os.path.join(dest,"index.html"))
    shutil.copy2(os.path.join(orig,"search.py"), os.path.join(dest,"search.py"))
    shutil.copy2(os.path.join(orig,"base.html"), os.path.join(dest,"base.html"))
    shutil.copy2(os.path.join(orig,"jquery-1.10.2.min.js"), os.path.join(dest,"jquery-1.10.2.min.js"))
    shutil.copy2(os.path.join(orig,"bootstrap.min.js"), os.path.join(dest,"bootstrap.min.js"))


def html_to_json(html):
    ###
    # taken from http://stackoverflow.com/a/14167916
    soup = BeautifulSoup(html)
    table = soup.find('table', attrs={'class': 'items'})
    headers = [header.text for header in table.find_all('th')]

    rows = []
    for row in table.find_all('tr'):
        rows.append([val.text for val in row.find_all('td')])
    ###

    filename = os.path.join(config.base_folder, "output.json")
    f = codecs.open(filename, "a", "utf8")
    for i in rows:
        if len(i) > 1:
            out = dict()
            out['date'] = i[0].strip()
            out['visitor'] = i[1].strip()
            out['id_document'] = i[2].strip()
            out['entity'] = i[3].strip()
            out['objective'] = i[4].strip()
            out['host'] = i[5].strip()
            out['office'] = i[6].strip()
            out['meeting_place'] = i[7].strip()
            out['time_start'] = i[8].strip()
            try:
                out['time_end'] = i[9].strip()
            except:
                out['time_end'] = ""

            f.write(json.dumps(out) + "\n")
    f.close()


def get_data():
    # get data from json file
    filename = os.path.join(config.base_folder, "visitas.db")
    db = dataset.connect("sqlite:///" + filename)
    table = db['visitas']
    
    filename = os.path.join(config.base_folder, "output.json")
    f = codecs.open(filename, "r", "utf8")
    data = f.readlines()
    f.close()
    
    items = []
    for line in data:
       line = line.strip()
       item = json.loads(line)
    
       if 'id_document' in item:
           id_doc_number = re.search("([0-9]+)", item['id_document'])
           if id_doc_number:
               id_doc_number = id_doc_number.groups()[0]
           else:
               id_doc_number = ""
       else:
           id_doc_number = ""

       string  = str(item['date']) + str(id_doc_number) + str(item['time_start'])
       m = hashlib.sha1()
       m.update(string)
       item['sha1'] = m.hexdigest()
    
       items.append(item)
    return items



def prettify(item):
    out = "<tr>"
    out += "<td><a href='search?q=" + item['date'] + "'>" + item['date'] + "</a></td>"
    out += "<td><a href='search?q=" + item['visitor'] + "'>" + item['visitor'] + "</a></td>"
    out += "<td><a href='search?q=" + item['id_document'] + "'>" + item['id_document'] + "</a></td>"
    out += "<td><a href='search?q=" + item['entity'] + "'>" + item['entity'] +"</a></td>"
    out += "<td><a href='search?q=" + item['objective'] + "'>" + item['objective'] + "</a></td>"
    out += "<td><a href='search?q=" + item['host'] + "'>" + item['host'] + "</a></td>"
    out += "<td><a href='search?q=" + item['office'] + "'>" + item['office'] +"</a></td>"
    out += "<td><a href='search?q=" + item['meeting_place'] + "'>" + item['meeting_place'] + "</a></td>"
    out += "<td>" + item['time_start'] + "</td>"
    out += "<td>" + item['time_end'] + "</td>"
    out += "</tr>\n"
    return out


def insert_to_db(line):
    filename = os.path.join(config.base_folder, "visitas.db")
    db = dataset.connect("sqlite:///" + filename)
    table = db['visitas']
    
    # line is a line of downloaded data
    i = line.split(",")
    item = dict()
    item['date'] = i[0]
    item['visitor'] = i[1]
    item['id_document'] = i[2]
    item['entity'] = i[3]
    item['objective'] = i[4]
    item['host'] = i[5]
    item['office'] = i[6]
    item['meeting_place'] = i[7]
    item['time_start'] = i[8]
    item['time_end'] = i[9]

    string = str(item['date']) + str(item['id_document']) + str(item['time_start'])
    m = hashlib.sha1()
    m.update(string)
    item['sha1'] = m.hexdigest()

    print "uploading %s" % str(item['date']) + "_" + str(item['time_start'])
    table.insert(item)

def create_database():
    import sqlalchemy

    print "Creating database"
    filename = os.path.join(config.base_folder, "visitas.db")
    if not os.path.isfile(filename):
        try:
            db = dataset.connect('sqlite:///' + filename)
            table = db.create_table("visitas")
            table.create_column('sha1', sqlalchemy.String)
            table.create_column('date', sqlalchemy.String)
            table.create_column('visitor', sqlalchemy.Text)
            table.create_column('id_document', sqlalchemy.String)
            table.create_column('entity', sqlalchemy.Text)
            table.create_column('objective', sqlalchemy.Text)
            table.create_column('host', sqlalchemy.Text)
            table.create_column('office', sqlalchemy.Text)
            table.create_column('meeting_place', sqlalchemy.Text)
            table.create_column('time_start', sqlalchemy.String)
            table.create_column('time_end', sqlalchemy.String)
        except:
            pass

def main():
    print ""

if __name__ == "__main__":
    main()
