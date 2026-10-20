"""Gera favicons quadrados nítidos a partir da marca NAPI (ícone do robô)."""
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "static" / "images"

# Fundo claro: lê na aba escura do Chrome. Roxo mais aberto que a logo original.
BG = (250, 249, 255, 255)
MARK = (124, 114, 232, 255)
BORDER = (214, 208, 245, 255)


def _rounded_rect(draw, box, radius, fill):
    draw.rounded_rectangle(box, radius=radius, fill=fill)


def draw_mark(size: int) -> Image.Image:
    """Desenha o cruzamento arredondado + visor com dois losangos (olhos)."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Área útil com folga para não colar na borda do tile.
    m = size * (0.06 if size <= 32 else 0.10)
    x0, y0, x1, y1 = m, m, size - m, size - m
    w, h = x1 - x0, y1 - y0
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2

    arm = w * (0.42 if size <= 32 else 0.34)
    rad = max(1, arm * 0.42)

    # Braço horizontal e vertical (união = cruz).
    _rounded_rect(
        draw,
        [cx - w / 2, cy - arm / 2, cx + w / 2, cy + arm / 2],
        rad,
        MARK,
    )
    _rounded_rect(
        draw,
        [cx - arm / 2, cy - h / 2, cx + arm / 2, cy + h / 2],
        rad,
        MARK,
    )

    if size >= 24:
        vw, vh = w * 0.42, h * 0.22
        visor = [cx - vw / 2, cy - vh / 2, cx + vw / 2, cy + vh / 2]
        _rounded_rect(draw, visor, max(1, vh * 0.35), BG)
        eye_r = min(vw, vh) * 0.22
        gap = vw * 0.16
        for sign in (-1, 1):
            ex = cx + sign * (gap + eye_r * 0.15)
            ey = cy
            draw.polygon(
                [
                    (ex, ey - eye_r),
                    (ex + eye_r * 0.85, ey),
                    (ex, ey + eye_r),
                    (ex - eye_r * 0.85, ey),
                ],
                fill=MARK,
            )
    return img


def tile(size: int, mark: Image.Image) -> Image.Image:
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    radius = max(4, round(size * 0.22))
    bw = max(1, round(size / 28))
    draw.rounded_rectangle(
        [bw / 2, bw / 2, size - 1 - bw / 2, size - 1 - bw / 2],
        radius=radius,
        fill=BG,
        outline=BORDER,
        width=bw,
    )
    canvas.alpha_composite(mark)
    return canvas


def main():
    master = draw_mark(512)
    sizes = {
        16: "favicon-16.png",
        32: "favicon-32.png",
        48: "favicon-48.png",
        64: "favicon-64.png",
        180: "apple-touch-icon.png",
    }
    pngs = []
    for size, name in sizes.items():
        if size <= 32:
            mark = draw_mark(size)
        else:
            mark = master.resize((size, size), Image.Resampling.LANCZOS)
        out = tile(size, mark)
        path = OUT_DIR / name
        out.save(path, "PNG", optimize=True)
        pngs.append(out.convert("RGBA"))
        print("wrote", name, out.size)

    ico_path = OUT_DIR / "favicon.ico"
    pngs[0].save(
        ico_path,
        format="ICO",
        sizes=[(16, 16), (32, 32), (48, 48)],
        append_images=pngs[1:3],
    )
    print("wrote", ico_path.name)


if __name__ == "__main__":
    main()
