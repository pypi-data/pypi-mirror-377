"""Template tags for image generation in cache."""

import datetime
import hashlib
import logging
import math
import os
import re
import time
from enum import IntEnum
from html import escape
from typing import Callable, Dict, Iterable, List, Optional, Set, Union

from django import template
from django.conf import settings
from django.core.cache import BaseCache, caches
from django.core.files.storage import Storage, storages
from django.core.files.storage.filesystem import FileSystemStorage
from django.db.models.fields.files import FieldFile
from django.http import Http404, HttpRequest
from django.urls import reverse
from django.utils.safestring import mark_safe
from PIL import Image

register = template.Library()
logger = logging.getLogger(__name__)


class AspectPolicy(IntEnum):
    """Aspect aspect_policy of resized images."""

    FORCE_HEIGHT_CROP = 0  # height will be respected, width will be cropped or too small
    FORCE_WIDTH_CROP = 1  # width will be respected, height will be cropped or too small
    FORCE_MIN_CROP = 2  # the smallest dimension will be respected, the other will be cropped
    FORCE_MAX_FIT = 3  # the largest dimension will be respected, the other will be too small
    FORCE_MAX_TRANSPARENT = 4  # the largest dimension will be respected, the other extra will be transparent

    @classmethod
    def get_policy(cls, int_policy: int) -> "AspectPolicy":
        """Return the AspectPolicy corresponding to the given integer."""
        for policy in AspectPolicy:
            if policy.value == int_policy:
                return policy
        raise ValueError(f"Invalid aspect policy: {int_policy}")


@register.simple_tag(takes_context=True)
def media_image(
    context,
    path: Union[str, FieldFile, callable],
    widths: Optional[Union[str, List[int]]] = None,
    write: bool = True,
    aspect_policy: AspectPolicy = AspectPolicy.FORCE_MAX_TRANSPARENT,
    fmt: str = "webp",
    height: Optional[int] = None,
    width: Optional[int] = None,
    alt: str = "",
    crossorigin: str = "anonymous",
    loading: str = "lazy",
    referrerpolicy: str = "same-origin",
    **kwargs,
):
    """Generate a <img> tag with associated attributes for a media file.

    :param context: the template context
    :param path: the path to the image
    :param storage: where thumbnail images will be stored
    :param widths: list of widths to create, given in the src-set attribute
    :param write: whether to actually create the thumbnail images
    :param aspect_policy: the policy to apply about the aspect ratio
    :param fmt: the format of the thumbnail images
    :param height: the targeted height of the image
    :param width: the targeted width of the image
    :param alt: the alt attribute, passed as-is to the <img> tag
    :param crossorigin: the crossorigin attribute, passed as-is to the <img> tag
    :param loading: the loading attribute, passed as-is to the <img> tag
    :param referrerpolicy: the referrerpolicy attribute, passed as-is to the <img> tag
    :param kwargs: additional attributes that are passed as-is to the <img> tag
    """
    if isinstance(widths, str):
        widths = [int(x.strip()) for x in widths.split(",")]
    if callable(path):
        path = path()
    elif isinstance(path, FieldFile):
        path: str = path.name
    img = CachedImage(
        CachedImage.sources["media"]["src_storage"],
        CachedImage.sources["media"]["dst_storage"],
        CachedImage.sources["media"]["cache"],
        path,
        CachedImage.sources["media"]["prefix"],
        height=height,
        width=width,
        widths=widths,
        aspect_policy=aspect_policy,
        fmt=fmt,
        write_thumbnails=write,
    )
    img.process()
    result = img.as_html_tag(alt=alt, crossorigin=crossorigin, loading=loading, referrerpolicy=referrerpolicy, **kwargs)
    if result == "":
        img.log_error(context.get("request"))
    return result


