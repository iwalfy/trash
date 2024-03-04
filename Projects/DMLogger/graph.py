#!/usr/bin/env python3

import argparse
import sqlite3
import pytimeparse2 as pytimeparse
import time
import matplotlib.pyplot as plt

con = sqlite3.connect("data.db")
cur = con.cursor()

FROM_WORLD = "world"

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--save", help="Save graph to file")
parser.add_argument("-t", "--timedelta", default="24h")

def loadData(timedelta):
  min_time = round(
    (time.time() - timedelta)
  ) * 1000

  print(min_time)

  sql_query = "SELECT timestamp, player_name, x, y, z, player_world FROM logging WHERE timestamp > ?;"
  res = cur.execute(sql_query, [min_time])
  return res.fetchall()

def renderGraph(data, save_file=None):
  point_groups = {}

  for entry in data:
    timestamp = entry[0]
    player_name = entry[1]
    player_pos = [ entry[2], entry[3], entry[4] ]
    player_world = entry[5]

    if player_world != FROM_WORLD:
      continue

    if player_name not in point_groups:
      point_groups[player_name] = []

    point_groups[player_name].append([ player_pos[0], player_pos[2] ])

  for player, group in point_groups.items():
    x_values = []
    y_values = []

    for point in group:
      x_values.append(point[0])
      y_values.append(point[1])

    plt.scatter(x_values, y_values, label=player)

  plt.gca().invert_yaxis()
  plt.legend()

  if save_file:
    plt.savefig(save_file)
    return

  plt.show()

def main():
  args = parser.parse_args()

  timedelta = pytimeparse.parse(args.timedelta)
  data = loadData(timedelta)

  if args.save:
    renderGraph(data, save_file=args.save)
    return

  renderGraph(data)

if __name__ == "__main__":
  main()
