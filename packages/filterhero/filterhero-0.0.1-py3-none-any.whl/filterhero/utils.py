def load_html(path: str) -> str:
    """Read a local HTML file and return its contents as a string (UTF-8)."""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def read_md(path: str) -> str:
    """
    Read a markdown file and return its contents as a string (UTF-8).
    
    Parameters
    ----------
    path : str
        Path to the markdown file to read
        
    Returns
    -------
    str
        The contents of the markdown file
        
    Raises
    ------
    FileNotFoundError
        If the file does not exist
    IOError
        If there's an error reading the file
        
    Examples
    --------
    >>> content = read_md("samples/example.md")
    >>> print(content[:100])  # Print first 100 characters
    """
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()
    



def prepare_numbered_content(lines, max_line_length=None, line_format="[{n}]"):
        """
        Convert lines to numbered content for LLM processing.
        
        Parameters
        ----------
        lines : list
            List of text lines to number
        max_line_length : int or None
            Maximum characters per line before truncation. 
            If None, no truncation is applied.
            Default None means show full lines.
        line_format : str
            Format string for line numbers. Use {n} for the line number.
            Examples: "[{n}]" → "[1]", "L{n}:" → "L1:", "{n:04d}|" → "0001|"
            Default: "[{n}]"
        
        Returns
        -------
        str
            Numbered content with optional truncation for LLM processing
        """
        numbered_lines = []
        
        for i, line in enumerate(lines, 1):
            # Optionally truncate long lines
            if max_line_length and len(line) > max_line_length:
                display_line = f"{line[:max_line_length]}..."
            else:
                display_line = line
            
            # Format the line number
            line_prefix = line_format.format(n=i)
            numbered_lines.append(f"{line_prefix} {display_line}")
        
        return '\n'.join(numbered_lines)