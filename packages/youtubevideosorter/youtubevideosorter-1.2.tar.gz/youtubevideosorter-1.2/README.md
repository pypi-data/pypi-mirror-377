# YouTube Video Sorter

Simple tool to sort videos with directories by channel

# How to use?

What you need:
* Python 3
* A directory full of videos downloaded with `yt-dlp`
* A YouTube API key

## Installation

```shell-session
$ pipx install youtubevideosorter
```

<details>
<summary>
Getting an API key
</summary>


Go to [Google Cloud Console](https://console.cloud.google.com), create a new project if needed

In the "Quick Access" section, click "APIs & Services"

![](https://cdn.swee.codes/screenshots/ytvs1.png)

Click the "+ Enable APIs & services" button

![](https://cdn.swee.codes/screenshots/ytvs2.png)

Search and enable "YouTube Data API v3"

![](https://cdn.swee.codes/screenshots/ytvs3.png)

On the right side of the screen, click the "Credentials" section, click "+ Create credentials" and click "API key"

![](https://cdn.swee.codes/screenshots/ytvs4.png)

Now you have your API key!

![](https://cdn.swee.codes/screenshots/ytvs5.png)
</details>

## Usage

Make sure your current working directory is the directory full of videos.

```shell-session
$ ytvs [api key]
```

Now your videos will be sorted with this directory structure:

* Channel Name (@handle)
    * Shorts
        * Some Short [video id].mp4
    * Some video [video id].mp4
