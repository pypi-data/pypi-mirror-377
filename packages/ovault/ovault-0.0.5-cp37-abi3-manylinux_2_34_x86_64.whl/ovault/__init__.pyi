"""
A library for managing an [Obsidian](https://obsidian.md/) vault.
"""

from typing import Union, List, Optional, Set, Dict, Any, Tuple

__version__: str = ...


def normalize(name: str) -> str:
    """
    Normalize a note name or path to be used in Obsidian links.

    Example:
        ```python
        normalize("My Note") => "my-note"
        ```
    """
    ...

def parse_yaml(source: str) -> List[object]:
    """
    Parses a YAML string and returns a Python list of parsed objects.

    Args:
        source: A string containing the YAML content.

    Returns:
        A list of Python objects parsed from the YAML source.
    """
    ...

def text_to_tokens(text: str) -> List["Token"]:
    """
    Tokenize a string to a list of tokens.

    Args:
        text: The string to tokenize.

    Returns:
        A list of tokens.

    Example:
        >>> tokens = text_to_tokens("# Hello World!")
        >>> tokens
        [<Token.Header ...>, <Token.Text ...>]
    """
    ...

def to_markdown(obj: object) -> str:
    """
    Converts a Python objects to a Markdown string.

    Args:
        obj: The object or list of objects to convert.

    Returns:
        A string containing the Markdown representation of the object.
    """
    ...

class Span:
    """Represents a span of text in the source, with a start and end position."""
    start: int
    end: int

class Attachment:
    """
    An attachment in an Obsidian vault. An attachment is any
    file that is not a markdown file.
    """
    path: str

FrontmatterValue = Union[str, int, float, bool, List[Any]]

class Frontmatter:
    """
    Represents the frontmatter of a note, which is a collection of ordered key-value pairs.
    This class acts like a dictionary, where keys are strings and values can be various types,
    including numbers, strings, booleans, arrays.

    The main difference from a standard dictionary is that the order of items is preserved
    """

    def __init__(self) -> None:
        """Creates a new empty `Frontmatter`."""
        ...

    def __repr__(self) -> str:
        """Returns a string representation of the frontmatter, showing its keys."""
        ...

    def __len__(self) -> int:
        """Returns the number of items in the frontmatter."""
        ...

    def __contains__(self, key: str) -> bool:
        """Checks if the frontmatter contains a specific key."""
        ...

    def __delitem__(self, key: str) -> None:
        """Deletes a key-value pair from the frontmatter by key."""
        ...

    def __setitem__(self, key: str, value: FrontmatterValue) -> None:
        """Sets the value for a specific key, or adds the key-value pair if it does not exist."""
        ...

    def get(self, key: str) -> Optional[FrontmatterValue]:
        """Retrieves the value associated with a specific key."""
        ...

    def set(self, key: str, value: FrontmatterValue) -> None:
        """Sets the value for a specific key, or adds the key-value pair if it does not exist."""
        ...

    def clear(self) -> None:
        """Clears all items from the frontmatter."""
        ...

    def is_empty(self) -> bool:
        """Checks if the frontmatter is empty."""
        ...

    def copy(self) -> "Frontmatter":
        """Creates a copy of this `Frontmatter`."""
        ...

    def keys(self) -> List[str]:
        """Returns a list of keys in the frontmatter."""
        ...

    def values(self) -> List[FrontmatterValue]:
        """Returns a list of values in the frontmatter."""
        ...

    def items(self) -> List[Tuple[str, FrontmatterValue]]:
        """Returns a list of key-value pairs as tuples in the frontmatter."""
        ...

    def dict(self) -> Dict[str, FrontmatterValue]:
        """Returns a python dictionary representation of the frontmatter."""
        ...

    def yaml(self, indent: int = 2) -> str:
        """Converts the frontmatter to a YAML string representation."""
        ...

