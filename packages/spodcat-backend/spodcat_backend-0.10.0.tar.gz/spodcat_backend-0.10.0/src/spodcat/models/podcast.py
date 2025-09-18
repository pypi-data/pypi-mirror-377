import logging
import mimetypes
import re
import uuid
from base64 import b64encode
from io import BytesIO
from typing import TYPE_CHECKING, Any
from urllib.parse import urljoin

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.files.images import ImageFile
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from iso639 import iter_langs
from markdownify import markdownify
from martor.models import MartorField

from spodcat.model_mixin import ModelMixin
from spodcat.models.querysets import PodcastQuerySet
from spodcat.settings import spodcat_settings
from spodcat.types import RssFeed
from spodcat.utils import (
    delete_storage_file,
    downscale_image,
    generate_thumbnail,
    markdown_to_html,
)

from .functions import (
    podcast_banner_storage,
    podcast_banner_upload_to,
    podcast_cover_storage,
    podcast_cover_thumbnail_storage,
    podcast_cover_thumbnail_upload_to,
    podcast_cover_upload_to,
    podcast_favicon_storage,
    podcast_favicon_upload_to,
)


if TYPE_CHECKING:
    from django.db.models.fields.related_descriptors import RelatedManager

    from spodcat.models import Category, FontFace, PodcastLink
    from spodcat.models.querysets import PodcastContentManager, PodcastManager


logger = logging.getLogger(__name__)


def get_language_choices():
    return [(l.pt1, l.name) for l in iter_langs() if l.pt1]


def podcast_slug_validator(value: str):
    VERBOTEN = ["sw.js", "episode", "workbox-4723e66c.js", "post"]
    if value.lower() in VERBOTEN:
        raise ValidationError(_("'%(value)s' is a forbidden slug for podcasts.") % {"value": value})


