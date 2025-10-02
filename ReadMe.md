# ImageResizerTool

A simple Python tool to resize images using the Pillow library.

## Files

- `image_resizer.py`: Main script to resize images. Run this file to use the tool.
- `requirements.txt`: Contains package requirements (mainly `Pillow`). Install dependencies with:
  ```bash
  pip install -r requirements.txt
  ```
- `imgs/`: Directory for input images and output results.

## Usage

1. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
2. Place images in the `imgs/` folder.
3. Run the script:
    ```bash
    python image_resizer.py
    ```
4. Resized images will be saved in the specified output directory (update the script if needed).

## Dependencies

- [Pillow](https://python-pillow.org/): Python Imaging Library.

## Notes

- Customize the script as needed to change input/output directories or resizing options.
- Make sure your images are in the correct folder (`imgs/`) before running the tool.
