from dataclasses import dataclass

from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

_HEADERS_TO_SPLIT_ON = [("##", "section")]
_CHUNK_SIZE = 800
_CHUNK_OVERLAP = 100


@dataclass
class Chunk:
    text: str
    section: str | None


def chunk_markdown(body: str) -> list[Chunk]:
    """Découpe un document en chunks : d'abord par section (`##`), puis par taille."""
    header_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=_HEADERS_TO_SPLIT_ON)
    sections = header_splitter.split_text(body)

    size_splitter = RecursiveCharacterTextSplitter(chunk_size=_CHUNK_SIZE, chunk_overlap=_CHUNK_OVERLAP)

    chunks: list[Chunk] = []
    for section in sections:
        section_title = section.metadata.get("section")
        for piece in size_splitter.split_text(section.page_content):
            chunks.append(Chunk(text=piece, section=section_title))

    return chunks
