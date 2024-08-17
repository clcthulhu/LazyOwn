"""
utils.py

Autor: Gris Iscomeback 
Correo electrónico: grisiscomeback[at]gmail[dot]com
Fecha de creación: 09/06/2024
Licencia: GPL v3

Descripción: Este archivo contiene la definición de la lógica de todas las funciones usadas en la clase LazyOwnShell

██╗      █████╗ ███████╗██╗   ██╗ ██████╗ ██╗    ██╗███╗   ██╗
██║     ██╔══██╗╚══███╔╝╚██╗ ██╔╝██╔═══██╗██║    ██║████╗  ██║
██║     ███████║  ███╔╝  ╚████╔╝ ██║   ██║██║ █╗ ██║██╔██╗ ██║
██║     ██╔══██║ ███╔╝    ╚██╔╝  ██║   ██║██║███╗██║██║╚██╗██║
███████╗██║  ██║███████╗   ██║   ╚██████╔╝╚███╔███╔╝██║ ╚████║
╚══════╝╚═╝  ╚═╝╚══════╝   ╚═╝    ╚═════╝  ╚══╝╚══╝ ╚═╝  ╚═══╝

"""
import re
import os
import sys
import subprocess
import shlex
import signal
import json
import time
import base64
import string
import glob
import readline
import requests
from urllib.parse import quote, unquote
from modules.lazyencoder_decoder import encode, decode

# Cargar la versión desde el archivo version.json
def load_version():
    try:
        with open('version.json', 'r') as f:
            data = json.load(f)
            return data.get('version', 'release/v0.0.14')
    except FileNotFoundError:
        return 'release/v0.0.14'

# Establecer la versión del proyecto
version = load_version()

# Definimos algunos códigos de escape ANSI para colores
RESET = "\033[0m"
BOLD = "\033[1m"
UNDERLINE = "\033[4m"
INVERT = "\033[7m"
BLINK = "\033[5m"

# Colores de texto
BLACK = "\033[30m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"

# Colores de fondo
BG_BLACK = "\033[40m"
BG_RED = "\033[41m"
BG_GREEN = "\033[42m"
BG_YELLOW = "\033[43m"
BG_BLUE = "\033[44m"
BG_MAGENTA = "\033[45m"
BG_CYAN = "\033[46m"
BG_WHITE = "\033[47m"
# Variables de control
NOBANNER = False
COMMAND = None
RUN_AS_ROOT = False


