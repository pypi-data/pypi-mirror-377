"""
Main script for analyzing memory profiler output files.
"""

import typer
from .analyzer import stats, dump_events, type_stats

def main():
    app = typer.Typer(help="Analyze memory profiler output")

    app.command("stats")(stats)
    app.command("type_stats")(type_stats)
    app.command("dump_events")(dump_events)

    app()

if __name__ == "__main__":
    main()