@register.simple_tag(takes_context=True)
def static_image(
    context,
    path: Union[callable, str],
    widths: Optional[Union[str, List[int]]] = None,
    write: bool = True,
    aspect_policy: AspectPolicy = AspectPolicy.FORCE_MAX_TRANSPARENT,
    fmt: str = "webp",
    height: Optional[int] = None,
    width: Optional[int] = None,
    alt: str = "",
    crossorigin: str = "anonymous",
    loading: str = "lazy",
    referrerpolicy: str = "same-origin",
    **kwargs,
):
    """Generate a <img> tag with associated attributes for a static file."""
    if callable(path):
        path = path()
    if isinstance(widths, str):
        widths = [int(x.strip()) for x in widths.split(",")]
    img = CachedImage(
        CachedImage.sources["static"]["src_storage"],
        CachedImage.sources["static"]["dst_storage"],
        CachedImage.sources["static"]["cache"],
        path,
        CachedImage.sources["static"]["prefix"],
        height=height,
        width=width,
        widths=widths,
        aspect_policy=aspect_policy,
        fmt=fmt,
        write_thumbnails=write,
    )
    img.process()
    result = img.as_html_tag(alt=alt, crossorigin=crossorigin, loading=loading, referrerpolicy=referrerpolicy, **kwargs)
    if result == "":
        img.log_error(context.get("request"))
    return result


IMAGE_THUMBNAILS = getattr(
    settings,
    "DF_IMAGE_THUMBNAILS",
    {
        "media": {
            "src_storage": "default",
            "dst_storage": "staticfiles",
            "cache": "default",
            "prefix": "T",
            "reversible": True,
        },
        "static": {
            "src_storage": "staticfiles",
            "dst_storage": "staticfiles",
            "cache": "default",
            "prefix": "S",
            "reversible": True,
        },
    },
)


