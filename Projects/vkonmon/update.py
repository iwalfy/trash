#!/usr/bin/env python3
import requests
import rrdtool
import os
import json

_workdir = os.path.dirname(os.path.realpath(__file__))

f = open(_workdir + "/token.txt", "r")
_token = f.read()
f.close()

def listdir_nohidden(path):
    for f in os.listdir(path):
        if not f.startswith('.'):
            yield f

_users = ",".join(listdir_nohidden(_workdir + "/data"))

def main():
	r = requests.get("https://api.vk.com/method/users.get?user_ids={users}&fields=online&access_token={token}&v=5.131".format(token = _token, users = _users))
	_resp = r.json().get("response")

	for _user in _resp:
		_id = _user.get("id")
		_first_name = _user.get("first_name")
		_last_name = _user.get("last_name")
		_dir = _workdir + "/data/" + str(_id)

		_tojson = {"first_name":_first_name,"last_name":_last_name}
		f = open(_dir + "/info.json", "w")
		f.write(json.dumps(_tojson))
		f.close()

		if (_user.get("online") == 1):
			if (_user.get("online_mobile") == 1):
				rrdtool.update(_dir + "/data.rrd", "N:0:1")
			else:
				rrdtool.update(_dir + "/data.rrd", "N:1:0")
		else:
				rrdtool.update(_dir + "/data.rrd", "N:0:0")

if __name__ == "__main__":
	main()
