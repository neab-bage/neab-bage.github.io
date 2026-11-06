#!/usr/bin/env python3
"""Gerador do site do NEAB — Núcleo dos Engenheiros e Arquitetos de Bagé.

Uso:
    python build.py            # gera a pasta dist/
    python build.py --serve    # gera e abre em http://localhost:8000

Conteúdo:
    data/site.yml       dados do núcleo: finalidade, governança, diretoria, parceiros, documentos
    data/agenda.yml     atividades (separadas em "próximas" e "realizadas" pela data)
    noticias/*.md       uma notícia por arquivo (Markdown com cabeçalho YAML)
    templates/          modelos HTML (Jinja2)
    static/             CSS, JS, imagens, documentos em PDF
"""
import argparse
import datetime as dt
import functools
import http.server
import re
import shutil
import socketserver
from pathlib import Path
from zoneinfo import ZoneInfo

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).parent
DIST = ROOT / "dist"
TZ = ZoneInfo("America/Sao_Paulo")

MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
         "agosto", "setembro", "outubro", "novembro", "dezembro"]
MESES_ABREV = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
DIAS_SEMANA = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira",
               "sexta-feira", "sábado", "domingo"]


def data_br(d):
    return f"{d.day} de {MESES[d.month - 1]} de {d.year}"


def hora_br(h):
    """'19:00' -> '19h', '19:30' -> '19h30'."""
    hh, mm = str(h).split(":")
    return f"{int(hh)}h" + ("" if mm == "00" else mm)


def md(texto):
    return markdown.markdown(texto or "", extensions=["extra", "sane_lists"])


# ---------------------------------------------------------------- dados

def carregar_site():
    with open(ROOT / "data" / "site.yml", encoding="utf-8") as f:
        site = yaml.safe_load(f)
    hoje = dt.datetime.now(TZ).date()
    f = site.get("fundacao", {})
    if f.get("ano"):
        site["idade"] = hoje.year - int(f["ano"])
    contato = site["contato"] = site.get("contato") or {}
    insta = (contato.get("instagram") or "").strip()
    usuario = insta.split("?")[0].split("#")[0].rstrip("/").rsplit("/", 1)[-1].lstrip("@") if insta else ""
    contato["instagram_user"] = f"@{usuario}" if usuario else ""
    logos = site.get("logos_institucionais") or {}
    for item in logos.get("itens") or []:
        arq = ROOT / "static" / "img" / "logos" / (item.get("arquivo") or "")
        item["tem_imagem"] = bool(item.get("arquivo")) and arq.is_file()
        if not item["tem_imagem"]:
            print(f"Aviso: logotipo de {item.get('nome')} não encontrado em static/img/logos/; exibindo o nome.")
    return site


def slug(texto):
    """'Ana Lúcia Kalil Sarmento' -> 'ana-lucia-kalil-sarmento' (nome do arquivo da foto)."""
    import unicodedata
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def carregar_associados():
    """Lê data/associados.yml e resolve a foto de cada associado, se houver.

    A foto vai em static/img/associados/<slug-do-nome>.jpg (ou .png/.webp). Quando não existe,
    o site mostra as iniciais no lugar — nenhuma imagem quebrada.
    """
    arq = ROOT / "data" / "associados.yml"
    if not arq.exists():
        return None
    dados = yaml.safe_load(arq.read_text(encoding="utf-8")) or {}
    pasta = ROOT / "static" / "img" / "associados"
    faltando = 0
    for g in dados.get("grupos", []):
        g["slug"] = slug(g["area"])
        g["total"] = len(g.get("pessoas", []))
        for p in g.get("pessoas", []):
            s = p.get("foto") or slug(p["nome"])
            achou = None
            for ext in (".jpg", ".jpeg", ".png", ".webp"):
                if (pasta / (s + ext)).is_file():
                    achou = s + ext
                    break
            p["foto_arquivo"] = achou
            p["slug"] = s
            partes = [x for x in p["nome"].split() if len(x) > 2]
            p["iniciais"] = (partes[0][0] + partes[-1][0]).upper() if len(partes) > 1 else p["nome"][:2].upper()
            if not achou:
                faltando += 1
    pessoas = {}
    for g in dados.get("grupos", []):
        for p in g.get("pessoas", []):
            reg = pessoas.setdefault(p["slug"], dict(p, areas=[]))
            reg["areas"].append(g["area"])
            if p.get("registro") and not reg.get("registro"):
                reg["registro"] = p["registro"]
            p["ficha"] = p["slug"]
    dados["pessoas"] = sorted(pessoas.values(), key=lambda p: p["slug"])
    if faltando:
        print(f"Aviso: {faltando} associado(s) sem foto em static/img/associados/; exibindo as iniciais.")
    return dados


