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
        
        if not source.exists():
            raise FileNotFoundError(f"Input PDF does not exist: {source}")
        if not source.is_file():
            raise NotADirectoryError(f"Input is not a file: {source}")
        if not source.suffix.lower() == ".pdf":
            raise ValueError(f"Input is not a PDF file: {source}")
        
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
        
        if not source.exists():
            raise FileNotFoundError(f"Input folder does not exist: {source}")
        if not source.is_dir():
            raise NotADirectoryError(f"Input is not a directory: {source}")
        if not any(source.iterdir()):
            raise ValueError(f"Input folder is empty: {source}")
        
        image_files = [
            f for f in source.iterdir()
            if f.suffix.lower() in [".jpg", ".jpeg", ".png"]
        ]
        if not image_files:
            raise ValueError(f"No valid image files found in folder. Supported formats: .jpg, .jpeg, .png")
        return sorted(image_files)

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