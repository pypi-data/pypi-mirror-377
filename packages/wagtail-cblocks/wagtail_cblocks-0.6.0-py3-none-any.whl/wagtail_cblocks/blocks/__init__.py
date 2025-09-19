from collections import namedtuple

from django import forms
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from wagtail import blocks as wagtail_blocks
from wagtail.blocks.struct_block import (
    StructBlockAdapter,
    StructBlockValidationError,
)
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.telepath import register

# TYPED CHOICES
# ------------------------------------------------------------------------------

Size = namedtuple("Size", ["name", "label", "rendition"])
Style = namedtuple("Style", ["name", "label", "css_class"])


class BaseTypedChoiceBlock(wagtail_blocks.ChoiceBlock):
    type_class = None

    def __init__(self, choices, default=None, **kwargs):
        self.typed_choices = {c.name: c for c in choices}

        super().__init__(
            choices=[(c.name, c.label) for c in choices],
            default=default,
            **kwargs,
        )

    def to_python(self, value):
        return self.typed_choices.get(value, None)

    def get_prep_value(self, value):
        return value.name

    def normalize(self, value):
        if isinstance(value, self.type_class):
            return value
        return self.typed_choices.get(value, None)

    def value_for_form(self, value):
        return value and value.name

    def value_from_form(self, value):
        return self.typed_choices.get(value, None)


class SizeChoiceBlock(BaseTypedChoiceBlock):
    type_class = Size

    class Meta:
        label = _("Size")


class StyleChoiceBlock(BaseTypedChoiceBlock):
    type_class = Style

    class Meta:
        label = _("Style")


# CSS & STYLE
# ------------------------------------------------------------------------------


class CSSClassMixin:
    """
    Add the CSS class defined for a block to its rendering context.
    """

    def get_css_classes(self, value):
        if hasattr(self.meta, "css_class"):
            if isinstance(self.meta.css_class, str):
                return [self.meta.css_class]
            if not isinstance(self.meta.css_class, list):
                return list(self.meta.css_class)
            return self.meta.css_class
        return []

    def get_context(self, value, **kwargs):
        context = super().get_context(value, **kwargs)
        context["css_class"] = " ".join(self.get_css_classes(value))
        return context


class StylizedStructBlock(CSSClassMixin, wagtail_blocks.StructBlock):
    """
    A group of sub-blocks which defines an element with different styles.
    """

    styles = ()

    class Meta:
        default_style = None

    def __init__(self, *args, styles=None, **kwargs):
        super().__init__(*args, **kwargs)

        if styles is None:
            styles = self.styles

        if styles:
            style = StyleChoiceBlock(styles, default=self.meta.default_style)
            style.set_name("style")

            self.child_blocks["style"] = style

    def get_css_classes(self, value):
        css_classes = super().get_css_classes(value)
        style = value.get("style", None)
        if style and style.css_class:
            css_classes.append(style.css_class)
        return css_classes


# TYPOGRAPHY
# ------------------------------------------------------------------------------

HEADING_LEVELS = [
    (i, _("Level %(level)d heading") % {"level": i}) for i in range(2, 6)
]


class HeadingValue(wagtail_blocks.StructValue):
    @cached_property
    def tag(self):
        """Return the HTML tag to use for the level."""
        return "h{}".format(self.get("level"))

    @cached_property
    def anchor(self):
        """Generate a slug from the title to be used as an anchor."""
        return slugify(self.get("text"))


class HeadingBlock(wagtail_blocks.StructBlock):
    """
    A section heading with a choosable level.
    """

    text = wagtail_blocks.CharBlock(label=_("Title"), classname="title")
    level = wagtail_blocks.ChoiceBlock(
        choices=HEADING_LEVELS,
        default=2,
        label=_("Level"),
    )

    class Meta:
        icon = "title"
        label = _("Title")
        template = "wagtail_cblocks/heading_block.html"
        value_class = HeadingValue


class ParagraphBlock(wagtail_blocks.RichTextBlock):
    """
    A paragraph with simple or customized features.
    """

    features = ("bold", "italic", "ol", "ul", "hr", "link", "document-link")

    def __init__(self, features=None, **kwargs):
        if features is None:
            features = self.features
        return super().__init__(features=features, **kwargs)

    class Meta:
        icon = "pilcrow"
        label = _("Paragraph")
        template = "wagtail_cblocks/paragraph_block.html"


# LINK
# ------------------------------------------------------------------------------


class LinkTargetStructValue(wagtail_blocks.StructValue):
    @cached_property
    def href(self):
        if block_type := self.get("type"):
            value = self.get(block_type)
            if block_type == "page":
                return value.url
            if block_type in ("document", "image"):
                return value.file.url
            return value
        return ""


