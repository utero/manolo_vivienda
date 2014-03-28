#!/usr/bin/python
# -*- coding: utf8 -*-

from urllib import urlencode
import json
import cgi
import cgitb
import dataset
import lib
import sys
import re
import codecs
import string
import config
#cgitb.enable()

data = cgi.FieldStorage()


def sanitize(s):
    s = s.replace("'", "")
    s = s.replace("-", "")
    s = s.replace('"', "")
    s = s.replace("\\", "")
    s = s.replace(";", "")
    s = s.replace("=", "")
    s = s.replace("*", "")
    s = s.replace("%", "")

    if "/" in s:
        res = re.search("([0-9]{2,}/[0-9]{2,}/[0-9]{4,})", s)
        if res:
            s = res.groups()[0]
        else:
            s = ""
    return s

def sanitize_page(s):
    res = re.search("([0-9]+)", s)
    if res:
        s = res.groups()[0]
    else:
        s = ""
    return s

message = u"""<h2>Este es Manolo</h2>
            <b>Manolo es un buscador de las personas</b> que visitan las instalaciones del
            Organismo Supervisor de las Contrataciones del Estado.
            <br />
            Todos los datos son descargados diariamente de aquí: <b><a href="http://visitas.osce.gob.pe/controlVisitas/index.php?r=consultas/visitaConsulta/index">
            http://visitas.osce.gob.pe/controlVisitas/index.php?r=consultas/visitaConsulta/index</a></b>
            </p>
            <div class='well'>
            Puedes buscar por nombre o palabra clave. Por ejemplo tipea
            <b>ROMULO</b> y hacer click en "Buscar".
            </div>
            <p>
            También puedes hacer búsquedas haciendo click sobre cada uno de los resultados.
            </p>
            """

if 'q' in data:
    q = sanitize(data['q'].value)

    if q != "":
        db = dataset.connect("sqlite:///visitas.db")
        # We will limit to show only 20 results per page
        query = "SELECT * FROM visitas WHERE "
        query += " date like '%" + q + "%' OR"
        query += " visitor like '%" + q + "%' OR"
        query += " id_document like '%" + q + "%' OR"
        query += " entity like '%" + q + "%' OR"
        query += " objective like '%" + q + "%' OR"
        query += " host like '%" + q + "%' OR"
        query += " office like '%" + q + "%' OR"
        query += " meeting_place like '%" + q + "%' "
        res = db.query(query)

        count = 0
        for i in res:
            count += 1

        # do we need to create a paginator?
        if 'page' in data:
            page = sanitize_page(data['page'].value)
            if page != "":
                page = int(page)
                count -= (page - 1)*200
            else:
                page = 1
        else:
            page = 1

        out = ""
        out += u"También puedes hacer búsquedas haciendo click sobre cada uno de los resultados."

        # show simple paginator if needed
        if count > 200:
            out += "<div class='pull-right'><a href='http://" 
            out += config.base_url + "search?"
            out += urlencode({'q': q}) + "&page=" + str(page + 1) + u"'>Más resultados>></a></div>"

        out += "<table class='table table-hover table-striped table-bordered table-responsive table-condensed' "
        out += " style='font-size: 12px;'>"
        out += "<th>Fecha</th><th>Visitante</th><th>Documento</th><th>Entidad</th>"
        out += u"<th>Motivo</th><th>Empleado público</th><th>Oficina/Cargo</th>"
        out += u"<th>Lugar de reunión</th><th>Hora ing.</th><th>Hora sal.</th>\n"


        if page > 1:
            # Slice results for paginator
            # LIMIT skip, count
            query += " LIMIT " + str((page - 1)*200) + ", 200 "
        else:
            query += " LIMIT 200 " 

        res = db.query(query)
        j = 0
        for i in res:
            out += lib.prettify(i)
            j += 1
            if i == 200:
                break
        out += "\n</table>"

        if j < 1:
            out = False

    f = codecs.open("base.html", "r", "utf8")
    html = f.read()
    f.close()

    try:
        out = html.replace("{% content %}", out)
        out = out.replace("{% intro_message %}", "")
        out = out.replace("{% base_url %}", config.base_url)
        out = out.replace("{% keyword %}", q.decode("utf-8"))
    except:
        out = html.replace("{% intro_message %}", message)
        out = out.replace("{% content %}", "")
        out = out.replace("{% base_url %}", config.base_url)
        out = out.replace("{% keyword %}", q.decode("utf-8"))

    print "Content-Type: text/html\n"
    print out.encode("utf8")
else:
    f = codecs.open("base.html", "r", "utf8")
    html = f.read()
    f.close()

    out = html.replace("{% intro_message %}", message)
    out = out.replace("{% content %}", "")
    out = out.replace("{% base_url %}", config.base_url)

    print "Content-Type: text/html\n"
    print out.encode("utf8")
