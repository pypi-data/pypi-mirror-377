from googleapiclient.discovery import build
from rich.progress import Progress
from rich.traceback import install
import requests
import re
import sys
import os
import threading
from time import sleep

install(show_locals=True)
bp = re.compile(r'"canonicalBaseUrl":"\/(.*?)"')
fp = re.compile(r".+\[(.+)\]\..+")

def isValid(f):
    return os.path.isfile(f) and fp.fullmatch(f)
def isShort(id):
    e = requests.head("https://www.youtube.com/shorts/" + id)
    if e.status_code == 200:
        return True
    return False
global tries
tries = []
global handles
handles = {}
def doTask(file, progress, task):
    global tries
    global handles
    tries.append(file)
    DEVELOPER_KEY = sys.argv[1]
    youtube = build('youtube', 'v3', developerKey=DEVELOPER_KEY)
    try:
        id = fp.fullmatch(file).group(1)
        short = isShort(id)
        request = youtube.videos().list(part='snippet', id=id)
        details = request.execute()
        chanid = details["items"][0]["snippet"]["channelId"]
        if chanid not in handles:
            handle = bp.search(requests.get("https://www.youtube.com/channel/" + chanid).text).group(1)
            handles[chanid] = handle
        else:
            handle = handles[chanid]
        folder = details["items"][0]["snippet"]["channelTitle"] + " (" + handle + ")"
        if not os.path.isdir(folder):
            os.mkdir(folder)
        if short and not os.path.isdir(folder + "/Shorts"):
            os.mkdir(folder + "/Shorts")
        os.rename(file, folder + ("/Shorts" if short else "") + "/" + file)
    finally:
        sleep(0.1)
        tries.remove(file)
        progress.update(task, advance=1)

def app():
    if len(sys.argv) == 1:
        print("This program needs a YouTube API key as a parameter!")
        exit(1)
    with Progress(expand=True) as progress:
        progress.start()
        threads = os.cpu_count()
        lst = [f for f in os.listdir() if isValid(f)]
        maintask = progress.add_task("Processing files...", total=len(lst))
        for file in lst:
            while lst:
                if len(tries) < threads:
                    e = lst.pop(0)
                    threading.Thread(target=doTask, args=[e, progress, maintask]).start()
                    sleep(0.01)
            while tries:
                pass
