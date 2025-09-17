import errno
import logging.config
import math
import os
import re
import socket
import subprocess
from contextlib import closing
from functools import cache
from logging import getLogger
from time import sleep, time
from typing import Literal
from pyx3270.x3270_commands import x3270_command
from pyx3270.exceptions import (
    CommandError,
    FieldTruncateError,
    KeyboardStateError,
    NotConnectedException,
    TerminatedError,
)
from pyx3270.iemulator import (
    AbstractCommand,
    AbstractEmulator,
    AbstractEmulatorCmd,
    AbstractExecutableApp,
)
from pyx3270.logging_config import LOGGING_CONFIG

logger = getLogger(__name__)

BINARY_FOLDER = os.path.join(os.path.dirname(__file__), 'bin')
MODEL_TYPE = Literal['2', '3', '4', '5']
MODEL_DIMENSIONS = {
    '2': {
        'rows': 24,
        'columns': 80,
    },
    '3': {
        'rows': 32,
        'columns': 80,
    },
    '4': {
        'rows': 43,
        'columns': 80,
    },
    '5': {
        'rows': 27,
        'columns': 132,
    },
}


class ExecutableApp(AbstractExecutableApp):
    args = list()

    def __init__(self, shell: bool = False, model: MODEL_TYPE = '2') -> None:
        logger.debug(f'Inicializando ExecutableApp ({shell=}, {model=})')
        self.shell = shell
        self.subprocess = None
        self.args = self._get_executable_app_args(model)
        self._spawn_app()

    def _spawn_app(self, args=None) -> None:
        logger.debug('Iniciando processo do aplicativo')
        kwargs = {
            'shell': self.shell,
            'stdin': subprocess.PIPE,
            'stdout': subprocess.PIPE,
            'stderr': subprocess.PIPE,
        }

        if args:
            self.args = args

        if os.name == 'nt':
            logger.debug(
                'Detectado sistema Windows, configurando flags específicos'
            )
            kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
        else:
            logger.debug(
                'Detectado sistema não-Windows, configurando nova sessão'
            )
            kwargs['start_new_session'] = True

        try:
            logger.debug(f'Executando comando: {self.args}')
            self.subprocess = subprocess.Popen(self.args, **kwargs)
            logger.debug(f'Processo iniciado com PID: {self.subprocess.pid}')
        except Exception:
            logger.error('Erro ao iniciar processo')
            raise

    def _get_executable_app_args(self, model: MODEL_TYPE) -> list:
        logger.debug(f'Obtendo argumentos para modelo: {model}')
        args = self.__class__.args + [
            '-xrm',
            f'*model:{model}',
            '-utf8',
        ]
        logger.debug(f'Argumentos completos: {args}')
        return args

    def connect(*args) -> bool:
        logger.debug(f'Método connect chamado com args: {args}')
        return False

    def close(self):
        logger.info('Fechando aplicativo')
        if self.subprocess and self.subprocess.poll() is None:
            logger.debug('Terminando processo em execução')
            self.subprocess.terminate()
        return_code = self.subprocess.returncode or self.subprocess.poll()
        return_code = return_code if return_code is not None else 0
        logger.info(f'Aplicativo fechado com código de retorno: {return_code}')
        return return_code

    def write(self, data: str):
        logger.debug(f'Escrevendo dados para o processo: {data}')
        try:
            self.subprocess.stdin.write(data)
            self.subprocess.stdin.flush()
            logger.debug('Dados escritos com sucesso')
        except Exception:
            logger.error('Erro ao escrever dados')
            raise

    def readline(self, timeout=5) -> bytes:
        try:
            logger.debug('Aguardando dados no buffer do processo')
            line = self.subprocess.stdout.readline()
            logger.debug(f'Linha lida: {line}')
            return line
        except Exception:
            logger.error('Erro ao ler linha')
            raise


