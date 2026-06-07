from io import BytesIO
from pathlib import Path

from PIL import Image

from env import APPLIED_DIR


def save_cropped_image(
    content: bytes,
    *,
    width: int,
    height: int,
    left: int,
    top: int,
    crop_width: int,
    crop_height: int,
    original_name: str,
) -> Path:
    APPLIED_DIR.mkdir(parents=True, exist_ok=True)

    with Image.open(BytesIO(content)) as img:
        cropped = img.crop((left, top, left + crop_width, top + crop_height))
        if width > 0 and height > 0:
            cropped = cropped.resize((width, height), Image.Resampling.LANCZOS)

        stem = Path(original_name).stem
        out = APPLIED_DIR / f"{stem}-{width}x{height}.png"
        cropped.save(out, format="PNG")

    return out
