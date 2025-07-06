from typing import List

from src.page import Page



class Document:
    def __init__(self, name, pages):
        self.name = name

        self.pages: List[Page] = pages

        self.text = None

        self.pages_texts: List[str] = []
        self.pages_tables: List = []
        self.pages_images: List = []

    def preprocess_pages(self, llm_handler):
        # TODO: Multiprocessing for page preprocessing

        for page in self.pages:
            text, tables, images = page.preprocess(llm_handler)

            self.pages_texts += [text]
            self.text = " ".join(self.pages_texts).strip()
            self.pages_tables += tables
            self.pages_images += images

    def get_text(self):
        return self.text if self.text else ""

    def get_tables(self):
        return self.tables if self.tables else []

    def get_images(self):
        return self.images if self.images else []
