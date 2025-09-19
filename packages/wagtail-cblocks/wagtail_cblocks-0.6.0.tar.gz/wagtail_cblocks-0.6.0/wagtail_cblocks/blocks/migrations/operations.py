from wagtail.blocks.migrations.operations import BaseBlockOperation


class MergeLinkBlockOperation(BaseBlockOperation):
    """Merge a LinkBlock to the new LinkTargetBlock.

    The LinkBlock was initially a StuctBlock with one `target` child block which
    defines the link type and value through a LinkTargetBlock. Starting from the
    v0.5.0, the LinkBlock has been merged to LinkTargetBlock to simplify its
    structure and make it more reliable.

    Note:
        The `block_path_str` should point to the LinkBlock.
    """

    def apply(self, block_value):
        if targets := block_value.get("target"):
            return {
                "type": targets[0]["type"],
                targets[0]["type"]: targets[0]["value"],
            }
        return {}

    @property
    def operation_name_fragment(self):
        return "merge_link_block"
