def simple_chunking(text, size, overlap):
    """
    Chunks the given text into segments of n characters with overlap.

    Args:
    text (str): The text to be chunked.
    size (int): The number of characters in each chunk.
    overlap (int): The number of overlapping characters between chunks.

    Returns:
    List[str]: A list of text chunks.
    """
    chunks = []  # Initialize an empty list to store the chunks

    # Loop through the text with a step size of (size - overlap)
    for i in range(0, len(text), size - overlap):
        # Append a chunk of text from index i to i + size to the chunks list
        chunks.append(text[i:i + size])

    return chunks  # Return the list of text chunks