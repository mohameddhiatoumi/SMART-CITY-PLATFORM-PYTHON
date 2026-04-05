"""
Smart City Analytics Platform - Neo-Sousse 2030
Main entry point for CLI interface
"""
import sys
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


@click.group()
def cli():
    """Smart City Analytics Platform - Neo-Sousse 2030 CLI."""
    pass


@cli.command("init-db")
def init_db():
    """Initialize the database schema."""
    try:
        from database.init_db import main as db_main
        db_main()
    except Exception as e:
        console.print(f"[red]Error initializing database: {e}[/red]")
        console.print("[yellow]Make sure PostgreSQL is running and .env is configured.[/yellow]")
        sys.exit(1)


@cli.command("seed-data")
def seed_data():
    """Seed sample data into the database."""
    try:
        from database.seed_data import main as seed_main
        seed_main()
    except Exception as e:
        console.print(f"[red]Error seeding data: {e}[/red]")
        console.print("[yellow]Make sure the database is initialized first.[/yellow]")
        sys.exit(1)


@cli.command("compile-query")
@click.argument("query")
def compile_query(query: str):
    """Compile a natural language query to SQL.
    
    Example: smart-city compile-query "Show the 5 most polluted zones"
    """
    from compiler.query_builder import QueryBuilder

    builder = QueryBuilder()
    result = builder.build(query)

    if result["success"]:
        console.print(Panel(
            f"[bold green]Generated SQL:[/bold green]\n\n[cyan]{result['sql']}[/cyan]",
            title="Query Compilation Result",
            border_style="green",
        ))

        if result.get("tokens"):
            table = Table(title="Tokens")
            table.add_column("Type", style="magenta")
            table.add_column("Value", style="cyan")
            table.add_column("Position", style="yellow")
            for token in result["tokens"]:
                table.add_row(
                    str(token.get("type", "")),
                    str(token.get("value", "")),
                    str(token.get("position", "")),
                )
            console.print(table)
    else:
        console.print(f"[red]Compilation failed: {result.get('error', 'Unknown error')}[/red]")


@cli.command("demo")
def run_demo():
    """Run a demo showing all platform components."""
    console.print(Panel(
        "[bold cyan]Smart City Analytics Platform - Neo-Sousse 2030[/bold cyan]\n"
        "Demo Mode",
        border_style="blue",
    ))

    # Demo 1: Compiler
    console.print("\n[bold yellow]== Compiler Demo ==[/bold yellow]")
    from compiler.query_builder import QueryBuilder

    builder = QueryBuilder()
    demo_queries = [
        "Show the 5 most polluted zones",
        "Which citizens have an ecological score greater than 80",
        "List all active sensors",
        "How many interventions are AI validated",
        "Count sensors by type",
    ]
    table = Table(title="NL → SQL Compiler")
    table.add_column("Natural Language Query", style="cyan", width=45)
    table.add_column("Generated SQL", style="green")
    for q in demo_queries:
        result = builder.build(q)
        sql = result["sql"] if result["success"] else f"ERROR: {result.get('error', '')}"
        table.add_row(q, sql)
    console.print(table)

    # Demo 2: Automata
    console.print("\n[bold yellow]== Automata Demo ==[/bold yellow]")
    from automata.sensor_dfa import SensorDFA
    from automata.intervention_dfa import InterventionDFA
    from automata.vehicle_dfa import VehicleDFA

    sensor = SensorDFA(sensor_id=1)
    console.print(f"Sensor DFA initial state: [cyan]{sensor.get_current_state()}[/cyan]")
    sensor.process_event("activate")
    console.print(f"After 'activate': [green]{sensor.get_current_state()}[/green]")
    sensor.process_event("signal_fault")
    console.print(f"After 'signal_fault': [yellow]{sensor.get_current_state()}[/yellow]")

    intervention = InterventionDFA(intervention_id=1)
    console.print(f"\nIntervention DFA initial state: [cyan]{intervention.get_current_state()}[/cyan]")
    intervention.process_event("assign_tech1")
    console.print(f"After 'assign_tech1': [green]{intervention.get_current_state()}[/green]")

    vehicle = VehicleDFA(vehicle_id=1)
    console.print(f"\nVehicle DFA initial state: [cyan]{vehicle.get_current_state()}[/cyan]")
    vehicle.process_event("depart")
    console.print(f"After 'depart': [green]{vehicle.get_current_state()}[/green]")

    # Demo 3: AI Reports
    console.print("\n[bold yellow]== AI Report Demo (template-based fallback) ==[/bold yellow]")
    from ai.report_generator import ReportGenerator

    gen = ReportGenerator(use_openai=False)
    report = gen.generate_city_dashboard_report({
        "active_sensors": 42,
        "interventions_pending": 7,
        "avg_pollution": 35.2,
        "citizens": 30,
    })
    console.print(Panel(report[:500] + "...", title="City Health Report", border_style="cyan"))

    console.print("\n[bold green]✓ Demo complete! Run 'streamlit run dashboard/app.py' to launch the dashboard.[/bold green]")


@cli.command("dashboard")
def launch_dashboard():
    """Launch the Streamlit dashboard."""
    import subprocess
    console.print("[cyan]Launching Smart City Dashboard...[/cyan]")
    subprocess.run(["streamlit", "run", "dashboard/app.py"], check=True)


if __name__ == "__main__":
    cli()
