# Site do NEAB — Núcleo dos Engenheiros e Arquitetos de Bagé

Site estático em Python (Jinja2), publicado no GitHub Pages em
https://neab-bage.github.io. Idioma do site e dos textos: português do Brasil.

## Comandos
- `pip install -r requirements.txt`
- `python build.py` gera `dist/`
- `python build.py --serve` gera e serve em http://localhost:8000
- Publicação: push na `main` → workflow `.github/workflows/pages.yml`.

## Onde fica cada coisa
- `data/site.yml`: todo o conteúdo institucional — finalidade, sede, governança, diretoria,
  conselho fiscal, representação no CREA-RS, associe-se, parceiros, documentos, transparência.
- `data/agenda.yml`: uma atividade por item; o build separa em "próximas" e "realizadas" pela
  data e gera um arquivo `.ics` por atividade.
- `noticias/*.md`: uma notícia por arquivo (cabeçalho YAML: titulo, data, categoria, autor,
  resumo; `rascunho: true` não publica).
- `templates/`: HTML (Jinja2). `static/css/style.css`: visual. `static/img/`: logo e favicon.
  `static/documentos/`: PDFs publicados (estatuto, editais, atas, prestação de contas).

## Regras
- Links internos são **relativos** (`{{ root }}`), para funcionar em qualquer endereço. Não
  usar caminhos absolutos.
- Identidade visual: logotipo monocromático do NEAB; azul institucional #14314F, azul de
  apoio #235C86, acento ocre #8A6420, grafite #15202B. Títulos em Source Serif 4, texto em
  Inter. Trocar as variáveis no topo de `style.css` troca o site inteiro.
- Acessibilidade: uma `h1` por página, `alt` nas imagens, foco visível, contraste AA,
  respeitar `prefers-reduced-motion`.
- **Repositório público: nunca commitar dados pessoais** — CPF, RG, telefone e endereço
  particular, documentos assinados com dados de assinatura digital, listas de associados.
  Nomes e cargos de quem ocupa função eletiva são públicos; o resto, não.
  Antes de publicar um PDF, conferir se há CPF ou dado pessoal no documento ou na assinatura.
- Trocar o conteúdo pelos dados, não pelo HTML: editar `data/site.yml` sempre que possível.

## Pendências de conteúdo
Marcadas com `PENDENTE` em `data/site.yml`:
- Ano e data de fundação do núcleo (`fundacao.ano`, `fundacao.confirmado`, `fundacao.texto`).
  Enquanto `confirmado: false`, o site não exibe o histórico nem a idade da entidade.
- E-mail institucional, telefone e redes sociais (`contato`).
- Conselho Fiscal do biênio 2027/2028: três titulares e três suplentes.
- Representação junto ao CREA-RS: titular, suplente e substituto de suplente.
- Valor da contribuição mensal e forma de pagamento, se puder ser público.
- Benefícios de cada parceiro (Mútua, Clube Mútua, Tecnoprev) e links oficiais.
- Edital de convocação de 2026 em versão sem os dados pessoais da assinatura digital.
- Relatórios de atividades e demonstrações financeiras por exercício (`transparencia.exercicios`).
- Responsável pelo site no núcleo (`sobre_site.responsavel`).