class Command(AbstractCommand):
    def __init__(self, app: ExecutableApp, cmdstr: bytes | str) -> None:
        logger.debug(f'Inicializando Command com comando: {cmdstr}')
        if isinstance(cmdstr, str):
            cmdstr = bytes(cmdstr, 'utf-8', errors='replace')
        self.app = app
        self.cmdstr = cmdstr
        self.status_line = None
        self.data = []

    def execute(self) -> bool:
        logger.debug(f'Executando comando: {self.cmdstr}')
        try:
            self.app.write(self.cmdstr + b'\n')

            while True:
                line = self.app.readline()
                if not line.startswith('data:'.encode('utf-8')):
                    self.status_line = line.rstrip()
                    logger.debug(f'Status line: {self.status_line}')
                    result = self.app.readline().rstrip()
                    logger.debug(f'Resultado: {result}')
                    return self.handle_result(result.decode('utf-8'))

                logger.debug(f'Dados recebidos: {line}')
                self.data.append(line[6:].rstrip('\n\r'.encode('utf-8')))

        except Exception:
            logger.error(f'Erro durante execução do comando: {self.cmdstr}')
            raise

    def handle_result(self, result: str) -> bool:
        logger.debug(f'Processando resultado: {result}')
        count = 0
        max_loop = 5
        while count < max_loop:
            try:
                if not result and self.cmdstr == b'Quit':
                    logger.info('Comando Quit executado com sucesso')
                    return True
                elif result.lower() == 'ok':
                    logger.debug('Comando executado com sucesso (OK)')
                    return True
                else:
                    error_msg = f'"erro" esperado, mas recebido: {result}.'
                    logger.warning(error_msg)
                    raise ValueError(error_msg)
            except ValueError:
                logger.warning(
                    f'Tentativa {count + 1}/{max_loop} falhou, aguardando 1s'
                )
                sleep(0.35)
                count += 1

        msg = b'[sem mensagem de erro]'
        if self.data:
            msg = ''.encode('utf-8').join(self.data).rstrip()
        error_msg = msg.decode('utf-8')

        if (
            'keyboard locked' in error_msg.lower() 
            or 'canceled' in error_msg.lower()
        ):
            logger.error(f'Teclado travado detectado: {error_msg}')
            raise KeyboardStateError(error_msg)

        logger.error(f'Comando falhou: {error_msg}')
        raise CommandError(error_msg)


class Status:
    def __init__(self, status_line: str) -> None:
        logger.debug(f'Inicializando Status com linha: {status_line}')
        if not status_line:
            status_line = (' ' * 12).encode('utf-8')
            logger.debug('Status line vazia, usando padrão')
        self.status_line = status_line
        parts = status_line.split(' '.encode('utf-8'))

        try:
            self.keyboard = parts[0] or None
            self.screen_format = parts[1] or None
            self.field_protection = parts[2] or None
            self.connection_state = parts[3] or None
            self.emulator_mode = parts[4] or None
            self.model_number = parts[5] or None
            self.row_number = parts[6] or None
            self.col_number = parts[7] or None
            self.cursor_row = parts[8] or None
            self.cursor_col = parts[9] or None
            self.window_id = parts[10] or None
            self.exec_time = parts[11] or None
            logger.debug(
                f'Status: {self.connection_state=}, {self.emulator_mode=}'
            )
        except IndexError:
            logger.error('Status não tem items suficientes.')

    def __str__(self) -> str:
        return f'Status: {self.status_line}'


