#!/usr/bin/python
# coding: utf-8
from flask import Flask, jsonify, request, render_template, url_for, Response
import requests
from unicodedata import normalize
import MySQLdb

app = Flask(__name__)


def encrypt(password):
    publickey = '0x223d5fcde'
    plainpass = hex(int(password,10))
    key = int(publickey, 16) * int(plainpass, 16)

    return hex(key)


def decrypt(encrypted):
    key = "papapa"
    return key


def remover_acentos(txt, codif='utf-8'):
    return normalize('NFKD', txt.decode(codif)).encode('ASCII','ignore')


def database(SQL, function):
    db = MySQLdb.connect(host="localhost",
                         user="backend",
                         passwd="smartMonitor666",
                         db="database")
    cur = db.cursor()
    cur.execute(SQL)
    # print all the first cell of all the rows
    db.close()
    if function == "check":
        if cur.rowcount > 0:
            return 1
        else:
            return 0
    elif function == "execute":
        return cur.fetchall()[0]


def loginpucrs(matricula, senha, classe):
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.109 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Connection': 'keep-alive',
        }

        data = 'matricula=' + matricula + '&senha=' + str(senha) + '&classe=' + classe

        r = requests.post('http://webapp.pucrs.br/mobile/auth', headers=headers, data=data)

        if r.status_code == int(200):
            result = r.json()

            return result

        else:

            return r.status_code


@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
  return response


@app.route('/', methods=['POST'])
def login():
        matricula = request.form['matricula']
        plainPass = request.form['passwd']
        classe = request.form['class_select']
        senha = encrypt(plainPass).strip('0x')
        local = request.form['local']
        result = loginpucrs(matricula=matricula, senha=senha, classe=classe)

        if result:

            nome = result['aluno']['nomeAluno']
            email = result['aluno']['emailAluno']
            curso = result['aluno']['nomeCurso']

            cursor = database("SELECT * FROM locais WHERE CODIGO = '" + str(local) + "'", function="execute")
            sala = cursor[4]
            bloco = cursor[1]
            return render_template('form.html', nome=nome.split(' ', 1)[0].title(), sala=sala, local=local, email=email, bloco=bloco)

        else:

            return Response("Aluno inexistente ou senha inválida, " + str(result), 401)


@app.route('/<codigo>')
def loginpage(codigo=None):

    exists = database("SELECT * FROM locais WHERE CODIGO = '" + str(codigo) + "'", function="check")
    if exists:
        return render_template('login.html', codigo=codigo)
    else:
        return "Local não existente"


if __name__ == '__main__':
    app.run(host='192.168.1.124', debug=True, port=int("5000"))