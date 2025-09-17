"""Django settings for the project."""

from typing import List, Tuple

from df_config.config.dynamic_settings import CallableSetting, SettingReference
from django.utils.translation import gettext_lazy as _

from df_site.dynamic_settings import allauth_signup_form, are_tests_running, load_tox_environment

load_tox_environment()
DF_SITE_TITLE = "More batteries to Django"
DF_SITE_SECURITY_EMAIL = SettingReference("ADMIN_EMAIL")
DF_SITE_SECURITY_LANGUAGE_CODE = SettingReference("LANGUAGE_CODE")
DF_SITE_SECURITY_GPG_CONTENT = None

DF_SITE_DESCRIPTION = "A simple Django site with lots of batteries included."
DF_SITE_KEYWORDS = ["Django", "Bootstrap", "WebSockets", "HTMX", "Django Channels"]
DF_SITE_AUTHOR = "d9pouces"
DF_SITE_ORGANIZATION = "d9pouces"
DF_SITE_SOCIAL_NETWORKS = {
    "instagram": "https://www.instagram.com/d9pouces/",
    "twitter": "https://x.com/d9pouces/",
    "github": "https://github.com/d9pouces/",
}

DF_SITE_THEMES: List[Tuple[str, str, str]] = [  # ('theme name', 'theme label', 'icon name')
    ("auto", _("Auto"), "toggle-on"),
    ("light", _("Light"), "sun"),
    ("dark", _("Dark"), "moon"),
]
DF_ANDROID_THEME_COLOR = "#ffffff"
DF_ANDROID_BACKGROUND_COLOR = "#ffffff"
DF_MICROSOFT_BACKGROUND_COLOR = "#da532c"
DF_SAFARI_PINNED_COLOR = "#5bbad5"

DF_IMAGE_THUMBNAILS = {
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
}

CSP_IMG_SRC = ["'self'", "data: w3.org/svg/2000", "https://log.pinterest.com"]
# "https://log.pinterest.com" is used for Pinterest
CSP_STYLE_SRC = ["'self'"]
CSP_FONT_SRC = ["'self'"]
CSP_DEFAULT_SRC = ["'none'"]
CSP_SCRIPT_SRC = [
    "'self'",
    "https://www.google.com",
    "https://www.gstatic.com",
    "https://assets.pinterest.com",
    "'unsafe-inline'",
]
# unsafe-inline is used for django-allauth (inline JS)
# "https://www.google.com", "https://www.gstatic.com" are used for reCAPTCHA
# "https://assets.pinterest.com" is used for Pinterest
CSP_OBJECT_SRC = ["'self'"]
CSP_MEDIA_SRC = ["'self'"]
CSP_FRAME_SRC = ["'self'", "https://www.google.com", "https://assets.pinterest.com"]
# "https://www.google.com" is used for reCAPTCHA
# "https://assets.pinterest.com" is used for Pinterest
CSP_CHILD_SRC = ["'self'"]
CSP_FRAME_ANCESTORS = ["'self'"]
CSP_FORM_ACTION = ["'self'"]
CSP_MANIFEST_SRC = ["'self'"]
CSP_BASE_URI = ["'self'"]
CSP_REPORT_URI = "/csp-report/"
CSP_REPORT_TO = None
DF_TEMPLATE_CONTEXT_PROCESSORS = [
    "df_site.context_processors.global_site_infos",
    "django.template.context_processors.request",
]
TESTING = CallableSetting(are_tests_running)
RECAPTCHA_PUBLIC_KEY = ""
RECAPTCHA_PRIVATE_KEY = ""
DF_INSTALLED_APPS = [
    "django_bootstrap5",
    "df_site.apps.DFSiteApp",
    "cookie_consent",
    "postman",
    "allauth.mfa",
    "allauth.usersessions",
    "django_ckeditor_5",
    "django_recaptcha",
]

DF_MIDDLEWARE = [
    "df_site.middleware.websocket_middleware",
]