class Wc3270App(ExecutableApp):
    args = ['-xrm', '"wc3270.unlockDelay: False"']

    def __init__(self, model: MODEL_TYPE) -> None:
        logger.info(f'Inicializando Wc3270App com modelo: {model}')
        self.args = self._get_executable_app_args(model)
        self.script_port = Wc3270App._get_free_port()
        logger.debug(f'Porta de script alocada: {self.script_port}')
        super().__init__(shell=True, model=model)

    @staticmethod
    def _get_free_port() -> str:
        logger.debug('Obtendo porta livre para comunicação')
        try:
            with closing(
                socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            ) as s:
                s.bind(('127.0.0.1', 0))
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                port = s.getsockname()[1]
                logger.debug(f'Porta livre obtida: {port}')
                return port
        except Exception:
            logger.error('Erro ao obter porta livre.')
            raise

    @cache
    def _make_socket(self) -> None:
        logger.info(f'Criando socket para porta {self.script_port}')
        self.socket = sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        count = 0
        max_loop = 5
        while count < max_loop:
            try:
                logger.debug(
                    f'Tentativa {count + 1}/{max_loop} port:{self.script_port}'
                )
                sock.connect(('localhost', self.script_port))
                logger.info('Conexão de socket estabelecida com sucesso')
                break
            except socket.error as e:
                if e.errno != errno.ECONNREFUSED:
                    logger.error('Erro de conexão não recuperável.')
                    raise NotConnectedException
                logger.warning(
                    f'Conexão recusada, tentando novamente em 1s '
                    f'({count + 1}/{max_loop})'
                )
                sleep(1)
                count += 1
                if count >= max_loop:
                    logger.error(
                        f'Falha ao conectar após {max_loop} tentativas'
                    )

        self.socket_fh = sock.makefile(mode='rwb')
        logger.debug('File handle do socket criado')

    def connect(self, host: str) -> bool:
        logger.info(f'Conectando ao host: {host}')
        self.args = [
            'start',
            '/wait',
            '""',
            f'"{os.path.join(BINARY_FOLDER, "windows/wc3270")}"',
        ] + self.args
        self.args.extend(['-scriptport', str(self.script_port), host])
        logger.debug(f'Argumentos completos: {self.args}')

        try:
            self._spawn_app(' '.join(self.args))
            self._make_socket()
            return True
        except Exception:
            logger.error(f'Erro ao conectar ao host: {host}')
            raise

    def close(self) -> None:
        logger.info('Fechando conexão de socket')
        try:
            self.socket.close()
            logger.debug('Socket fechado com sucesso')
        except Exception:
            logger.error('Erro ao fechar socket.')

    def write(self, data: str) -> None:
        logger.debug(f'Escrevendo dados para socket: {data}')
        if self.socket_fh is None:
            logger.error('Tentativa de escrita em socket não inicializado')
            raise NotConnectedException
        try:
            self.socket_fh.write(data)
            self.socket_fh.flush()
            logger.debug('Dados escritos com sucesso')
        except OSError:
            logger.error('Erro de E/S ao escrever no socket')
            raise NotConnectedException

    def readline(self) -> bytes:
        logger.debug('Lendo linha do socket')
        if self.socket_fh is None:
            logger.error('Tentativa de leitura de socket não inicializado')
            raise NotConnectedException
        try:
            line = self.socket_fh.readline()
            logger.debug(f'Linha lida: {line}')
            return line
        except Exception:
            logger.error('Erro ao ler do socket')
            raise NotConnectedException


class Ws3270App(ExecutableApp):
    args = [
        os.path.join(BINARY_FOLDER, 'windows/ws3270'),
        '-xrm',
        'ws3270.unlockDelay:False',
    ]

    def __init__(self, model: MODEL_TYPE) -> None:
        logger.info(f'Inicializando Ws3270App com modelo: {model}')
        super().__init__(shell=False, model=model)


class X3270App(ExecutableApp):
    args = [
        os.path.join(BINARY_FOLDER, 'linux/x3270'),
        # 'x3270',
        '-xrm',
        'x3270.unlockDelay:False',
        '-script',
    ]

    def __init__(self, model: MODEL_TYPE) -> None:
        logger.info(f'Inicializando X3270App com modelo: {model}')
        super().__init__(shell=False, model=model)


