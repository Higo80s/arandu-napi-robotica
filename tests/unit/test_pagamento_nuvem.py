"""Pagamento → Nuvem: catch-up pós dia 20, duplicata e erro WebDAV sem HTML."""
from datetime import date
from types import SimpleNamespace

import pytest

from services import nuvem_service
from tasks import enviar_pagamento_bolsas as pagamento


class _FixedDate(date):
    _today = date(2026, 10, 20)

    @classmethod
    def today(cls):
        return cls._today


def test_nao_envia_antes_do_dia_20_sem_atraso(monkeypatch):
    """19/10: outubro ainda não venceu; setembro já publicado → nada a fazer."""
    class D(_FixedDate):
        _today = date(2026, 10, 19)

    monkeypatch.setattr(pagamento, 'date', D)
    monkeypatch.setattr(
        pagamento,
        '_folha_ja_publicada',
        lambda mes_yyyy_mm: mes_yyyy_mm in ('2026-08', '2026-09'),
    )
    assert pagamento.enviar_pagamento_bolsas(None) is None


def test_catch_up_folha_atrasada_apos_dia_20(monkeypatch):
    """25/11: novembro devido desde dia 20 e ainda sem SUCESSO → publica."""
    class D(_FixedDate):
        _today = date(2026, 11, 25)

    calls = {'mes': None}

    def fake_enviar_core(app, mes_referencia, forcar=False):
        calls['mes'] = mes_referencia
        return True

    monkeypatch.setattr(pagamento, 'date', D)
    # Outubro já publicado; novembro devido e pendente → catch-up de 2026-11
    monkeypatch.setattr(
        pagamento,
        '_folha_ja_publicada',
        lambda mes: mes == '2026-10',
    )
    monkeypatch.setattr(pagamento, '_executar_envio', fake_enviar_core)
    assert pagamento.enviar_pagamento_bolsas(None) is True
    assert calls['mes'] == '2026-11'


def test_ignora_folha_ja_publicada_na_competencia(monkeypatch):
    monkeypatch.setattr(pagamento, 'date', _FixedDate)
    monkeypatch.setattr(pagamento, '_folha_ja_publicada', lambda filename_or_mes: True)
    assert pagamento.enviar_pagamento_bolsas(None, mes_referencia='2026-10') == 'ja_enviado'


def test_erro_webdav_html_nao_vaza_pagina(monkeypatch):
    monkeypatch.setenv('CLOUD_WEBDAV_URL', 'https://nuvem.example/remote.php/dav/files/u/')
    monkeypatch.setenv('CLOUD_USER', 'user')
    monkeypatch.setenv('CLOUD_PASSWORD', 'secret')
    monkeypatch.setattr(nuvem_service, 'RETRY_ATTEMPTS', 1)
    monkeypatch.setattr(nuvem_service.time, 'sleep', lambda _s: None)
    monkeypatch.setattr(nuvem_service.requests, 'request', lambda *a, **k: SimpleNamespace(status_code=201))

    html = '<!DOCTYPE html><html><title>UTFPR - Cloud</title></html>'
    monkeypatch.setattr(
        nuvem_service.requests,
        'put',
        lambda *a, **k: SimpleNamespace(
            status_code=500,
            headers={'Content-Type': 'text/html'},
            text=html,
        ),
    )
    with pytest.raises(RuntimeError) as err:
        nuvem_service.upload_bytes('05_pagamentos/pagamento_2026-10.xlsx', b'xlsx')
    msg = str(err.value)
    assert '500' in msg
    assert '<!DOCTYPE' not in msg
    assert 'UTFPR - Cloud' not in msg


def test_webdav_retenta_500_e_grava(monkeypatch):
    monkeypatch.setenv('CLOUD_WEBDAV_URL', 'https://nuvem.example/remote.php/dav/files/u/')
    monkeypatch.setenv('CLOUD_USER', 'user')
    monkeypatch.setenv('CLOUD_PASSWORD', 'secret')
    monkeypatch.setattr(nuvem_service.time, 'sleep', lambda _s: None)
    monkeypatch.setattr(nuvem_service.requests, 'request', lambda *a, **k: SimpleNamespace(status_code=201))

    calls = {'n': 0}

    def fake_put(*a, **k):
        calls['n'] += 1
        if calls['n'] == 1:
            return SimpleNamespace(
                status_code=500,
                headers={'Content-Type': 'text/html'},
                text='<!DOCTYPE html>',
            )
        return SimpleNamespace(status_code=201, headers={}, text='')

    monkeypatch.setattr(nuvem_service.requests, 'put', fake_put)
    url = nuvem_service.upload_bytes('05_pagamentos/pagamento_2026-10.xlsx', b'xlsx')
    assert calls['n'] == 2
    assert url.endswith('05_pagamentos/pagamento_2026-10.xlsx')


def test_mes_folha_pendente_helpers():
    assert pagamento.ultimo_mes_folha_devido(date(2026, 11, 25)) == date(2026, 11, 1)
    assert pagamento.ultimo_mes_folha_devido(date(2026, 11, 19)) == date(2026, 10, 1)
    pendente = pagamento.mes_folha_pendente(
        date(2026, 11, 25),
        lambda mes: mes.strftime('%Y-%m') == '2026-10',
    )
    assert pendente == date(2026, 11, 1)
