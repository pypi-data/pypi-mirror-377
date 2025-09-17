"""Add an image to the media storage."""

import pathlib

from django.core.files.storage import Storage, storages
from django.core.management import BaseCommand
from django.urls import reverse

from df_site.templatetags.images import AspectPolicy, CachedImage


class Command(BaseCommand):
    """Add an image to the media storage."""

    help = "Add an image to the media storage."

    def add_arguments(self, parser):
        """Add arguments to the command."""
        parser.add_argument("path", type=pathlib.Path)
        parser.add_argument("--storage", choices=["default", "staticfiles"], default="default")
        parser.add_argument("--name", type=str, default=None)
        parser.add_argument("--height", type=int, default=None)
        parser.add_argument("--width", type=int, default=None)
        parser.add_argument("--format", type=str, default="webp", choices=CachedImage.formats)
        parser.add_argument("--overwrite", action="store_true", default=False)
        parser.add_argument("--print", action="store_true", default=False)
        parser.add_argument(
            "--policy",
            type=int,
            default=AspectPolicy.FORCE_MAX_TRANSPARENT.value,
            choices=[x.value for x in AspectPolicy],
        )

    def handle(self, *args, **options):
        """Add an image to the media storage and generate thumbnails."""
        aspect_policy = AspectPolicy.get_policy(options["policy"])
        src_path: pathlib.Path = options["path"]
        storage: str = options["storage"]
        name: str = options["name"] or src_path.name
        # we need to check if the file exists
        if not src_path.exists():
            raise FileNotFoundError(f"File {src_path} does not exist.")
        # we need to check if the file exists in the destination storage
        storage_obj: Storage = storages[storage]
        exists = storage_obj.exists(name)
        cache_engine = "locmem"
        fmt = options["format"]
        if exists and not options["overwrite"]:
            self.stderr.write(f"File {name} already exists in storage {storage}.")
            return
        elif exists:
            storage_obj.delete(name)
        # we save the file to the destination storage
        with src_path.open("rb") as src_file:
            storage_obj.save(name, src_file)
        #
        img = CachedImage.from_target_path(f"T/600x600_4/{name}.{fmt}")
        img.process()
        self.stdout.write(f"Generated thumbnails: {img.created_sizes}.")
        if options["print"]:
            self.stdout.write(img.as_html_tag())

        def url(p):
            """Return the URL of the thumbnail."""
            return reverse("thumbnails", kwargs={"path": p})

        img = CachedImage(
            CachedImage.sources["media"]["src_storage"],
            CachedImage.sources["media"]["dst_storage"],
            cache_engine,
            name,
            CachedImage.sources["media"]["prefix"],
            url=url,
            height=options["height"],
            width=options["width"],
            widths=None,
            aspect_policy=aspect_policy,
            fmt=fmt,
            write_thumbnails=True,
        )
        img.process()
        self.stdout.write(f"File {name} saved to storage {storage}.")
        self.stdout.write(f"Generated thumbnails: {img.created_sizes}.")
        if options["print"]:
            self.stdout.write(img.as_html_tag())
        img = CachedImage(
            CachedImage.sources["media"]["src_storage"],
            CachedImage.sources["media"]["dst_storage"],
            cache_engine,
            name,
            CachedImage.sources["media"]["prefix"],
            url=url,
            height=options["height"],
            width=options["width"],
            widths=[320, 480, 640, 1024, 2048],
            aspect_policy=aspect_policy,
            fmt=fmt,
            write_thumbnails=True,
        )
        img.process()
        self.stdout.write(f"File {name} saved to storage {storage}.")
        self.stdout.write(f"Generated thumbnails: {img.created_sizes}.")
        if options["print"]:
            self.stdout.write(img.as_html_tag())