class CachedImage:
    """Handle original images to create required thumbnails."""

    src_fast_check_expiration = 86400
    src_slow_check_expiration = 86400 * 30
    src_cache_expiration = 86400 * 365
    default_cache_data = {
        "width": None,
        "height": None,
        "filesize": None,
        "sha256": None,
        "next_fast_check": None,
        "next_slow_check": None,
        "mtime": None,
    }
    default_widths = [64, 160, 320, 640, 1280, 1920, 3840]
    formats = ["webp", "jpg", "jpeg", "png"]
    target_path_re = re.compile(
        r"(?P<cache_prefix>[^/]+)/"
        r"(?P<width>\d+)x(?P<height>\d+)_(?P<aspect_policy>[^/]+)/"
        r"(?P<src_path>.+)\.(?P<fmt>[^.]+)$",
    )
    sources: Dict[str, Dict[str, str]] = IMAGE_THUMBNAILS

    def __init__(
        self,
        src_storage: str,
        dst_storage: str,
        cache: str,
        src_path: str,
        cache_prefix: str,
        url: Callable[[str], str] = lambda p: reverse("thumbnails", kwargs={"path": p}),
        height: Optional[int] = None,
        width: Optional[int] = None,
        widths: Optional[List[int]] = None,
        aspect_policy: AspectPolicy = AspectPolicy.FORCE_MAX_TRANSPARENT,
        fmt: str = "webp",
        write_thumbnails: bool = True,
    ):
        """Initialize the CachedImage."""
        dst_name = hashlib.sha256(src_path.encode()).hexdigest()
        cache_key = f"{cache_prefix}{dst_name}"

        self.src_storage_obj: Storage = storages[src_storage]
        self.dst_storage_obj: Storage = storages[dst_storage]
        self.cache_obj: BaseCache = caches[cache]
        self.src_path = src_path
        self.cache_key = cache_key
        self.cache_prefix = cache_prefix
        self.url: Callable[[str], str] = url  # function to generate the URL of the thumbnails from the thumbnail path
        self.target_height = height  # target height of the image
        self.target_width = width  # target width of the image
        self.widths = widths  # list of widths to create if possible
        self.aspect_policy = aspect_policy  # aspect ratio policy when target width and height are given
        self.fmt = fmt  # format ('webp', 'jpg', 'jpeg', 'png') of the thumbnails
        self.cache_data: Dict[str, Union[None, str, int, Dict]] = self.default_cache_data.copy()
        self.cache_changed: bool = False  # whether the cache has been changed and must be saved
        self.write_thumbnail: bool = write_thumbnails  # whether the thumbnails must be actually created
        self.paths_srcset: Dict[str, str] = {}  # the sizes and paths for the srcset attribute
        self.path_src: str = ""  # the path used in the src attribute
        self.created_sizes: Set[int] = set()  # the list of actually created sizes

    def process(self):
        """Process the image, updating the cache if necessary."""
        cache_data = self.cache_obj.get(self.cache_key, {})
        self.cache_data.update(cache_data)
        try:
            self.process_thumbnails()
        except FileNotFoundError:
            logger.error("Image %s is missing.", self.src_path)
            timestamp = int(time.time())
            self.cache_data["next_slow_check"] = timestamp + self.src_slow_check_expiration
            self.cache_data["next_fast_check"] = timestamp + self.src_fast_check_expiration
            self.cache_changed = True
        except Exception as e:
            logger.error("Error while processing image %s [%s]", self.src_path, e)
            timestamp = int(time.time())
            self.cache_data["next_slow_check"] = timestamp + self.src_slow_check_expiration
            self.cache_data["next_fast_check"] = timestamp + self.src_fast_check_expiration
            self.cache_changed = True
        if self.cache_changed:
            self.cache_obj.set(self.cache_key, self.cache_data, self.src_cache_expiration)

    def process_thumbnails(self):
        """Update image metadata if required and create missing thumbnails."""
        old_cache_data = self.cache_data.copy()
        missing_data = any(self.cache_data[x] is None for x in self.default_cache_data)
        timestamp = int(time.time())
        if (
            missing_data
            or self.cache_data.get("next_slow_check") < timestamp
            or (self.cache_data.get("next_fast_check") < timestamp and self.get_mtime() > self.cache_data["mtime"])
        ):
            # we must recompute the cached data since either the data is missing
            # or the last slow check is too old
            # or the new fast check shows that the file has been modified
            self.update_image_data()
            self.cache_data["next_slow_check"] = timestamp + self.src_slow_check_expiration
            self.cache_data["next_fast_check"] = timestamp + self.src_fast_check_expiration
            self.cache_data["mtime"] = self.get_mtime()
            self.cache_changed = True
        must_recreate = any(
            self.cache_data[x] != old_cache_data[x] for x in ("width", "height", "filesize", "sha256", "mtime")
        )
        widths_to_create: Set[int] = set()
        for width in self.get_required_widths():
            if must_recreate or self.get_cache_key(width) not in self.cache_data:
                widths_to_create.add(width)
                self.cache_changed = True
        base_width = self.get_base_width()
        base_cache_key = self.get_cache_key(base_width)
        if must_recreate or base_cache_key not in self.cache_data:
            widths_to_create.add(base_width)
            self.cache_changed = True
        if widths_to_create:
            self.create_thumbnails(widths_to_create, force=must_recreate)
        for width in self.get_required_widths():
            self.paths_srcset[f"{width}w"] = self.cache_data[self.get_cache_key(width)]
        self.path_src = self.cache_data[base_cache_key]

    def get_mtime(self) -> int:
        """Return the modification time of the source image, when available."""
        try:
            dt: datetime.datetime = self.src_storage_obj.get_modified_time(self.src_path)
            return int(dt.timestamp())
        except NotImplementedError:
            return 0

    def get_base_width(self) -> int:
        """Return the base width of the displayed image."""
        if self.target_width is not None:
            return self.target_width
        elif self.target_height is not None:
            return math.ceil(self.target_height * self.cache_data["width"] / self.cache_data["height"])
        return self.cache_data["width"]

    def get_required_widths(self) -> Iterable[int]:
        """Return the list of required widths for the image."""
        if self.widths is None:
            self.widths = self.default_widths
        return [x for x in self.widths if x <= self.cache_data["width"]]

    def update_image_data(self):
        """Update the cache data for the image, allowing to check if thumbnails must be computed."""
        with self.src_storage_obj.open(self.src_path, "rb") as fd:
            img = Image.open(fd)
            self.cache_data["width"], self.cache_data["height"] = img.size
            sha256 = hashlib.sha256()
            fd.seek(0)
            for data in iter(lambda: fd.read(4096), b""):
                sha256.update(data)
            self.cache_data["filesize"] = fd.tell()
            self.cache_data["sha256"] = hashlib.sha256().hexdigest()
            img.close()

    def create_thumbnails(self, widths: Iterable[int], force: bool = False, write: bool = True):
        """Create the thumbnails for the all given widths."""
        if write:
            with self.src_storage_obj.open(self.src_path, "rb") as fd:
                img = Image.open(fd)
                for width in widths:
                    self.create_thumbnail(img, width, force=force, write=write)
                img.close()
        else:
            for width in widths:
                self.create_thumbnail(None, width, force=force, write=write)

    def get_target_path(self, width: int, height: int) -> str:
        """Return the target path for the given width."""
        return f"{self.cache_prefix}/{width}x{height}_{self.aspect_policy}/{self.src_path}.{self.fmt}"

    @classmethod
    def from_target_path(cls, dst_path: str):
        """Build a CachedImage from the URL path, if a thumbnail is missing."""
        if not (matcher := cls.target_path_re.match(dst_path)):
            raise Http404("Invalid path")
        cache_prefix = matcher.group("cache_prefix")
        for source in cls.sources.values():
            if cache_prefix == source["prefix"]:
                break
        else:
            raise Http404("Unkown image path.")
        src_storage = source["src_storage"]
        dst_storage = source["dst_storage"]
        cache = source["cache"]
        if not source.get("reversible"):
            raise Http404("Invalid image path.")
        width = int(matcher.group("width"))
        height = int(matcher.group("height"))
        if not (0 < height < 10000 and 0 < width < 10000):
            raise Http404("Invalid image size.")
        try:
            aspect_policy = AspectPolicy.get_policy(int(matcher.group("aspect_policy")))
        except ValueError:
            raise Http404("Invalid aspect policy.")
        src_path = matcher.group("src_path")
        src_path = os.path.normpath(src_path)
        if src_path.startswith("../") or src_path in {".", ".."}:
            raise Http404("Invalid source path.")
        fmt = matcher.group("fmt")
        if fmt not in cls.formats:
            raise Http404("Invalid format.")
        return cls(
            src_storage,
            dst_storage,
            cache,
            src_path,
            cache_prefix,
            height=height,
            width=width,
            widths=[],
            aspect_policy=aspect_policy,
            fmt=fmt,
        )

    @classmethod
    def get_cache_key(cls, width: int) -> str:
        """Return the cache key for the given width."""
        return f"{width}w"

    def create_thumbnail(
        self,
        img_src: Optional[Image],
        required_width: int,
        force: bool = False,
        write: bool = True,
    ):
        """Create a thumbnail for the given width and stores the new name in the cache."""
        src_width = self.cache_data["width"]
        src_height = self.cache_data["height"]
        width_cache_key = self.get_cache_key(required_width)
        aspect_ratio_height = math.ceil(required_width * src_height / src_width)
        if self.target_width and self.target_height:
            required_height = math.ceil(required_width * self.target_height / self.target_width)
        else:
            required_height = aspect_ratio_height
        dst_path = self.get_target_path(required_width, required_height)
        if width_cache_key not in self.cache_data:
            self.cache_data[width_cache_key] = dst_path
            self.cache_changed = True
        if not write:
            return
        exists = self.dst_storage_obj.exists(dst_path)
        if not force and exists:
            return
        logger.info("Creating thumbnail %s", dst_path)
        if aspect_ratio_height == required_height:
            # perfect fit: the target aspect ratio is the same as the source aspect ratio
            # always true when only one dimension is specified
            img = img_src.resize((required_width, required_height))
        elif aspect_ratio_height < required_height:
            # the image is not high enough
            if (
                self.aspect_policy == AspectPolicy.FORCE_HEIGHT_CROP
                or self.aspect_policy == AspectPolicy.FORCE_MIN_CROP
            ):
                tmp_width = math.ceil(required_height * src_width / src_height)
                img = img_src.resize((tmp_width, required_height))  # larger than expected
                half = (tmp_width - required_width) // 2
                img = img.crop((half, 0, required_width + half, required_height))  # we crop
            elif (
                self.aspect_policy == AspectPolicy.FORCE_WIDTH_CROP or self.aspect_policy == AspectPolicy.FORCE_MAX_FIT
            ):
                img = img_src.resize((required_width, aspect_ratio_height))  # shorter than expected
            else:  # if self.aspect_policy == AspectPolicy.FORCE_MAX_TRANSPARENT:
                r_img: Image = img_src.resize((required_width, aspect_ratio_height))  # shorter than expected
                img = Image.new("RGBA", (required_width, required_height), (255, 0, 0, 0))
                img.paste(r_img, (0, (required_height - aspect_ratio_height) // 2))
                r_img.close()
        else:
            # the image is not wide enough
            aspect_ratio_width = math.ceil(required_height * src_width / src_height)
            if self.aspect_policy == AspectPolicy.FORCE_HEIGHT_CROP or self.aspect_policy == AspectPolicy.FORCE_MAX_FIT:
                img = img_src.resize((aspect_ratio_width, required_height))  # thinner than expected
            elif (
                self.aspect_policy == AspectPolicy.FORCE_WIDTH_CROP or self.aspect_policy == AspectPolicy.FORCE_MIN_CROP
            ):
                tmp_height = math.ceil(required_width * src_height / src_width)
                img = img_src.resize((required_width, tmp_height))  # taller than expected
                half = (tmp_height - required_height) // 2
                img = img.crop((0, half, required_width, required_height + half))  # we crop
            else:  # if self.aspect_policy == AspectPolicy.FORCE_MAX_TRANSPARENT:
                r_img: Image = img_src.resize((aspect_ratio_width, required_height))
                img = Image.new("RGBA", (required_width, required_height), (255, 0, 0, 0))
                img.paste(r_img, ((required_width - aspect_ratio_width) // 2, 0))
                r_img.close()
        self.prepare_storage(dst_path)
        if exists:
            self.dst_storage_obj.delete(dst_path)
        with self.dst_storage_obj.open(dst_path, "wb") as fd:
            img.save(fd, format=self.fmt.upper())
        self.created_sizes.add(required_width)

    def prepare_storage(self, path):
        """Prepare the storage for the given path, creating directories if required."""
        if isinstance(self.dst_storage_obj, FileSystemStorage):
            full_path = self.dst_storage_obj.path(path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)

    @property
    def attr_src(self) -> str:
        """Return the src attribute for the <img> tag."""
        return self.url(self.path_src)

    @property
    def attr_srcset(self) -> str:
        """Return the srcset attribute for the <img> tag."""
        return ",".join(f"{self.url(path)} {size}" for size, path in self.paths_srcset.items())

    def as_html_tag(
        self,
        alt: str = "",
        crossorigin: str = "anonymous",
        loading: str = "lazy",
        referrerpolicy: str = "same-origin",
        **kwargs,
    ):
        """Return a URL tag with all required attributes."""
        if not self.path_src:
            return ""
        attrs = {"src": escape(self.attr_src)}
        if self.paths_srcset:
            attrs["srcset"] = escape(self.attr_srcset)
        attrs["alt"] = escape(alt)
        attrs["crossorigin"] = escape(crossorigin)
        attrs["loading"] = escape(loading)
        attrs["referrerpolicy"] = escape(referrerpolicy)
        if self.target_width:
            attrs["width"] = str(self.target_width)
        if self.target_height:
            attrs["height"] = str(self.target_height)
        for k, v in kwargs.items():
            k = k.replace("_", "-")
            if k == "class-":
                k = "class"
            attrs[escape(k)] = escape(v)
        attrs = " ".join(f'{k}="{v}"' for k, v in attrs.items())
        return mark_safe(f"<img {attrs}/>")  # noqa S308

    def log_error(self, request: Optional[HttpRequest]):
        """Log errors."""
        if request is None:
            logger.error("Image %s not found", self.src_path)
        else:
            request_path = request.path
            referer = request.META.get("HTTP_REFERER", "")
            logger.error("Image %s not found (referer: %s, URI: %s)", self.src_path, referer, request_path)