class Note:
    """A note in an Obsidian vault."""
    vault_path: str
    path: str
    name: str
    length: int
    tags: Set[str]
    backlinks: Set[str]
    links: Set[str]

    def __repr__(self) -> str:
        """Get a string representation of the note."""
        ...

    def __len__(self) -> int:
        """Get the length of the note in characters."""
        ...

    def tokens(self) -> List["Token"]:
        """Get content note as a list of tokens."""
        ...

    def all_tokens(self) -> List["Token"]:
        """
        Get all tokens in the note, including tokens within nested structures like lists and callouts.
        """
        ...

    def full_path(self) -> str:
        """Get the absolute path to the note file."""
        ...

    def frontmatter(self) -> Optional[Frontmatter]:
        """Get the frontmatter as a python dictionary"""
        ...

    def set_frontmatter(self, frontmatter: Frontmatter) -> None:
        """Set the frontmatter of the note from a python dictionary."""
        ...

    def normalized_name(self) -> str:
        """Get the normalized name of the node."""
        ...

    def read(self) -> str:
        """Read the content of the note and return it as a string"""
        ...

    def insert_at(self, pos: int, text: str) -> None:
        """Inserts a string at a position in the note."""
        ...

    def replace_between(self, start: int, end: int, text: str) -> None:
        """Replaces the text between two positions in the note with the given text."""
        ...

    def replace_span(self, span: Span, text: str) -> None:
        """
        Replaces a `Span` in the note with the given text.
        This can be used to replace tokens within the note.
        """
        ...

    def insert_before_token(self, token: "Token", text: str, offset: int = 0) -> None:
        """
        Inserts a string into the note *before* a given token.

        NOTE: The token should originate from this note as this
        method uses the internal `Span` of the note to determine
        the insertion position.
        """
        ...

    def insert_after_token(self, token: "Token", text: str, offset: int = 0) -> None:
        """
        Insert a string into the note *after* a given token.

        NOTE: The token should originate from this note as this
        method uses the internal `Span` of the note to determine
        the insertion position.
        """
        ...

class Vault:
    """
    An Obsidian vault containing notes and attachments. The vault is indexed
    on creation and can be re-indexed with the `index` method.
    """
    path: str
    dangling_links: Dict[str, List[str]]
    ignored: Set[str]

    def __init__(self, path: str, ignore = [], ignore_file = None, create: bool = False) -> None:
        """
        Create a new vault from the given path. The path must be an existing directory.

        Args:
        - `path`: Path to the vault directory.
        - `ignore`: A list of glob patterns to ignore when indexing the vault.
        - `ignore_file`: Path to a custom ignore file.
          If not provided, the `.vault-ignore` file in the vault directory will be used.
        - `create`: Whether to create the vault directory if it does not exist.
        """
        ...

    def notes(self) -> List[Note]:
        """Get a list of all notes in the vault. Order is not guaranteed."""
        ...

    def attachments(self) -> List[Attachment]:
        """Get a list of all attachments in the vault. Order is not guaranteed."""
        ...

    def tags(self) -> List[str]:
        """Get a list of all tags in the vault. Order is not guaranteed."""
        ...

    def index(self) -> None:
        """
        Index the vault. This will clear the current index and re-index the vault.

        This is useful if you have edited, added or removed notes or attachments from the vault.
        """
        ...

    def get_notes_by_tag(self, tag: str) -> List[Note]:
        """Get all notes that have the given tag."""
        ...

    def note(self, name: str) -> Optional[Note]:
        """Get note by its name."""
        ...

    def get_note_by_name(self, name: str) -> Optional[Note]:
        """Get note by its name."""
        ...

    def get_note_by_path(self, path: str) -> Optional[Note]:
        """Get note by its path in the vault. Either absolute or relative to the vault path."""
        ...

    def add_note(self, vault_path: str, content: str, reindex: bool = False) -> str:
        """
        Add a note to the vault.

        Args:
            vault_path: The relative path of the new note within the vault.
            content: The content of the note.
            reindex: Whether to reindex the vault after adding the note.
        """
        ...

    def rename_note(self, old_name: str, new_name: str) -> Note:
        """
        Rename a note in the vault. This will update the note's name, path, and all backlinks to the note.

        Args:
            old_name: The current name of the note.
            new_name: The new name for the note.

        Returns:
            The renamed Note object.
        """
        ...

    def rename_tag(self, old_tag: str, new_tag: str) -> None:
        """
        Rename a tag in the vault. This will update all notes that have the tag.

        Args:
            old_tag: The tag to be renamed.
            new_tag: The new name for the tag.
        """
        ...

class VaultItem:
    """
    An item in an Obsidian vault can be either a note or an attachment.
    """
    class Note(VaultItem):
        """A note in the vault (markdown file)"""
        note: Note

    class Attachment(VaultItem):
        """An attachment in the vault"""
        attachment: Attachment

class ExternalLink:
    """
    Represents an external link to an external URL.

    Example:
        ```markdown
        ![alt text](https://imageimage--link.domain)
        [show_how](https://github.com/BalderHolst)
        ```
    """
    render: bool
    url: str
    show_how: str
    options: Optional[str]
    position: Optional[str]

class InternalLink:
    """
    Represents an internal link to another note.

    Example:
        ```markdown
        ![[note_name#position|display text]]
        ```
    """
    dest: str
    position: Optional[str]
    show_how: Optional[str]
    options: Optional[str]
    render: bool