class S3270App(ExecutableApp):
    args = [
        os.path.join(BINARY_FOLDER, 'linux/s3270'),
        '-xrm',
        's3270.unlockDelay:False',
    ]

    def __init__(self, model: MODEL_TYPE) -> None:
        logger.info(f'Inicializando S3270App com modelo: {model}')
        super().__init__(shell=True, model=model)


class X3270Cmd(AbstractEmulatorCmd):
    def __init__(self, time_unlock: int = 60) -> None:
        logger.info(f'Inicializando X3270Cmd com time_unlock: {time_unlock}')
        self.time_unlock = time_unlock

    def __getattr__(self, name):
        def x3270_builtin_func(*args, **kwargs):
            return x3270_command(self, name, *args, **kwargs)
        return x3270_builtin_func

    def clear_screen(self) -> None:
        logger.info('Limpando tela')
        count = 0
        max_loop = 6
        while count < max_loop:
            logger.debug(f'Tentativa {count + 1}/{max_loop} de limpar tela')
            self.clear()
            self.wait(self.time_unlock, 'unlock')
            if not self.get_full_screen(header=True).strip():
                logger.info('Tela limpa com sucesso')
                break
            logger.warning(
                f'Tela não foi limpa completamente na tentativa {count + 1}'
            )
            count += 1
        if count >= max_loop:
            logger.warning(
                f'Não foi possível limpar a tela completamente'
                f' após {max_loop} tentativas'
            )

    def wait_for_field(self, timeout: int = 30) -> None:
        logger.debug(f'Aguardando campo de entrada (timeout={timeout}s)')
        try:
            self.wait(timeout, 'InputField')
            logger.debug('Campo de entrada carregado.')
        except CommandError:
            logger.warning(
                f'Timeout atingido: {timeout}s.campo entrada não encontrado.'
            )

    def wait_string_found(
        self,
        ypos: int,
        xpos: int,
        string: str,
        equal: bool = True,
        timeout: int = 5,
    ) -> bool:
        logger.debug(
            f'Aguardando {string=} na posição '
            f'({ypos},{xpos}), {equal=}, {timeout=}s'
        )

        end_time = time() + timeout
        result = None

        while time() < end_time:
            try:
                found = self.get_string(ypos, xpos, len(string))
                logger.debug(f"String encontrada: '{found}'")
                if equal:
                    result = found == string
                else:
                    result = found != string
                logger.debug(f'Resultado da comparação: {result}')
                if result:
                    break
            except Exception:
                logger.debug('Erro ao buscar string, tentando novamente')
                continue

        logger.warning(
            f'Timeout atingido após {timeout}s, resultado final: {result}'
        )
        return result

    def string_found(self, ypos: int, xpos: int, string: str) -> bool:
        logger.debug(
            f'Verificando se {string=} existe na posição ({ypos},{xpos})'
        )
        try:
            found = self.get_string(ypos, xpos, len(string))
            result = found == string
            logger.debug(f"Resultado: {result} (encontrado: '{found}')")
            return result
        except Exception:
            logger.error(
                f'Erro ao verificar {string=}',
            )
            return False

    def delete_field(self) -> None:
        logger.debug('Deletando campo atual')
        self.deletefield()
        logger.debug('Campo deletado')

    def move_to(self, ypos: int, xpos: int) -> None:
        logger.debug(f'Movendo cursor para posição ({ypos},{xpos})')
        self.movecursor1(ypos, xpos)
        logger.debug('Cursor movido')

    def send_pf(self, value: int) -> None:
        logger.info(f'Enviando tecla PF{value}')
        self.pf(value)
        logger.debug(f'PF{value} enviado e tela desbloqueada')

    def send_string(
        self,
        tosend: str,
        ypos: int | None = None,
        xpos: int | None = None,
        password: bool = False,
    ) -> None:
        if not tosend:
            logger.warning('tosend não é string, send_string não executado.')
            return
        # Remove caracteres especiais
        original = tosend
        tosend = re.sub(r"[()\"']", '', tosend)

        tosend_str = 'password' if password else tosend

        if original != tosend:
            logger.debug(
                f'String modificada para {tosend_str} '
                f'(removidos caracteres especiais)'
            )

        if xpos is not None and ypos is not None:
            logger.info(
                f"Enviando string '{tosend_str}' para posição {ypos=} {xpos=}"
            )
            self.move_to(ypos, xpos)
        else:
            logger.info(f"Enviando string '{tosend_str}' na posição atual.")

        self.string(f'"{tosend}"')
        self.wait(self.time_unlock, 'unlock')
        logger.debug("String '{tosend_str}' enviada para o emulador.")

    def send_enter(self) -> None:
        logger.info('Enviando tecla ENTER')
        self.enter()
        self.wait(self.time_unlock, 'unlock')
        logger.debug('ENTER enviado e tela desbloqueada')

    def send_home(self) -> None:
        logger.info('Enviando tecla HOME')
        self.home()
        self.wait(self.time_unlock, 'unlock')
        logger.debug('HOME enviado e tela desbloqueada')

    def get_string(self, ypos: int, xpos: int, length: int) -> str:
        logger.debug(
            f'Obtendo string na posição ({ypos},{xpos})'
            f' com comprimento {length}'
        )
        try:
            self.check_limits(ypos, xpos)
            if (xpos + length) > (self.model_dimensions['columns'] + 1):
                logger.error(
                    f'Comprimento excede limite da tela: {xpos}+{length}'
                    f' > {self.model_dimensions["columns"] + 1}'
                )
                raise FieldTruncateError

            xpos -= 1
            ypos -= 1
            result = self.ascii(ypos, xpos, length)
            logger.debug(f"String obtida: '{result}'")
            return result
        except Exception:
            logger.error(
                'Erro ao obter string',
            )
            raise

    def get_string_area(
        self, yposi: int, xposi: int, ypose: int, xpose: int
    ) -> str:
        logger.debug(
            f'Obtendo área de texto de ({yposi},{xposi}) até ({ypose},{xpose})'
        )
        try:
            self.check_limits(yposi, xposi)
            self.check_limits(ypose, xpose)
            yposi -= 1
            xposi -= 1
            ypose -= yposi
            xpose -= xposi
            result = self.ascii(yposi, xposi, ypose, xpose)
            logger.debug(f'Área obtida com {len(result)} caracteres')
            return result
        except Exception:
            logger.error('Erro ao obter área de texto')
            raise

    def get_full_screen(self, header: bool = True) -> str:
        logger.debug(
            f'Obtendo conteúdo completo da tela (com header: {header})'
        )
        try:
            text = self.ascii()
            if not header:
                start = self.model_dimensions['columns']
                text = text[start:]
                logger.debug('Header removido do conteúdo')
            logger.debug(f'Conteúdo obtido com {len(text)} caracteres')
            return text
        except Exception:
            logger.error(
                'Erro ao obter conteúdo da tela.',
            )
            raise

    def save_screen(self, file_path: str, file_name: str):
        logger.info(f'Salvando tela em {file_path}\\{file_name}.html')
        try:
            if not os.path.exists(file_path):
                logger.debug(f'Criando diretório: {file_path}')
                os.makedirs(file_path)
            self.printtext('html', 'file', f'{file_path}\\{file_name}.html')
            logger.info('Tela salva com sucesso')
        except Exception:
            logger.error(
                'Erro ao salvar tela.',
            )
            raise

    def check_limits(self, ypos, xpos):
        logger.debug(f'Verificando limites para posição ({ypos},{xpos})')
        if ypos > self.model_dimensions['rows']:
            error_msg = (
                f'Você excedeu o limite do eixo y da tela do mainframe: '
                f'{ypos} > {self.model_dimensions["rows"]}'
            )
            logger.error(error_msg)
            raise FieldTruncateError(error_msg)
        if xpos > self.model_dimensions['columns']:
            error_msg = (
                f'Você excedeu o limite do eixo x da tela do mainframe: '
                f'{xpos} > {self.model_dimensions["columns"]}'
            )
            logger.error(error_msg)
            raise FieldTruncateError(error_msg)
        logger.debug('Posição dentro dos limites')

    def search_string(self, string: str, ignore_case: bool = False) -> bool:
        logger.info(f"Buscando texto '{string}' na tela ({ignore_case=})")
        try:
            for ypos in range(1, self.model_dimensions['rows'] + 1):
                line = self.get_string(
                    ypos, 1, self.model_dimensions['columns']
                )
                if ignore_case:
                    string_comp = string.lower()
                    line_comp = line.lower()
                    logger.debug(
                        f'Comparando (ignorando case) na linha {ypos}'
                    )
                else:
                    string_comp = string
                    line_comp = line
                    logger.debug(
                        f'Comparando (case sensitive) na linha {ypos}'
                    )

                if string_comp in line_comp:
                    logger.info(f'Texto encontrada na linha {ypos}')
                    return True

            logger.info('Texto não encontrada em nenhuma linha')
            return False
        except Exception:
            logger.error('Erro durante busca de texto')
            return False

    def get_string_positions(
        self, string: str, ignore_case=False
    ) -> list[tuple[int]]:
        logger.info(f"Buscando posições da texto '{string}' ({ignore_case=})")
        try:
            screen_content = self.get_full_screen(header=True)
            flags = 0 if not ignore_case else re.IGNORECASE
            indices_object = re.finditer(
                re.escape(string), screen_content, flags
            )
            indices = [index.start() for index in indices_object]
            logger.debug(f'Encontradas {len(indices)} ocorrências')

            positions = [
                self._get_ypos_and_xpos_from_index(index + 1)
                for index in indices
            ]
            logger.info(f'Posições encontradas: {positions}')
            return positions
        except Exception:
            logger.error('Erro ao buscar posições')
            return []

    def _get_ypos_and_xpos_from_index(self, index):
        logger.debug(f'Convertendo índice {index} para coordenadas (y,x)')
        ypos = math.ceil(index / self.model_dimensions['columns'])
        remainder = index % self.model_dimensions['columns']
        if remainder == 0:
            xpos = self.model_dimensions['columns']
        else:
            xpos = remainder
        logger.debug(f'Índice {index} convertido para ({ypos},{xpos})')
        return (ypos, xpos)


