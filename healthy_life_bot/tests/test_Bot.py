import pytest
from Bot import signal_handler
import signal


def test_signal_handler(capsys):
    """Проверка корректной обработки сигнала завершения"""
    with pytest.raises(SystemExit) as e:
        signal_handler(signal.SIGINT, None)

    captured = capsys.readouterr()
    assert captured.out == '\nExit\n'
    assert e.value.code == 0