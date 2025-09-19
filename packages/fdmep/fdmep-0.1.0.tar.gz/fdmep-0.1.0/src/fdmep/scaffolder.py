# -*- coding: utf-8 -*-
import os

# ---- cores ---------------------------------------------------------------
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except Exception:
    # fallback sem cores se colorama não estiver instalada
    class _NoColor:
        def __getattr__(self, _): return ''
    Fore = Style = _NoColor()

ICON_OK   = '✔'
ICON_INFO = 'ℹ'
ICON_WARN = '▲'
ICON_ERR  = '✖'
ICON_STEP = '»'

def ok(msg):    print(f"{Fore.GREEN}{ICON_OK} {msg}{Style.RESET_ALL}")
def info(msg):  print(f"{Fore.CYAN}{ICON_INFO} {msg}{Style.RESET_ALL}")
def warn(msg):  print(f"{Fore.YELLOW}{ICON_WARN} {msg}{Style.RESET_ALL}")
def err(msg):   print(f"{Fore.RED}{ICON_ERR} {msg}{Style.RESET_ALL}")
def step(msg):  print(f"{Style.BRIGHT}{Fore.MAGENTA}{ICON_STEP} {msg}{Style.RESET_ALL}")

def ask(prompt):
    return input(f"{Fore.CYAN}{prompt}{Style.RESET_ALL}")

# ---- lógica --------------------------------------------------------------
def create_extension_folder(name, extension):
    path_name = f"{name}.{extension}"
    step(f"Preparando pasta de extensão: {path_name}")

    try:
        if path_name in os.listdir():
            info(f"Pasta já existe, entrando em: {path_name}")
            os.chdir(path_name)
            return None

        for folder in os.listdir():
            if folder.endswith(f".{extension}"):
                os.rename(folder, path_name)
                ok(f"Renomeado {folder} → {path_name}")
                os.chdir(path_name)
                return None

        os.mkdir(path_name)
        ok(f"Criada pasta .{extension}: {path_name}")
        os.chdir(path_name)
    except Exception as e:
        err(f"Falha ao preparar pasta {path_name}: {e}")
        raise


def create_command_folder(name, extension):
    path_name = f"{name}.{extension}"
    step(f"Criando comando: {path_name}")

    try:
        if path_name in os.listdir():
            info(f"Pasta de comando já existe, entrando em: {path_name}")
            os.chdir(path_name)
            return None

        os.mkdir(path_name)
        ok(f"Criada pasta de comando: {path_name}")
        os.chdir(path_name)
    except Exception as e:
        err(f"Falha ao criar comando {path_name}: {e}")
        raise


def create_default_files(command_name, author_name="Seu Nome"):
    step("Gerando arquivos padrão do comando")
    default_files = {
        'script.py': (
            f'# -*- coding: utf-8 -*-\n'
            f'__title__ = "{command_name}"\n'
            f'__author__ = "{author_name}"\n'
            f'__version__ = "1.0"\n\n'
            f'print("Continue explorando o pyRevit...")\n'
        ),
        'bundle.yaml': (
            f'title:\n'
            f'  en_us: {command_name}\n'
            f'  pt_br: {command_name}\n'
            f'tooltip: Descrição do comando {command_name}.\n'
            f'author: {author_name}\n'
        )
    }

    for file_name, content in default_files.items():
        try:
            if file_name not in os.listdir():
                with open(file_name, 'w', encoding='utf-8') as file:
                    file.write(content)
                ok(f"Arquivo criado: {file_name}")
            else:
                warn(f"Arquivo já existia e foi mantido: {file_name}")
        except Exception as e:
            err(f"Erro criando {file_name}: {e}")
            raise


def get_valid_name(field_name, default_name):
    while True:
        name = ask(
            f"Informe um nome para {Style.BRIGHT}{field_name}{Style.NORMAL} "
            f"(sem espaços/acentos) {Style.DIM}[padrão: {default_name}]"
            f"{Style.NORMAL}: "
        ).strip()
        if not name:
            info(f"Usando padrão para {field_name}: {default_name}")
            return f'{field_name} = {default_name}'
        if all(c.isalnum() or c == '_' for c in name):
            ok(f"Nome aceito para {field_name}: {name}")
            return f'{field_name} = {name}'
        err("Nome inválido. Use apenas letras, números e _ (underline). Tente novamente.")


def mount_config(config_file):
    if config_file not in os.listdir():
        step(f"Criando {config_file}")
        data = []
        data.append(get_valid_name('extension','MyExtension'))
        data.append(get_valid_name('tab','MyTab'))
        data.append(get_valid_name('panel','MyPanel'))
        data.append(get_valid_name('pushbutton','MyCommand'))

        try:
            with open(config_file, 'w', encoding='utf-8') as file:
                file.write('\n'.join(data))
            ok(f"Arquivo de configuração criado: {config_file}")
        except Exception as e:
            err(f"Não foi possível criar {config_file}: {e}")
            raise
    else:
        info(f"Usando configuração existente: {config_file}")
        return True


def run_install():
    """Executa o fluxo de criação da extensão."""
    config_file = 'config.yaml'
    if mount_config(config_file):
        while True:
            continue_process = ask("Um projeto já existe, desejar atualizar? (s/n) [padrão: s]: ").strip().lower()
            if continue_process in ('', 's', 'sim', 'n', 'não', 'nao', 'no', 'y', 'yes'):
                break
            else:
                err("Resposta inválida. Digite 's' para sim ou 'n' para não.")
        if continue_process not in ('', 's', 'sim'):
            info("Processo cancelado pelo usuário.")
            return
    
    try:
        with open(config_file, 'r', encoding='utf-8') as file:
            config = [line.strip().split(' = ') for line in file.readlines()]
    except Exception as e:
        err(f"Não consegui ler {config_file}: {e}")
        return

    for key, value in config:
        if key in ['extension', 'tab', 'panel']:
            create_extension_folder(value, key)

        if key == 'pushbutton':
            create_command_folder(value, key)
            create_default_files(value)
            os.chdir('..')

        info(f"{key} = {Style.BRIGHT}{value}{Style.NORMAL}")

    ok("Extensão pyRevit criada/atualizada com sucesso!")
