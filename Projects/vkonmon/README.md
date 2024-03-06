# vkonmon
Simple VK Online Monitoring System
## Installation
```
sudo apt install git python3 python3-pip python3-rrdtool librrd-dev
git clone https://github.com/iwalfy/vkonmon
cd vkonmon
pip3 install -r requirements.txt
echo "your token here" > token.txt
python3 main.py
```
Also add to crontab: `* * * * * /path/to/vkonmon/update.py`

If you want to make it public please use uWSGI.
## Usage
Go to /admin and authorize (by default admin/admin).
