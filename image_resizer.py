#!/usr/bin/env python3

import argparse
import os
import sys
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

from PIL import Image, ImageOps


SUPPORTED_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff", ".gif"}


def parse_size(size_text: str) -> Tuple[int, int]:
	parts = size_text.lower().replace("x", " ").replace(",", " ").split()
	if len(parts) != 2:
		raise argparse.ArgumentTypeError("Size must be WIDTHxHEIGHT, e.g., 1280x1280")
	try:
		w = int(parts[0])
		h = int(parts[1])
		if w <= 0 or h <= 0:
			raise ValueError
		return w, h
	except ValueError:
		raise argparse.ArgumentTypeError("Size must be positive integers, e.g., 1280x1280")


def discover_images(root: Path, recursive: bool, include_exts: Optional[Iterable[str]] = None) -> List[Path]:
	include_exts = {e.lower() for e in include_exts} if include_exts else SUPPORTED_EXTS
	images: List[Path] = []
	if recursive:
		for dirpath, _dirnames, filenames in os.walk(root):
			for name in filenames:
				ext = Path(name).suffix.lower()
				if ext in include_exts:
					images.append(Path(dirpath) / name)
	else:
		for name in os.listdir(root):
			p = root / name
			if p.is_file() and p.suffix.lower() in include_exts:
				images.append(p)
	return images


def ensure_output_dir(path: Path) -> None:
	path.mkdir(parents=True, exist_ok=True)


def derive_output_path(src: Path, src_root: Path, out_root: Path, suffix: Optional[str], force_ext: Optional[str]) -> Path:
	rel = src.relative_to(src_root)
	base = rel.stem + (suffix or "")
	ext = force_ext.lower() if force_ext else rel.suffix.lower()
	if not ext.startswith("."):
		ext = "." + ext
	return (out_root / rel.parent / (base + ext)).resolve()


def human_readable_size(size: Tuple[int, int]) -> str:
	return f"{size[0]}x{size[1]}"


def should_resize(current: Tuple[int, int], target: Tuple[int, int], allow_upscale: bool) -> bool:
	cw, ch = current
	tw, th = target
	if not allow_upscale and (cw <= tw and ch <= th):
		return False
	return True


def resize_image_keep_aspect(img: Image.Image, target: Tuple[int, int]) -> Image.Image:
	return ImageOps.contain(img, target, method=Image.LANCZOS)


def strip_metadata(img: Image.Image) -> Image.Image:
	data = list(img.getdata())
	clean = Image.new(img.mode, img.size)
	clean.putdata(data)
	return clean


def save_image(img: Image.Image, dest: Path, fmt: Optional[str], quality: int, optimize: bool) -> None:
	dest.parent.mkdir(parents=True, exist_ok=True)
	params = {}
	fmt_upper = None
	if fmt:
		fmt_upper = fmt.upper().lstrip(".")
		if fmt_upper == "JPG":
			fmt_upper = "JPEG"
	if (fmt_upper or dest.suffix.lower() in {".jpg", ".jpeg", ".webp"}):
		params["quality"] = int(quality)
	if (fmt_upper or dest.suffix.lower() in {".png"}):
		params["optimize"] = bool(optimize)
	if fmt_upper:
		img.save(dest, format=fmt_upper, **params)
	else:
		img.save(dest, **params)


