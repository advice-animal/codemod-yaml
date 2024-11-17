from dataclasses import dataclass

from .py.scalar import QuoteStyle


@dataclass
class YamlStyle:
    """
    Stores stylistic preferences about how sequences get formatted.

    These are really only intended to be set as global defaults or set on a
    single sequence item to match its preceeding one.
    """

    #: - foo <-- before/after dash
    #:   bar <-- line with indent
    sequence_whitespace_before_dash: str = " "
    sequence_whitespace_after_dash: str = " "
    sequence_whitespace_indent: str = "   "  # <-- overwritten in post init

    #: preference for whether single-line flow should be forced on their own
    #: line (more verbose, and fairly uncommon in documents I've seen), e.g.
    #: -
    #:   foo <-- line with indent
    #:
    #: block or multi-line flow items always start on their own line for
    #: consistency, because something like seq of seq on same line is weird:
    #: -
    #:   - foo <-- line with whitespace_indent + whitespace_before_dash
    sequence_flow_on_next_line: bool = False

    def __post_init__(self) -> None:
        """
        Although it's possible to add additional indent, we'll only output lined-up ourselves for consistency.
        """
        self.sequence_whitespace_indent = (
            self.sequence_whitespace_before_dash
            + " "
            + self.sequence_whitespace_after_dash
        )

    #: key<>:<>value <-- before/after colon`
    #: key<>:
    #:   value <-- line with indent
    #:
    #: technically whitespace_before_key could also be a thing, but we'll track that as obj.base_indent()
    mapping_whitespace_before_colon: str = ""
    mapping_flow_space_after_colon: str = " "
    mapping_flow_on_next_line: bool = False
    mapping_next_line_indent: str = "  "  #: arbitrary, must be at least one space

    quote_style: QuoteStyle = QuoteStyle.AUTO