class Podcast(ModelMixin, models.Model):
    class ItunesType(models.TextChoices):
        EPISODIC = "episodic"
        SERIAL = "serial"

    FONT_SIZES = ["small", "normal", "large"]

    authors: "models.ManyToManyField[AbstractUser, Any]" = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="podcasts",
        blank=True,
        verbose_name=_("authors"),
    )
    banner = models.ImageField(
        null=True,
        default=None,
        blank=True,
        upload_to=podcast_banner_upload_to,
        storage=podcast_banner_storage,
        verbose_name=_("banner image"),
        help_text=_("Should be >= 960px wide and have aspect ratio 3:1."),
        max_length=300,
    )
    banner_height = models.PositiveIntegerField(null=True, default=None)
    banner_width = models.PositiveIntegerField(null=True, default=None)
    categories: "models.ManyToManyField[Category, Any]" = models.ManyToManyField(
        "spodcat.Category",
        blank=True,
        verbose_name=_("categories"),
    )
    cover = models.ImageField(
        null=True,
        default=None,
        blank=True,
        upload_to=podcast_cover_upload_to,
        storage=podcast_cover_storage,
        help_text=_("This is the round 'avatar' image. It should ideally have height and width >= 1400px."),
        verbose_name=_("cover"),
        max_length=300,
    )
    cover_height = models.PositiveIntegerField(null=True, default=None)
    cover_mimetype = models.CharField(max_length=50, null=True, default=None)
    cover_thumbnail = models.ImageField(
        null=True,
        default=None,
        blank=True,
        upload_to=podcast_cover_thumbnail_upload_to,
        storage=podcast_cover_thumbnail_storage,
        max_length=300,
    )
    cover_thumbnail_height = models.PositiveIntegerField(null=True, default=None)
    cover_thumbnail_mimetype = models.CharField(max_length=50, null=True, default=None)
    cover_thumbnail_width = models.PositiveIntegerField(null=True, default=None)
    cover_width = models.PositiveIntegerField(null=True, default=None)
    custom_guid = models.UUIDField(
        null=True,
        default=None,
        blank=True,
        verbose_name=_("custom GUID"),
        help_text=_(
            "Don't set if you don't know what you're doing. "
            "Ref: https://podcasting2.org/podcast-namespace/tags/guid"
        ),
    )
    description = MartorField(null=True, default=None, blank=True, verbose_name=_("description"))
    enable_comments = models.BooleanField(default=False, verbose_name=_("enable comments"))
    episode_rss_suffix = MartorField(
        verbose_name=_("Episode RSS suffix"),
        null=True,
        blank=True,
        default=None,
        help_text=_("Will be added to the bottom of every episode description in the RSS feed."),
    )
    favicon = models.ImageField(
        null=True,
        default=None,
        blank=True,
        upload_to=podcast_favicon_upload_to,
        storage=podcast_favicon_storage,
        verbose_name=_("favicon"),
        max_length=300,
    )
    favicon_content_type = models.CharField(null=True, default=None, blank=True, max_length=50)
    itunes_type = models.CharField(max_length=10, choices=ItunesType.choices, default=ItunesType.EPISODIC)
    language = models.CharField(
        max_length=5,
        choices=get_language_choices,
        null=True,
        blank=True,
        default=None,
        verbose_name=_("language"),
    )
    name = models.CharField(max_length=100, verbose_name=_("name"))
    name_font_face = models.ForeignKey["FontFace | None"](
        "spodcat.FontFace",
        related_name="+",
        on_delete=models.SET_NULL,
        verbose_name=_("name font face"),
        null=True,
        default=None,
        blank=True,
    )
    name_font_size = models.CharField(
        max_length=10,
        choices=[(c, c) for c in FONT_SIZES],
        default="normal",
        verbose_name=_("name font size"),
    )
    owner = models.ForeignKey["AbstractUser"](
        settings.AUTH_USER_MODEL,
        related_name="owned_podcasts",
        on_delete=models.PROTECT,
        verbose_name=_("owner"),
    )
    require_comment_approval = models.BooleanField(default=True, verbose_name=_("require comment approval"))
    slug = models.SlugField(
        primary_key=True,
        validators=[podcast_slug_validator],
        help_text=_("Will be used in URLs."),
        verbose_name=_("slug"),
    )
    tagline = models.CharField(max_length=500, null=True, blank=True, default=None, verbose_name=_("tagline"))

    contents: "PodcastContentManager"
    links: "RelatedManager[PodcastLink]"

    objects: "PodcastManager" = PodcastQuerySet.as_manager()

    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["name"])]
        verbose_name = _("podcast")
        verbose_name_plural = _("podcasts")

    @property
    def description_html(self) -> str:
        return markdown_to_html(self.description)

    @property
    def episodes_fm_url(self) -> str:
        return "https://episodes.fm/" + b64encode(self.rss_url.encode()).decode().strip("=")

    @property
    def frontend_url(self) -> str:
        return urljoin(spodcat_settings.FRONTEND_ROOT_URL, self.slug)

    @property
    def guid(self):
        if self.custom_guid:
            return self.custom_guid
        url = re.sub(r"^\w+://", "", self.rss_url).strip("/")
        # https://github.com/Podcast-Standards-Project/PSP-1-Podcast-RSS-Specification?tab=readme-ov-file#podcastguid
        return uuid.uuid5(uuid.UUID("ead4c236-bf58-58c6-a2c6-a6b28d128cb6"), url)

    @property
    def rss_url(self) -> str:
        return spodcat_settings.get_absolute_backend_url("spodcat:podcast-rss", args=(self.slug,))

    def __str__(self):
        return self.name

    # pylint: disable=no-member
    def handle_uploaded_banner(self, save: bool = False):
        downscale_image(self.banner, max_width=960, max_height=320, save=save)
        if self.banner:
            self.banner_height = self.banner.height
            self.banner_width = self.banner.width
        else:
            self.banner_height = None
            self.banner_width = None
        if save:
            self.save()

    # pylint: disable=no-member
    def handle_uploaded_cover(self, save: bool = False):
        delete_storage_file(self.cover_thumbnail)
        if self.cover:
            mimetype = generate_thumbnail(self.cover, self.cover_thumbnail, 150, save)
            self.cover_mimetype = mimetype
            self.cover_thumbnail_mimetype = mimetype
            self.cover_height = self.cover.height
            self.cover_width = self.cover.width
            self.cover_thumbnail_height = self.cover_thumbnail.height
            self.cover_thumbnail_width = self.cover_thumbnail.width
        else:
            self.cover_mimetype = None
            self.cover_thumbnail_mimetype = None
            self.cover_height = None
            self.cover_width = None
            self.cover_thumbnail_height = None
            self.cover_thumbnail_width = None
        if save:
            self.save()

    def handle_uploaded_favicon(self, save: bool = False):
        downscale_image(self.favicon, max_width=100, max_height=100, save=save)

    def has_change_permission(self, request):
        assert isinstance(request.user, AbstractUser)
        return request.user.is_superuser or request.user == self.owner or request.user in self.authors.all()

    def update_from_feed(self, feed: RssFeed):
        from spodcat.models import Category

        self.name = markdownify(feed["title"])

        if "description" in feed:
            self.description = markdownify(feed["description"])

        if "image" in feed and "href" in feed["image"] and feed["image"]["href"]:
            logger.info("Importing cover image: %s", feed["image"]["href"])
            response = requests.get(feed["image"]["href"], timeout=10)
            if response.ok:
                suffix = ""
                content_type = response.headers.get("Content-Type", "")
                if content_type:
                    suffix = mimetypes.guess_extension(content_type) or ("." + content_type.split("/")[-1])
                delete_storage_file(self.cover)
                # pylint: disable=no-member
                self.cover.save(
                    name=f"cover{suffix}",
                    content=ImageFile(file=BytesIO(response.content)),
                    save=False,
                )
                self.handle_uploaded_cover()

        if "language" in feed:
            self.language = feed["language"]

        self.save()

        if "tags" in feed:
            tags = [t["term"] for t in feed["tags"]]
            self.categories.add(*list(Category.objects.filter(Q(cat__in=tags) | Q(sub__in=tags))))
        if "authors" in feed:
            users = get_user_model().objects.filter(email__in=[a["email"] for a in feed["authors"] if "email" in a])
            self.authors.add(*list(users)) # type: ignore
