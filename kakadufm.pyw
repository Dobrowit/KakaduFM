import os, re, sys, time, random, pygubu, pickle, pathlib, requests, calendar, webbrowser, urllib.parse
import tkinter as tk
import tkinter.ttk as ttk
from io import BytesIO
from PIL import Image, ImageTk
from time import sleep
from tkinter import messagebox
from datetime import datetime
from pyradios import RadioBrowser
from colorthief import ColorThief
#from ui.style import configure_styles

try:
    import vlc
except:
    response = messagebox.askquestion("KakaduFM", "VLC media player is missing!\n\nDo you want to download and install VLC from https://www.videolan.org?")
    if response == 'yes':
        webbrowser.open("https://www.videolan.org", new=2)
        quit()
    else:
        quit()

VERBOSE = False
THEME = "default" # default alt clam classic vista winnative xpnative
PROJECT_PATH = pathlib.Path(__file__).parent
PROJECT_UI = PROJECT_PATH / "ui" / "gui.ui"
PROJECT_STYLE = PROJECT_PATH / "ui" / "style.py"
VER_TK = tk.Tcl().eval('info patchlevel')
SEARCH_ENGINES = [
    "https://open.spotify.com/search/",
    "https://duckduckgo.com/?q=",
    "https://www.qwant.com/?q=",
    "https://www.bing.com/search?q=",
    "https://www.google.com/search?q="
    ]
SEARCH_ENGINE = SEARCH_ENGINES[0]
ISO_COUNTRY_CODE = "PL"
MAXL_NAME = 26

class OutputHandler:
    def __init__(self):
        pass

    def write(self, text):
        pass

    def flush(self):
        pass

if not VERBOSE:
    output_handler = OutputHandler() # Tworzenie instancji klasy OutputHandler
    sys.stdout = output_handler # Przekierowanie wyjścia

def zapisz_stan_do_pliku(nazwa_pliku, **zmienne):
    with open(nazwa_pliku, 'wb') as plik:
        pickle.dump(zmienne, plik)

def wczytaj_stan_z_pliku(nazwa_pliku):
    if os.path.exists(nazwa_pliku):
        with open(nazwa_pliku, 'rb') as plik:
            return pickle.load(plik)
    else:
        return None

rb = RadioBrowser()

wczytane_zmienne = wczytaj_stan_z_pliku('radios.pickle')
if wczytane_zmienne is not None:
    globals().update(wczytane_zmienne)
else:
    root = tk.Tk()
    root.configure(height=100, width=200)
    root.title("KakaduFM")
    root.label11 = tk.Label(root)
    root.label11.configure(font="{Arial} 16 {}", text="Downloading stations...")
    root.label11.pack(padx=30, pady=30, side="top")
    root.update()
    try:
        radios = rb.stations()
        zapisz_stan_do_pliku('radios.pickle', radios=radios)
    except:
        messagebox.showerror("KakaduFM", "Download error!\n\nRestart KakaduFM.")
        quit()
    
    # radios = rb.search(countrycode=ISO_COUNTRY_CODE)

    # FIX some .m3u and .pls not playing on vlc.py
    try:
        for i in range(len(radios)):
            url = radios[i]["url"]
            if url.find('.m3u') > -1 or url.find('.pls') > -1:
                radios.pop(i)
    except:
        pass

    # Deduplicate
    url0 = radios[0]["url"]
    try:
        for i in range(1, len(radios)):
            url = radios[i]["url"]
            if url == url0:
                radios.pop(i)
            url0 = radios[i]["url"]
    except:
        pass

    root.destroy()

options = (
#    "--no-xlib",        # Unikaj problemów z X Window System (Linux)
#    "--file-logging",   # Logowanie do pliku
#    "--logfile=vlc.log",# Określenie pliku logów
    "--input-repeat=-1",
    "--fullscreen"
)
if not VERBOSE: options = (*options, "--quiet")
instance = vlc.Instance(options)
player = instance.media_player_new()
player.audio_set_volume(100)
player.audio_set_mute(False)

