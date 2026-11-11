#!/usr/bin/env python3
"""Prepara as fotos dos associados para o site.

Uso:
    python3 ferramentas/preparar_fotos.py ../fotos_associados

Para cada imagem da pasta de origem, recorta um quadrado enquadrado no rosto,
redimensiona para 800x800 e grava em static/img/associados/<slug>.jpg.

O nome do arquivo de origem precisa identificar a pessoa: pode ser o nome
completo ("Cecilia Nunes Vieira Lacerda da Luz.jpg"), o slug já pronto
("cecilia-nunes-vieira-lacerda-da-luz.jpg") ou o primeiro nome, desde que
não haja outro associado com o mesmo primeiro nome.

A detecção de rosto usa as cascatas Haar do OpenCV. Se o OpenCV não estiver
instalado ou as cascatas não forem encontradas, o recorte cai para o
enquadramento superior, que é o que costuma funcionar em retrato vertical.
"""
import sys, os, re, unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DESTINO = RAIZ / "static" / "img" / "associados"
LADO = 800

def slug(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", t.lower())).strip("-")

def associados():
    import yaml
    d = yaml.safe_load((RAIZ / "data" / "associados.yml").read_text(encoding="utf-8"))
    return {slug(p["nome"]): p["nome"] for g in d["grupos"] for p in g["pessoas"]}

def casar(nome_arquivo, mapa):
    s = slug(Path(nome_arquivo).stem)
    if s in mapa:
        return s
    candidatos = [k for k in mapa if k.startswith(s + "-") or k == s]
    if len(candidatos) == 1:
        return candidatos[0]
    if len(candidatos) > 1:
        print(f"  ambíguo: {nome_arquivo} casa com {', '.join(candidatos)} — renomeie o arquivo")
    return None

def detectar_rosto(caminho):
    """Devolve (x, y, w, h) do rosto, ou None."""
    try:
        import cv2
    except ImportError:
        return None
    pasta = Path(cv2.data.haarcascades) if hasattr(cv2, "data") else None
    nomes = ["haarcascade_frontalface_default.xml", "haarcascade_frontalface_alt2.xml"]
    cascatas = [str(pasta / n) for n in nomes if pasta and (pasta / n).is_file()]
    if not cascatas or not hasattr(cv2, "CascadeClassifier"):
        return None
    img = cv2.imread(str(caminho))
    g = cv2.equalizeHist(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))
    h, w = g.shape
    caixas = []
    for c in cascatas:
        d = cv2.CascadeClassifier(c)
        for esc in (1.05, 1.1, 1.2):
            for viz in (4, 6):
                for r in d.detectMultiScale(g, esc, viz, minSize=(int(min(h, w) * 0.08),) * 2):
                    caixas.append(tuple(map(int, r)))
    if not caixas:
        return None

    def iou(a, b):
        ax, ay, aw, ah = a; bx, by, bw, bh = b
        x1, y1 = max(ax, bx), max(ay, by)
        x2, y2 = min(ax + aw, bx + bw), min(ay + ah, by + bh)
        i = max(0, x2 - x1) * max(0, y2 - y1)
        return i / (aw * ah + bw * bh - i + 1e-9)

    grupos = []
    for b in caixas:
        for gr in grupos:
            if iou(gr[0], b) > 0.3:
                gr.append(b); break
        else:
            grupos.append([b])
    maior = max(grupos, key=len)
    n = len(maior)
    return tuple(sum(v[i] for v in maior) // n for i in range(4))

def preparar(origem, destino):
    from PIL import Image
    im = Image.open(origem).convert("RGB")
    W, H = im.size
    rosto = detectar_rosto(origem)
    if rosto:
        x, y, w, h = rosto
        cx, cy = x + w // 2, y + h // 2
        S = min(int(h * 2.6), W, H)
        esq = max(0, min(W - S, cx - S // 2))
        topo = max(0, min(H - S, int(cy - 0.42 * S)))
        como = f"rosto {w}px"
    else:
        S = min(W, H)
        esq = (W - S) // 2
        topo = 0 if H > W else (H - S) // 2   # retrato: ancora no topo
        como = "sem rosto detectado, enquadramento superior"
    im.crop((esq, topo, esq + S, topo + S)).resize((LADO, LADO), Image.LANCZOS) \
      .save(destino, "JPEG", quality=88, optimize=True, progressive=True)
    return como, S

def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    origem = Path(sys.argv[1]).expanduser()
    if not origem.is_dir():
        print(f"pasta não encontrada: {origem}"); sys.exit(1)
    DESTINO.mkdir(parents=True, exist_ok=True)
    mapa = associados()
    feitos = 0
    for arq in sorted(origem.iterdir()):
        if arq.suffix.lower() not in (".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"):
            continue
        s = casar(arq.name, mapa)
        if not s:
            print(f"  ignorado: {arq.name} — não encontrei esse nome no quadro de associados")
            continue
        saida = DESTINO / f"{s}.jpg"
        como, lado = preparar(arq, saida)
        kb = saida.stat().st_size // 1024
        print(f"  {mapa[s]:<42} {arq.name} -> {saida.name}  ({como}, recorte {lado}px, {kb} KB)")
        feitos += 1
    print(f"\n{feitos} foto(s) preparada(s) em {DESTINO.relative_to(RAIZ)}")
    print("Rode 'python3 build.py' e confira o resultado antes de publicar.")

if __name__ == "__main__":
    main()