BANNER = f"""{GREEN}{BG_BLACK}
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣠⡤⠴⠶⠖⠒⠛⠛⠀⠀⠀⠒⠒⢰⠖⢠⣤⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣭⠷⠞⠉⠫⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠁⠀⠈⠉⠒⠲⠤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⣿⣿⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠲⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢀⣤⣾⣿⣿⣿⣷⡁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠑⢄⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⣠⡾⢋⠷⣻⣿⣟⢿⣿⠿⠆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠂⠸⣄⠀⠀⠀⠀
⠀⠀⠀⣀⣾⣯⢶⣿⣾⣿⡟⠁⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⢦⠀⠀⠀
⠀⠀⢠⣿⣿⣤⣽⣿⣿⣿⣃⣴⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠈⢀⣽⣿⣿⣿⣿⣿⣿⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠠⠠⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⢸⣿⣿⣿⣿⣿⣿⣿⣷⣶⣶⣦⣴⣆⣀⣀⣀⣀⢀⠀⠀⣐⠄⢀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⠀⠀⢀⣀⠴⠶⠛⠛⠛⠛⠛⠳⠶⣶⣦⡀⠀⠀⠘
⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠇⠀⠀⠀⠀⠀⠀⠀⠐⠤⣯⣀⡰⡋⣡⣐⣶⣽⣶⣶⣾⣿⣷⣶⣤⣝⡣⠀⠀⠀
⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⡉⣿⣿⣿⣿⣿⣿⣿⣭⡿⣿⡋⠉⠙⢿⡦⠀⠀⠀⠀⠀⠀⠀⢀⣌⣼⡩⢻⣷⣿⣿⣿⣿⣿⣿⡏⣛⢿⣿⣿⡿⠃⢰⠀⠀
⠀⢿⣿⣿⣿⣿⣿⣿⣛⠿⣷⣄⣙⣿⠿⠿⠟⠛⣿⣿⣜⣶⡂⡉⣿⣧⠀⠀⠀⠀⠀⠀⠀⠈⢻⣿⢻⣾⡛⠛⢿⠿⠿⠟⢻⣧⣽⣿⠿⠋⠀⠄⢸⣧⠔
⠀⠘⢿⣿⣿⣿⣿⢿⣿⣿⣷⣾⣭⣿⣿⣟⣛⣛⣛⣛⢿⣽⣿⣧⣿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠃⣿⡿⠿⠿⠿⠿⢻⣛⣛⣋⣉⣁⠤⠒⠒⠂⣠⣿⠏⠀
⠀⠀⠈⠻⢿⣿⣿⣶⣄⣉⠉⠉⠉⠉⠉⠛⠉⠉⠁⠉⠁⢹⢻⣿⣏⢹⠀⠘⠀⠀⠀⠀⠀⠀⠀⠀⠉⠉⠉⠉⠉⠉⠉⠉⠁⠀⠀⠀⠀⣀⣴⠿⠝⠁⠀
⠀⠀⠀⠀⠀⠙⢿⣿⣿⣿⣿⣷⣶⣶⣶⣦⣴⣴⣾⢬⡤⢬⡜⠛⠀⢾⢿⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠶⣦⣤⣄⣤⣐⣢⣤⣴⣾⠟⠁⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠙⢿⣿⣿⣿⣿⣿⣿⣿⣯⣤⣄⡤⣄⣠⡤⣄⣀⠀⠀⠀⠀⡀⠀⠀⠀⡀⠀⠀⢀⣠⣤⣴⣤⣤⢹⣿⣿⣿⡿⠛⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠻⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣤⣬⣥⣤⡴⠶⠶⠖⠒⠛⠋⠉⡩⢁⣼⣿⣿⣿⠟⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡈⠙⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⢻⡓⠁⠁⠀⠀⠀⠀⠀⠀⠀⠀⢠⢶⣧⣻⣿⣿⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠁⠀⠀⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⠾⠀⠀⠀⠀⠀⠀⠀⠀⣀⡜⠼⣷⣸⡿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⣿⣿⣿⣿⣿⣿⣶⣄⣀⣀⣀⡀⠀⢀⠀⠀⣠⡼⣋⣪⣾⡿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⡟⠙⡀⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⠛⡿⡁⡟⣡⢀⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣿⣿⣿⣿⣿⣿⣿⣿⡟⠉⢛⠀⣸⠆⠈⠹⠀⠀⠀⠀⠀⠀⠀{RED}{BG_BLACK}
 ██▓    ▄▄▄      ▒███████▒▓██   ██▓ ▒█████   █     █░███▄    █                
▓██▒   ▒████▄    ▒ ▒ ▒ ▄▀░ ▒██  ██▒▒██▒  ██▒▓█░ █ ░█░██ ▀█   █                
▒██░   ▒██  ▀█▄  ░ ▒ ▄▀▒░   ▒██ ██░▒██░  ██▒▒█░ █ ░█▓██  ▀█ ██▒               
▒██░   ░██▄▄▄▄██   ▄▀▒   ░  ░ ▐██▓░▒██   ██░░█░ █ ░█▓██▒  ▐▌██▒               
░██████▒▓█   ▓██▒▒███████▒  ░ ██▒▓░░ ████▓▒░░░██▒██▓▒██░   ▓██░               
░ ▒░▓  ░▒▒   ▓▒█░░▒▒ ▓░▒░▒   ██▒▒▒ ░ ▒░▒░▒░ ░ ▓░▒ ▒ ░ ▒░   ▒ ▒                
░ ░ ▒  ░ ▒   ▒▒ ░░░▒ ▒ ░ ▒ ▓██ ░▒░   ░ ▒ ▒░   ▒ ░ ░ ░ ░░   ░ ▒░               
  ░ ░    ░   ▒   ░ ░ ░ ░ ░ ▒ ▒ ░░  ░ ░ ░ ▒    ░   ░    ░   ░ ░                
    ░  ░     ░  ░  ░ ░     ░ ░         ░ ░      ░            ░                
                 ░         ░ ░                                                
  █████▒██▀███   ▄▄▄       ███▄ ▄███▓▓█████  █     █░ ▒█████   ██▀███   ██ ▄█▀
▓██   ▒▓██ ▒ ██▒▒████▄    ▓██▒▀█▀ ██▒▓█   ▀ ▓█░ █ ░█░▒██▒  ██▒▓██ ▒ ██▒ ██▄█▒ 
▒████ ░▓██ ░▄█ ▒▒██  ▀█▄  ▓██    ▓██░▒███   ▒█░ █ ░█ ▒██░  ██▒▓██ ░▄█ ▒▓███▄░ 
░▓█▒  ░▒██▀▀█▄  ░██▄▄▄▄██ ▒██    ▒██ ▒▓█  ▄ ░█░ █ ░█ ▒██   ██░▒██▀▀█▄  ▓██ █▄ 
░▒█░   ░██▓ ▒██▒ ▓█   ▓██▒▒██▒   ░██▒░▒████▒░░██▒██▓ ░ ████▓▒░░██▓ ▒██▒▒██▒ █▄
 ▒ ░   ░ ▒▓ ░▒▓░ ▒▒   ▓▒█░░ ▒░   ░  ░░░ ▒░ ░░ ▓░▒ ▒  ░ ▒░▒░▒░ ░ ▒▓ ░▒▓░▒ ▒▒ ▓▒
 ░       ░▒ ░ ▒░  ▒   ▒▒ ░░  ░      ░ ░ ░  ░  ▒ ░ ░    ░ ▒ ▒░   ░▒ ░ ▒░░ ░▒ ▒░
 ░ ░     ░░   ░   ░   ▒   ░      ░      ░     ░   ░  ░ ░ ░ ▒    ░░   ░ ░ ░░ ░ 
          ░           ░  ░       ░      ░  ░    ░        ░ ░     ░     ░  ░   
    [⚠] Starting 👽 LazyOwn Framew0rk ☠ [;,;] """