class GuiApp:
    def __init__(self, master=None):
        self.builder = builder = pygubu.Builder(on_first_object=self.setup_ttk_styles)
        builder.add_resource_path(PROJECT_PATH)
        builder.add_from_file(PROJECT_UI)
        # Main widget
        self.mainwindow = builder.get_object("toplevel1", master)

        self.dialog1 = builder.get_object("dialog1", self.mainwindow)
        self.dialog2 = builder.get_object("dialog2", self.mainwindow)
        self.about = builder.get_object("dialog_about", self.mainwindow)
        self.stations = builder.get_object("dialog_stations", self.mainwindow)
        self.history = builder.get_object("dialog_history", self.mainwindow)

        builder.connect_callbacks(self)

        self.rid = 0
        self.url = radios[self.rid]["url"]
        self.media = instance.media_new(self.url)
        self.tmp_title = ''
        self.tmp_vol = 100

        # center window on screen after creation
        self._first_init = True
        self.mainwindow.bind("<Map>", self.center_window)

        # Connect Delete event to toplevel window
        self.mainwindow.protocol("WM_DELETE_WINDOW", self.app_quit)

        self.mainwindow.after(1000, self.task)

        widget = self.builder.get_object('label_rid')
        widget.configure(text=str(len(radios)) + " stations")

    def center_window(self, event):
        if self._first_init:
            toplevel = self.mainwindow
            height = toplevel.winfo_height()
            width = toplevel.winfo_width()
            x_coord = int(toplevel.winfo_screenwidth() / 2 - width / 2)
            y_coord = int(toplevel.winfo_screenheight() / 2 - height / 2)
            geom = f"{width}x{height}+{x_coord}+{y_coord}"
            toplevel.geometry(geom)
            self._first_init = False

    def setup_ttk_styles(self, widget=None):
        # ttk styles configuration
        self.style = style = ttk.Style()
        #optiondb = style.master
        style.theme_use(THEME)
        if THEME != 'default':
            with open(PROJECT_STYLE, "r") as file:
                code = file.read()
            exec(code) # Czy to da się zrobić inaczej np. za pomocą import, bez zmiany style.py?

    def run(self):
        self.mainwindow.iconify()
        self.mainwindow.update()
        self.mainwindow.deiconify()
        self.mainwindow.mainloop()  # forever

    def update_info(self):
        meta_list = ['name', 'stationuuid', 'url', 'homepage', 'favicon', 'country', 'countrycode',
                     'language', 'tags', 'bitrate', 'codec', 'votes', 'clickcount']

        meta_data = {
            'name': 'label_name',
            'country': 'label_country',
            'countrycode': 'label_countrycode',
            'language': 'label_language',
            'tags': 'label_tags',
            'bitrate': 'label_bitrate',
            'codec': 'label_codec',
            'votes': 'label_votes',
            'clickcount': 'label_clickcount',
        }

        for i in meta_data:
            widget = self.builder.get_object(meta_data[i])
            txt = radios[self.rid][i]
            if str(type(txt)) == "<class 'str'>":
                txt = txt.strip()
                txt = self.name_trim(txt)
            if str(type(txt)) == "<class 'str'>" and len(txt) > MAXL_NAME and i == 'name':
                txt = txt[:MAXL_NAME] + '...'
            if str(type(txt)) == "<class 'str'>" and len(txt) > (2*MAXL_NAME) and i == 'tags':
                txt = txt[:(2*MAXL_NAME)] + '...'
            if i == 'bitrate' and str(txt) == '0':
                txt = 'N/A'
            if str(txt) == '' and i != 'tags':
                txt = 'N/A'
            if i != 'name' and i != 'tags':
                txt = i[:1].upper() + i[1:] + ": " + str(txt)
            widget.configure(text=txt)

        widget = self.builder.get_object('label_rid')
        txt = "RadioID: " + str(self.rid)
        widget.configure(text=txt)

        widget = self.builder.get_object('button_homepage')
        if radios[self.rid]['homepage']:
            widget.configure(state="normal")
        else:
            widget.configure(state="disabled")

        # widget = self.builder.get_object('button_nowplaying')
        # if self.media.get_meta(12):
        #     widget.configure(state="normal")
        # else:
        #     widget.configure(state="disabled")

        widget = self.builder.get_object('entry_dialogbox')
        widget.configure(state="normal")
        widget.delete (0, last=len(widget.get()))
        widget.insert(0,self.url)
        widget.configure(state="readonly")

        fi_url = radios[self.rid]["favicon"]
        try:
            response = requests.get(fi_url)

            img = Image.open(BytesIO(response.content))
            size = 300, 300
            # img.thumbnail(size)
            img = img.resize(size)
            favicon = ImageTk.PhotoImage(img)

            widget = self.builder.get_object('label_icon')
            widget.configure(image=favicon)
            widget.image=favicon

            image = ColorThief(requests.get(fi_url, stream=True).raw)
            color = image.get_color(quality=1)
            hexc = '#'
            for n in color:
                hexc = hexc + str(hex(n))[2:]
            widget = self.builder.get_object('toplevel1')
            widget.configure(background=hexc)

        except:
            img = Image.open("ui/kakadu.png")
            favicon = ImageTk.PhotoImage(img)
            widget = self.builder.get_object('label_icon')
            widget.configure(image=favicon)
            widget.image=favicon
            widget = self.builder.get_object('toplevel1')
            widget.configure(background='#d8d043')

        # print("")
        # for i in meta_list:
        #     if radios[self.rid][i]: print(i + ":", radios[self.rid][i])

    def shuffle(self):
        self.rid = random.randrange(0, len(radios))
        self.url = radios[self.rid]["url"]

        self.update_info()

        r = rb.click_counter(radios[self.rid]["stationuuid"])

        self.fade_down()
        self.media = instance.media_new(self.url)
        player.set_media(self.media)
        player.audio_set_volume(0)
        # self.tmp_vol = 100
        player.play()
        self.fade_up()

        widget = self.builder.get_object('button_stop')
        widget.configure(state="normal")
        widget = self.builder.get_object('button_play')
        widget.configure(state="disabled")

    def play(self):
        self.media = instance.media_new(self.url)
        player.set_media(self.media)
        player.audio_set_volume(0)
        player.play()
        self.fade_up()
        widget = self.builder.get_object('button_stop')
        widget.configure(state="normal")
        widget = self.builder.get_object('button_play')
        widget.configure(state="disabled")
        self.update_info()

    def stop(self):
        self.fade_down()
        player.stop()
        widget = self.builder.get_object('button_stop')
        widget.configure(state="disabled")
        widget = self.builder.get_object('button_play')
        widget.configure(state="normal")

    def mute(self):
        if player.is_playing():
            player.audio_toggle_mute()
            if player.audio_get_mute() == 0:
                widget = self.builder.get_object('button_mute')
                widget.configure(text="UnMute")
            else:
                widget = self.builder.get_object('button_mute')
                widget.configure(text="Mute")

    def prev_station(self):
        if self.rid > 0:
            self.rid -= 1
        else:
            self.rid = len(radios) - 1
        self.url = radios[self.rid]["url"]

        self.update_info()

        r = rb.click_counter(radios[self.rid]["stationuuid"])

        self.fade_down()
        self.media = instance.media_new(self.url)
        player.set_media(self.media)
        player.audio_set_volume(0)
        player.play()
        self.fade_up()
        widget = self.builder.get_object('button_stop')
        widget.configure(state="normal")
        widget = self.builder.get_object('button_play')
        widget.configure(state="disabled")

    def next_station(self):
        if self.rid < len(radios) - 1:
            self.rid += 1
        else:
            self.rid = 0
        self.url = radios[self.rid]["url"]

        self.update_info()

        r = rb.click_counter(radios[self.rid]["stationuuid"])

        self.fade_down()
        self.media = instance.media_new(self.url)
        player.set_media(self.media)
        player.audio_set_volume(0)
        player.play()
        self.fade_up()
        widget = self.builder.get_object('button_stop')
        widget.configure(state="normal")
        widget = self.builder.get_object('button_play')
        widget.configure(state="disabled")

    def config(self, skip=None):
        if skip == None:
            self.clear_all()
            self.stations.run()
        widget = self.builder.get_object('treeview1')
        for i in range(len(radios)):
            column_values = (
                radios[i]["countrycode"],
                radios[i]["tags"],
                radios[i]["stationuuid"]
            )
            parent = ""
            txt = self.name_trim(radios[i]["name"])
            widget.insert(parent, tk.END, text=txt, values=column_values)

        label = "Radio stations (" + str(len(radios)) + ")"
        widget = self.builder.get_object('labelframe3')
        widget.configure(text=label)

    def name_trim(self, txt):
        txt = re.sub(r"_", " ", txt)
        txt = txt.strip()
        txt = re.sub(r"[\n\t]*", "", txt)
        return txt

    def on_row_select(self, event=None):
        widget = self.builder.get_object('treeview1')
        sel = widget.selection()
        if sel:
            item = sel[0]
            values = widget.item(item)
            # print(values['text'])
            # print(values['values'][0])
            # print(values['values'][2])
            sleep(0.01)
            self.play_uuid(values['values'][2])

    def play_uuid(self, radio_uuid):
        for i in range(len(radios)):
            stationuuid = radios[i]["stationuuid"]
            if stationuuid == radio_uuid:
                self.rid = i
                break

        self.url = radios[self.rid]["url"]

        self.update_info()

        r = rb.click_counter(radios[self.rid]["stationuuid"])

        self.fade_down()
        self.media = instance.media_new(self.url)
        player.set_media(self.media)
        player.audio_set_volume(0)
        # self.tmp_vol = 100
        player.play()
        self.fade_up()

        widget = self.builder.get_object('button_stop')
        widget.configure(state="normal")
        widget = self.builder.get_object('button_play')
        widget.configure(state="disabled")

    def clear_all(self, event=None):
        widget = self.builder.get_object('treeview1')
        for item in widget.get_children():
            widget.delete(item)

    def search_enter(self, event=None):
        self.search()

    def search(self):
        self.clear_all()
        r = 0
        widget = self.builder.get_object('entry_search')
        keys = widget.get().upper()
        if keys == '':
            self.config(skip=True)
            return
        keys = keys.replace(",", " ")
        keys = keys.split()

        widget = self.builder.get_object('treeview1')
        for i in range(len(radios)):
            name = radios[i]["name"].upper() + radios[i]["tags"].upper()
            s = 0
            for ik in keys:
                if name.find(ik) >= 0:
                    s += 1

            if s > len(keys) - 1:
                r += 1
                column_values = (
                    radios[i]["countrycode"],
                    radios[i]["tags"],
                    radios[i]["stationuuid"]
                )
                parent = ""
                # txt = radios[i]["name"]
                # txt = txt.strip()
                # txt = re.sub(r"[\n\t]*", "", txt)
                txt = self.name_trim(radios[i]["name"])
                widget.insert(parent, tk.END, text=txt, values=column_values)

        label = "Radio stations (" + str(r) + ")"
        widget = self.builder.get_object('labelframe3')
        widget.configure(text=label)

    def stationurl(self):
        self.dialog1.run()

    def open_about(self):
        self.about.run()

    def about_click(self, event):
        label = event.widget.cget("text")
        if label == "More info.":
            webbrowser.open('https://github.com/morgor/KakaduFM', new=2)
        elif label == "GPL3":
            webbrowser.open('https://www.gnu.org/licenses/gpl-3.0.html', new=2)
        else:
            webbrowser.open(label, new=2)

    def about_close(self):
        self.about.close()

    def nowplaying(self):
        song = self.media.get_meta(12)
        if song:
            widget = self.builder.get_object('entry_song')
            widget.configure(state="normal")
            widget.delete (0, last=len(widget.get()))
            widget.insert(0,song)
            widget.configure(state="readonly")
            self.dialog2.run()

    def homepage(self):
        s = radios[self.rid]["homepage"]
        if s:
            webbrowser.open(s, new=2)

    def fade_down(self):
        scale = self.builder.get_object("scale_vol")
        v1 = player.audio_get_volume()
        self.tmp_vol = v1
        for v in range(v1, -1, -2):
            player.audio_set_volume(v)
            sleep(0.01)
        player.audio_set_volume(0)
        scale.set(0)

    def fade_up(self):
        scale = self.builder.get_object("scale_vol")
        v0 = 0
        v1 = self.tmp_vol
        for v in range(0, v1, +2):
            player.audio_set_volume(v)
            sleep(0.01)
        player.audio_set_volume(v1)
        scale.set(v1)

    def search_song(self):
        s = self.media.get_meta(12)
        if s:
            webbrowser.open(SEARCH_ENGINE + urllib.parse.quote(s), new=2)

    def open_radiobrowser(self):
        url_rb = 'https://www.radio-browser.info/history/'
        uuid = radios[self.rid]["stationuuid"]
        webbrowser.open(url_rb + uuid, new=2)

    def vol_up(self):
        scale = self.builder.get_object("scale_vol")
        v0 = player.audio_get_volume()
        v = v0 + 10
        if v > 100:
            v = 100
        for i in range(v0, v + 1):
            sleep(0.01)
            player.audio_set_volume(i)
            scale.set(i)
        self.tmp_vol = player.audio_get_volume()

    def vol_down(self):
        scale = self.builder.get_object("scale_vol")
        v0 = player.audio_get_volume()
        v = v0 - 10
        if v < 0:
            v = 0
        for i in range(v0, v - 1, -1):
            sleep(0.01)
            player.audio_set_volume(i)
            scale.set(i)
        self.tmp_vol = player.audio_get_volume()

    def scale_volume(self, event):
        # print(int(float(event)))
        scale = self.builder.get_object("scale_vol")
        player.audio_set_volume(int(scale.get()))

    def song_history(self):
        self.history.run()

    def task(self):
        s = self.media.get_meta(12)
        if s and self.tmp_title != s and s != '':
            date_time = datetime.fromtimestamp(calendar.timegm(time.gmtime()))
            str_date_time = date_time.strftime("%Y-%m-%d %H:%M:%S >> ")
            # print(str_date_time, s)
            widget = self.builder.get_object('text_history')
            line = str_date_time + s + '\n'
            widget.configure(state="normal")
            widget.insert(tk.END, line)
            widget.configure(state="disabled")
            self.tmp_title = s
        widget = self.builder.get_object('label_volume')
        txt_vol = "Vol: " + str(player.audio_get_volume())
        widget.configure(text=txt_vol)
        self.mainwindow.after(1000, self.task)  # reschedule event in 2 seconds

    def app_quit(self, event=None):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.fade_down()
            player.stop()
            self.mainwindow.destroy()

if __name__ == "__main__":
    app = GuiApp()
    app.run()
