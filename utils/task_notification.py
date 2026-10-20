"""Saída estruturada para o balão das tarefas agendadas do Windows."""
from __future__ import annotations

import json


MARKER = 'ARANDU_TASK_NOTIFICATION='


def emit_task_notification(
    message: str,
    *,
    count: int = 0,
    recipients: str | list[str] | None = None,
) -> None:
    count = max(0, int(count or 0))
    text = f'{message.rstrip(" .")} ({count:02d}).'
    if recipients:
        if isinstance(recipients, (list, tuple, set)):
            recipients = ', '.join(str(item) for item in recipients if item)
        if recipients:
            text += f' Destino: {recipients}.'
    print(
        MARKER + json.dumps(
            {'count': count, 'message': text},
            # ASCII evita conflito cp1252/UTF-8 no redirecionamento do Agendador.
            ensure_ascii=True,
        )
    )
