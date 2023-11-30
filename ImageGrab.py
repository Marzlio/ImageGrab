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
    def __init__(self, environment='Test'):
        if environment == 'Live':
            self.folder_to_monitor = 'V:\\Videos'
            self.main_screenshots_dir = 'V:\\screenshots'
        else:
            self.folder_to_monitor = 'Videos'
            self.main_screenshots_dir = 'screenshots'

        # Common configurations
        self.target_size = (420, 560)
        self.number_of_images = 20
        self.gif_speed = 100
        self.start_time = 300
        self.number_of_gif_images = 10
        self.create_gif_enabled = True
        self.delete_original = False
        self.supported_file_types = ['.mp4', '.avi', '.mov']
        self.file_ready_wait = 20  # Wait time in seconds

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
    def __init__(self, config):
        self.config = config

    def on_created(self, event):
        if not event.is_directory and any(event.src_path.endswith(ext) for ext in self.config.supported_file_types):
            self.handle_new_video(event.src_path)

    def handle_new_video(self, file_path):
        logging.info(f"New video detected: {file_path}")
        time.sleep(self.config.file_ready_wait)
        try:
            images, movie_name = extract_frames(file_path, self.config, resize_image=False)
            if self.config.create_gif_enabled:
                create_gif(images, movie_name, self.config)
            
            if self.config.delete_original:
                os.remove(file_path)
                logging.info(f"Deleted original video file: {file_path}")

        except Exception as e:
            logging.error(f"Error processing video {file_path}: {e}")

def monitor_folder(path_to_watch, config):
    logging.basicConfig(level=logging.INFO)
    event_handler = NewFileHandler(config)
    observer = Observer()
    observer.schedule(event_handler, path_to_watch, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

# Configurations for test or live environment
config = Config(environment='Test')  # Change to 'Live' for live environment

# Start monitoring
monitor_folder(config.folder_to_monitor, config)