def print_error(error):
    """
    Prints an error message to the console.

    This function takes an error message as input and prints it to the console
    with a specific format to indicate that it is an error.

    :param error: The error message to be printed.
    :type error: str
    :return: None
    """
    print(f"    {YELLOW}[-]{RED} {error}{RESET} [☠]")
    return


def print_msg(msg):
    """
    Prints a message to the console.

    This function takes a message as input and prints it to the console
    with a specific format to indicate that it is an informational message.

    :param msg: The message to be printed.
    :type msg: str
    :return: None
    """

    print(f"    {GREEN}[+]{WHITE} {msg}{RESET} [👽]")
    return


def print_warn(warn):
    """
    Prints a warning message to the console.

    This function takes a warning message as input and prints it to the console
    with a specific format to indicate that it is a warning.

    :param warn: The warning message to be printed.
    :type warn: str
    :return: None
    """

    print(f"    {MAGENTA}[~]{YELLOW} {warn}{RESET} [⚠]")
    return


def signal_handler(sig, frame):
    """
    Handles signals such as Control + C and shows a message on how to exit.

    This function is used to handle signals like Control + C (SIGINT) and prints
    a warning message instructing the user on how to exit the program using the
    commands 'exit', 'q', or 'qa'.

    :param sig: The signal number.
    :type sig: int
    :param frame: The current stack frame.
    :type frame: frame
    :return: None
    """

    global should_exit
    print_warn(
        f"{RED}{YELLOW} para salir usar el comando{GREEN} exit, q or qa ...{RESET}"
    )
    should_exit = True
    readline.set_history_length(0)
    return


