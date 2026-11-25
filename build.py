#!/usr/bin/env python3
"""Gera o app (site instalável) de um cliente a partir de um modelo.

Uso:
    python3 build.py clientes/exemplo saida/exemplo
    python3 build.py clientes/exemplo saida/exemplo --modelo velvet

A pasta do cliente precisa ter config.json e, opcionalmente, uma pasta fotos/.
A pasta de saída fica pronta para subir no GitHub Pages.
"""
import argparse, json, re, shutil, subprocess, sys, time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent


def carregar_modelos():
    cmd = ["node", "-e", "console.log(JSON.stringify(require('./src/models.js').MODELS))"]
    r = subprocess.run(cmd, cwd=RAIZ, capture_output=True, text=True, check=True)
    return {m["id"]: m for m in json.loads(r.stdout)}


def familia(css_font):
    m = re.search(r"'([^']+)'", css_font)
    return m.group(1) if m else None


def url_fontes(m):
    pesos = {}
    f = familia(m["hf"])
    if f:
        pesos.setdefault(f, set()).add(int(m["hw"]))
    b = familia(m["bf"])
    if b:
        pesos.setdefault(b, set()).update({400, 500, 600, 700})
    partes = []
    for nome, ps in pesos.items():
        partes.append("family=%s:wght@%s" % (nome.replace(" ", "+"), ";".join(str(p) for p in sorted(ps))))
    return "https://fonts.googleapis.com/css2?" + "&".join(partes) + "&display=swap"


def icone(tamanho, fundo, cor, letras, destino):
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new("RGB", (tamanho, tamanho), fundo)
    d = ImageDraw.Draw(img)
    margem = int(tamanho * 0.18)
    d.ellipse([margem, margem, tamanho - margem, tamanho - margem], outline=cor, width=max(4, tamanho // 40))
    fonte = None
    for caminho in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                    "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf"):
        if Path(caminho).exists():
            fonte = ImageFont.truetype(caminho, int(tamanho * 0.30))
            break
    if fonte is None:
        fonte = ImageFont.load_default(int(tamanho * 0.30))
    box = d.textbbox((0, 0), letras, font=fonte)
    w, h = box[2] - box[0], box[3] - box[1]
    d.text(((tamanho - w) / 2 - box[0], (tamanho - h) / 2 - box[1]), letras, font=fonte, fill=cor)
    img.save(destino)


def iniciais(nome):
    palavras = [p for p in re.sub(r"[^\w\s]", "", nome, flags=re.U).split() if p]
    if not palavras:
        return "?"
    return (palavras[0][0] + (palavras[1][0] if len(palavras) > 1 else "")).upper()


SW = """const V='%(v)s';
self.addEventListener('install',e=>{e.waitUntil(caches.open(V).then(c=>c.addAll(['./','index.html','manifest.webmanifest','icons/icon-192.png'])));self.skipWaiting()});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(x=>x!==V).map(x=>caches.delete(x)))));self.clients.claim()});
self.addEventListener('fetch',e=>{
  if(e.request.method!=='GET')return;
  e.respondWith(fetch(e.request).then(r=>{
    if(new URL(e.request.url).origin===location.origin){const c=r.clone();caches.open(V).then(x=>x.put(e.request,c))}
    return r;
  }).catch(()=>caches.match(e.request)));
});
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cliente")
    ap.add_argument("saida")
    ap.add_argument("--modelo")
    a = ap.parse_args()

    pasta = Path(a.cliente)
    cfg = json.loads((pasta / "config.json").read_text(encoding="utf-8"))
    modelos = carregar_modelos()
    mid = a.modelo or cfg.get("modelo")
    if mid not in modelos:
        sys.exit("Modelo '%s' não existe. Opções: %s" % (mid, ", ".join(modelos)))
    m = modelos[mid]

    avisos = [k for k in ("nome", "whatsapp", "endereco", "instagram") if not cfg.get(k)]
    if avisos:
        print("Aviso: faltam no config.json:", ", ".join(avisos))

    nome = cfg.get("nome") or m["name"]
    saida = Path(a.saida)
    if saida.exists():
        shutil.rmtree(saida)
    (saida / "icons").mkdir(parents=True)

    if (pasta / "fotos").is_dir():
        shutil.copytree(pasta / "fotos", saida / "fotos")

    html = (RAIZ / "src" / "template.html").read_text(encoding="utf-8")
    app = json.dumps({"model": m, "cfg": cfg}, ensure_ascii=False).replace("</", "<\\/")
    descricao = cfg.get("descricao") or ("%s. Agende seu horário pelo app." % nome)
    html = (html.replace("__TITLE__", nome.replace("<", ""))
                .replace("__DESCRIPTION__", descricao.replace('"', "'"))
                .replace("__THEME_COLOR__", m["bg"])
                .replace("__FONTS__", url_fontes(m))
                .replace("__APP__", app))
    (saida / "index.html").write_text(html, encoding="utf-8")

    manifest = {
        "name": nome, "short_name": nome[:12], "start_url": "./", "scope": "./",
        "display": "standalone", "lang": "pt-BR",
        "background_color": m["bg"], "theme_color": m["bg"],
        "icons": [
            {"src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any maskable"},
            {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"},
        ],
    }
    (saida / "manifest.webmanifest").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    (saida / "sw.js").write_text(SW % {"v": "v" + str(int(time.time()))}, encoding="utf-8")

    letras = cfg.get("iniciais") or iniciais(nome)
    for t in (192, 512):
        icone(t, m["bg"], m["ac"], letras, saida / "icons" / ("icon-%d.png" % t))
    (saida / ".nojekyll").write_text("", encoding="utf-8")
    print("Pronto: %s (modelo %s, %s)" % (saida, mid, nome))


if __name__ == "__main__":
    main()