def carregar_gestoes():
    """Lê data/gestoes/*.yml — um arquivo por gestão. Arquivos iniciados por _ são ignorados."""
    pasta = ROOT / "data" / "gestoes"
    gestoes = []
    for arq in sorted(pasta.glob("*.yml")) if pasta.exists() else []:
        if arq.name.startswith("_"):
            continue
        g = yaml.safe_load(arq.read_text(encoding="utf-8")) or {}
        g["arquivo"] = arq.name
        gestoes.append(g)
    gestoes.sort(key=lambda g: g.get("inicio") or 0, reverse=True)
    return gestoes


def carregar_formacao():
    """Lê data/formacao.yml e agrupa cursos e palestras por ano, do mais recente ao mais antigo."""
    arq = ROOT / "data" / "formacao.yml"
    itens = (yaml.safe_load(arq.read_text(encoding="utf-8")) or []) if arq.exists() else []
    anos = {}
    for x in itens:
        anos.setdefault(x.get("ano") or 0, []).append(x)
    com_ano = [{"ano": a, "itens": anos[a]} for a in sorted((k for k in anos if k), reverse=True)]
    if 0 in anos:  # sem ano definido: vai para o fim, rotulado
        com_ano.append({"ano": None, "rotulo": "Ano a confirmar", "itens": anos[0]})
    return com_ano


def carregar_agenda(hoje):
    """Lê data/agenda.yml e separa em próximas e realizadas (data no fuso de Brasília)."""
    arq = ROOT / "data" / "agenda.yml"
    itens = (yaml.safe_load(arq.read_text(encoding="utf-8")) or []) if arq.exists() else []
    for a in itens:
        d = a["data"]
        if isinstance(d, str):
            d = dt.date.fromisoformat(d)
        a["data"] = d
        a["dia"], a["mes"] = d.day, MESES_ABREV[d.month - 1]
        a["data_br"] = data_br(d)
        a["dia_semana"] = DIAS_SEMANA[d.weekday()]
        a["horario"] = (hora_br(a["inicio"]) + (f" às {hora_br(a['fim'])}" if a.get("fim") else "")) if a.get("inicio") else ""
        a["html"] = md(a.get("descricao"))
        a["futura"] = d >= hoje
    proximas = sorted([a for a in itens if a["futura"]], key=lambda a: (a["data"], a.get("inicio") or ""))
    realizadas = sorted([a for a in itens if not a["futura"]], key=lambda a: a["data"], reverse=True)
    return proximas, realizadas


def ics_atividade(a):
    """Arquivo .ics (calendário) de uma atividade. Horário de Brasília convertido para UTC."""
    def utc(d, h):
        hh, mm = map(int, str(h).split(":"))
        return dt.datetime(d.year, d.month, d.day, hh, mm, tzinfo=TZ).astimezone(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    def esc(t):
        return str(t).replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")

    desc = [a.get("resumo", "")]
    if a.get("link"):
        desc.append("Link: " + a["link"])
    if a.get("inscricao"):
        desc.append("Inscrição: " + a["inscricao"])
    ini, fim = a.get("inicio", "19:00"), a.get("fim")
    if not fim:  # sem horário de término: 1 hora
        hh, mm = map(int, str(ini).split(":"))
        fim = f"{min(hh + 1, 23):02d}:{mm:02d}"
    linhas = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//NEAB//Agenda//PT-BR", "CALSCALE:GREGORIAN",
              "BEGIN:VEVENT", f"UID:{a['id']}@neab-bage.github.io",
              "DTSTAMP:" + dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
              *(["DTSTART;VALUE=DATE:" + a["data"].strftime("%Y%m%d"),
                 "DTEND;VALUE=DATE:" + (a["data"] + dt.timedelta(days=1)).strftime("%Y%m%d")]
                if not a.get("inicio") else
                ["DTSTART:" + utc(a["data"], ini), "DTEND:" + utc(a["data"], fim)]),
              "SUMMARY:" + esc(a["titulo"]),
              "DESCRIPTION:" + esc("\n".join(x for x in desc if x)),
              "LOCATION:" + esc(a.get("local", "")), "END:VEVENT", "END:VCALENDAR"]
    return "\r\n".join(linhas) + "\r\n"


def carregar_noticias():
    posts = []
    pasta = ROOT / "noticias"
    for arq in sorted(pasta.glob("*.md")) if pasta.exists() else []:
        texto = arq.read_text(encoding="utf-8")
        m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", texto, re.S)
        meta, corpo = (yaml.safe_load(m.group(1)) or {}, m.group(2)) if m else ({}, texto)
        if meta.get("rascunho"):
            continue
        data = meta.get("data")
        if isinstance(data, str):
            data = dt.date.fromisoformat(data)
        data = data or dt.date.today()
        posts.append({
            "slug": re.sub(r"^\d{4}-\d{2}-\d{2}-", "", arq.stem),
            "titulo": meta.get("titulo", arq.stem),
            "data": data,
            "data_br": data_br(data),
            "resumo": meta.get("resumo", ""),
            "autor": meta.get("autor", ""),
            "categoria": meta.get("categoria", "Notícia"),
            "html": md(corpo),
        })
    posts.sort(key=lambda p: p["data"], reverse=True)
    return posts


