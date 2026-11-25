# modelos-base

Modelos de app de agendamento para salões e barbearias. Cada cliente recebe um site instalável no celular (PWA) com as telas Início, Agendar e Galeria.

## Estrutura

| Pasta ou arquivo | Para que serve |
| --- | --- |
| `src/models.js` | Os 23 modelos: 9 masculinos, 9 femininos e 5 campanhas de datas especiais (cores, fontes e textos). |
| `src/template.html` | O app em si. Lê os dados do cliente e do modelo. |
| `build.py` | Gera a pasta do site de um cliente. |
| `clientes/<nome>/config.json` | Os dados de cada cliente. |
| `clientes/<nome>/fotos/` | As fotos do cliente. |
| `exemplos/` | Sites gerados para teste. |

## Criar o app de um cliente

1. Copie a pasta `clientes/exemplo` para `clientes/<nome-do-cliente>`.
2. Edite o `config.json`: modelo escolhido, nome, endereço, Instagram, WhatsApp, serviços e preços.
3. Coloque as fotos em `clientes/<nome-do-cliente>/fotos/` e liste cada uma em `fotos` no `config.json`:
   `{ "arquivo": "fotos/01.jpg", "categoria": "Corte", "titulo": "Degradê" }`.
4. Gere o site:

   ```bash
   python3 build.py clientes/<nome-do-cliente> saida/<nome-do-cliente>
   ```

5. Publique a pasta `saida/<nome-do-cliente>` (veja abaixo).

Para trocar o modelo, mude o campo `modelo` do `config.json` ou use `--modelo <id>`.

## Ids dos modelos

- **Masculinos:** `iron`, `fade`, `royal`, `urban`, `oldtown`, `steel`, `maison`, `obsidian`, `imperial`
- **Femininos:** `aura`, `lumi`, `rose`, `vita`, `glam`, `bloom`, `champagne`, `velvet`, `seda`
- **Datas especiais:** `maes`, `pais`, `natal`, `virada`, `black`

Nas campanhas, preencha `campanha` (`data`, `prazo`, `desconto`) e `ofertas` no `config.json`.

## Como o agendamento funciona

O app não guarda agendamentos. Quando o cliente final escolhe serviço, dia e horário, o botão abre o WhatsApp do estabelecimento com a mensagem pronta, e o estabelecimento confirma por lá. Para isso o `whatsapp` do `config.json` precisa estar preenchido, com código do país e DDD (`5511999999999`).

## Publicar no GitHub Pages

1. Coloque o conteúdo da pasta gerada na raiz de um repositório público (ou em uma subpasta).
2. No repositório, vá em **Settings, Pages**, escolha **Deploy from a branch**, branch `main`, pasta `/ (root)`, e salve.
3. O endereço será `https://<usuario>.github.io/<repositorio>/`.

O exemplo deste repositório fica em `exemplos/barbearia-exemplo/`.

## Fotos

Use apenas fotos que o cliente tenha direito de publicar. Não coloque fotos de clientes de outros salões. Repositórios com Pages grátis são públicos, então tudo que estiver neles pode ser visto por qualquer pessoa.