def process_image(
	src: Path,
	src_root: Path,
	out_root: Path,
	target_size: Tuple[int, int],
	keep_aspect: bool,
	allow_upscale: bool,
	suffix: Optional[str],
	force_ext: Optional[str],
	strip_meta: bool,
	overwrite: bool,
	quality: int,
	optimize: bool,
) -> Optional[Path]:
	try:
		with Image.open(src) as im:
			mode = im.mode
			if mode not in ("RGB", "RGBA"):
				if mode in ("P", "LA", "L"):
					im = im.convert("RGBA" if "A" in mode else "RGB")
				else:
					im = im.convert("RGB")

			current_size = im.size

			if keep_aspect:
				if should_resize(current_size, target_size, allow_upscale):
					resized = resize_image_keep_aspect(im, target_size)
				else:
					resized = im.copy()
			else:
				# exact resize requested; may upscale
				resized = im.resize(target_size, Image.LANCZOS)

			if strip_meta:
				resized = strip_metadata(resized)

		dest = derive_output_path(src, src_root, out_root, suffix, force_ext)
		if dest.exists() and not overwrite:
			return None
		save_image(resized, dest, force_ext, quality=quality, optimize=optimize)
		return dest
	except Exception as exc:
		print(f"Failed to process {src}: {exc}", file=sys.stderr)
		return None


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
	parser = argparse.ArgumentParser(
		description="Batch resize and convert images",
		formatter_class=argparse.ArgumentDefaultsHelpFormatter,
	)
	parser.add_argument("source", type=Path, help="Source folder containing images")
	parser.add_argument("--output", type=Path, default=None, help="Output folder (default: <script_dir>/resized)")
	parser.add_argument("--size", type=parse_size, default=(1280, 1280), help="Target size as WIDTHxHEIGHT")
	# Defaults: exact resize ON, upscaling ON
	parser.add_argument("--exact", action="store_true", help="Resize to exact size (ignore aspect ratio)")
	parser.add_argument("--keep-aspect", dest="keep_aspect_flag", action="store_true", help="Keep aspect ratio (contain within size)")
	parser.add_argument("--upscale", action="store_true", help="Allow upscaling smaller images")
	parser.add_argument("--no-upscale", dest="no_upscale", action="store_true", help="Disallow upscaling")
	parser.add_argument("--ext", type=str, default=None, help="Force output extension/format (e.g., webp, jpg, png)")
	parser.add_argument("--suffix", type=str, default="_auto", help="Filename suffix; '_auto' becomes _<WxH>")
	parser.add_argument("--include", type=str, nargs="*", default=None, help="Extensions to include (e.g., jpg png webp)")
	parser.add_argument("--recursive", action="store_true", default=True, help="Recurse into subfolders")
	parser.add_argument("--no-recursive", dest="recursive", action="store_false", help="Do not recurse into subfolders")
	parser.add_argument("--overwrite", action="store_true", help="Overwrite existing output files")
	parser.add_argument("--quality", type=int, default=85, help="Quality for lossy formats (JPEG/WebP)")
	parser.add_argument("--png-optimize", action="store_true", default=True, help="Optimize PNG output")
	parser.add_argument("--no-png-optimize", dest="png_optimize", action="store_false", help="Disable PNG optimize")
	parser.add_argument("--strip-metadata", action="store_true", default=True, help="Strip EXIF/metadata")
	parser.add_argument("--preserve-metadata", dest="strip_metadata", action="store_false", help="Preserve metadata")

	# Set default behavior: exact resize ON, upscale ON
	parser.set_defaults(exact=True)
	parser.set_defaults(upscale=True)
	return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
	args = parse_args(argv)
	src_root = args.source.resolve()
	if not src_root.exists() or not src_root.is_dir():
		print(f"Source folder not found: {src_root}", file=sys.stderr)
		return 2
	# Default output next to the script (Task7/resized)
	default_out = (Path(__file__).resolve().parent / "resized").resolve()
	out_root = args.output.resolve() if args.output else default_out
	ensure_output_dir(out_root)

	include_exts = None
	if args.include:
		include_exts = {("." + e.lower().lstrip(".")) for e in args.include}

	# Determine keep_aspect and upscale from flags
	keep_aspect = bool(getattr(args, "keep_aspect_flag", False))
	if args.exact and keep_aspect:
		# If both set, favor keep-aspect when requested explicitly
		args.exact = False
		keep_aspect = True

	upscale = True
	if getattr(args, "no_upscale", False):
		upscale = False
	elif getattr(args, "upscale", False):
		upscale = True

	# Compute suffix
	w, h = args.size
	suffix = args.suffix
	if suffix == "_auto":
		suffix = f"_{w}x{h}"

	images = discover_images(src_root, recursive=args.recursive, include_exts=include_exts)
	if not images:
		print("No images found.")
		return 0

	count = 0
	for img_path in images:
		result = process_image(
			src=img_path,
			src_root=src_root,
			out_root=out_root,
			target_size=(w, h),
			keep_aspect=keep_aspect if keep_aspect else not args.exact and True,
			allow_upscale=upscale,
			suffix=suffix,
			force_ext=(args.ext if args.ext else None),
			strip_meta=args.strip_metadata,
			overwrite=args.overwrite,
			quality=args.quality,
			optimize=args.png_optimize,
		)
		if result:
			count += 1

	print(f"Processed {count} / {len(images)} images. Output: {out_root}")
	return 0


if __name__ == "__main__":
	sys.exit(main())