class LinkTargetBlock(wagtail_blocks.StructBlock):
    class Meta:
        icon = "link"
        label = _("Link")
        value_class = LinkTargetStructValue
        form_template = "wagtail_cblocks/admin/forms/link_target_block.html"

    page = wagtail_blocks.PageChooserBlock(required=False, label=_("Page"))
    document = DocumentChooserBlock(required=False, label=_("Document"))
    image = ImageChooserBlock(required=False, label=_("Image"))
    url = wagtail_blocks.URLBlock(required=False, label=_("External link"))
    anchor = wagtail_blocks.CharBlock(
        required=False,
        label=_("Anchor link"),
        help_text=mark_safe(  # noqa: S308
            _(
                "An anchor in the current page, for example: "
                "<code>#target-id</code>."
            )
        ),
    )

    def __init__(self, local_blocks=None, required=True, **kwargs):
        super().__init__(local_blocks=local_blocks, **kwargs)

        self.meta.required = required

        # Retrieve available block types from the defined blocks
        self.block_types = list(self.child_blocks.keys())

        # Construct dynamically the choice block and append it
        type_block = wagtail_blocks.ChoiceBlock(
            choices=[
                (name, self.child_blocks[name].label)
                for name in self.block_types
            ]
        )
        type_block.set_name("type")

        self.child_blocks["type"] = type_block

    @property
    def required(self):
        return self.meta.required

    def clean(self, value):
        # Build up a list of (name, value) tuples to be passed to the
        # StructValue constructor
        result = []

        errors = {}

        if block_type := value.get("type"):
            result.append(("type", block_type))

            if block_value := value.get(block_type):
                try:
                    result.append(
                        (
                            block_type,
                            self.child_blocks[block_type].clean(block_value),
                        )
                    )
                except ValidationError as e:
                    errors[block_type] = e
            else:
                errors[block_type] = ValidationError(
                    _("This field is required."), code="required"
                )
        elif self.required:
            errors["type"] = ValidationError(
                _("This field is required."), code="required"
            )

        if errors:
            raise StructBlockValidationError(errors)

        return self._to_struct_value(result)


class LinkTargetBlockAdapter(StructBlockAdapter):
    js_constructor = "wagtail_cblocks.blocks.LinkTargetBlock"

    def js_args(self, block):
        js_args = super().js_args(block)
        js_args[2]["blockTypes"] = block.block_types
        return js_args

    @cached_property
    def media(self):
        css = super().media._css
        css.setdefault("all", [])
        css["all"].append("wagtail_cblocks/admin/css/link-target-block.css")

        js = super().media._js
        js.append("wagtail_cblocks/admin/js/link-target-block.js")

        return forms.Media(css=css, js=js)


register(LinkTargetBlockAdapter(), LinkTargetBlock)


# BUTTONS
# ------------------------------------------------------------------------------


class ButtonBlock(StylizedStructBlock):
    """
    A button which acts like a link.
    """

    text = wagtail_blocks.CharBlock(label=_("Text"))
    link = LinkTargetBlock()

    class Meta:
        icon = "link"
        label = _("Button")
        template = "wagtail_cblocks/button_block.html"


# IMAGES
# ------------------------------------------------------------------------------


class ImageBlock(wagtail_blocks.StructBlock):
    """
    An image with optional caption and link.
    """

    image = ImageChooserBlock(label=_("Image"))
    caption = wagtail_blocks.CharBlock(required=False, label=_("Caption"))
    link = LinkTargetBlock(required=False)

    class Meta:
        icon = "image"
        label = _("Image")
        template = "wagtail_cblocks/image_block.html"


class SizedImageBlock(ImageBlock):
    """
    An image with choosable size, optional caption and link.
    """

    class Meta:
        icon = "image"
        label = _("Adjusted image")
        template = "wagtail_cblocks/sized_image_block.html"

        # Parameters of the 'size' block which can be overwritten at init
        sizes = [
            Size("small", _("Small"), "max-400x400"),
            Size("medium", _("Medium"), "max-800x800"),
            Size("large", _("Large"), "max-1200x1200"),
        ]
        default_size = "medium"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        size = SizeChoiceBlock(
            self.meta.sizes,
            default=self.meta.default_size,
            help_text=_(
                "Note that the image will not be enlarged. This may have no "
                "effect if the image's original size is too small."
            ),
        )
        size.set_name("size")

        self.child_blocks["size"] = size

    def get_context(self, value, **kwargs):
        context = super().get_context(value, **kwargs)
        context["rendition"] = value["image"].get_rendition(
            value["size"].rendition
        )
        return context


# LAYOUT
# ------------------------------------------------------------------------------

HORIZONTAL_ALIGNMENTS = [
    ("start", _("Left")),
    ("center", _("Center")),
    ("end", _("Right")),
]
HORIZONTAL_ALIGNMENT_DEFAULT = None


class ColumnsBlock(wagtail_blocks.StructBlock):
    """
    A list of columns which can be horizontally aligned.
    """

    horizontal_align = wagtail_blocks.ChoiceBlock(
        choices=HORIZONTAL_ALIGNMENTS,
        default=HORIZONTAL_ALIGNMENT_DEFAULT,
        required=False,
        label=_("Horizontal alignment"),
    )

    class Meta:
        icon = "table"
        label = _("Columns")
        template = "wagtail_cblocks/columns_block.html"

    def __init__(self, column_block=None, **kwargs):
        super().__init__(**kwargs)

        if column_block is None:
            if not hasattr(self.meta, "column_block"):
                raise ImproperlyConfigured(
                    "ColumnsBlock was not passed a 'column_block' object"
                )
            column_block = self.meta.column_block

        columns = wagtail_blocks.ListBlock(
            column_block,
            collapsed=True,
            form_classname="columns-block-list",
            label=_("Columns"),
        )
        columns.set_name("columns")

        self.child_blocks["columns"] = columns
        self.child_blocks.move_to_end("columns", last=False)
