import layoutparser as lp
from pdf2image import convert_from_bytes
import pytesseract
import numpy as np


class OCRUtils:
    @staticmethod
    def extract_layoutparser_blocks_from_pdf_bytes(pdf_bytes: bytes) -> list[str]:
        model = lp.Detectron2LayoutModel(
            config_path='lp://PubLayNet/faster_rcnn_R_50_FPN_3x/config',
            extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.5],
            label_map={0: "Text", 1: "Title", 2: "List", 3: "Table", 4: "Figure"},
        )

        images = convert_from_bytes(pdf_bytes, dpi=300, poppler_path=r"C:\poppler\Library\bin")
        pages_text = []

        for image in images:
            image_np = np.array(image)
            layout = model.detect(image_np)

            # Organiza os blocos de texto do topo para o final
            layout = lp.Layout(sorted(layout, key=lambda b: b.block.y_1))
            blocks_text = []

            for block in layout:
                if block.type in ["Text", "Title"]:
                    segment_image = block.pad(5, 5, 5, 5).crop_image(image_np)
                    text = pytesseract.image_to_string(segment_image, lang="por").strip()
                    if text:
                        blocks_text.append(text)

            joined_text = "\n\n".join(blocks_text)
            pages_text.append(joined_text)

        return pages_text
