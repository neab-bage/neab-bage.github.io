# Site do NEAB

Site institucional do **Núcleo dos Engenheiros e Arquitetos de Bagé (NEAB)**, sociedade civil
que reúne engenheiros, arquitetos e profissionais de especialidades afins da regional do
CREA-RS de Bagé.

🌐 **https://neab-bage.github.io**

## Como funciona

Gerador estático em Python: `build.py` lê os dados em `data/`, as notícias em `noticias/` e os
modelos em `templates/`, e escreve o site pronto em `dist/`. A cada `push` na branch `main`, o
GitHub Actions gera e publica o site no GitHub Pages.

```
data/site.yml       conteúdo institucional (finalidade, diretoria, parceiros, documentos…)
data/agenda.yml     atividades do núcleo
noticias/*.md       notícias, uma por arquivo
templates/          modelos HTML (Jinja2)
static/             CSS, JS, imagens e PDFs publicados
build.py            gerador
```

## Rodar na sua máquina

```bash
pip install -r requirements.txt
python build.py --serve     # abre em http://localhost:8000
```

## Como atualizar o site

| O que mudar | Onde |
| --- | --- |
| Diretoria, Conselho Fiscal, representação no CREA-RS | `data/site.yml` |
| Texto da página inicial, finalidade, sede, contato | `data/site.yml` |
| Parceiros e benefícios | `data/site.yml` → `parceiros` |
| Documentos para download | PDF em `static/documentos/` + item em `data/site.yml` → `documentos` |
| Prestação de contas | PDFs em `static/documentos/` + item em `transparencia.exercicios` |
| Nova atividade na agenda | `data/agenda.yml` |
| Nova notícia | novo arquivo em `noticias/AAAA-MM-DD-titulo.md` |

Depois de editar, basta fazer o commit na `main`: o site se publica sozinho em poucos minutos.

## Atenção aos dados pessoais

O repositório é público. Não inclua CPF, RG, telefone ou endereço particular, documentos com
dados de assinatura digital, nem listas de associados. Nomes e cargos de quem ocupa função
eletiva no núcleo são informação pública; o restante, não.

## Licença

Código do site sob licença MIT (ver `LICENSE.md`). O conteúdo institucional, os textos e os
documentos são do NEAB.
