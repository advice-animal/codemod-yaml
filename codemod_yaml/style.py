from dataclasses import dataclass, replace


@dataclass
class YamlStyle:
    """
    Stores stylistic preferences about how sequences get formatted.

    These are really only intended to be set as global defaults or set on a
    single sequence item to match its preceeding one.
    """

    #: the number of (presumably whitespace) characters to indent this item
    #: (and all its children).  Additional hanging indent on mappings is
    #: `mapping_next_line_indent` below.
    base_indent: int = 0
    increment_indent: int = 2

    #: - foo <-- after dash
    #:   bar <-- line with indent
    sequence_whitespace_after_dash: int = 1

    #: preference for whether single-line flow should be forced on their own
    #: line (more verbose, and fairly uncommon in documents I've seen), e.g.
    #: -
    #:   foo <-- line with indent
    #:
    #: block or multi-line flow items always start on their own line for
    #: consistency, because something like seq of seq on same line is weird:
    #: -
    #:   - foo <-- line with whitespace_indent + whitespace_before_dash
    sequence_whitespace_indent: int = 2
    sequence_flow_on_next_line: bool = False

    def __post_init__(self) -> None:
        """
        Although it's possible to add additional indent, we'll only output lined-up ourselves for consistency.
        """
        self.sequence_whitespace_indent = self.sequence_whitespace_after_dash + 1

    #: key<>:<>value <-- before/after colon`
    #: key<>:
    #:   value <-- line with indent
    #:
    mapping_whitespace_before_colon: int = 0
    mapping_flow_space_after_colon: int = 1
    mapping_flow_on_next_line: bool = False
    mapping_next_line_indent: int = 2  #: arbitrary, must be at least one space

    # quote_style: QuoteStyle = QuoteStyle.AUTO

    def indent(self, n: int = -1) -> "YamlStyle":
        if n == -1:
            return replace(self, base_indent=self.base_indent + self.increment_indent)
        else:
            return replace(self, base_indent=self.base_indent + n)
