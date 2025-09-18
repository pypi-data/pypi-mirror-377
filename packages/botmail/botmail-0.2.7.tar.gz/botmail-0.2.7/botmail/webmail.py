import os
import re
import uuid
import email
import logging
import smtplib
import imaplib
import getpass
import platform
import mimetypes
import subprocess
from email import encoders
from datetime import datetime
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.message import EmailMessage
from email.header import decode_header
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart


class Email:

    def __init__(
            self,
            smtp_url,
            imap_url,
            prefix_env="WEBMAIL",
            smtp_port=587,
            imap_port=993
    ):
        self.prefix_env = prefix_env
        self.smtp_url = smtp_url
        self.imap_url = imap_url
        self.smtp_port = smtp_port
        self.imap_port = imap_port
        self.message = None
        self.all_mails_to_send = None
        self.mail_ids_imap = []
        self.credentials = dict.fromkeys(
            'USUARIO SENHA'.split()
        )
        self._load_credentials()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logout_imap()
        return False

    def _load_credentials(self):
        self.credentials = {
            key: os.getenv(f"{self.prefix_env}_{key}")
            for key in self.credentials
        }
        if params := [key for key in self.credentials
                      if not self.credentials[key]]:
            self.ask_credentials_cli(params)

    def ask_credentials_cli(self, list_params: list) -> None:
        for param in list_params:
            if param.lower() in ("senha", "password"):
                value = getpass.getpass(
                    f"Informe a Senha para" f" ({self.prefix_env}): "
                )
            else:
                value = input(f"Informe o(a) {param} "
                              f"para ({self.prefix_env}): ")
            self.set_persistent_env_var(
                f"{self.prefix_env}_{param}".upper(),
                value
            )
            self.credentials[param] = value

    def set_persistent_env_var(self, var_name: str, var_value: str) -> None:
        system = platform.system()

        if system == "Windows":
            subprocess.run(["setx", var_name, var_value], check=True)
        elif system == "Linux":
            home = os.path.expanduser("~")
            bashrc_path = os.path.abspath(os.path.join(home, ".bashrc"))
            with open(bashrc_path, "a") as bashrc:
                bashrc.write(f'\nexport {var_name}="{var_value}"\n')
            logging.debug(
                f"Variable added to {bashrc_path}. "
                "Please re-login or source the file."
            )
        else:
            raise NotImplementedError(
                f"Setting environment variables persistently"
                f" is not implemented for {system}"
            )

    def create_file_txt(
            self,
            text: str = "",
            name_file: str = "",
            path_to_save: str = "",
            subs: bool = False,
    ):

        os.makedirs(path_to_save, exist_ok=True)
        full_path_file = os.path.abspath(f"{path_to_save}/{name_file}.txt")

        if not os.path.exists(full_path_file) or subs:
            with open(full_path_file, "w") as f:
                f.write(text)
        else:
            with open(full_path_file, "r") as f:
                text = f.read()
        return text

    @staticmethod
    def thread_it(qtd_threads, list_params, function):
        from tqdm import tqdm
        import threading as td

        threads = [td.Thread() for _ in range(qtd_threads)]
        counter = 0
        for param in tqdm(list_params, desc="Threading", unit="item"):
            threads[counter] = td.Thread(target=lambda: function(param))
            threads[counter].start()
            counter += 1
            if counter >= qtd_threads:
                [threads[i].join() for i in range(counter)]
                counter = 0
        if counter < qtd_threads:
            [threads[i].join() for i in range(counter)]

    @staticmethod
    def convert_string_date_to_datetime(date_string, date_format: str = "%d/%m/%Y"):
        # Convert the date string to a datetime object
        return datetime.strptime(date_string, date_format)

    def _conect_server_imap(self):
        self.imap_server = imaplib.IMAP4_SSL(
            self.imap_url,
            port=self.imap_port
        )

    def _conect_server_smtp(self):
        self.smtp_server = smtplib.SMTP(self.smtp_url, self.smtp_port)
        self.smtp_server.connect(self.smtp_url, self.smtp_port)

    def _start_server_smtp(self):
        self._conect_server_smtp()
        self.smtp_server.ehlo()
        self.smtp_server.starttls()
        self.smtp_server.ehlo()

    def _close_server_smtp(self):
        self.smtp_server.quit()

    def _login_smtp(self):
        self.smtp_server.login(
            user=self.credentials['USUARIO'],
            password=self.credentials['SENHA'],
        )

    def _header_mail_smtp(self, assunto, email_destinatario, emails_em_copia):
        if not isinstance(emails_em_copia, list):
            emails_em_copia = emails_em_copia.split(";")
        #emails_em_copia.append(self.credentials['USUARIO'])
        COMMASPACE = ", "
        self.message = MIMEMultipart()
        self.message["From"] = self.credentials['USUARIO']
        self.message["To"] = COMMASPACE.join([email_destinatario])
        self.message["Cc"] = COMMASPACE.join(emails_em_copia)
        self.message["Subject"] = assunto
        self.all_mails_to_send = [email_destinatario] + emails_em_copia

    def generate_simple_html_body(
            self,
            saudacao,
            destinatario,
            text_mail,
            header_html: str | None = None,
            body_html: str | None = None
    ):

        if not header_html:
            header = """
            <!DOCTYPE html>
            <html>
                <head>
                    <style>
                        body {
                            font-family: Arial, sans-serif;
                            background-color: #F5F5F5;
                            padding: 20px;
                            color: #333;
                        }
                        .container {
                            background-color: #fff;
                            border-radius: 5px;
                            padding: 20px;
                        }
                        h1 {
                            color: #4F4F4F;
                        }
                        h2 {
                            color: #414651;
                        }
                        h4 {
                            color: #4E74C3;
                        }
                        a {
                            color: #2F80ED;
                            text-decoration: none;
                        }
                        a:hover {
                            color: #0F53A6;
                        }
                    </style>
                </head>

            """
        else:
            header = header_html

        if not body_html:
            body = """
                <body>
                    <div class="container">
                        <h2>#saudacao #destinatario</h1>
                        <h3>#text_mail</h2>
                    </div>
                </body>
            </html>
            """
        else:
            body = body_html

        html = header + body

        html = (
            html.replace("#saudacao", saudacao)
            .replace("#destinatario", destinatario)
            .replace("#text_mail", text_mail)
        )
        return html

    def _body_mail_smtp(
            self,
            body_message,
            format_mail: str = "html"
    ):
        self.message.attach(
            MIMEText(
                body_message,
                format_mail,
            )
        )

    def _append_file_smtp(self, file_paths: str, *args, **kwargs) -> None:
        """
        Anexa ao e-mail (`self.message`) um ou vários arquivos separados por “;”.
        Agora reconhece automaticamente imagens (png, jpg, gif, …).
        """
        for raw_path in file_paths.split(";"):
            file_path = raw_path.strip()
            if not file_path:
                continue

            # Descobre o tipo MIME ⇒ 'image/png', 'application/pdf', etc.
            mime_type, _ = mimetypes.guess_type(file_path)
            main, sub = (mime_type or "application/octet-stream").split("/", 1)

            with open(os.path.abspath(file_path), "rb") as fp:
                data = fp.read()

            # Imagens usam MIMEImage (fica inline-safe); demais usam MIMEBase
            if main == "image":
                continue # imagens sendo tratadas em _embed_images_cid
                #part = MIMEImage(data, _subtype=sub)
            else:
                part = MIMEBase(main, sub)
                part.set_payload(data)
                encoders.encode_base64(part)

            part.add_header(
                "Content-Disposition",
                f'attachment; filename="{os.path.basename(file_path).replace(" ", "_")}"'
            )
            self.message.attach(part)

    def _embed_images_cid(self, html: str, image_paths: str) -> str:
        """
        Anexa imagens como partes inline e devolve o HTML já
        com os <img src="cid:..."> corretos.

        Exemplo de uso:
            html = '''
                <h1>Olá</h1>
                <p>Veja o logo:</p>
                <!-- placeholder será trocado por CID -->
                <img src="cid:logo.png">
            '''
            html = self._embed_images_cid(html, 'logo.png')
        """
        if not image_paths:
            return html

        for raw_path in image_paths.split(";"):
            file_path = raw_path.strip()
            if not file_path:
                continue

            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type or not mime_type.startswith("image/"):
                # não é imagem → pula
                continue

            # Extrai o subtipo (jpeg, png, gif etc)
            _, subtype = mime_type.split("/", 1)

            # Gera um CID único (evita conflito se o mesmo arquivo aparecer 2×)
            cid = f"{uuid.uuid4().hex}@inline"

            with open(os.path.abspath(file_path), "rb") as fp:
                img = MIMEImage(fp.read(), _subtype=subtype)
                img.add_header("Content-ID", f"<{cid}>")
                img.add_header("Content-Disposition", "inline", filename=os.path.basename(file_path))
                self.message.attach(img)

            # Substitui qualquer ocorrência de cid:<nome-arquivo> pelo novo CID
            basename = os.path.basename(file_path)
            html = html.replace(f"cid:{basename}", f"cid:{cid}")

        return html

    def _send_smtp(self):
        self.smtp_server.sendmail(
            self.credentials['USUARIO'],
            self.all_mails_to_send,
            self.message.as_string()
        )

    def send_email(
            self,
            assunto: str,
            email_destinatario: str,
            emails_em_copia: list | str,
            body_message: str,
            path_file: str | None = None,
            type_file: str = "octet-stream",
            format_mail: str = "html",
    ):
        self._start_server_smtp()
        self._login_smtp()
        self._header_mail_smtp(
            assunto,
            email_destinatario,
            emails_em_copia
        )
        body_message = self._embed_images_cid(body_message, path_file)
        self._body_mail_smtp(
            body_message,
            format_mail
        )
        if path_file is not None and len(path_file) > 0:
            self._append_file_smtp(path_file, type_file)
        self._send_smtp()
        self._close_server_smtp()
        logging.debug('Email successfully sent!')

    def extract_payload(self, message):
        """Extrai o payload principal (texto) de uma mensagem de e-mail."""
        if message.is_multipart():
            # Itera pelas partes e encontra a parte de texto
            for part in message.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":  # Prioriza o texto simples
                    return (part.get_payload(decode=True).
                            decode(part.get_content_charset() or 'utf-8'))
        else:
            # Mensagem não multipart, extrai o payload diretamente
            return (message.get_payload(decode=True)
                    .decode(message.get_content_charset() or 'utf-8'))

    def forward_email(
            self,
            original_email_id: str | int,
            forward_to: str | list,
            body: str
    ) -> None:
        """Cria e envia um e-mail de encaminhamento."""
        status, data = self.imap_server.fetch(str(original_email_id), '(RFC822)')
        if status == 'OK':
            original_message = email.message_from_bytes(data[0][1])
        else:
            raise Exception("Erro ao recuperar e-mail.")

        forwarded_message = EmailMessage()
        COMMASPACE = ", "
        forward_to = (forward_to.split(';')
                      if isinstance(forward_to, str)
                      else forward_to)
        subject = original_message['Subject'].replace('\n', '').replace('\r', '')
        forwarded_message['Subject'] = f"Fwd: {subject}"
        forwarded_message['From'] = self.credentials['USUARIO']
        forwarded_message['To'] = COMMASPACE.join(forward_to)
        # Extrai o conteúdo do e-mail original
        # original_content = self.extract_payload(original_message)

        # Torna a mensagem multipart para aceitar anexos
        forwarded_message.make_mixed()
        # Opcional: incluir o e-mail original como anexo (preserva 100% dos dados)
        forwarded_message.attach(MIMEText(
            body
        ))
        # forwarded_message.set_content(f"Encaminhando o e-mail:\n\n---\n{original_content}")

        forwarded_message.add_attachment(
            original_message.as_bytes(),
            maintype='message',
            subtype='rfc822'
        )

        self._start_server_smtp()
        self._login_smtp()
        self.smtp_server.send_message(forwarded_message)
        logging.debug("E-mail encaminhado com sucesso!")
        self._close_server_smtp()

    def forward_email2(
            self,
            original_email_id: str | int,
            forward_to: str | list,
            forward_to_cc: str | list,
            body: str
    ) -> None:
        """Cria e envia um e-mail de encaminhamento."""
        # Recupera o e-mail original
        status, data = self.imap_server.fetch(str(original_email_id), '(RFC822)')
        if status == 'OK':
            original_message = email.message_from_bytes(data[0][1])
        else:
            raise Exception("Erro ao recuperar e-mail.")

        forwarded_message = EmailMessage()
        COMMASPACE = ", "

        # Configura o assunto
        subject = original_message['Subject'].replace('\n', '').replace('\r', '')
        forwarded_message['Subject'] = f"Fwd: {subject}"
        forwarded_message['From'] = self.credentials['USUARIO']
        forwarded_message['To'] = COMMASPACE.join(forward_to.split(';'))
        forwarded_message["Cc"] = COMMASPACE.join(forward_to_cc.split(';'))

        # Extrai o conteúdo do e-mail original
        original_content = self.extract_payload(original_message)

        # Constrói o corpo do e-mail com o histórico
        forwarded_message.set_content(f"{body}\n\n--- Histórico do E-mail Original ---\n{original_content}")

        # Torna a mensagem multipart para aceitar anexos
        forwarded_message.make_mixed()

        # Anexa os anexos do e-mail original
        for part in original_message.walk():
            content_disposition = part.get("Content-Disposition")
            if content_disposition and "attachment" in content_disposition:
                # Extrai o conteúdo do anexo
                attachment_data = part.get_payload(decode=True)
                filename = part.get_filename()
                # Limpa o nome do arquivo para remover caracteres inválidos
                if filename:
                    filename = filename.replace('\n', '').replace('\r', '')

                if filename:
                    # Cria o anexo
                    attachment = MIMEBase(part.get_content_type().split('/')[0], part.get_content_type().split('/')[1])
                    attachment.set_payload(attachment_data)
                    encoders.encode_base64(attachment)
                    attachment.add_header('Content-Disposition', f'attachment; filename="{filename}"')
                    # Adiciona o anexo ao e-mail de encaminhamento
                    forwarded_message.add_attachment(
                        attachment_data,
                        maintype=part.get_content_type().split('/')[0],
                        subtype=part.get_content_type().split('/')[1],
                        filename=filename
                    )

        forwarded_message.add_attachment(
            original_message.as_bytes(),
            maintype='message',
            subtype='rfc822'
        )
        # Envia o e-mail
        self._start_server_smtp()
        self._login_smtp()
        self.smtp_server.send_message(forwarded_message)
        logging.debug("E-mail encaminhado com sucesso!")
        self._close_server_smtp()

    def set_flag(self, email_id, flag: str) -> bool:
        r"""
        Além das flagas padrão do imap:
        Seen: Indica que o e-mail foi lido.
        Answered: Indica que o e-mail foi respondido.
        Flagged: Indica que o e-mail foi marcado como importante.
        Deleted: Indica que o e-mail foi marcado para exclusão.
        Draft: Indica que o e-mail é um rascunho.
        Recent: Indica que o e-mail é novo e ainda não foi acessado por nenhum cliente de e-mail.
        Com este metodo voce pode settar novas flags personalizadas passando uma string.
        Não inserir "\" na flag, pois o servidor imap não reconhecerá sua "\flag" como válida
        """
        try:
            # Note the absence of `\` before the flag for custom flags
            result = self.imap_server.store(str(email_id), "+FLAGS", flag)
            if result[0] == "OK":
                logging.debug(f"Flag {flag} set for email ID {email_id}")
                return True
            else:
                logging.error(f"Falha ao setar flag {flag} para o email ID {email_id}")
                return False
        except Exception as e:
            logging.exception(f"Erro ao setar flag {flag} ao email ID {email_id}: {str(e)}")
            return False

    def remove_flag(self, email_id, flag: str) -> bool:
        r"""Remove uma flag acicionada.
        Não inserir "\" na flag, pois o servidor imap não reconhecerá sua "\flag" como válida
        """
        try:
            result = self.imap_server.store(str(email_id), "-FLAGS", flag)
            if result[0] == "OK":
                logging.debug(f"Flag {flag} removed for email ID {email_id}")
                return True
            else:
                logging.error(f"Falha ao remover flag {flag} do email ID {email_id}")
                return False
        except Exception as e:
            logging.exception(f"Error ao remover flag {flag} do email ID {email_id}: {str(e)}")
            return False

    def check_flag(self, email_id, flag: str) -> bool:
        r"""Verifica se uma determinada flag foi setada no email
        Não inserir "\" na flag, pois o servidor imap não reconhecerá sua "\flag" como válida
        """
        try:
            result, data = self.imap_server.uid("fetch", str(email_id), "(FLAGS)")
            if result == "OK":
                flags = data[0].decode()
                if flag in flags:
                    logging.debug(f"Email ID {email_id} contém a flag {flag}")
                    return True
                else:
                    logging.debug(f"Email ID {email_id} não possui a flag {flag}")
                    return False
            else:
                logging.error(f"Falha ao verificar flags no email ID {email_id}")
                return False
        except Exception as e:
            logging.exception(f"Erro ao verificar flag {flag} no email ID {email_id}: {str(e)}")
            return False

    def login_imap(self):
        self._conect_server_imap()
        try:
            self.imap_server.login(
                user=self.credentials['USUARIO'],
                password=self.credentials['SENHA'],
            )
        except imaplib.IMAP4.error as e:
            logging.exception('Error during login, ensure you dont tried to login twice with an already ative session')
            self.logout_imap()
            self.imap_server.login(
                user=self.credentials['USUARIO'],
                password=self.credentials['SENHA'],
            )

    def select_imap(self, partition: str = "INBOX"):
        self.imap_server.select(partition)

    def logout_imap(self):
        self.imap_server.logout()

    def get_all_emails_ids(self):
        result, data = self.imap_server.uid("search", None, "ALL")
        mail_ids = data[0]
        id_list = mail_ids.split()
        id_list = [int(id_) for id_ in id_list]
        return id_list

    def get_content_from_email_id(self, id_):
        logging.debug(id_)
        result, message_raw = self.imap_server.uid("fetch", str(id_), "(BODY.PEEK[])")
        if message_raw is not None and message_raw[0] is not None:
            raw_email = message_raw[0][1].decode(
                "utf-8"
            )  # converts byte literal to string removing b''"utf-8"
            email_message = email.message_from_string(raw_email)
        return email_message

    def extract_all_tables_from_email_html(self, id_):
        import chardet
        import pandas as pd
        from bs4 import BeautifulSoup

        message = self.get_content_from_email_id(id_)
        email_body = None
        try:
            if message.is_multipart():
                for part in message.walk():
                    content_type = part.get_content_type()
                    if content_type == "text/html":
                        part_content = part.get_payload(decode=True)
                        detected_encoding = chardet.detect(part_content)['encoding']  # Detecta a codificação
                        logging.debug(f'Detected encoding: {detected_encoding}')
                        email_body = part_content.decode(detected_encoding,
                                                         errors='replace')  # Decodifica com a codificação detectada
            else:
                email_body = message.get_payload(decode=True).decode()
        except UnicodeDecodeError as e:
            logging.error(e)

        # Lista para armazenar os DataFrames
        dataframes = []
        if email_body:
            soup = BeautifulSoup(email_body, 'html.parser')
            # Procura a tabela no corpo do e-mail
            tables = soup.find_all('table')
            if not tables:
                raise Exception("Tabela não encontrada no e-mail.")

            for table in tables:
                rows = []
                # Itera pelas linhas da tabela
                for row in table.find_all('tr'):
                    # Extrai o texto de cada célula (td ou th)
                    cells = [cell.get_text(strip=True) for cell in row.find_all(['td', 'th'])]
                    rows.append(cells)
                # Converte para DataFrame
                if rows:
                    df = pd.DataFrame(rows)
                    df.columns = df.iloc[0]  # Define a primeira linha como cabeçalho
                    df = df[1:].reset_index(drop=True)  # Remove a primeira linha e redefine os índices
                    logging.debug(df)
                    dataframes.append(df)

        return dataframes

    def get_content_from_email_id_by_fetch(self, id_):
        _, data = self.imap_server.fetch(str(id_).encode(), "(RFC822)")
        email_message = data[0][1].decode("utf-8")
        email_message = email.message_from_string(email_message)
        return email_message

    def get_sender_mail_from_email_id(self, id_):
        email_message = self.get_content_from_email_id_by_fetch(id_)
        mail_from = email_message["From"]
        logging.debug(mail_from)
        return mail_from

    def get_text_from_email_id(self, id_):
        content = self.get_content_from_email_id(id_)
        logging.debug("#" * 60)
        texts = [
            part.as_string()
            for part in content.walk()
            if part.get_content_maintype() == "text"
        ]
        logging.debug(texts)
        return texts

    def get_email_ids_by_sender_mail(self, sender_mail):
        result, email_ids = self.imap_server.search(None, f'(FROM "{sender_mail}")')
        email_ids = email_ids[0].split()
        email_ids = [int(id_) for id_ in email_ids]
        logging.debug(email_ids)
        return email_ids

    def get_email_ids_by_subject(self, subject):
        # Use the SUBJECT search criterion instead of FROM
        result, email_ids = self.imap_server.search(None, f'(SUBJECT "{subject}")')
        email_ids = email_ids[0].split()
        email_ids = [int(id_) for id_ in email_ids]
        logging.debug(email_ids)
        return email_ids

    def get_email_ids_by_range_date(self, data_ini, data_fim):
        data_ini = self.convert_string_date_to_datetime(data_ini)
        data_fim = self.convert_string_date_to_datetime(data_fim)
        criteria = '(OR SINCE "{0:%d-%b-%Y}" ON "{1:%d-%b-%Y}")'.format(data_ini, data_fim)
        logging.debug(criteria)
        status, email_ids = self.imap_server.search(
            None,
            criteria,
        )
        email_ids = email_ids[0].split()
        email_ids = [int(id_) for id_ in email_ids]
        logging.debug(email_ids)
        return email_ids

    def clean_filename(self, filename):
        if isinstance(filename, str):
            # Define a pattern to match any character that is not allowed in filenames
            invalid_characters = r'[<>:"/\\|?*\;\n\r+,-]'

            # Replace invalid characters with an underscore or remove them
            cleaned_filename = re.sub(invalid_characters, '_', filename)

            # Optionally, trim leading and trailing whitespace
            cleaned_filename = cleaned_filename.strip()
            logging.debug(f"Filename: {filename}", )
            logging.debug(f"Cleaned Filename: {cleaned_filename}")
            return cleaned_filename

    def get_attachments_from_email_id(
            self,
            id_,
            folder_to,
            list_types_to_download: list | None = None
    ):
        os.makedirs(folder_to, exist_ok=True)
        content = self.get_content_from_email_id_by_fetch(id_)
        for part in content.walk():
            if part.get_content_maintype() == "multipart":
                continue
            if part.get("Content-Disposition") is None:  # or 'attachment' not in part.get("Content-Disposition"):
                continue

            fileName = part.get_filename()
            decoded_header = decode_header(fileName)
            # decode_header pode retornar uma lista de tuplas, cada uma (decodificado, charset)
            fname_decoded = ''
            for dec, charset in decoded_header:
                if charset:
                    # Converte para string usando o charset
                    fname_decoded += dec.decode(charset)
                else:
                    # Já está em str (Python 3), ou bytes sem charset
                    if isinstance(dec, bytes):
                        fname_decoded += dec.decode('utf-8', errors='replace')
                    else:
                        fname_decoded += dec

            logging.debug(f"Nome decodificado do arquivo: {fname_decoded}")
            fileName = self.clean_filename(fname_decoded)
            if fileName is None:
                continue
            ext = fileName.split('.')[-1] if '.' in fileName else None
            list_types_to_download = [value.upper() for value in
                                      list_types_to_download] if list_types_to_download is not None else None
            if ext is not None and list_types_to_download is not None and ext.upper() not in list_types_to_download:
                continue
            if bool(fileName):
                try:
                    filePath = os.path.abspath(os.path.join(folder_to, fileName))
                    if not os.path.isfile(filePath):
                        logging.debug(fileName)
                        with open(filePath, "wb") as f:
                            f.write(part.get_payload(decode=True))
                except Exception as e:
                    logging.exception(e)


if __name__ == "__main__":
    mail = Email(
        "smtp.example.com.br",
        "imap.example.com.br"
    )
    mail.send_email(
        "Nem Email Class",
        "example1@gmail.com",
        ["example2@gmail.com"],
        mail.generate_simple_html_body('Hi', 'BotMail', "What's up?"),
    )
