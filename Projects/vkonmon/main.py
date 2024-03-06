from flask import Flask
from flask import send_from_directory
from flask import request
from flask import redirect
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
import rrdtool
import shutil
import requests

app = Flask(__name__)
auth = HTTPBasicAuth()

users = {
	"admin": generate_password_hash("admin")
}

def listdir_nohidden(path):
    for f in os.listdir(path):
        if not f.startswith('.'):
            yield f

@auth.verify_password
def verify_password(username, password):
	if username in users and \
		check_password_hash(users.get(username), password):
			return username

@app.route("/")
def _list():
	_users = listdir_nohidden("./data")
	_out = """<!DOCTYPE html>
<html>
<head>
<title>VkOnlineMon</title>
<meta charset="UTF-8">
<meta name="robots" content="noindex">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
body {
	font-family: -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", "Open Sans", "Helvetica Neue", Helvetica, Arial, sans-serif;
	text-align: center;
	padding-bottom: 50px;
}
a {
	color: #0d6efd;
	text-decoration: none;
	font-size: 20px;
}
a:hover {
	color: #0a58ca;
}
table {
	margin: auto;
}
</style>
</head>
<body>
<h1>VkOnlineMon</h1>
<table>"""
	for _user in _users:
		f = open("./data/" + _user + "/info.json", "r")
		_info = json.loads(f.read())
		f.close()
		_first_name = _info.get("first_name")
		_last_name = _info.get("last_name")
		_out += "<tr><td><a href=\"/{user}\">{first_name} {last_name}</a></td></tr>".format(user = _user, first_name = _first_name, last_name = _last_name)
	_out += "</table></body></html>"
	return _out

@app.route("/<_user>")
def _graph(_user):
	_dir = "./data/" + _user
	_graphdir = "./static/" + _user
	if (not os.path.exists(_dir)):
		return "invalid user"

	if (not os.path.exists(_graphdir)):
		os.mkdir(_graphdir)

	f = open("./data/" + _user + "/info.json", "r")
	_info = json.loads(f.read())
	f.close()
	_first_name = _info.get("first_name")
	_last_name = _info.get("last_name")

	# 8 hours
	rrdtool.graph("./static/" + _user + "/online-hours.svg",
		      "--imgformat", "SVG", "--end", "now", "--start", "end-28800s", "--y-grid", "none", "--vertical-label", "", "--zoom", "2", "--border", "0",
		      "--width", "600", "--height", "50", "--upper-limit", "1", "--lower-limit", "0",
		      "DEF:online=./data/" + _user + "/data.rrd:online:MAX",
			  "DEF:online_mobile=./data/" + _user + "/data.rrd:online_mobile:MAX",
			  "CDEF:online2=online,10,0,IF",
			  "CDEF:online_mobile2=online_mobile,10,0,IF",
		      "AREA:online2#00FF00:Online from desktop",
		      "AREA:online_mobile2#80A6FF:Online from mobile",
		      "CDEF:wrongdata=online,UN,INF,UNKN,IF", "AREA:wrongdata#00000015")
	# day
	rrdtool.graph("./static/" + _user + "/online-day.svg",
		      "--imgformat", "SVG", "--end", "now", "--start", "end-86399s", "--y-grid", "none", "--vertical-label", "", "--zoom", "2", "--border", "0",
		      "--width", "600", "--height", "50", "--upper-limit", "1", "--lower-limit", "0",
		      "DEF:online=./data/" + _user + "/data.rrd:online:MAX",
			  "DEF:online_mobile=./data/" + _user + "/data.rrd:online_mobile:MAX",
			  "CDEF:online2=online,10,0,IF",
			  "CDEF:online_mobile2=online_mobile,10,0,IF",
		      "AREA:online2#00FF00:Online from desktop",
		      "AREA:online_mobile2#80A6FF:Online from mobile",
		      "CDEF:wrongdata=online,UN,INF,UNKN,IF", "AREA:wrongdata#00000015")
	# week
	rrdtool.graph("./static/" + _user + "/online-week.svg",
		      "--imgformat", "SVG", "--end", "now", "--start", "end-7d", "--y-grid", "none", "--vertical-label", "", "--zoom", "2", "--border", "0",
		      "--width", "600", "--height", "50", "--upper-limit", "1", "--lower-limit", "0",
		      "DEF:online=./data/" + _user + "/data.rrd:online:MAX",
			  "DEF:online_mobile=./data/" + _user + "/data.rrd:online_mobile:MAX",
			  "CDEF:online2=online,10,0,IF",
			  "CDEF:online_mobile2=online_mobile,10,0,IF",
		      "AREA:online2#00FF00:Online from desktop",
		      "AREA:online_mobile2#80A6FF:Online from mobile",
		      "CDEF:wrongdata=online,UN,INF,UNKN,IF", "AREA:wrongdata#00000015")
	# 30 days
	rrdtool.graph("./static/" + _user + "/online-30d.svg",
		      "--imgformat", "SVG", "--end", "now", "--start", "end-30d", "--y-grid", "none", "--vertical-label", "", "--zoom", "2", "--border", "0",
		      "--width", "600", "--height", "50", "--upper-limit", "1", "--lower-limit", "0",
		      "DEF:online=./data/" + _user + "/data.rrd:online:MAX",
			  "DEF:online_mobile=./data/" + _user + "/data.rrd:online_mobile:MAX",
			  "CDEF:online2=online,10,0,IF",
			  "CDEF:online_mobile2=online_mobile,10,0,IF",
		      "AREA:online2#00FF00:Online from desktop",
		      "AREA:online_mobile2#80A6FF:Online from mobile",
		      "CDEF:wrongdata=online,UN,INF,UNKN,IF", "AREA:wrongdata#00000015")

	return """<!DOCTYPE html>
<head>
<meta charset="UTF-8">
<meta http-equiv="pragma" content="no-cache">
<meta http-equiv="refresh" content="30">
<meta name="robots" content="noindex">
<title>{first_name} {last_name}</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
body {{
	font-family: -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", "Open Sans", "Helvetica Neue", Helvetica, Arial, sans-serif;
	text-align: center;
	padding-bottom: 50px;
}}
a {{
	color: #0d6efd;
	text-decoration: none;
}}
a:hover {{
	color: #0a58ca;
}}
img {{
	width: 800px;
}}
@media only screen and (max-width: 800px) {{
	img {{
		width: 100%;
	}}
}}
</style>
</head>
<body>
<h1><a href="https://vk.com/id{user}" target="_blank">{first_name} {last_name}</a></h1>
<img src="/static/{user}/online-hours.svg"><br>За последние 8 часов<br><br>
<img src="/static/{user}/online-day.svg"><br>За сутки<br><br>
<img src="/static/{user}/online-week.svg"><br>За неделю<br><br>
<img src="/static/{user}/online-30d.svg"><br>За месяц<br><br>
</body>
</html>
""".format(user = _user, first_name = _first_name, last_name = _last_name)

