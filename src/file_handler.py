from abc import abstractmethod, ABC
from typing import Optional, List

from PyPDF2 import PdfReader
import pymupdf
import docx2txt

import json
import logging
import time
from pathlib import Path
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    AcceleratorDevice,
    AcceleratorOptions,
    PdfPipelineOptions
)
from docling.document_converter import DocumentConverter, PdfFormatOption

from src.document import Document, Page


class FileHandler(ABC):
    # Abstract class for handling different file types
    # Supported file types: PDF, DOCX, TXT, PNG(could be converted from JPEG, etc.)
    # Not supported file types: PPTX, XLSX, CSV, HTML

    SUPPORTED_FILE_TYPES = Optional['.pdf', '.docx', '.txt', '.png', '.jpg']

    def __init__(self, device):
        self.device = device

    def read_files(self, paths) -> List[Document]:
        documents: List[Document] = []
        for path in paths:
            if path.suffix in self.SUPPORTED_FILE_TYPES:
                document = self.read_file(path)
                documents.append(document)
        return documents

    def read_file(self, path) -> Document:
        document = None
        if path.suffix == '.pdf':
            document = self.read_pdf(path)
        elif path.suffix == '.docx':
            document = self.read_docx(path)
        elif path.suffix == '.txt':
            document = self.read_txt(path)
        elif path.suffix == '.png':
            document = self.read_png(path)
        elif path.suffix == '.jpg':
            document = self.read_image(path)
        return document

    @abstractmethod
    def read_pdf(self, path) -> Document:
        raise NotImplementedError('PDF read method not implemented')

    @abstractmethod
    def read_docx(self, path) -> Document:
        raise NotImplementedError('DOCX read method not implemented')

    @abstractmethod
    def read_txt(self, path) -> Document:
        raise NotImplementedError('TXT read method not implemented')

    @abstractmethod
    def read_png(self, path) -> Document:
        raise NotImplementedError('PNG read method not implemented')

    @abstractmethod
    def read_image(self, path) -> Document:
        raise NotImplementedError('Image read method not implemented')

    def get_supported_file_types(self):
        return self.__dict__.items()



class DoclingHandler(FileHandler):

    ENGINE = 'EasyOCR'

    def __init__(self, device):
        super().__init__(device)

        docling_pipeline_options = PdfPipelineOptions()
        docling_pipeline_options.do_ocr = True
        docling_pipeline_options.do_table_structure = True
        docling_pipeline_options.do_formula_enrichment = False
        docling_pipeline_options.generate_page_images = True
        docling_pipeline_options.generate_picture_images = False

        docling_pipeline_options.table_structure_options.do_cell_matching = True

        docling_pipeline_options.ocr_options.lang = ["ru", "en"]


        docling_pipeline_options.accelerator_options = AcceleratorOptions(
            num_threads=4, device=AcceleratorDevice.CUDA if self.device == 'cuda' else AcceleratorDevice.CPU
        )

        self.docling_document_converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=docling_pipeline_options)
            }
        )

    def read_pdf(self, path):
        pages: List[Page] = []

        pymupdf_doc = pymupdf.Document(path)
        page_count = pymupdf_doc.page_count

        for page_num in range(1, page_count + 1):
            # Extracting text from PDF using PyMuPDF

            pymupdf_page = pymupdf_doc[page_num]

            raw_text = pymupdf_page.get_text()

            # Extracting text with tables(markdown)/page image from PDF using docling

            docling_conversion_result = self.docling_document_converter.convert(path, page_range=(page_num, page_num))

            page_image = docling_conversion_result.document.pages[0].page_image
            markdown = docling_conversion_result.document.export_to_markdown()
            # TODO: Also could be added raw tables

            page: Page = Page(raw_text, page_image, markdown)

            pages.append(page)

        document = Document(pages, path.name)

        # TODO: Multiprocessing for page preprocessing
        return document

    def read_docx(self, path):
        text = docx2txt.process(path)
        return text

    def read_file(self, path):
        if '.pdf' in path:
            return FileHandler.read_pdf(path)
        elif '.docx' in path:
            return FileHandler.read_docx(path)
        return None
