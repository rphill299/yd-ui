import tkinter as tk
from tkinter import ttk, messagebox
import threading
import util

def get_and_clean_url(url_entry) :
    url = url_entry.get()
    if not url.strip():
        messagebox.showerror("Error", "Please enter a YouTube URL first.")
        return -1
    return url[-11:]

def run(splash) :
    def format_label(f):
        format = f.get('format')
        format_id = f.get('format_id')
        ext = f.get('ext', '???')
        vcodec = f.get('vcodec')
        acodec = f.get('acodec')
        resolution = f.get('resolution')
        abr = f.get('abr')  # average bitrate in kbps
        tbr = f.get('tbr')  # total bitrate

        if vcodec and vcodec != 'none':
            # Video format
            return f"{format_id} - {resolution.split('x')[1]}p {ext}\t({vcodec})"
        else:
            # Audio format
            return f"{format} - {ext}"

    def click_load():
        url = get_and_clean_url(url_entry)
        if url == -1 : return

        try:
            clear_listboxes()

            audio, video, av = util.get_all_formats(url)

            format_lists['audio'].clear()
            format_lists['video'].clear()
            format_lists['av'].clear()

            listbox_map.clear()
            for f in audio:
                label = format_label(f)
                format_lists['audio'].append(label)
                listbox_map[label] = f['format_id']
            for f in video:
                label = format_label(f)
                format_lists['video'].append(label)
                listbox_map[label] = f['format_id']
            for f in av:
                label = format_label(f)
                format_lists['av'].append(label)
                listbox_map[label] = f['format_id']

            populate_listboxes()

        except Exception as e:
            messagebox.showerror("Error loading formats", str(e))

    def clear_listboxes() :
        audio_listbox.delete(0, tk.END)
        video_listbox.delete(0, tk.END)
        av_listbox.delete(0, tk.END)

    def populate_listboxes() :
        clear_listboxes
        for label in format_lists['audio']:
            audio_listbox.insert(tk.END, label)

        for label in format_lists['video']:
            video_listbox.insert(tk.END, label)

        for label in format_lists['av']:
            av_listbox.insert(tk.END, label)

    def update_listbox():
        selected_type = format_type_var.get()

        if selected_type == 'combine' :
            merged_frame.pack_forget()
            combine_frame.pack(pady=10)
        elif selected_type == 'merged' :
            combine_frame.pack_forget()
            merged_frame.pack(pady=10)

    def click_download() :
        url = get_and_clean_url(url_entry)
        if url == -1 : return

        try:
            selected_type = format_type_var.get()
            if selected_type == 'combine' :
                audio_index = audio_listbox.curselection()
                video_index = video_listbox.curselection()
                if not audio_index:
                    messagebox.showwarning("No Audio Format", "Please select an audio format to download.")
                    return
                if not video_index:
                    messagebox.showwarning("No Video Format", "Please select a video format to download.")
                    return

                audio_label = audio_listbox.get(audio_index[0])
                audio_id = listbox_map.get(audio_label)
                video_label = video_listbox.get(video_index[0])
                video_id = listbox_map.get(video_label)

            elif selected_type == 'merged' :
                audio_index = av_listbox.curselection()
                video_index = audio_index
                if not audio_index :
                    messagebox.showwarning("No Audiovisual Format", "Please select an audiovisual format to download.")
                    return

                audio_label = av_listbox.get(audio_index[0])
                audio_id = listbox_map.get(audio_label)
                video_id = audio_id

            print(f'Selected {audio_id} audio format and {video_id} video format.')

            def run_download():
                try:
                    util.download(url, audio_id, video_id)
                except Exception as e:
                    messagebox.showerror("Download failed", str(e))

            threading.Thread(target=run_download, daemon=True).start()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_exit():
        # if messagebox.askokcancel("Exit", "Do you really want to quit?"):
            root.destroy()  # or root.quit()

    # --- GUI Setup ---
    splash.destroy()
    root = tk.Tk()
    root.title("YouTube Downloader")
    root.geometry("1000x1000")
    root.protocol("WM_DELETE_WINDOW", on_exit) # call on_exit when delete window

    # URL Entry

    label_text =  "YouTube URL (eg. b89CnP0Iq30):"
    entry = tk.Entry(root, width=30, readonlybackground=root.cget("bg"), borderwidth=0)
    entry.insert(0, label_text)
    entry.config(state='readonly')
    entry.pack()

    url_entry = tk.Entry(root, width=70)
    url_entry.pack()

    # Radio Buttons
    format_type_var = tk.StringVar(value='combine')
    # format_type_var = tk.StringVar(value=None)
    radio_frame = tk.Frame(root)
    radio_frame.pack()
    tk.Radiobutton(radio_frame, text="Combine (Audio+Video)", variable=format_type_var, value="combine", command=update_listbox).pack(side="left")
    tk.Radiobutton(radio_frame, text="Merged (Audiovisual)", variable=format_type_var, value="merged", command=update_listbox).pack(side="right")

    # Load Formats Button
    tk.Button(root, text="Load Formats", command=click_load).pack(pady=5)

    # listbox frame holds 1 or 2 listboxes
    listbox_frame = tk.Frame(root)
    listbox_frame.pack()

    # frame for combining audio+video
    combine_frame = tk.Frame(listbox_frame)

    # combined audio and video frames
    audio_frame = tk.Frame(combine_frame)
    audio_scrollbar = tk.Scrollbar(audio_frame, orient=tk.VERTICAL)
    audio_listbox = tk.Listbox(audio_frame, height=10, width=30, yscrollcommand=audio_scrollbar.set, selectmode=tk.SINGLE, exportselection=False)
    audio_scrollbar.config(command=audio_listbox.yview)
    audio_listbox.pack(side="left", fill="y")
    audio_scrollbar.pack(side="right", fill="y")
    audio_frame.grid(row=0, column=0, padx=20)

    video_frame = tk.Frame(combine_frame)
    video_scrollbar = tk.Scrollbar(video_frame, orient=tk.VERTICAL)
    video_listbox = tk.Listbox(video_frame, height=10, width=30, yscrollcommand=video_scrollbar.set, selectmode=tk.SINGLE, exportselection=False)
    video_scrollbar.config(command=video_listbox.yview)
    video_listbox.pack(side="left", fill="y")
    video_scrollbar.pack(side="right", fill="y")
    video_frame.grid(row=0, column=1, padx=20)

    # frame for merged
    merged_frame = tk.Frame(listbox_frame)
    av_scrollbar = tk.Scrollbar(merged_frame, orient=tk.VERTICAL)
    av_listbox = tk.Listbox(merged_frame, yscrollcommand=av_scrollbar.set, height=10, width=65, selectmode=tk.SINGLE, exportselection=False)
    av_scrollbar.config(command=av_listbox.yview)
    av_listbox.pack(side="left", fill="y", padx=10)
    av_scrollbar.pack(side="right", fill="y")

    # Download + Quit buttons
    tk.Button(root, text="Download", command=click_download).pack(pady=10)
    tk.Button(root, text="Quit", command=on_exit).pack()

    # --- Data Structures ---
    listbox_map = {}  # Maps label -> format_id
    format_lists = {
        'audio': [],
        'video': [],
        'av': []
    }

    update_listbox()
    root.mainloop()

if __name__ == '__main__' :
    run()
    # example yt video : b89CnP0Iq30
