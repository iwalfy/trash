#!/usr/bin/env python3


import textwrap
import requests
import time
import sqlite3
import json
import os
import html

import sys
import logging
from logging import StreamHandler, Formatter
from threading import Thread

DM_SERVER = "https://map.fursenko.space"
LOG_INTVAL = 10

BOT_TOKEN = "[[ REDACTED FOR PRIVACY REASON ]]"
TELEGRAM_ID = 1970959071

TILE_SAVE_DIR = "tiles"
TILE_SAVE_DIR_LIMIT = 1000

MAX_TG_WARN = 30

HEADERS = {
  "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
  "Referer":    DM_SERVER,
}

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = StreamHandler(stream=sys.stdout)
handler.setFormatter(Formatter(fmt='[%(asctime)s] [%(levelname)s] %(message)s'))
logger.addHandler(handler)

con = sqlite3.connect("data.db")
cur = con.cursor()

next_timestamp = None

class TileDownloader(Thread):

  session = requests.Session()
  queue = []

  def download(self, world, tile, timestamp):
    rtime = round(time.time())
    new_dir = os.path.join(TILE_SAVE_DIR, str(rtime))

    tmpdirs = [ os.path.join(TILE_SAVE_DIR, i) for i in os.listdir(TILE_SAVE_DIR) ]
    dirs = sorted(filter(os.path.isdir, tmpdirs), key=os.path.getmtime)

    if len(dirs) == 0:
      logger.info(f"Creating new tile dir {new_dir}")
      os.mkdir(new_dir)
      dir = new_dir
    else:
      last_dir = dirs[-1]
      last_dir_files = os.listdir(last_dir)

      if len(last_dir_files) >= TILE_SAVE_DIR_LIMIT:
        logger.info(f"Old tile dir is full! Creating new tile dir {new_dir}")
        os.mkdir(new_dir)
        time.sleep(5) # pizdec
        dir = new_dir
      else:
        dir = last_dir

    url = f"{DM_SERVER}/tiles/{world}/{tile}?timestamp={timestamp}"
    tmp_name = tile.replace("/", "___")
    filename = os.path.join(dir, f"{rtime}___{tmp_name}")

    logger.info(f"Saving new tile {url} to {filename}...")

    r = self.session.get(url, headers=HEADERS, stream=True)
    with open(filename, "wb") as f:
      for chunk in r.iter_content(chunk_size=1024):
        if chunk:
          f.write(chunk)

    logger.info(f"Tile {url} saved successfuly!")

  def __init__(self, world, logger):
    Thread.__init__(self)
    self.logger = logger
    self.world  = world

  def run(self):
    while True:
      for tile in self.queue:
        if "attempt" not in tile:
          tile["attempt"] = 0
        tile_name = tile["name"]

        try:
          self.download(self.world, tile["name"], tile["timestamp"])
          self.queue.remove(tile)
        except:
          self.logger.exception(f"Failed to download tile {tile_name}")
          tile["attempt"] += 1

          if tile["attempt"] > 5:
            self.logger.info(f"Tile {tile_name} excluded from queue due to 5 failed download attempts")
            self.queue.remove(tile)

      time.sleep(1)

  def appendQueue(self, update):
    self.queue.append(update)

def telegramSend(sender, msg):
  logger.info(f"Sending telegram message: \"{msg}\"...")
  payload = {
    "chat_id": TELEGRAM_ID,
    "text": "<b>{}</b> {}".format(html.escape(sender), html.escape(msg)),
    "parse_mode": "HTML",
  }
  url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
  try:
    r = requests.post(url, data=payload)
    resp = r.json()
    if not resp["ok"]:
      logger.error("Failed to send message")
      logger.error(r.text)
  except:
    logger.exception("Failed to send message")

def getWorlds():
  worlds = []

  reqUrl = f"{DM_SERVER}/up/configuration"
  resp = requests.get(reqUrl)
  data = resp.json()

  for world in data["worlds"]:
    worlds.append(world["name"])

  return worlds

def dmLogger(worlds):
  fail_counter = 0
  s = requests.Session()
  downloaders = {}
  while True:
    if fail_counter == MAX_TG_WARN:
      telegramSend("\U0001f6d1", f"More than {MAX_TG_WARN} failed dynmap request in sequence")

    for world in worlds:
      if world not in downloaders:
        logger.info(f"Starting TileDownloader for world:{world}...")
        downloaders[world] = TileDownloader(world, logger)
        downloaders[world].start()

      downloader = downloaders[world]

      logger.info(f"Saving state for {world}...")

      try:
        saveState(s, world, downloader)
        fail_counter = 0
      except:
        logger.exception(f"Failed to save state for {world}!")
        fail_counter += 1

    logger.info(f"Next save in {LOG_INTVAL} seconds...")
    time.sleep(LOG_INTVAL)

def saveState(s, world, downloader):
  global next_timestamp

  if next_timestamp is None:
    ts = round(time.time() * 1000)
  else:
    ts = next_timestamp

  reqUrl = f"{DM_SERVER}/up/world/{world}/{ts}"
  resp = s.get(reqUrl, headers=HEADERS)
  data = resp.json()

  next_timestamp = data["timestamp"]

  print(data)
  players = data["players"]

  updates = data["updates"]
  for update in updates:
    if update["type"] == "chat":
      if update["source"] == "player":
        player_name = update["playerName"]
        message = update["message"]
        telegramSend(f"\U0001f4ac {player_name}:", message)

      elif update["source"] == "web":
        player_name = update["playerName"]
        message = update["message"]
        telegramSend(f"\U0001f4ac WEB:{player_name}:", message)

      else:
        message = update["message"]
        telegramSend(f"\U0001f4e2 BROADCAST:", message)

    elif update["type"] == "playerjoin":
      player_name = update["playerName"]
      telegramSend("\u2795", f"{player_name} joined")

    elif update["type"] == "playerquit":
      player_name = update["playerName"]
      telegramSend("\u2796", f"{player_name} quit")

    elif update["type"] == "tile":
      downloader.appendQueue(update)

  raw_query = "INSERT INTO raw_log VALUES (?, ?);"
  raw_data = [
    ts, json.dumps(data, separators=(",", ":")),
  ]
  cur.execute(raw_query, raw_data)

  sql_query = "INSERT INTO logging VALUES (?, ?, ?, ?, ?, ?);"
  sql_data = []
  for player in players:
    sql_data.append([
      ts, player["name"], int(player["x"]), int(player["y"]), int(player["z"]), player["world"]
    ])

  cur.executemany(sql_query, sql_data)
  con.commit()

def initTables():
  logger.info("Creating tables...")
  cur.execute("""
CREATE TABLE IF NOT EXISTS raw_log(
  timestamp INT NOT NULL,
  json_data TEXT NOT NULL
);
""")
  cur.execute("""
CREATE TABLE IF NOT EXISTS logging(
  timestamp    INT  NOT NULL,
  player_name  TEXT NOT NULL,
  x INT NOT NULL,
  y INT NOT NULL,
  z INT NOT NULL,
  player_world TEXT NOT NULL
);
""")

def main():
  initTables()
  #worlds = getWorlds()
  worlds = ["world"]
  dmLogger(worlds)

if __name__ == "__main__":
  main()