USERSESSIONS_TRACK_ACTIVITY = True
POSTMAN_DISALLOW_ANONYMOUS = True
POSTMAN_AUTO_MODERATE_AS = True
POSTMAN_I18N_URLS = False
AUTH_USER_MODEL = "df_site.PreferencesUser"
AUTH_USER_SETTINGS_VIEW = "df_site.users.views.UserSettingsView"
COOKIE_CONSENT_SECURE = SettingReference("USE_SSL")
COOKIE_CONSENT_DOMAIN = "{SERVER_NAME}"
COOKIE_CONSENT_SAMESITE = "Strict"
PIPELINE = {
    "PIPELINE_ENABLED": SettingReference("PIPELINE_ENABLED"),
    "JAVASCRIPT": {
        "base": {
            "source_filenames": [
                "js/base.js",
                "js/df_websockets.min.js",
                # "django_ckeditor_5/dist/bundle.js"
            ],
            "output_filename": "js/base.min.js",
            #            "integrity": "sha384",
            "crossorigin": "anonymous",
            "extra_context": {
                "defer": True,
            },
        },
        "app": {
            "source_filenames": ["js/app.ts"],
            "output_filename": "js/app.min.js",
            #            "integrity": "sha384",
            "crossorigin": "anonymous",
            "extra_context": {
                "defer": True,
            },
        },
    },
    "STYLESHEETS": {
        "base": {
            "source_filenames": [
                "django_ckeditor_5/src/override-django.css",
                "css/ckeditor5.css",
                "css/base.css",
            ],
            "output_filename": "css/base.min.css",
            "extra_context": {"media": "all"},
            #            "integrity": "sha384",
            "crossorigin": "anonymous",
        },
        "app": {
            "source_filenames": ["css/app.css"],
            "output_filename": "css/app.min.css",
            "extra_context": {"media": "all"},
            #            "integrity": "sha384",
            "crossorigin": "anonymous",
        },
    },
    "CSS_COMPRESSOR": SettingReference("PIPELINE_CSS_COMPRESSOR"),
    "JS_COMPRESSOR": SettingReference("PIPELINE_JS_COMPRESSOR"),
    "COMPILERS": SettingReference("PIPELINE_COMPILERS"),
}
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True
SOCIALACCOUNT_LOGIN_ON_GET = True
MFA_SUPPORTED_TYPES = ["totp", "webauthn", "recovery_codes"]
MFA_PASSKEY_LOGIN_ENABLED = True
MFA_WEBAUTHN_ALLOW_INSECURE_ORIGIN = SettingReference("DEBUG")
ACCOUNT_LOGIN_BY_CODE_ENABLED = True
ACCOUNT_EMAIL_VERIFICATION = "optional"
ACCOUNT_SIGNUP_FORM_CLASS = CallableSetting(allauth_signup_form)

CKEDITOR_5_USER_LANGUAGE = True
special_chars = [
    {"title": _("smiley face"), "character": "😊"},
    {"title": _("smiley face"), "character": ":)"},
]
CK_EDITOR_5_UPLOAD_FILE_VIEW = "django_ckeditor_5.views.upload_file"
CK_EDITOR_5_UPLOAD_FILE_VIEW_NAME = "upload_file"
CKEDITOR_5_CONFIGS = {
    "inline": {
        "specialChars": special_chars,
        "toolbar": [
            "bold",
            "italic",
            "underline",
            "strikethrough",
            "subscript",
            "superscript",
            "|",
            "specialCharacters",
            "removeFormat",
        ],
        "plugins": [
            "Essentials",
            "Autoformat",
            "Bold",
            "Italic",
            "Underline",
            "Strikethrough",
            "Code",
            "Subscript",
            "Superscript",
            "Paragraph",
            "Font",
            "PasteFromOffice",
            "RemoveFormat",
            "Highlight",
            "SpecialCharacters",
            "SpecialCharactersEssentials",
            "ShowBlocks",
            "SelectAll",
        ],
    },
    "inline_link": {
        "specialChars": special_chars,
        "toolbar": [
            "bold",
            "italic",
            "underline",
            "strikethrough",
            "subscript",
            "superscript",
            "link",
            "|",
            "specialCharacters",
            "removeFormat",
        ],
        "plugins": [
            "Essentials",
            "Autoformat",
            "Bold",
            "Italic",
            "Underline",
            "Strikethrough",
            "Code",
            "Subscript",
            "Superscript",
            "Link",
            "Paragraph",
            "Font",
            "PasteFromOffice",
            "RemoveFormat",
            "Highlight",
            "SpecialCharacters",
            "SpecialCharactersEssentials",
            "ShowBlocks",
            "SelectAll",
        ],
    },
    "default": {
        "specialChars": special_chars,
        "toolbar": [
            "heading",
            "bulletedList",
            "numberedList",
            "blockQuote",
            "|",
            "bold",
            "italic",
            "underline",
            "strikethrough",
            "subscript",
            "superscript",
            "link",
            "highlight",
            "|",
            "insertTable",
            "insertImage",
            "specialCharacters",
            "removeFormat",
            "undo",
            "redo",
        ],
        "image": {
            "toolbar": [
                "imageTextAlternative",
                "|",
                "imageStyle:full",
                "imageStyle:alignLeft",
                "imageStyle:alignRight",
                "imageStyle:alignCenter",
                "imageStyle:side",
                "|",
            ],
            "styles": [
                "full",
                "side",
                "alignLeft",
                "alignRight",
                "alignCenter",
            ],
        },
        "list": {"properties": {"styles": False, "startIndex": True, "reversed": True}},
        "table": {
            "defaultHeadings": {"rows": 1, "columns": 1},
            "contentToolbar": ["tableColumn", "tableRow", "mergeTableCells"],
        },
    },
}
