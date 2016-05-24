# modules import
import sys
import numpy as np
import sqlite3
from contextlib import closing
from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash, jsonify

sys.path.append('./extlib')

import freesound
import myToken

# config
DATABASE = './db/freesoundscapes.db'
SECRET_KEY = 'fscapes'
USERNAME = 'fsadmin'
PASSWORD = 'fsadmin'
INIFILE = './performance.ini'
DEBUG = True

# create the app
app = Flask(__name__)
app.config.from_object(__name__)
# read the config file if set the FLASKR_SETTINGS env variable
# the values will override previous loaded one from the config section of this file
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

# db connection method
def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

# initialize db method (create a brand new empty database)
def init_db(sqlfile='./db/schema.sql'):
    with closing(connect_db()) as db:
        with app.open_resource(sqlfile, mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit

def read_ini_file():
    try:
        with open(app.config['INIFILE'], 'r') as inifile:
            pid = inifile.read()
            if not pid:
                pid = 888
    except (IOError, OSError) as e:
        pid = 999
    
    return pid

def write_ini_file(inicontent):
    try:
        with open(app.config['INIFILE'], 'wb') as inifile:
            inifile.write(inicontent)
            return True
    except (IOError, OSError) as e:
        return False
    

def add_soundid(fsid, search_text):
    pid = read_ini_file()
    g.db.execute('insert into fssounds (fsid, search_text, performance_id) values (?, ?, ?)', [fsid, search_text, pid])
    g.db.commit()
    
# search sounds in freesound store the ID in the DB and embed the frame in the return page
def freesound_search(form_text):
    fsclient = myToken.freesound_client()
    result = fsclient.text_search(query=str(form_text),fields="id,name,previews,images",page_size=100,filter=" duration:[1.0 TO 5.0]",sort="rating_desc")
    if result.count>0:
        if result.count==1:
            thisSample = 0
        else:
            nsamples = result.count
            thisSample = int(round(np.random.random()*nsamples))-1
            if thisSample > 100:
                thisSample = 99
        sound = result[thisSample]
        soundid = sound.id
        return_msg = "Great! You submitted a sound!"
    else:
        soundid = 0
        return_msg = "No Sound Found!"
    
    return soundid, return_msg

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
    app_title = 'Freesound Scapes'
    #return render_template('index.html', app_title = app_title)
    # Go straight to the search page
    return redirect(url_for('search_form'))

@app.route('/performance', methods=['GET', 'POST'])
def search_form():
    # check if there is an active performance 
    if request.method == 'POST':
        # redirect to main page if string is empty!
        if request.form['search_string']: #
            form_text = request.form['search_string']
            # Use Unicode strings for freesound search
            uform_text = form_text.encode('utf-8')
            soundid, msg = freesound_search(uform_text)
            # insert the sound into the DB
            if soundid>0:
                add_soundid(soundid, form_text)
            return render_template('fssearchform.html', form_text=form_text, form_out=soundid, form_msg=msg)
        else:
            form_text = ""
            return redirect(url_for('search_form'))    
    else:
        form_text = ""
        #return redirect(url_for('search_form'))
        return render_template('fssearchform.html')

@app.route('/performance/list_sounds')
def list_sounds():
    pid = read_ini_file()
    queryout = g.db.execute('select * from fssounds where performance_id = ? order by id', [pid])
    submitted_sounds = [dict(id=row[0], fsid=row[1], text=row[2], perfid=row[3]) for row in queryout.fetchall()]
    return render_template('current_sound_list.html', fssounds=submitted_sounds)
    
@app.route('/archive')
def archive():
    return render_template('archive.html')

@app.route('/api/list_sounds')
def api_list_sound():
    pid = read_ini_file()
    queryout = g.db.execute('select * from fssounds where performance_id = ? order by id', [pid])
    submitted_sounds = {} #dict(fsid=row[1]) for row in queryout.fetchall()
    #submitted_sounds['fsid'] = {}
    for row in queryout.fetchall():
        if 'fsid' in submitted_sounds:
            submitted_sounds['fsid'].append(row[1])
        else:
            submitted_sounds['fsid'] = [row[1]]
        
    #return render_template('api_list_sounds.html', output=submitted_sounds)
    return jsonify(submitted_sounds)

@app.route('/api/set_performance/<int:perfid>/<key>', methods=['GET', 'POST'])
def set_performance_id(perfid,key):
    if key==app.config['SECRET_KEY']:
        write_ini_file(str(perfid))
        return 'Performance ID: %d' % perfid
    else:
        return 'wrong password'
    
# run standalone application
if __name__ == '__main__':
    app.run()
    #app.run(host='0.0.0.0',port='3333',debug=False)
