"""Django Prosemirror constants."""

from typing import TypedDict


class ProseMirrorConfig(TypedDict):
    """Main configuration for django-prosemirror settings."""

    tag_to_classes: dict[str, str]
    allowed_node_types: list[str]
    allowed_mark_types: list[str]
    history: bool


EMPTY_DOC = {"type": "doc", "content": []}

SETTINGS_KEY = "DJANGO_PROSEMIRROR"

DEFAULT_SETTINGS: ProseMirrorConfig = {
    "tag_to_classes": {},
    "allowed_node_types": [
        "paragraph",
        "blockquote",
        "horizontal_rule",
        "heading",
        "image",
        "hard_break",
        "code_block",
        "bullet_list",
        "ordered_list",
        "list_item",
        "table",
        "table_row",
        "table_cell",
        "table_header",
    ],
    "allowed_mark_types": [
        "strong",
        "em",
        "link",
        "code",
        "underline",
        "strikethrough",
    ],
    "history": True,
}
