from abc import abstractmethod, ABC
from typing import List

import pymupdf
#import docx2txt

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

    SUPPORTED_FILE_TYPES = ['.pdf', '.docx', '.txt', '.png', '.jpg']

    def __init__(self, device):
        self.device = device

    def read_files(self, paths, llm_handler=None) -> List[Document]:
        documents: List[Document] = []
        for path in paths:
            if path.suffix in self.SUPPORTED_FILE_TYPES:
                document = self.read_file(path, llm_handler)
                documents.append(document)
        return documents

    def read_file(self, path, llm_handler=None) -> Document:
        document = None
        if path.suffix == '.pdf':
            document = self.read_pdf(path, llm_handler)
        elif path.suffix == '.docx':
            document = self.read_docx(path, llm_handler)
        elif path.suffix == '.txt':
            document = self.read_txt(path, llm_handler)
        elif path.suffix == '.png':
            document = self.read_png(path, llm_handler)
        elif path.suffix == '.jpg':
            document = self.read_image(path, llm_handler)
        return document

    @abstractmethod
    def read_pdf(self, path, llm_handler=None) -> Document:
        raise NotImplementedError('PDF read method not implemented')

    @abstractmethod
    def read_docx(self, path, llm_handler=None) -> Document:
        raise NotImplementedError('DOCX read method not implemented')

    #@abstractmethod
    #def read_txt(self, path, llm_handler=None) -> Document:
    #    raise NotImplementedError('TXT read method not implemented')
#
    #@abstractmethod
    #def read_png(self, path, llm_handler=None) -> Document:
    #    raise NotImplementedError('PNG read method not implemented')
#
    #@abstractmethod
    #def read_image(self, path, llm_handler=None) -> Document:
    #    raise NotImplementedError('Image read method not implemented')

    def get_supported_file_types(self):
        return self.__dict__.items()



class DoclingHandler(FileHandler):

    ENGINE = 'EasyOCR'
    SUPPORTED_FILE_TYPES = ['.pdf', '.docx']

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

    def read_pdf(self, path, llm_handler=None):
        pages: List[Page] = []

        pymupdf_doc = pymupdf.Document(path)
        page_count = pymupdf_doc.page_count

        # TODO: Multiprocessing for page extracting
        for page_num in range(1, page_count + 1):
            # Extracting text from PDF using PyMuPDF

            pymupdf_page = pymupdf_doc[page_num - 1]

            raw_text = pymupdf_page.get_text()

            # Extracting text with tables(markdown)/page image from PDF using docling
            docling_conversion_result = self.docling_document_converter.convert(path, page_range=(page_num, page_num))

            page_image = str(docling_conversion_result.document.pages[page_num].image.uri).replace('data:image/png;base64,', '')
            markdown = docling_conversion_result.document.export_to_markdown()
            tables_raw = [table.export_to_dataframe().to_markdown() for table in docling_conversion_result.document.tables]
            # TODO: Also could be added raw tables

            page: Page = Page(raw_text, page_image, markdown, tables_raw=tables_raw)

            pages.append(page)

        document = Document(path.name, pages)
        if llm_handler:
            document.preprocess_pages(llm_handler)

        return document

    def read_docx(self, path):
        text = docx2txt.process(path)
        return text

    #def read_file(self, path):
    #    if '.pdf' in path:
    #        return FileHandler.read_pdf(path)
    #    elif '.docx' in path:
    #        return FileHandler.read_docx(path)
    #    return None
