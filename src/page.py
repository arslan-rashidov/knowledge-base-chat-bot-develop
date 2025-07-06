from src.llm_handler import LLMHandler


class Page:
    def __init__(self, raw_text, page_image, markdown, save_dir_path=None, tables_raw=None, images=None):
        raw_text = raw_text.replace("-\n", "").replace("- ", "")
        self.raw_text = raw_text

        self.page_image = page_image
        self.markdown = markdown

        self.tables = []
        self.tables_raw = tables_raw if tables_raw else []
        self.tables_description = []

        self.images = images if images else []
        self.images_description = []

        self.save_dir_path = save_dir_path
        self.save_path = None

    def get_text(self):
        return self.raw_text

    def get_tables(self):
        return self.tables

    def get_images(self):
        return self.images

    def preprocess(self, llm_handler: LLMHandler):
        for table_raw in self.tables_raw:
            table_description = llm_handler.extract_table_description(image=self.page_image,
                                                                      page_text=self.markdown,
                                                                      table_raw=table_raw)
            self.tables_description.append(table_description)
            self.tables.append({"raw": table_raw, "description": table_description})

        #images = llm_handler.extract_image_description(image=self.page_image, page_text=self.raw_text)
        #self.images = images

        return self.get_text(), self.get_tables(), self.get_images()



