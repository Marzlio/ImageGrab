import time
import os
import random
import logging
import threading
from PIL import Image
from moviepy.editor import VideoFileClip
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configuration class
class Config:
    def __init__(self, environment='Test'):
        if environment == 'Live':
            self.folder_to_monitor = 'V:\\Videos'
            self.main_screenshots_dir = 'V:\\Screenshots'
        else:
            self.folder_to_monitor = 'Videos'
            self.main_screenshots_dir = 'Screenshots'

        # Common configurations
        self.target_size = (420, 560)
        self.number_of_images = 20
        self.gif_speed = 100
        self.start_time = 300
        self.number_of_gif_images = 10
        self.create_gif_enabled = False
        self.delete_original = True
        self.supported_file_types = ['.mp4', '.avi', '.mov']
        self.file_ready_wait = 20  # Wait time in seconds before processing a new file
        self.max_retries = 3  # Maximum number of retries for processing a file
        self.retry_wait = 10  # Wait time in seconds before retrying
        self.max_concurrent_tasks = 5  # Maximum number of videos to process at the same time


def is_file_accessible(filepath, mode='r'):
    try:
        with open(filepath, mode):
            return True
    except IOError:
        return False
    
def extract_frames(movie_path, config, resize_image=True):
    clip = None
    try:
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

        return True, images, movie_name
    except IOError as e:
        logging.error(f"IOError while processing {movie_path}: {e}")
        return False, [], movie_name
    except ValueError as e:
        logging.error(f"ValueError in processing {movie_path}: {e}")
        return False, [], movie_name
    except Exception as e:
        logging.error(f"Unexpected error extracting frames from {movie_path}: {e}")
        return False, [], movie_name
    finally:
        if clip:
            clip.close()

def create_gif(images, movie_name, config):
    try:
        frames = [Image.open(image) for image in images[:config.number_of_gif_images]]
        gif_path = os.path.join(config.main_screenshots_dir, f"{movie_name}.gif")
        frames[0].save(gif_path, format='GIF', append_images=frames[1:], save_all=True, duration=config.gif_speed, loop=0)
    except Exception as e:
        logging.error(f"Error creating GIF for {movie_name}: {e}")

class NewFileHandler(FileSystemEventHandler):
    def __init__(self, config):
        self.config = config
        self.file_queue = Queue()
        self.init_workers()

    def init_workers(self):
        for _ in range(self.config.max_concurrent_tasks):
            worker = threading.Thread(target=self.process_files)
            worker.daemon = True
            worker.start()

    def on_created(self, event):
        if not event.is_directory and any(event.src_path.endswith(ext) for ext in self.config.supported_file_types):
            # Add a delay to ensure the file is completely written
            time.sleep(2)
            if os.path.getsize(event.src_path) > 0:  # Check if file is non-empty
                self.file_queue.put(event.src_path)

    def process_files(self):
        while True:
            file_path = self.file_queue.get()
            self.handle_new_video(file_path)
            self.file_queue.task_done()

    def handle_new_video(self, file_path):
        attempt = 0
        success = False

        while attempt < self.config.max_retries and not success:
            if is_file_accessible(file_path, 'r'):
                logging.info(f"Attempt {attempt+1}: Processing video {file_path}")
                time.sleep(self.config.file_ready_wait)
                success, images, movie_name = extract_frames(file_path, self.config, resize_image=False)

                if success:
                    if self.config.create_gif_enabled:
                        create_gif(images, movie_name, self.config)

                    if self.config.delete_original:
                        os.remove(file_path)
                        logging.info(f"Deleted original video file: {file_path}")
                else:
                    logging.error(f"Attempt {attempt+1} failed for {file_path}. Retrying...")
                    time.sleep(self.config.retry_wait)
            else:
                logging.info(f"File {file_path} is not accessible, waiting before retry...")
                time.sleep(self.config.retry_wait)

            attempt += 1

        if not success:
            logging.error(f"All retries failed for {file_path}. File not processed.")

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
config = Config(environment='Live')  # Change to 'Live' for live environment

# Start monitoring
monitor_folder(config.folder_to_monitor, config)