signal.signal(signal.SIGINT, signal_handler)


def check_rhost(rhost):
    """
    Checks if the remote host (rhost) is defined and shows an error message if it is not.

    This function verifies if the `rhost` parameter is set. If it is not defined,
    an error message is printed, providing an example and directing the user to
    additional help.

    :param rhost: The remote host to be checked.
    :type rhost: str
    :return: True if rhost is defined, False otherwise.
    :rtype: bool
    """

    if not rhost:
        print_error(
            f"rhost must be set, {GREEN}Example: set rhost 10.10.10.10, {WHITE}more info see help set, or help <TOPIC> {RESET}"
        )
        return False
    return True


def check_lhost(lhost):
    """
    Checks if the local host (lhost) is defined and shows an error message if it is not.

    This function verifies if the `lhost` parameter is set. If it is not defined,
    an error message is printed, providing an example and directing the user to
    additional help.

    :param lhost: The local host to be checked.
    :type lhost: str
    :return: True if lhost is defined, False otherwise.
    :rtype: bool
    """

    if not lhost:
        print_error(
            f"lhost must be set, {GREEN}Example: set lhost 10.10.10.10, {WHITE}more info see help set, or help <TOPIC> {RESET}"
        )
        return False
    return True


def check_lport(lport):
    """
    Checks if the local port (lport) is defined and shows an error message if it is not.

    This function verifies if the `lport` parameter is set. If it is not defined,
    an error message is printed, providing an example and directing the user to
    additional help.

    :param lport: The local port to be checked.
    :type lport: int or str
    :return: True if lport is defined, False otherwise.
    :rtype: bool
    """

    if not lport:
        print_error(
            f"lport must be set, {GREEN}Example: set lport 5555, {WHITE}more info see help set, or help <TOPIC> {RESET}"
        )
        return False
    return True


def is_binary_present(binary_name):
    """
    Internal function to verify if a binary is present on the operating system.

    This function checks if a specified binary is available in the system's PATH
    by using the `which` command. It returns True if the binary is found and False
    otherwise.

    :param binary_name: The name of the binary to be checked.
    :type binary_name: str
    :return: True if the binary is present, False otherwise.
    :rtype: bool
    """
    result = os.system(f"which {binary_name} > /dev/null 2>&1")
    return result == 0


def handle_multiple_rhosts(func):
    """
    Internal function to handle multiple remote hosts (rhost) for operations.

    This function is a decorator that allows an operation to be performed across
    multiple remote hosts specified in `self.params["rhost"]`. It converts a single
    remote host into a list if necessary, and then iterates over each host,
    performing the given function with each host. After the operation, it restores
    the original remote host value.

    :param func: The function to be decorated and executed for each remote host.
    :type func: function
    :return: The decorated function.
    :rtype: function
    """

    def wrapper(self, *args, **kwargs):
        """internal wrapper of internal function to implement multiples rhost to operate. """
        rhosts = self.params["rhost"]
        if isinstance(rhosts, str):
            rhosts = [rhosts]  # Convertir a lista si es un solo host

        for rhost in rhosts:
            if not check_rhost(rhost):
                continue
            original_rhost = self.params["rhost"]
            self.params["rhost"] = rhost  # Actualizar rhost temporalmente
            func(self, *args, **kwargs)
            self.params["rhost"] = original_rhost  # Restaurar rhost original

    return wrapper


