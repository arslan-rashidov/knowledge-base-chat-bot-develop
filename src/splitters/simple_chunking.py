import spacy
import src.spacy.ru2


def dynamic_chunking(text, max_chunk_size=200):
    nlp = spacy.load('ru2_combined_400ks_96')
    nlp.add_pipe(nlp.create_pipe('sentencizer'), first=True)

    doc = nlp(text)
    chunks = []
    current_chunk = []
    current_size = 0

    for sent in doc.sents:
        if current_size + len(sent.text) > max_chunk_size:
            chunks.append(" ".join(current_chunk))
            current_chunk = [sent.text]
            current_size = len(sent.text)
        else:
            current_chunk.append(sent.text)
            current_size += len(sent.text)

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks