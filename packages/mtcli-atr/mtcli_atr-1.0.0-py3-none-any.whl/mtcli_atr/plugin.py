"""Comando para calcular o indicador ATR."""

import click
import MetaTrader5 as mt5
from . import conf
from .atr import calcular_atr
from mtcli.conecta import conectar, shutdown
from mtcli.logger import setup_logger

log = setup_logger()


@click.command()
@click.version_option(package_name="mtcli-atr")
@click.option("--symbol", "-s", default="IBOV", help="Símbolo do ativo (default IBOV).")
@click.option(
    "--periodo", "-po", type=int, default=14, help="Período do ATR (default 14)."
)
@click.option("--timeframe", "-t", default="D1", help="Timeframe (ex: M1, H1, D1).")
def atr(symbol, periodo, timeframe):
    """Exibe o indicador ATR (Average True Range)"""
    conectar()

    tf = getattr(mt5, f"TIMEFRAME_{timeframe.upper()}", None)
    if tf is None:
        msg = f"Timeframe inválido: {timeframe}"
        click.echo(msg)
        log.error(msg)
        shutdown()
        return

    if not mt5.symbol_select(symbol, True):
        msg = f"Erro ao selecionar símbolo {symbol}"
        click.echo(msg)
        log.error(msg)
        shutdown()
        return

    rates = mt5.copy_rates_from_pos(symbol, tf, 0, periodo + 1)
    if rates is None or len(rates) < periodo + 1:
        msg = "Dados insuficientes para cálculo do ATR"
        click.echo(msg)
        log.warning(msg)
        shutdown()
        return

    atr_value = calcular_atr(rates, periodo)
    click.echo(
        f"ATR({periodo}) de {symbol} no timeframe {timeframe.upper()}: {atr_value:.{conf.digitos}f}"
    )
    shutdown()
