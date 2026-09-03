"""Собирает index.html из src/site-template.html, встраивая фото из img/ как data-URI.

Запуск:  python build.py
Метки вида @@имя-файла@@ в шаблоне заменяются на img/имя-файла.jpg.
"""
import base64
import re
from pathlib import Path

ROOT = Path(__file__).parent
src = (ROOT / "src" / "site-template.html").read_text(encoding="utf-8")

# Статичные <img src="@@id@@"> -> data-img, JS-строки '@@id@@' -> 'id'
src = re.sub(r'src="@@([\w-]+)@@"', r'data-img="\1"', src)
src = re.sub(r"'@@([\w-]+)@@'", r"'\1'", src)

# В карточках и галерее фото берутся из словаря IMG
for a, b in [
    ('src="${p.imgs[0][0]}"', 'src="${IMG[p.imgs[0][0]]}"'),
    ('src="${p.imgs[1][0]}"', 'src="${IMG[p.imgs[1][0]]}"'),
    ('src="${p.imgs[idx][0]}"', 'src="${IMG[p.imgs[idx][0]]}"'),
    ('src="${im[0]}"', 'src="${IMG[im[0]]}"'),
]:
    src = src.replace(a, b)

ids = sorted(
    set(re.findall(r'data-img="([\w-]+)"', src))
    | set(re.findall(r"\['([\w-]{20,})',", src))
)
img = {
    i: "data:image/jpeg;base64,"
    + base64.b64encode((ROOT / "img" / f"{i}.jpg").read_bytes()).decode()
    for i in ids
}
blob = (
    "<script>const IMG=" + repr(img).replace("'", '"') + ";"
    'document.querySelectorAll("[data-img]").forEach(el=>{el.src=IMG[el.dataset.img]});'
    "</script>\n"
)
src = src.replace("<script>\nconst P = [", blob + "<script>\nconst P = [")

out = ROOT / "index.html"
out.write_text(src, encoding="utf-8")
print(f"{out.name}: {len(ids)} фото, {out.stat().st_size / 1e6:.2f} МБ")