@app.route("/admin")
@auth.login_required
def _admin():
	_users = listdir_nohidden("./data")
	_out = """<!DOCTYPE html>
<html>
<head>
<title>VkOnlineMon</title>
<meta charset="UTF-8">
</head>
<body>
<table>
<form method="GET" action="/admin/add">
<input type="text" name="id">
<input type="submit" value="Add">
</form>"""
	for _user in _users:
		f = open("./data/" + _user + "/info.json", "r")
		_info = json.loads(f.read())
		f.close()
		_first_name = _info.get("first_name")
		_last_name = _info.get("last_name")
		_out += "<tr><td><a href=\"/{user}\">{first_name} {last_name}</a></td><td><a href=\"/admin/delete/{user}\" style=\"color:red\">Delete</a></td></tr>".format(user = _user, first_name = _first_name, last_name = _last_name)
	_out += "</table></body></html>"
	return _out

@app.route("/admin/delete/<_user>")
@auth.login_required
def _delete(_user):
	if (not os.path.exists("./data/" + _user)):
		return "user not exists"

	shutil.rmtree("./data/" + _user)
	if (os.path.exists("./static/" + _user)):
		shutil.rmtree("./static/" + _user)

	return redirect("/admin", code=302)

@app.route("/admin/add")
@auth.login_required
def _add():
	_user = request.args.get("id")
	if (not _user != ""):
		return "no id provided"

	f = open("./token.txt", "r")
	_token = f.read()
	f.close()

	r = requests.get("https://api.vk.com/method/users.get?user_ids={user}&fields=last_seen&access_token={token}&v=5.131".format(token = _token, user = _user))
	if (not r.json().get("response")):
		return "account with this id not exists"
	_resp = r.json().get("response")[0]

	_id = _resp.get("id")

	_dir = "./data/" + str(_id)
	if (os.path.exists(_dir)):
		return "user already exists"

	if not _resp.get("last_seen"):
		return "cannot retrive online"

	_first_name = _resp.get("first_name")
	_last_name = _resp.get("last_name")

	if (os.path.exists("./data/" + str(_id))):
		return "user already exists"

	os.mkdir(_dir)
	rrdtool.create(_dir + "/data.rrd",
			      "-s", "60",
			      "DS:online:GAUGE:3600:0:1",
			      "DS:online_mobile:GAUGE:3600:0:1",
			      "RRA:MAX:0.5:1:10000",
			      "RRA:MAX:0.5:5:10000",
			      "RRA:MAX:0.5:20:10000",
			      "RRA:MAX:0.5:60:10000",
			      "RRA:MAX:0.5:180:10000",
			      "RRA:MAX:0.5:720:10000",
			      "RRA:MAX:0.5:1440:10000")

	_tojson = {"first_name":_first_name,"last_name":_last_name}
	f = open(_dir + "/info.json", "w")
	f.write(json.dumps(_tojson))
	f.close()

	return redirect("/admin", code=302)

@app.route("/static/<_file>")
def _static(_file):
	if (not os.path.exists("./static/" + _file)):
		return "file not exists"

	return send_from_directory("./static", _file)

@app.route("/robots.txt")
def _robots():
	return send_from_directory("./static", "robots.txt")

if __name__ == "__main__":
	app.run(host='0.0.0.0')
