import os
from pathlib import Path
from typing import ClassVar

import cv2
import pytesseract
import requests

from macuitest.config.constants import Region
from macuitest.lib.core import wait_condition
from macuitest.lib.elements.ui.monitor import monitor


class OCRManager:
    ocr_engine_mode: ClassVar[int] = 3
    page_segmentation_mode: ClassVar[int] = 6
    tesseract_config: ClassVar[str] = f'--oem {ocr_engine_mode} --psm {page_segmentation_mode}'

    def __init__(self, language: str = 'eng'):
        self.language = language
        self.trained_data = f'{self.language}.traineddata'
        self.trained_data_path: Path = Path('/usr/local/share/tessdata')
        self.__assert_trained_data_present()

    def wait_text(self, text: str, where: Region, timeout: int = 10) -> bool:
        return wait_condition(lambda: self.recognize(region=where) == text, timeout=timeout)

    def recognize(self, region: Region) -> str:
        img_gray = cv2.cvtColor(monitor.snapshot, cv2.COLOR_BGR2GRAY)
        _, img_bw = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        payload = pytesseract.image_to_string(
            img_gray[region.y1:region.y2, region.x1:region.x2],
            config=self.tesseract_config, lang=self.language
        )
        return os.linesep.join([s for s in payload.splitlines() if s])

    def __assert_trained_data_present(self):
        if not self.trained_data_path.joinpath(self.trained_data).exists():
            Path(self.trained_data_path).mkdir(parents=True, exist_ok=True)
            response = requests.get(f'https://github.com/tesseract-ocr/tessdata_best/raw/master/{self.trained_data}')
            with open(self.trained_data_path.joinpath(self.trained_data), 'wb') as dataset:
                dataset.write(response.content)


ocr_manager = OCRManager()