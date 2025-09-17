"""Generate the favicons."""

import importlib
import os
import pathlib
from argparse import ArgumentParser

from django.conf import settings
from django.core.management import BaseCommand
from PIL import Image


class Command(BaseCommand):
    """Generate the favicons."""

    specs = [
        ("android-chrome-192x192.png", 192, 192),
        ("android-chrome-512x512.png", 512, 512),
        ("apple-touch-icon.png", 256, 256),
        ("favicon.ico", 64, 64),
        ("favicon-16x16.png", 16, 32),
        ("favicon-32x32.png", 32, 32),
        ("mstile-150x150.png", 150, 150),
    ]

    def add_arguments(self, parser: ArgumentParser):
        """Add the arguments."""
        mod = importlib.import_module(settings.DF_MODULE_NAME)
        default = pathlib.Path(mod.__path__[0]) / "static/favicon"
        parser.add_argument("input", help="Path of the image to add.", type=pathlib.Path)
        parser.add_argument("--output", help="Destination directory.", type=pathlib.Path, default=default)

    def handle(self, *args, **options):
        """Generate the favicons from an original image to the destination directory."""
        src_path: pathlib.Path = options["input"]
        dst_dir: pathlib.Path = options["output"]
        img_src = Image.open(src_path)
        for dst_name, width, height in self.specs:
            img_dst = img_src.resize((width, height))
            dst_path: pathlib.Path = dst_dir / dst_name
            basename, sep, ext = dst_name.rpartition(".")
            os.makedirs(dst_path.parent, exist_ok=True)
            with open(dst_path, "wb") as fd:
                img_dst.save(fd, format=ext.upper())
            self.stdout.write(f"Generated {dst_path}")

        img_src.close()
