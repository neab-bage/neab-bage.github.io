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
- Identidade visual: paleta "Concreto e cobre" — marca e títulos em preto #0A0A0A, texto
  #46433E, secundário #6E6A63, cobre #9C5A2C para links e botões, concreto #F4F2EE nas faixas
  e #DDD7CC nas linhas. Tipografia IBM Plex Sans. Logotipo do NEAB em preto, horizontal
  (proporção 2,17:1). Trocar as variáveis no topo de `style.css` troca o site inteiro.

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

## Pendências do guia de 23/11/2026 (conferir com a secretaria)
O PDF dessa revisão foi exportado em PDF/X com as fontes convertidas em curvas: **não tem camada
de texto**. A conferência foi feita por OCR em duas resoluções (200 e 400 dpi); só foram gravados
os e-mails lidos igualmente nas duas passagens. Os itens abaixo não puderam ser confirmados.

- **Aliane da Croce** — guia: `alianedacroce@gmail.com`; cadastro atual: `alianecroce@gmail.com`
  (informado pelo núcleo em 11/11). Endereços diferentes, não é erro de leitura. Confirmar qual vale.
- **Nubia Margot Menezes Jardim** — guia: `arqmargot_asm@yahoo.com.br`; cadastro:
  `arqnubiamargot_asm@yahoo.com.br`, montado a partir de um endereço truncado no guia anterior.
- **Júlia Bueno Raota Fernandes** — guia (OCR): `juliaraota721@`; cadastro: `juliaraota791@`.
  Mantido o do cadastro, que veio da camada de texto do guia de 18/11.
- **Gisele Pinheiro** — OCR divergiu entre as duas leituras (`...ge@` e `...go@`). Cadastro mantido:
  `giselepinheirogp@hotmail.com`.
- **Gustavo Scherer Fatturi Pires**, **Caíque Nunes Maria Santana**, **Magali Nocchi Collares
  Gonçalves** — OCR corrompeu o endereço. Cadastro mantido.
- **Gladis Barcellos Saavedra (Neneca)** — gravado `neneca.sasavedra@gmail.com` conforme as duas
  leituras; pode ser erro de digitação no próprio guia (Saavedra com dois "a").
- **Juliana de Oliveira Taschetto** — as duas leituras discordam na pontuação
  (`arqjuliana.` x `arq.juliana.`). Campo deixado vazio.
- **Rafael Daneris Delabary** — consta apenas na seção do conselho fiscal, sem entrada na listagem
  profissional. Igual no guia de 18/11.
- **Ana Paula Lopes Siqueira Ritta** e as demais removidas após 18/11 seguem ausentes em 23/11.
  Ana Paula enviou foto; aguardando retorno da diretoria. Foto guardada em
  `fotos_associados/_previa/ana_paula_recorte.jpg`.
- **www.neab.org.br** — divulgado nos canais de relacionamento do guia, mas o domínio não existe.
