from abc import ABC, abstractmethod
from pathlib import Path
from typing import List
from config.log_config import LoggingConfig
from pdf2image import convert_from_path

console = LoggingConfig().console

class BaseHandler(ABC):
    """Abstract base class for input handlers."""
    def __init__(self):
        self.console = console
    
    @abstractmethod
    def extract_content(self, source: Path):
        pass

class PDFHandler(BaseHandler):
    """Handler for PDF files."""   
    def extract_content(self, source: Path) -> List[Path]:
        self.console.print(f"Input PDF: {source}", style="info")
        image_paths = self.pdf_to_images(source)
        return image_paths

    def pdf_to_images(self, source: Path) -> List[Path]:
        images = convert_from_path(str(source))
        image_paths = []
        for i, img in enumerate(images):
            img_path = f"{source.stem}/{source.stem}_page_{i+1}.jpg"
            img.save(img_path, "JPEG")
            image_paths.append(img_path)
        return image_paths

class ImageHandler(BaseHandler):
    """Handler for folder of images."""
    def extract_content(self, source: Path) -> List[Path]:
        self.console.print(f"Input folder: {source}", style="info")
        return sorted([
            f for f in source.iterdir()
            if f.suffix.lower() in [".jpg", ".jpeg", ".png"]
        ])  

class InputHandler:
    """Input handler for different types of files."""
    def __init__(self):
        self.handlers = {
            '.pdf': PDFHandler(),
            '': ImageHandler(), # folder of images
        }

    def extract(self, source: Path):
        """Extract content from the given source Path."""
        handler = self.handlers.get(source.suffix)
        if not handler:
            raise ValueError(f"No handler available for source type: {source.suffix}")
        return handler.extract_content(source)