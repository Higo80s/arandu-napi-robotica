"""Upload de arquivos para a Nuvem UTFPR (WebDAV / Nextcloud)."""
import os
import time
from urllib.parse import quote

import requests
from requests.exceptions import RequestException

RETRY_STATUS = {500, 502, 503, 504}
RETRY_ATTEMPTS = 3


def _webdav_base_url():
    base = os.getenv('CLOUD_WEBDAV_URL', '').rstrip('/')
    if not base:
        raise ValueError('CLOUD_WEBDAV_URL não configurada no .env')
    return base + '/'


def _webdav_auth():
    user = os.getenv('CLOUD_USER')
    password = os.getenv('CLOUD_PASSWORD')
    if not user or not password:
        raise ValueError('CLOUD_USER / CLOUD_PASSWORD não configurados no .env')
    return (user, password)


def ensure_folder(folder_path):
    """Cria pasta no WebDAV se não existir (MKCOL recursivo simplificado)."""
    base = _webdav_base_url()
    auth = _webdav_auth()
    parts = [p for p in folder_path.strip('/').split('/') if p]
    current = ''
    for part in parts:
        current = f"{current}{quote(part, safe='')}/"
        url = f"{base}{current}"
        requests.request('MKCOL', url, auth=auth, timeout=60)


def _short_webdav_error(response):
    ctype = (response.headers.get('Content-Type') or '').lower()
    text = (response.text or '').strip()
    looks_html = (
        'html' in ctype
        or text[:15].lower().startswith('<!doctype')
        or text[:6].lower().startswith('<html')
    )
    if looks_html:
        return f'Falha no upload WebDAV ({response.status_code}) na Nuvem UTFPR.'
    return f'Falha no upload WebDAV ({response.status_code}): {text[:200]}'


def upload_bytes(remote_path, data, content_type='application/octet-stream'):
    """
    Envia bytes para remote_path relativo à raiz WebDAV do usuário.
    Retorna a URL completa usada no PUT.
    """
    base = _webdav_base_url()
    auth = _webdav_auth()
    remote_path = remote_path.strip('/')
    folder = '/'.join(remote_path.split('/')[:-1])
    if folder:
        ensure_folder(folder)

    url = base + quote(remote_path, safe='/')
    last_error = None
    for attempt in range(1, RETRY_ATTEMPTS + 1):
        try:
            response = requests.put(
                url,
                data=data,
                auth=auth,
                headers={'Content-Type': content_type, 'Overwrite': 'T'},
                timeout=120,
            )
        except RequestException as exc:
            last_error = exc
            if attempt < RETRY_ATTEMPTS:
                time.sleep(2 * attempt)
                continue
            raise RuntimeError(f'Falha no upload WebDAV: {exc}') from exc

        if response.status_code in (200, 201, 204):
            return url
        if response.status_code in RETRY_STATUS and attempt < RETRY_ATTEMPTS:
            time.sleep(2 * attempt)
            continue
        raise RuntimeError(_short_webdav_error(response))

    raise RuntimeError(f'Falha no upload WebDAV: {last_error}')
