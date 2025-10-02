🖼️ Image Resizer CLI

A simple yet powerful Python command-line tool to batch resize, convert, and optimize images.
Supports multiple formats, recursive folder scanning, metadata stripping, and aspect ratio handling.

📂 Project Structure
TASK7/
├── .venv/                  # Virtual environment
├── imgs/                   # Original images
│   ├── download (1).jpeg
│   ├── download (2).jpeg
│   └── ...
├── resized/                # Output folder for resized images
│   ├── download (1)_1280x1280.jpeg
│   ├── download (2)_1280x1280.jpeg
│   └── ...
├── image_resizer.py        # Main Python script
├── requirements.txt        # Python dependencies
└── .gitignore

⚙️ Installation

Clone this repository:

git clone <your-repo-url>
cd TASK7


Create and activate a virtual environment:

python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate      # Windows


Install dependencies:

pip install -r requirements.txt

🚀 Usage

Basic command:

python image_resizer.py imgs --size 1280x1280

Options
Option	Description	Example
source	Source folder containing images	imgs
--output	Output folder (default: resized/)	--output out_folder
--size	Target size in WIDTHxHEIGHT format	--size 800x600
--exact	Resize to exact size (ignore aspect ratio)	--exact
--keep-aspect	Keep aspect ratio (contain within size)	--keep-aspect
--upscale	Allow upscaling smaller images	--upscale
--no-upscale	Disallow upscaling	--no-upscale
--ext	Force output format (jpg, png, webp, etc.)	--ext webp
--suffix	Add custom filename suffix (default: _WIDTHxHEIGHT)	--suffix _resized
--include	Filter by extensions	--include jpg png
--recursive / --no-recursive	Scan subfolders or not	--no-recursive
--overwrite	Overwrite existing output files	--overwrite
--quality	Quality for lossy formats (JPEG/WebP)	--quality 90
--strip-metadata / --preserve-metadata	Remove or preserve EXIF metadata	--strip-metadata
📌 Examples

Resize all images in imgs/ to 1280x1280 (default, keeping aspect ratio):

python image_resizer.py imgs


Convert images to WebP and save in output/:

python image_resizer.py imgs --ext webp --output output


Resize to exact 640x480, overwrite existing files:

python image_resizer.py imgs --size 640x480 --exact --overwrite


Strip metadata and optimize PNG images:

python image_resizer.py imgs --ext png --strip-metadata --png-optimize

📦 Requirements

Python 3.8+

Pillow

Install with:

pip install pillow

✨ Features

✅ Batch image resizing

✅ Supports JPEG, PNG, WebP, BMP, TIFF, GIF

✅ Metadata stripping for privacy

✅ Preserve or ignore aspect ratio

✅ Lossless optimization for PNG

✅ Adjustable quality for JPEG/WebP

✅ Recursive folder scanning
