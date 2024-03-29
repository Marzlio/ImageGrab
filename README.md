# ImageGrab: Video Frame Extractor and GIF Creator

ImageGrab is a Python script designed to automatically monitor a specified folder for new video files, extract frames, create screenshots, and generate GIFs from these videos.

## Features

- Monitors a designated folder for new video files.
- Extracts frames from videos, saving them as screenshots.
- Creates GIFs from selected extracted frames.
- Supports multiple video formats including .mp4, .avi, .mov.
- Configurable settings for customizing screenshot size, number of frames, GIF speed, and more.
- Options for live or test environment setups.
- Automated deletion of original video files after processing (configurable).
- Robust error handling and retry mechanism for failed processes.
- Monitors a designated folder for new video files, with a focus on handling large files efficiently.
- Enhanced retry mechanism that checks file accessibility to ensure files are fully written and not locked by other processes before processing.

## Prerequisites

Before you begin, ensure you have:
- Python 3.x installed on your system.
- Installed the following Python packages: `moviepy`, `Pillow`, `watchdog`.

You can install these packages using pip:
```bash
pip install moviepy Pillow watchdog
```

## Installation

Clone this repository:
```bash
git clone https://github.com/Marzlio/ImageGrab.git

```
Navigate to the cloned repository:
```bash
cd imagegrab
```

## Configuration
Modify the Config class in the ImageGrab script to suit your needs:

- `folder_to_monitor`: The path of the folder to monitor for new video files.
- `main_screenshots_dir`: The directory where screenshots and GIFs will be saved.
- `target_size`: The desired size for screenshots (width, height).
- `number_of_images`: The number of frames to extract per video.
- `gif_speed`: The speed of the GIF in milliseconds.
- `start_time`: The time offset for starting frame extraction (in seconds).
- `number_of_gif_images`: The number of images to use in the GIF.
- `create_gif_enabled`: Enable or disable GIF creation.
- `delete_original`: Set to True to delete original video files after processing.
- `file_ready_wait`: Wait time before processing a new file.
- `max_retries`: Maximum number of retries for processing a file.
- `retry_wait`: Wait time before retrying a failed process.

## Usage
- Copy video files into the `folder_to_monitor`. Ensure that files are fully copied and not open in any other application before the script processes them.
- Run ImageGrab:
    ```bash
    python ImageGrab.py
    ```
- Ensure that the script name matches the file name in your repository.
- Locating Images and GIFs: The extracted images and GIFs will be located in the directory specified by main_screenshots_dir. They are organized in subfolders named after the respective video files.

## Customization Options
The behavior of the script can be customized through the Config class:

- Folder Monitoring: Set the folder to be monitored for new video files.
- Image and GIF Storage: Specify the directory for storing all screenshots and GIFs.
- Image Size and Quantity: Control the dimensions and number of frames extracted from each video.
- GIF Creation: Adjust the GIF speed and frame count.
- Start Time for Frame Extraction: Set a delay to skip the initial part of the video.
- Environment Setup: Choose between 'Live' and 'Test' environments for different paths.
- Concurrent Processing: Manage file processing in parallel threads.


## Contributing
Contributions to this project are welcome. Please follow the standard fork and pull request workflow.

## License
This project is licensed under the MIT License.