# Verificar y relanzar con sudo si es necesario
def check_sudo():
    """
    Checks if the script is running with superuser (sudo) privileges, and if not,
    restarts the script with sudo privileges.

    This function verifies if the script is being executed with root privileges
    by checking the effective user ID. If the script is not running as root,
    it prints a warning message and restarts the script using sudo.

    :return: None
    """

    if os.geteuid() != 0:
        print_warn(
            "Este script necesita permisos de superusuario. Relanzando con sudo..."
        )
        args = ["sudo", sys.executable] + sys.argv
        os.execvpe("sudo", args, os.environ)


def activate_virtualenv(venv_path):
    """
    Activates a virtual environment and starts an interactive shell.

    This function activates a virtual environment located at `venv_path` and then
    launches an interactive bash shell with the virtual environment activated.

    :param venv_path: The path to the virtual environment directory.
    :type venv_path: str
    :return: None
    """

    process = subprocess.Popen(
        ["bash", "-c", f"source {venv_path}/bin/activate && exec bash"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # Captura la salida del proceso hijo
    stdout, stderr = process.communicate()
    print_msg(f"Entorno Activado.{RESET}")


def parse_proc_net_file(file_path):
    """
    Internal function to parse a /proc/net file and extract network ports.

    This function reads a file specified by `file_path`, processes each line to
    extract local addresses and ports, and converts them from hexadecimal to decimal.
    The IP addresses are converted from hexadecimal format to standard dot-decimal
    notation. The function returns a list of tuples, each containing an IP address
    and a port number.

    :param file_path: The path to the /proc/net file to be parsed.
    :type file_path: str
    :return: A list of tuples, each containing an IP address and a port number.
    :rtype: list of tuple
    """

    ports = []
    try:
        with open(file_path, "r") as f:
            lines = f.readlines()

        for line in lines[1:]:  # Skip the header line
            parts = line.split()
            if len(parts) < 2:
                continue

            local_address = parts[1]
            # Local address is in the format: "IP:PORT"
            ip, port_hex = local_address.split(":")
            port = int(port_hex, 16)  # Convert hex port to decimal

            # Convert IP address from hex format to standard dot-decimal notation
            ip_parts = [str(int(ip[i : i + 2], 16)) for i in range(0, len(ip), 2)]
            ip_address = ".".join(ip_parts[::-1])  # Reverse the IP parts

            ports.append((ip_address, port))
    except FileNotFoundError:
        print_error(f"File {file_path} not found{RESET}")
    except Exception as e:
        print_error(f"An error occurred: {e}{RESET}")

    return ports


def get_open_ports():
    """
    Internal function to get open TCP and UDP ports on the operating system.

    This function uses the `parse_proc_net_file` function to extract open TCP and UDP
    ports from the corresponding /proc/net files. It returns two lists: one for TCP
    ports and one for UDP ports.

    :return: A tuple containing two lists: the first list with open TCP ports and
            the second list with open UDP ports.
    :rtype: tuple of (list of tuple, list of tuple)
    """

    tcp_ports = parse_proc_net_file("/proc/net/tcp")
    udp_ports = parse_proc_net_file("/proc/net/udp")

    return tcp_ports, udp_ports


def find_credentials(directory):
    """
    Searches for potential credentials in files within the specified directory.

    This function uses a regular expression to find possible credentials such as
    passwords, secrets, API keys, and tokens in files within the given directory.
    It iterates through all files in the directory and prints any matches found.

    :param directory: The directory to search for files containing credentials.
    :type directory: str
    :return: None
    """
    regex = re.compile(
        r"(password|passwd|secret|api_key|token)[\s:=]*[\w\d]{6,}", re.IGNORECASE
    )

    for root, dirs, files in os.walk(directory):
        for file in files:
            try:
                with open(os.path.join(root, file), "r") as f:
                    content = f.read()
                    matches = regex.findall(content)
                    if matches:
                        print_msg(
                            f"Credenciales encontradas en {os.path.join(root, file)}:"
                        )
                        for match in matches:
                            print_msg(f"{match}")
            except Exception as e:
                print_error(f"No se pudo leer el archivo {file}: {e}")
        

def rotate_char(c, shift):
    """
    Internal function to rotate characters for ROT cipher.

    This function takes a character and a shift value, and rotates the character
    by the specified shift amount. It only affects alphabetical characters, leaving
    non-alphabetical characters unchanged.

    :param c: The character to be rotated.
    :type c: str
    :param shift: The number of positions to shift the character.
    :type shift: int
    :return: The rotated character.
    :rtype: str
    """

    if c in string.ascii_letters:
        start = ord('a') if c.islower() else ord('A')
        return chr((ord(c) - start + shift) % 26 + start)
    return c

def get_network_info():
    """
    Retrieves network interface information with their associated IP addresses.

    This function executes a shell command to gather network interface details, 
    parses the output to extract interface names and their corresponding IP addresses, 
    and returns this information in a dictionary format. The dictionary keys are
    interface names, and the values are IP addresses.

    :return: A dictionary where the keys are network interface names and the values
             are their associated IP addresses.
    :rtype: dict
    """
    command = (
        'ip a show scope global | '
        'awk \'/^[0-9]+:/ { sub(/:/,"",$2); iface=$2 } '
        '/^[[:space:]]*inet / { split($2, a, "/"); print iface " " a[1] }\''
    )
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    output = result.stdout.strip()
    network_info = {}

    for line in output.split('\n'):
        parts = line.split(maxsplit=1)
        if len(parts) == 2:
            iface, ip = parts
            network_info[iface] = ip
        else:
            print_error(f"Formato inesperado en la línea: '{line}'")

    return network_info

def getprompt():
    """Generate a command prompt string with network information and user status.

    :param: None

    :returns: A string representing the command prompt with network information and user status.

    Manual execution:
    To manually get a prompt string with network information and user status, ensure you have `get_network_info()` implemented to return a dictionary of network interfaces and their IPs. Then use the function to create a prompt string based on the current user and network info.

    Example:
    If the function `get_network_info()` returns:
        {
            'tun0': '10.0.0.1',
            'eth0': '192.168.1.2'
        }

    And the user is root, the prompt string generated might be:
        [LazyOwn👽10.0.0.1]# 
    If the user is not root, it would be:
        [LazyOwn👽10.0.0.1]$ 

    If no 'tun' interface is found, the function will use the first available IP or fallback to '127.0.0.1'.
    """

    network_info = get_network_info()
    ip = next((ip for iface, ip in network_info.items() if 'tun' in iface), None)

    if ip is None:
        ip = next(iter(network_info.values()), '127.0.0.1')
    prompt_char = f'{RED}#' if os.geteuid() == 0 else '$'
    prompt = f"""{YELLOW}┌─{YELLOW}[{RED}LazyOwn{WHITE}👽{CYAN}{ip}{YELLOW}]
    {YELLOW}└╼ {BLINK}{GREEN}{prompt_char}{RESET} """.replace('    ','')

    return prompt

def copy2clip(text):
    """
    Copia el texto proporcionado al portapapeles usando xclip.

    Args:
        text (str): El texto que se desea copiar al portapapeles.

    Example:
        copy2clip("Hello, World!")
    """
    try:
        # Usa el comando xclip para copiar el texto al portapapeles
        subprocess.run(['xclip', '-selection', 'clipboard'], input=text.encode(), check=True)
        print_msg(f"Texto copiado al portapapeles. {text}")
    except subprocess.CalledProcessError as e:
        print_error(f"Error al copiar al portapapeles: {e}")
    except FileNotFoundError:
        print_error("xclip no está instalado. Por favor, instálalo usando `sudo apt-get install xclip`.")

def clean_output(output):
    """Elimina secuencias de escape de color y otros caracteres no imprimibles."""

    output = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', output)
    output = re.sub(r'(\x07|\x08|\x0A|\x0D|\x1B|\x7F|\x9B|\033\\|\033\\|\033\[|\033\]|\033\[[\d;]*[a-zA-Z])', '', output)
    output = re.sub(r'\\(?:33\[K|10|7)', '', output)
    output = re.sub(r' +', ' ', output)
    output = '\n'.join(line.strip() for line in output.split('\n') if line.strip())
    return output



def teclado_usuario(filename):
    """
    Procesa un archivo para extraer y mostrar caracteres desde secuencias de escritura específicas.

    Args:
        filename (str): El nombre del archivo a leer.

    Raises:
        FileNotFoundError: Si el archivo no se encuentra.
        Exception: Para otros errores que puedan ocurrir.
    """
    try:
        with open(filename, 'r') as file:
            content = file.readlines()

        output = ""
        for line in content:
            if line.startswith('write(5,'):
                match = re.search(r'write\(5, "(.*?)"', line)
                if match:
                    char = match.group(1)
                    if char in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -.':
                        output += char
                    elif char == '\\n':
                        print(output)
                        output = ""

        if output:  # Imprimir cualquier salida restante
            print(output)

    except FileNotFoundError:
        print(f"Archivo {filename} no encontrado.")
    except Exception as e:
        print(f"Error: {e}")



def salida_strace(filename):
    """
    Lee un archivo, extrae texto desde secuencias de escritura y muestra el contenido reconstruido.

    Args:
        filename (str): El nombre del archivo a leer.

    Raises:
        FileNotFoundError: Si el archivo no se encuentra.
        Exception: Para otros errores que puedan ocurrir.
    """    
    try:
        with open(filename, 'r') as file:
            content = file.readlines()

        output = ""
        for line in content:
            if line.startswith('write(5,'):
                match = re.search(r'write\(5, "(.*?)"', line)
                if match:
                    text = match.group(1)
                    if len(text) > 1:  # Solo considerar textos con más de un carácter
                        output += text

        if output:
            print("Contenido reconstruido:")
            print(output)
            print("Contenido despues de limpieza")
            print(clean_output(output))

    except FileNotFoundError:
        print(f"Archivo {filename} no encontrado.")
    except Exception as e:
        print(f"Error: {e}")

    
def exploitalert(content):
    try:
        if len(content) != 0:
            
            print_msg(f"|{GREEN}+ ExploitAlert Result {WHITE}")
            print_msg("|------------------------")


            predata = []
            for data in content:
                print_msg(f"|{BLUE}-{WHITE} Title : {data['name']}")
                print_msg(f"|{BLUE}-{WHITE} Link : https://www.exploitalert.com/view-details.html?id={data['id']}")
                


                predata.append({
                    "title" : data['name'],
                    "link" : f"https://www.exploitalert.com/view-details.html?id={data['id']}"
                })
            print_msg(f"|{BLUE}-{WHITE} Total Result : {GREEN}{len(content)}{WHITE} Exploits Found!")
            data.append({"exploitalert" : predata})
        else:
            print_error(f"|{RED}- No result in ExploitAlert!{WHITE}")
    except:
        print_error(f"|{RED}- Internal Error - No result in ExploitAlert!{WHITE}")
    return

def packetstormsecurity(content):
    try:
        reg = re.findall('<dt><a class="ico text-plain" href="(.*?)" title="(.*?)">(.*?)</a></dt>', content)
        if len(reg) != 0:
            
            print_msg(f"|{GREEN}+ PacketStorm Result {WHITE}")
            print_msg("|-----------------------")

            predata = []
            for data in reg:
                print_msg(f"|{BLUE}-{WHITE} Title : {data[2]}")
                print_msg(f"|{BLUE}-{WHITE} Link : https://packetstormsecurity.com{data[0]}")
            

                predata.append({
                    "title" : data[2],
                    "link" : f"https://packetstormsecurity.com{data[0]}"
                })
            print_msg(f"|{BLUE}-{WHITE} Total Result : {GREEN}{len(reg)}{WHITE} Exploits Found!")
            data.append({"packetstormsecurity" : predata})
        else:
            print_error(f"|{RED}- No result in PacketStorm!{WHITE}")
    except:
        print_error(f"|{RED}- Internal Error - No result in PacketStorm!{WHITE}")
    return

def nvddb(content):
    try:
        if len(content['vulnerabilities']) != 0:
            print_msg(f"{GREEN}|-----------------------------------------------")
            print_msg(f"{GREEN}|+ National Vulnearbility Database Result       +{WHITE}")
            print_msg(f"{GREEN}|-----------------------------------------------")

            predata = []
            for data in content['vulnerabilities']:
                print_msg(f"{BLUE}-{BG_YELLOW}{RED} ID : {data['cve']['id']}")
                print_msg(f"{BLUE}-{BG_BLACK}{WHITE} Description : {data['cve']['descriptions'][0]['value']}")
                print_msg(f"{BLUE}-{BG_BLACK}{BLUE} Link : https://nvd.nist.gov/vuln/detail/{data['cve']['id']}")

                predata.append({
                    "title" : data['cve']['id'],
                    "description" : data['cve']['descriptions'][0]['value'],
                    "link" : f"https://nvd.nist.gov/vuln/detail/{data['cve']['id']}"
                })
            print_msg(f"|{BLUE}-{RED} Total Result : {GREEN}{len(content)}{YELLOW} CVEs Found!")
            data.append({"nvddb" : predata})
        else:
            print_error("|")
            print_error(f"|{RED}- No result in National Vulnearbility Database!{WHITE}")
    except:
        print_error(f"|{RED}- Internal Error - No result in National Vulnearbility Database!{WHITE}")
    return

def find_ss(keyword = ""):
    keyword = f"{keyword}"
    keyword = keyword.replace(" ", "%20")
    resp = requests.get(f"https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch={keyword}")
    if resp.status_code == 200:
        return resp.json()
    else:
        return False

def find_ea(keyword=""):
    keyword = f"{keyword}"
    try:
        resp = requests.get(f"https://www.exploitalert.com/api/search-exploit?name={keyword}")
        if resp.status_code == 200:
            return resp.json()
        else:
            return False
    except:
        return False

def find_ps(keyword=""):
    keyword = f"{keyword}"
    resp = requests.get(f"https://packetstormsecurity.com/search/?q={keyword}")
    if resp.status_code == 200:
        return resp.text
    else:
        return False


signal.signal(signal.SIGINT, signal_handler)
arguments = sys.argv[1:]  


for arg in arguments:
    if arg == "--help":
        print(f"    {RED}[;,;]{GREEN} LazyOwn {CYAN}{version}{RESET}")
        print(f"    {GREEN}Uso: {WHITE}./run {GREEN}[opciones]{RESET}")
        print(f"    {YELLOW}Opciones:")
        print(f"    {BLUE}  --help         Muestra esta ayuda")
        print(f"    {BLUE}  -v             Muestra la version")
        print(f"    {BLUE}  -c             Ejecuta un comando del LazyOwn ej: ping")
        print(f"    {BLUE}  --no-banner    No muestra el Banner{RESET}")
        print(f"    {BLUE}  -s             Run as r00t {RESET}")
        sys.exit(0)

    elif arg == "-v":
        print_msg(f"LazyOwn Framework: {version}")
        sys.exit(0)

    elif arg == "--no-banner":
        NOBANNER = True

    elif arg == "-s":
        RUN_AS_ROOT = True

    elif arg.startswith("-c"):
        print_msg(f"Ejecutando comando {arg}")
        break
    else:
        print_error(f"Argumento no reconocido: {arg}")
        sys.exit(2)

if RUN_AS_ROOT:
    check_sudo()


if __name__ == "__main__":
    print_error("This script is not for execute apart from LazyOwn Framework")
    