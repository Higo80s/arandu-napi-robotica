"""
Módulo de Envio de E-mails
==========================
Responsável por gerenciar o envio assíncrono de notificações por e-mail.
Requer Flask-Mail.
"""
import os
from email import policy
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate

from flask import current_app
from flask_mail import Message, force_text, sanitize_address, sanitize_addresses, sanitize_subject
from threading import Thread

from extensions import mail  # [REFATORACAO] Instancia centralizada

# Content-ID nos templates (<img src="cid:napi_logo">) — anexo inline em multipart/related.
LOGO_CID = 'napi_logo'
_LOGO_CACHE = None


def _logo_path():
    try:
        static = current_app.static_folder
    except Exception:
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        static = os.path.join(root, 'static')
    return os.path.join(static, 'images', 'napi_robotica_logo.png')


def _load_logo_bytes():
    """Lê (e memoriza) os bytes do logo NAPI-Robótica."""
    global _LOGO_CACHE
    if _LOGO_CACHE is None:
        try:
            with open(_logo_path(), 'rb') as fh:
                _LOGO_CACHE = fh.read()
        except OSError:
            _LOGO_CACHE = b''
    return _LOGO_CACHE


def _read_inline_file(path):
    if not path or not os.path.isfile(path):
        return None, None
    with open(path, 'rb') as fh:
        data = fh.read()
    filename = os.path.basename(path)
    return data, filename


def _inline_parts_for_message(html_body, inline_images):
    """
    Monta lista (cid, bytes, filename, subtype) para imagens inline.
    Logo padrão é incluído quando o HTML referencia cid:napi_logo.
    """
    by_cid = {}
    if inline_images:
        for cid, path in inline_images.items():
            data, filename = _read_inline_file(path)
            if data:
                subtype = 'png' if filename.lower().endswith('.png') else 'jpeg'
                by_cid[cid] = (data, filename, subtype)

    if html_body and f'cid:{LOGO_CID}' in html_body and LOGO_CID not in by_cid:
        logo = _load_logo_bytes()
        if logo:
            by_cid[LOGO_CID] = (logo, 'napi_robotica_logo.png', 'png')

    return [(cid, *by_cid[cid]) for cid in sorted(by_cid.keys())]


def _enable_related_inline(msg, inline_parts):
    """
    Substitui multipart/mixed por multipart/related para CIDs aparecerem no HTML,
    não como anexo no rodapé (Outlook/Gmail).
    """
    def _message_related():
        encoding = msg.charset or 'utf-8'
        related = MIMEMultipart('related')

        alternative = MIMEMultipart('alternative')
        alternative.attach(msg._mimetext(msg.body, 'plain'))
        for mimetype, content in (msg.alts or {}).items():
            alternative.attach(msg._mimetext(content, mimetype))
        related.attach(alternative)

        for cid, data, filename, subtype in inline_parts:
            img = MIMEImage(data, _subtype=subtype)
            img.add_header('Content-ID', '<%s>' % cid)
            img.add_header('Content-Disposition', 'inline', filename=filename)
            related.attach(img)

        other = list(msg.attachments or [])
        root = related
        if other:
            root = MIMEMultipart('mixed')
            root.attach(related)
            for attachment in other:
                from email.encoders import encode_base64
                from email.mime.base import MIMEBase
                import re
                import unicodedata

                f = MIMEBase(*attachment.content_type.split('/'))
                f.set_payload(attachment.data)
                encode_base64(f)
                if attachment.filename is not None:
                    filename = attachment.filename
                    ascii_attachments = current_app.extensions['mail'].ascii_attachments
                    if ascii_attachments:
                        filename = unicodedata.normalize('NFKD', attachment.filename)
                        filename = filename.encode('ascii', 'ignore').decode('ascii')
                        filename = re.compile(r'[\s]+', re.UNICODE).sub(' ', filename).strip()
                    try:
                        filename.encode('ascii')
                    except UnicodeEncodeError:
                        f.add_header(
                            'Content-Disposition',
                            attachment.disposition,
                            filename=('UTF8', '', filename),
                        )
                    else:
                        f.add_header(
                            'Content-Disposition',
                            attachment.disposition,
                            filename=filename,
                        )
                for key, value in (attachment.headers or {}).items():
                    f.add_header(key, value)
                root.attach(f)

        if msg.subject:
            root['Subject'] = sanitize_subject(force_text(msg.subject), encoding)
        root['From'] = sanitize_address(msg.sender, encoding)
        root['To'] = ', '.join(list(set(sanitize_addresses(msg.recipients, encoding))))
        root['Date'] = formatdate(msg.date, localtime=True)
        root['Message-ID'] = msg.msgId
        if msg.cc:
            root['Cc'] = ', '.join(list(set(sanitize_addresses(msg.cc, encoding))))
        if msg.reply_to:
            root['Reply-To'] = sanitize_address(msg.reply_to, encoding)
        if msg.extra_headers:
            for k, v in msg.extra_headers.items():
                root[k] = v
        root.policy = policy.SMTP
        return root

    msg._message = _message_related


def send_async_email(app, msg):
    """Função background para envio real"""
    with app.app_context():
        try:
            mail.send(msg)
            print(f"📧 [EMAIL] Enviado com sucesso para: {msg.recipients}")
        except Exception as e:
            print(f"❌ [EMAIL ERRO] Falha no envio: {e}")


def send_email(subject, recipients, html_body, text_body=None, inline_images=None, cc=None):
    """
    Dispara um e-mail em background (Thread).

    Args:
        subject (str): Assunto
        recipients (list): Lista de e-mails (strings)
        html_body (str): Conteúdo HTML
        text_body (str): Conteúdo Texto Puro (Opcional)
        inline_images (dict|None): {cid: caminho_arquivo} para <img src="cid:...">
        cc (list|None): Cópia (CC)
    """
    mail_user = os.getenv('MAIL_USERNAME', '')
    if not mail_user or 'seu_email' in mail_user:
        print("⚠️  [EMAIL SIMULADO] Configuração SMTP ausente.")
        print(f"   Assunto: {subject}")
        print(f"   Para: {recipients}")
        if cc:
            print(f"   CC: {cc}")
        return

    app = current_app._get_current_object()
    msg = Message(subject, recipients=recipients, cc=cc or None)
    msg.html = html_body
    msg.body = text_body or "Visualize este e-mail em formato HTML."

    sender = os.getenv('MAIL_DEFAULT_SENDER')
    if sender:
        msg.sender = sender

    inline_parts = _inline_parts_for_message(html_body, inline_images)
    if inline_parts:
        _enable_related_inline(msg, inline_parts)

    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