class Callout:
    """
    Represents a callout block in the document.

    Example:
        ```markdown
        > [!note]- Title
        > This is a note callout.
        ```
    """
    kind: str
    title: str
    tokens: List["Token"]
    foldable: bool

class ListItem:
    """Represents a single item in a list."""
    span: Span
    indent: int
    tokens: List["Token"]

class NumericListItem:
    """Represents a single item in a numerated list."""
    span: Span
    number: int
    indent: int
    tokens: List["Token"]

class CheckListItem:
    """Represents a single item in a checklist."""
    checked: bool
    span: Span
    indent: int
    tokens: List["Token"]

class Token:
    """
    Represents a part of a note, such as text, code blocks, links, etc.

    Example - Token Stream
    A note might contain the following:
    ```markdown
    # Heading
    This is a paragraph with a [link](https://example.com).
    ```

    This would be represented as a sequence of `Token` instances:
    ```text
    - `Token.Header { level: 1, heading: "Heading" }`
    - `Token.Text { text: "This is a paragraph with a " }`
    - `Token.ExternalLink { link: ... }`
    - `Token.Text { text: "." }`
    ```

    Example - Find Headings
    To find all headings in a note, you can iterate over the tokens:
    ```python
    # Example 3: Find all headings in the "Start Here" note in the Obsidian Sandbox vault

    import ovault

    # Open the sandbox vault
    vault = ovault.Vault("./test-vaults/Obsidian Sandbox/")

    # Find a note by name
    note = vault.get_note_by_name("Start Here")

    # Get all tokens in the note
    tokens = note.tokens()

    # Iterate through tokens and print headings
    for token in tokens:
        if isinstance(token, token.Header):
            print(f"Found heading: {token.heading} at level {token.level}")

    ```
    """

    def __repr__(self) -> str:
        """String representation of the token."""
        ...

    def to_markdown(self) -> str:
        """Convert the token to a Markdown string."""
        ...

    class Frontmatter(Token):
        """
        Represents the frontmatter of a note, which is typically YAML formatted metadata.

        NOTE: This can only appear as the first token in a note.
        """
        span: Span
        yaml: str

    class Text(Token):
        """Represents a block of text in the note."""
        span: Span
        text: str

    class Tag(Token):
        """Represents a tag in the note."""
        span: Span
        tag: str

    class Header(Token):
        """
        Represents a header in the note, which can be of different levels.

        Example:
        ```text
        # First  => level = 1
        ## Second => level = 2
        ### Third => level = 3
        ```
        """
        span: Span
        level: int
        heading: str

    class Code(Token):
        """
        Represents a code block in the note.

        Example:
        ````markdown
        ```python
        def hello_world():
           print("Hello, world!")
        ```
        ````
        """
        span: Span
        lang: Optional[str]
        code: str

    class Quote(Token):
        """Represents a block quote in the note."""
        span: Span
        tokens: List["Token"]

    class InlineMath(Token):
        """Represents inline mathematical expressions in the note."""
        span: Span
        latex: str

    class DisplayMath(Token):
        """Represents display mathematical expressions in the note."""
        span: Span
        latex: str

    class Divider(Token):
        """Represents a horizontal divider in the note."""
        span: Span

    class Callout(Token):
        """Represents a callout block in the note."""
        span: Span
        callout: "Callout"

    class InternalLink(Token):
        """Represents an internal link to another note within the vault."""
        span: Span
        link: "InternalLink"

    class ExternalLink(Token):
        """Represents an external link to a URL."""
        span: Span
        link: "ExternalLink"

    class List(Token):
        """
        Represents a bulleted or numbered list in the note.

        Example:
        ```markdown
        - Item 1
        - Item 2
          - Subitem 2.1
        ```
        """
        span: Span
        items: List[ListItem]

    class NumericList(Token):
        """
        Represents a numerated list in the note.

        Example:
        ```markdown
        1. First item
        2. Second item
           1. Subitem 2.1
           2. Subitem 2.2
        ```
        """
        span: Span
        items: List[NumericListItem]

    class CheckList(Token):
        """
        Represents a checklist in the note.

        Example:
        ```markdown
        - [x] Completed item
        - [ ] Incomplete item
        ```
        """
        checked: bool
        span: Span
        indent: int
        tokens: List["Token"]

    class TemplaterCommand(Token):
        """
        Represents a Templater command in the note.

        Example:
        ```markdown
        <% tp.file.include("path/to/file.md") %>
        ```
        """
        span: Span
        command: str