class X3270(AbstractEmulator, X3270Cmd):
    def __init__(
        self,
        visible: bool = False,
        model: MODEL_TYPE = '2',
        save_log_file: bool = False,
        time_unlock: int = 60,
    ) -> None:
        if save_log_file:
            logging.config.dictConfig(LOGGING_CONFIG)
        X3270Cmd.__init__(self, time_unlock=time_unlock)
        logger.info(f'Inicializando X3270 (visible={visible}, model={model})')
        self.model = model
        self.model_dimensions = MODEL_DIMENSIONS[model]
        self.visible = visible
        self.app: ExecutableApp = self._create_app()
        self.is_terminated = False
        self.host = None
        self.port = None
        self.tls = None
        self.mode_3270 = None
        logger.debug('X3270 inicializado')

    def _create_app(self) -> None:
        logger.info('Criando aplicativo emulador')
        try:
            if os.name == 'nt':  # windows
                if self.visible:
                    logger.debug('Criando Wc3270App (Windows, visível)')
                    return Wc3270App(self.model)
                logger.debug('Criando Ws3270App (Windows, não visível)')
                return Ws3270App(self.model)

            if self.visible:  # linux
                logger.debug('Criando X3270App (Linux, visível)')
                return X3270App(self.model)
            logger.debug('Criando S3270App (Linux, não visível)')
            return S3270App(self.model)

        except Exception:
            logger.error('Erro ao criar aplicativo.')
            raise

    def _exec_command(self, cmdstr: str) -> Command:
        logger.debug(f'Executando comando: {cmdstr}')
        if self.is_terminated:
            error_msg = 'Tentativa de executar comando em emulador terminado'
            logger.error(error_msg)
            raise TerminatedError
        max_loop = 3
        for exec in range(max_loop):
            try:
                cmd = Command(self.app, cmdstr)
                cmd.execute()
                self.status = Status(cmd.status_line)
                logger.debug(f'Comando executado, status: {self.status}')
                return cmd
            except NotConnectedException:
                logger.error('Emulador não conectado.')
                raise NotConnectedException
            except KeyboardStateError:
                sleep(1)
                logger.warning(
                    f'Nova tentativa de exec command:'
                    f'{cmdstr} {exec + 1}/{max_loop}'
                )
                self.reset()
                self.wait(self.time_unlock, 'unlock')
                self.tab()
        logger.error(
            f'Erro ao executar {cmdstr} total de tentativas: {max_loop}'
        )
        raise CommandError

    def terminate(self) -> None:
        logger.info('Terminando emulador')
        if not self.is_terminated:
            try:
                logger.debug('Enviando comando quit')
                self.quit()
            except BrokenPipeError:
                logger.warning('BrokenPipeError ao enviar quit, ignorando')
                self.ignore()
            except socket.error as ex:
                if ex.errno != errno.ECONNRESET:
                    logger.error('Erro de socket ao terminar')
                    raise ConnectionError
                logger.warning('Erro de conexão resetada')

        logger.debug('Fechando aplicativo')
        self.app.close()
        self.is_terminated = True
        logger.info('Emulador terminado com sucesso')

    def is_connected(self) -> bool:
        logger.debug('Verificando estado de conexão')
        try:
            self.query('ConnectionState')
            is_connected = self.status.connection_state.startswith(b'C(')
            logger.info(f'Estado de conexão: {is_connected}')
            return is_connected
        except Exception:
            logger.error('Erro ao verificar conexão')
            return False

    def connect_host(
        self,
        host: str,
        port: int | str,
        tls: bool = True,
        mode_3270: bool = True
    ) -> None:
        logger.info(f'Conectando ao host: {host}:{port} (tls={tls})')
        self.host = host
        self.port = port
        self.tls = tls
        self.mode_3270 = mode_3270
        tls_prefix = 'L:Y:' if tls else ''
        strint_conn = f'{tls_prefix}{host}:{port}'
        logger.debug(f'String de conexão: {strint_conn}')

        try:
            if self.app:
                if not self.app.connect(strint_conn):
                    logger.debug(
                        'Método connect do app retornou False, '
                        + 'tentando método connect direto'
                    )
                    self.connect(strint_conn)
                if mode_3270:
                    logger.debug('Aguardando modo 3270')
                    self.wait(5, '3270mode')
                logger.info('Conexão estabelecida com sucesso')
        except CommandError:
            logger.warning('CommandError durante conexão')
        except Exception:
            logger.error('Erro ao conectar')
            raise

    def reconnect_host(self) -> 'X3270':
        logger.info('Tentando reconectar ao host')
        try:
            logger.debug('Executando comando reconnect')
            self.reconnect()
            logger.info('Reconexão bem-sucedida')
            return self
        except Exception:
            logger.warning('Erro durante reconexão.')
            logger.debug('Terminando instância atual')
            self.terminate()
        finally:
            logger.info('Criando nova instância para reconexão')
            args = self.host, self.port, self.tls, self.mode_3270
            logger.debug(f'Argumentos para nova instância: {args}')
            new_instance = X3270(self.visible, self.model)
            new_instance.connect_host(*args)
            logger.debug('Nova instância criada com sucesso')
            # Atualiza todos os atributos de self com os do novo objeto
            self.__dict__.update(new_instance.__dict__)

            logger.debug('Atributos de self atualizados com sucesso')
            return self
