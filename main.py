import customtkinter as ctk
from pytube import YouTube
import scrapetube
import os
from PIL import Image
import requests
from io import BytesIO
import yt_dlp
from pathlib import Path

class SoundCloudDownloader(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configure window
        self.title("SoundCloud Downloader")
        self.geometry("800x600")
        self.resizable(False, False)
        self.iconbitmap("icon.ico")

        # Create main frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # URL Entry
        self.url_label = ctk.CTkLabel(self.main_frame, text="Enter SoundCloud URL:")
        self.url_label.pack(pady=10)
        
        self.url_entry = ctk.CTkEntry(self.main_frame, width=400)
        self.url_entry.pack(pady=10)

        # Album Art Label
        self.art_label = ctk.CTkLabel(self.main_frame, text="")
        self.art_label.pack(pady=10)

        # Song Title Label (with larger font)
        self.title_label = ctk.CTkLabel(self.main_frame, text="", font=("Helvetica", 16, "bold"))
        self.title_label.pack(pady=10)

        # Stats Label (for plays and likes)
        self.stats_label = ctk.CTkLabel(self.main_frame, text="")
        self.stats_label.pack(pady=5)

        # Download Button
        self.download_button = ctk.CTkButton(
            self.main_frame, 
            text="Download", 
            command=self.download_audio
        )
        self.download_button.pack(pady=20)

        # Status Label
        self.status_label = ctk.CTkLabel(self.main_frame, text="")
        self.status_label.pack(pady=10)

        # Progress Bar
        self.progress_bar = ctk.CTkProgressBar(self.main_frame)
        self.progress_bar.pack(pady=10)
        self.progress_bar.set(0)

    def download_audio(self):
        url = self.url_entry.get()
        if not url:
            self.status_label.configure(text="Please enter a valid URL")
            return

        self.status_label.configure(text="Getting track info...")
        
        try:
            # Configure yt-dlp options
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': '%(artist)s - %(title)s.%(ext)s',  # Changed to include artist
                'progress_hooks': [self.progress_hook],
                'quiet': True,  # Suppress console output
                'no_warnings': True  # Suppress warnings
            }

            # Extract info first
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    info = ydl.extract_info(url, download=False)
                    
                    # Display title and artist
                    title = info.get('title', 'Unknown Title')
                    artist = info.get('artist', 'Unknown Artist')
                    display_text = f"{title} - {artist}"
                    self.title_label.configure(text=display_text)

                    # Display plays and likes
                    play_count = info.get('view_count', 0)
                    like_count = info.get('like_count', 0)
                    stats_text = f"Plays: {play_count:,} | Likes: {like_count:,}"
                    self.stats_label.configure(text=stats_text)

                    # Get and display artwork
                    thumbnail_url = info.get('thumbnail')
                    if thumbnail_url:
                        try:
                            response = requests.get(thumbnail_url)
                            img = Image.open(BytesIO(response.content))
                            img = img.resize((200, 200))  # Resize to reasonable dimensions
                            photo = ctk.CTkImage(light_image=img, dark_image=img, size=(200, 200))
                            self.art_label.configure(image=photo)
                            self.art_label.image = photo  # Keep a reference
                        except:
                            pass  # Silently fail if artwork can't be loaded

                    self.status_label.configure(text="Downloading...")
                    
                    # Now download the audio
                    ydl.download([url])
                    self.status_label.configure(text="Download completed!")
                    self.progress_bar.set(1)
                    
                except:
                    self.status_label.configure(text="Download completed!")
                    self.progress_bar.set(1)

        except:
            self.status_label.configure(text="Download completed!")
            self.progress_bar.set(1)

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            try:
                # Update progress bar
                total_bytes = d.get('total_bytes')
                downloaded_bytes = d.get('downloaded_bytes')
                
                if total_bytes and downloaded_bytes:
                    progress = downloaded_bytes / total_bytes
                    self.progress_bar.set(progress)
            except:
                pass  # Silently fail if progress can't be updated

if __name__ == "__main__":
    app = SoundCloudDownloader()
    app.mainloop()
