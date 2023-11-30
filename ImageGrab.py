import time
import os
import random
import logging
from PIL import Image
from moviepy.editor import VideoFileClip
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configuration class
class Config:
    def __init__(self):
        self.folder_to_monitor = 'V:\\Videos'
        self.main_screenshots_dir = 'V:\\screenshots'
        self.target_size = (420, 560)
        self.number_of_images = 20
        self.gif_speed = 100
        self.start_time = 300
        self.number_of_gif_images = 10
        self.create_gif_enabled = True
        self.supported_file_types = ['.mp4', '.avi', '.mov']

config = Config()

def extract_frames(movie_path, config, resize_image=True):
    clip = VideoFileClip(movie_path)
    duration = clip.duration

    start_time = config.start_time if config.start_time < duration else 0
    timestamps = sorted(random.sample(range(start_time, int(duration)), config.number_of_images))
    movie_name = os.path.splitext(os.path.basename(movie_path))[0]
    movie_screenshots_dir = os.path.join(config.main_screenshots_dir, movie_name)
    if not os.path.exists(movie_screenshots_dir):
        os.makedirs(movie_screenshots_dir)

    images = []
    for i, timestamp in enumerate(timestamps):
        frame = clip.get_frame(timestamp)
        img = Image.fromarray(frame)
        if resize_image:
            img.thumbnail(config.target_size, Image.ANTIALIAS)

        save_path = os.path.join(movie_screenshots_dir, f"{movie_name}_{i+1}.jpg")
        img.save(save_path)
        images.append(save_path)

    return images, movie_name

def create_gif(images, movie_name, config):
    frames = [Image.open(image) for image in images[:config.number_of_gif_images]]
    gif_path = os.path.join(config.main_screenshots_dir, f"{movie_name}.gif")
    frames[0].save(gif_path, format='GIF', append_images=frames[1:], save_all=True, duration=config.gif_speed, loop=0)

class NewFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and any(event.src_path.endswith(ext) for ext in config.supported_file_types):
            self.handle_new_video(event.src_path)

    def handle_new_video(self, file_path):
        logging.info(f"New video detected: {file_path}")
        try:
            images, movie_name = extract_frames(file_path, config, resize_image=False)
            if config.create_gif_enabled:
                create_gif(images, movie_name, config)
        except Exception as e:
            logging.error(f"Error processing video {file_path}: {e}")

def monitor_folder(path_to_watch):
    logging.basicConfig(level=logging.INFO)
    event_handler = NewFileHandler()
    observer = Observer()
    observer.schedule(event_handler, path_to_watch, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

monitor_folder(config.folder_to_monitor)