# ---------------------------------------------------------------- geração

def gerar():
    site = carregar_site()
    noticias = carregar_noticias()
    gestoes = carregar_gestoes()
    formacao = carregar_formacao()
    associados = carregar_associados()
    hoje = dt.datetime.now(TZ).date()
    ag_prox, ag_real = carregar_agenda(hoje)

    if DIST.exists():
        shutil.rmtree(DIST, ignore_errors=True)
    DIST.mkdir(exist_ok=True)
    shutil.copytree(ROOT / "static", DIST / "static", dirs_exist_ok=True)
    (DIST / ".nojekyll").write_text("")

    env = Environment(loader=FileSystemLoader(ROOT / "templates"),
                      autoescape=select_autoescape(["html"]),
                      trim_blocks=True, lstrip_blocks=True)
    env.filters["md"] = md
    env.filters["slug"] = slug
    ano = hoje.year

    def render(template, destino, base_abs=None, **ctx):
        """destino: caminho relativo dentro de dist/, ex.: 'diretoria/index.html'."""
        profundidade = len(Path(destino).parts) - 1
        root = base_abs if base_abs is not None else "../" * profundidade
        html = env.get_template(template).render(
            site=site, noticias=noticias, noticias_home=noticias[:3], gestoes=gestoes, formacao=formacao, associados=associados,
            agenda_prox=ag_prox, agenda_real=ag_real, agenda_home=ag_prox[:2],
            root=root, ano=ano, **ctx)
        saida = DIST / destino
        saida.parent.mkdir(parents=True, exist_ok=True)
        saida.write_text(html, encoding="utf-8")

    render("home.html", "index.html", active="home")
    render("neab.html", "o-neab/index.html", active="neab", title="O NEAB")
    render("atuacao.html", "atuacao/index.html", active="atuacao", title="Atuação")
    render("diretoria.html", "diretoria/index.html", active="diretoria", title="Diretoria e representação")
    render("associados.html", "associados/index.html", active="associados", title="Associados")
    for p in (associados or {}).get("pessoas", []):
        render("associado.html", f"associados/{p['slug']}/index.html", active="associados",
               title=p["nome"], pessoa=p)
    for g in (associados or {}).get("grupos", []):
        render("associados_area.html", f"associados/{g['slug']}/index.html", active="associados",
               title=g["area"], grupo=g)
    render("formacao.html", "formacao/index.html", active="formacao", title="Cursos e formação")
    render("gestoes.html", "diretoria/gestoes/index.html", active="diretoria", title="Gestões anteriores")
    render("associe.html", "associe-se/index.html", active="associe", title="Associe-se")
    render("parceiros.html", "beneficios/index.html", active="beneficios", title="Benefícios e convênios")
    render("agenda.html", "agenda/index.html", active="agenda", title="Agenda")
    render("documentos.html", "documentos/index.html", active="documentos", title="Documentos")
    render("transparencia.html", "transparencia/index.html", active="transparencia", title="Transparência")
    render("contato.html", "contato/index.html", active="contato", title="Contato")
    render("sobre.html", "sobre/index.html", active="sobre", title="Sobre o site")

    render("noticias.html", "noticias/index.html", active="noticias", title="Notícias")
    for p in noticias:
        render("post.html", f"noticias/{p['slug']}/index.html", active="noticias",
               title=p["titulo"], post=p, description=p["resumo"])

    for a in ag_prox + ag_real:
        (DIST / "agenda").mkdir(parents=True, exist_ok=True)
        (DIST / "agenda" / f"{a['id']}.ics").write_text(ics_atividade(a), encoding="utf-8", newline="")

    # 404: usa a raiz do site (base_url) em vez de caminho relativo
    render("404.html", "404.html", base_abs=site.get("base_url", "/"), title="Página não encontrada")

    print(f"Site gerado em {DIST} — {len(noticias)} notícia(s), {len(gestoes)} gestão(ões) registrada(s), "
          f"{len(ag_prox)} atividade(s) futura(s), {len(ag_real)} realizada(s).")


def servir(porta=8000):
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(DIST))
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", porta), handler) as httpd:
        print(f"Abra http://localhost:{porta}  (Ctrl+C para parar)")
        httpd.serve_forever()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--serve", action="store_true", help="serve dist/ em localhost:8000")
    args = ap.parse_args()
    gerar()
    if args.serve:
        servir()
