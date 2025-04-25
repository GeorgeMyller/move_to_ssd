# move_to_ssd
Script Python para migrar pastas e aplicativos do macOS para SSD externo com symlinks automáticos.
=======
# ssd_transfer.py

## Descrição

`ssd_transfer.py` é um script Python para macOS que automatiza a migração de pastas de usuário, aplicativos, caches e outros arquivos grandes do armazenamento interno para um SSD externo. Após a transferência, o script cria links simbólicos (symlinks) nos locais originais, permitindo que o sistema e os aplicativos continuem funcionando normalmente, mas utilizando o SSD para armazenamento dos itens movidos.

## Funcionalidades

- Move pastas de usuário (ex: Documentos, Música, Imagens, Filmes) para o SSD externo.
- Move a pasta Downloads separadamente.
- Permite mover aplicativos do diretório `/Applications`.
- Suporta a transferência de subpastas específicas de cache e de Application Support.
- Permite especificar outros caminhos absolutos para mover grandes volumes de dados (ex: máquinas virtuais, projetos).
- Cria links simbólicos nos locais originais, mantendo a transparência para o sistema e aplicativos.
- Relatório detalhado de sucesso, falhas e itens ignorados.
- Confirmação interativa antes de executar qualquer operação.

## Pré-requisitos

- macOS
- Python 3.x instalado
- Permissões de administrador (necessário para mover itens em `/Applications`)
- SSD externo devidamente formatado e montado

## Instalação

1. Clone ou copie este repositório no seu computador.
2. Abra o Terminal e navegue até a pasta do projeto:
   ```bash
   cd /Volumes/SSD-EXTERNO/2025/Abril/move_to_ssd
   ```
3. (Opcional) Crie e ative um ambiente virtual Python:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

## Configuração

Abra o arquivo `ssd_transfer.py` e ajuste as seguintes variáveis de acordo com sua necessidade:

- `ssd_volume_name`: nome do volume do SSD externo (ex: "SSD-EXTERNO").
- `USER_FOLDERS_TO_MOVE`: lista de pastas do usuário a serem movidas (ex: "Documents", "Music").
- `APPS_TO_MOVE`: lista de aplicativos (nomes das pastas .app em `/Applications`) a serem movidos.
- `CACHE_SUBFOLDERS_TO_MOVE`: subpastas de cache em `~/Library/Caches` a serem movidas.
- `APP_SUPPORT_SUBFOLDERS_TO_MOVE`: subpastas em `~/Library/Application Support` a serem movidas.
- `OTHER_PATHS_TO_MOVE`: caminhos absolutos de outros arquivos ou pastas grandes.

> **Atenção:** Mover caches ou pastas de Application Support pode causar problemas em alguns aplicativos. Use com cautela e faça backup dos dados importantes.

## Uso

1. Certifique-se de que o SSD externo está conectado e montado.
2. Ajuste as listas de itens a serem movidos conforme desejado.
3. Execute o script pelo terminal:
   ```bash
   python3 ssd_transfer.py
   ```
4. Leia atentamente o resumo das operações planejadas e confirme apenas se estiver seguro.
5. O script irá mover os itens, criar os links simbólicos e exibir um relatório ao final.

## Exemplo de Operação

- Downloads: `~/Downloads` → `/Volumes/SSD-EXTERNO/Downloads`
- Documentos: `~/Documents` → `/Volumes/SSD-EXTERNO/Documents`
- Aplicativo: `/Applications/SeuApp.app` → `/Volumes/SSD-EXTERNO/Applications/SeuApp.app`
- Cache: `~/Library/Caches/pip` → `/Volumes/SSD-EXTERNO/Library/Caches/pip`

## Recomendações e Cuidados

- Feche todos os aplicativos que possam estar usando os arquivos/pastas a serem movidos.
- Faça backup dos dados importantes antes de executar o script.
- Para mover aplicativos, pode ser necessário rodar o script com `sudo`:
  ```bash
  sudo python3 ssd_transfer.py
  ```
- Após mover, verifique se os aplicativos e arquivos funcionam normalmente.
- Para desfazer, basta mover os itens de volta e remover os links simbólicos.

## Limitações

- O script não verifica dependências internas de aplicativos ou permissões especiais.
- Mover caches ou pastas de suporte pode causar comportamento inesperado em alguns apps.
- O uso de symlinks é transparente para a maioria dos aplicativos, mas pode não funcionar para todos.

## Licença

Este projeto é fornecido sem garantia. Use por sua conta e risco.

---

Para dúvidas ou sugestões, edite o script conforme sua necessidade ou abra uma issue no repositório.
>>>>>>> 30bd93f (Primeiro commit: script de migração para SSD externo)
