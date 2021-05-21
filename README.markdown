# Render Watch
<p align="center">
  <img src="https://github.com/mgregory1994/RenderWatch/blob/main/src/render_watch/render_watch_data/RenderWatch.png" alt="Render Watch Icon"/>
</p>

Render Watch is an open source professional video transcoder for Linux.

Render Watch can be used to convert video files from one format to another
in order to meet format specifications for devices, streaming, local playback, 
etc. Render Watch can also be used as a video compression tool so that you 
can make a lossy version of your video projects or make compressed backups 
of your videos.

## Compatibility
Render Watch is compatible with Debian and Ubuntu based distros.

Other distros require manual installation (see below).

## Installation
#### Debian or Ubuntu based distros:
1. [Download](https://github.com/mgregory1994/RenderWatch/releases/tag/v0.1.0-beta) the .deb file
2. Install by double-clicking the .deb file or by using apt
    ```console
    # apt install ./<name of file>.deb
    ```
   
#### Other distros:
1. Install dependencies
    * ffmpeg
    * [PyGObject](https://pygobject.readthedocs.io/en/latest/getting_started.html)
    * pip
2. Clone repository
    ```console
    $ git clone https://github.com/mgregory1994/RenderWatch.git
    ```
3. Manually install Render Watch
    ```console
    $ cd RenderWatch
    # python setup.py install
    ```
4. Copy .desktop file and program icons
    ```console
    $ cp data/render-watch.desktop ~/.local/share/applications
    $ cp -r data/icons/. ~/.icons
    ```

## Uninstall
#### Debian or Ubuntu based distros:
```console
# apt remove render-watch
```

#### Other distros:
1. Remove .desktop file
    ```console
    $ rm ~/.local/share/applications/render-watch.desktop
    ```
2. Remove Render Watch using pip
    ```console
    # pip uninstall render-watch
    ```

## Usage
Once you have installed Render Watch, you can find it among your installed
applications.

You can also run Render Watch from the command line
```console
$ render-watch
```

You can also run Render Watch in debug mode
```console
$ render-watch-debug
```

The log file can then be found in
```console
~/.config/"Render Watch"/
```

## Screenshots
<p align="center">
  <img src="https://github.com/mgregory1994/RenderWatch/blob/main/src/render_watch/render_watch_data/screenshots/rw_import.png"
  alt="Render Watch Import" />
</p>

<p align="center">
  <img src="https://github.com/mgregory1994/RenderWatch/blob/main/src/render_watch/render_watch_data/screenshots/rw_encode.png"
  alt="Render Watch Encoding" />
</p>

## Contributing
Pull requests and issue reports are welcome.

Before opening a pull request, consider discussing the change
as an issue first.

## License
Render Watch is licensed under [GPLV3](https://www.gnu.org/licenses/gpl-3.0.en.html)

--Screenshots with Big Buck Bunny--

(c) copyright 2008, Blender Foundation / www.bigbuckbunny.org