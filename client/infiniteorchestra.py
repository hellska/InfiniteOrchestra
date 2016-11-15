"""
    Read a json containing sounds data
    Download the sound preview (hq, mp3)
    Count the mumber of occurrende
"""
import sys, os, traceback, time
import json
from os import walk
from os.path import isdir
import requests

sys.path.append('../extlib/')
import myToken

rootpath = '/Volumes/ssdData/infiniteorchestra/'
#sounddir = rootpath+'sounds_test'
sounddir = rootpath+'sounds'
#apiendpoint = 'http://localhost:5000/api/list_sounds'
apiendpoint = 'http://labs.freesound.org/infiniteorchestra/api/list_sounds'

c = myToken.freesound_client()

req = requests.get(apiendpoint)
idict = req.json()

for i in idict['fsid']:
    if not os.path.exists(sounddir+'/'+str(i)+'.mp3'):
        try:
            sound = c.get_sound(i)
            try:
                sound.retrieve_preview(sounddir+'/', str(i)+'.mp3' )
                print sound.previews.preview_hq_mp3, "downloaded"
                time.sleep(1)
            except:
                print "Error in Get Sound for: ", str(i)
                traceback.print_exc()
        except:
            print "Freesound Errore block!"
            print '####'
            traceback.print_exc()
            print 'Downloaded '+str(idcount)+' sounds for '+subdir
            print 'Checked '+str(totcount)+' sounds - inside loop'
            sys.exit(3)
