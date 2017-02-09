import numpy as np
import sqlite3
from contextlib import closing
from flask import Flask, request, g, redirect, url_for, render_template, jsonify
import extlib.myToken as myToken
import random


# TODO: Use sqlAlchemy for database operations

# config
# DATABASE = './db/freesoundscapes.db'
# SECRET_KEY = 'fscapes'
# USERNAME = 'fsadmin'
# PASSWORD = 'fsadmin'
# INIFILE = './performance.ini'
# DEBUG = True


app = Flask(__name__)
# read config from a file
app.config.from_pyfile('freesoundscapes.cfg')


# db connection method
def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


def init_db(sqlfile='./db/schema.sql'):
    """initialize db (create a brand new empty database)

    :param sqlfile: path to the text file with sql statement to create the DB
    :return: boolean True if DB created, False if DB not created
    """
    with closing(connect_db()) as db:
        with app.open_resource(sqlfile, mode='r') as f:
            try:
                db.cursor().executescript(f.read())
            except Exception as e:
                print e
                return False
            else:
                db.commit()
                return True


def read_ini_file():
    with open(app.config['INIFILE'], 'r') as inifile:
        try:
            pid = inifile.read()
        except (IOError, OSError) as e:
            raise e
            pid = 999
        else:
            if not pid:
                pid = 888
    return pid


def write_ini_file(inicontent):
    with open(app.config['INIFILE'], 'wb') as inifile:
        try:
            inifile.write(inicontent)
        except (IOError, OSError) as e:
            print e
            return False
        else:
            return True


def add_soundid(fsid, search_text):
    pid = read_ini_file()
    g.db.execute('insert into fssounds (fsid, search_text, performance_id) values (?, ?, ?)', [fsid, search_text, pid])
    g.db.commit()


# search sounds in freesound store the ID in the DB and embed the frame in the return page
def freesound_search(form_text):
    fsclient = myToken.freesound_client()
    result = fsclient.text_search(query=str(form_text), fields="id,name,previews,images", page_size=100,
                                  filter=" duration:[1.0 TO 5.0]", sort="rating_desc")
    if result.count > 0:
        if result.count == 1:
            thissample = 0
        else:
            nsamples = result.count
            thissample = int(round(np.random.random() * nsamples)) - 1
            if thissample > 100:
                thissample = 99
        sound = result[thissample]
        soundid = sound.id
        return_msg = "Great! You submitted a sound!"
    else:
        soundid = 0
        return_msg = "No Sound Found!"

    return soundid, return_msg


# @app.context_processor
def freesound_advanced_search(search_dict):
    """Format and Perform Freesound API search using input data

    :param search_dict: Dictionary containing search DATA
    :return:
    """
    fsclient = myToken.freesound_client()
    print 'freesound advanced search'
    print search_dict
    return search_dict


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


@app.route('/')
def show_index():
    # app_title = 'Freesound Scapes'
    # return render_template('index.html', app_title = app_title)
    # Go straight to the search page
    return redirect(url_for('search_form', rannum=random.random()))


@app.route('/performance', methods=['GET', 'POST'])
def search_form():
    # check if there is an active performance 
    if request.method == 'POST':
        # redirect to main page if string is empty!
        if request.form['search_string']:  #
            form_text = request.form['search_string']
            # Use Unicode strings for freesound search
            uform_text = form_text.encode('utf-8')
            soundid, msg = freesound_search(uform_text)
            # insert the sound into the DB
            if soundid > 0:
                add_soundid(soundid, form_text)
            return render_template('fssearchform.html', form_text=form_text, form_out=soundid, form_msg=msg,
                                   rannum=random.random())
        else:
            return redirect(url_for('search_form', rannum=random.random()))
    else:
        return render_template('fssearchform.html', rannum=random.random())


@app.route('/performance/advanced_search', methods=['GET', 'POST'])
def advanced_search_form():
    """Search multiple sounds according to the complete form

    :return: dictionary json song_dict
    """
    if request.method == 'GET':
        return render_template('fsadvsearchform.html', rannum=random.random())
    elif request.method == 'POST':
        # TODO: verify if the form fields are filled
        minlength = float(request.form['min_length'])
        maxlength = float(request.form['max_length'])
        search_dict = "{ text: '%s', mindur: %f, maxdur: %f }" % \
                      (request.form['search_string'], minlength, maxlength)
        freesound_advanced_search(search_dict)
        return render_template('fsadvsearchform.html', rannum = random.random())


@app.route('/performance/list_sounds')
def list_sounds():
    pid = read_ini_file()
    queryout = g.db.execute('select * from fssounds where performance_id = ? order by id', [pid])
    submitted_sounds = [dict(id=row[0], fsid=row[1], text=row[2], perfid=row[3]) for row in queryout.fetchall()]
    return render_template('current_sound_list.html', fssounds=submitted_sounds, rannum = random.random())


@app.route('/archive')
def archive():
    return render_template('archive.html', rannum = random.random())


@app.route('/api/list_sounds')
def api_list_sound():
    pid = read_ini_file()
    queryout = g.db.execute('select * from fssounds where performance_id = ? order by id', [pid])
    submitted_sounds = {}  # dict(fsid=row[1]) for row in queryout.fetchall()
    # submitted_sounds['fsid'] = {}
    for row in queryout.fetchall():
        if 'fsid' in submitted_sounds:
            submitted_sounds['fsid'].append(row[1])
        else:
            submitted_sounds['fsid'] = [row[1]]

    # return render_template('api_list_sounds.html', output=submitted_sounds)
    return jsonify(submitted_sounds)


@app.route('/api/set_performance/<int:perfid>/<key>', methods=['GET', 'POST'])
def set_performance_id(perfid, key):
    if key == app.config['SECRET_KEY']:
        write_ini_file(str(perfid))
        return 'Performance ID: %d' % perfid
    else:
        return 'wrong password'


# run standalone application
if __name__ == '__main__':
    app.run()
    # app.run(host='0.0.0.0',port='3333',debug=False)
