import os
import json

cfgFile = os.path.dirname(os.path.abspath(__file__)) + '/settings.json'


def getSettings():
	with open(cfgFile, 'r') as cfg:
		prefs = json.load(cfg)
	return prefs

def setSettings(prefs):
	with open(cfgFile, 'w') as cfg:
		json.dump(prefs, cfg, indent='\t')

def getSetting(k):
	prefs = getSettings()
	return prefs.get(k, None)
