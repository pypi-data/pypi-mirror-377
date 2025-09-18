#!/usr/bin/env python
"""
PolyPrime CLI - Command-line interface
"""

import click
import sys
from pathlib import Path
from typing import Optional

from . import __version__
from .compiler import Compiler
from .runtime import Runtime

@click.group()
@click.version_option(version=__version__, prog_name="PolyPrime")
def main():
    """PolyPrime - The Multi-Paradigm Programming Language"""
    pass

@main.command()
@click.argument('source_file', type=click.Path(exists=True))
@click.option('--target', '-t', default='python', type=click.Choice(['python', 'javascript']))
@click.option('--output', '-o', type=click.Path())
def compile(source_file: str, target: str, output: Optional[str]):
    """Compile a PolyPrime source file"""
    try:
        # Read source
        with open(source_file, 'r') as f:
            source = f.read()

        # Compile
        compiler = Compiler()
        result = compiler.compile(source, target)

        # Determine output file
        if not output:
            source_path = Path(source_file)
            ext = '.py' if target == 'python' else '.js'
            output = str(source_path.with_suffix(ext))

        # Write output
        with open(output, 'w') as f:
            f.write(result)

        click.echo(f"Successfully compiled to {output}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

@main.command()
@click.argument('source_file', type=click.Path(exists=True))
def run(source_file: str):
    """Run a PolyPrime program"""
    try:
        # Read source
        with open(source_file, 'r') as f:
            source = f.read()

        # Execute
        runtime = Runtime()
        result = runtime.execute_source(source)

        if result:
            click.echo(f"Result: {result}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

@main.command()
@click.argument('project_name')
def init(project_name: str):
    """Initialize a new PolyPrime project"""
    try:
        project_dir = Path(project_name)
        project_dir.mkdir(exist_ok=True)

        # Create src directory
        src_dir = project_dir / 'src'
        src_dir.mkdir(exist_ok=True)

        # Create main.pp
        main_file = src_dir / 'main.pp'
        main_content = '''// Main PolyPrime program

function main() {
    let message = "Hello from PolyPrime!";
    print(message);
    return 0;
}
'''
        main_file.write_text(main_content)

        # Create README
        readme = project_dir / 'README.md'
        readme_content = f'''# {project_name}

A PolyPrime project.

## Build

```bash
polyprime compile src/main.pp --target python
```

## Run

```bash
polyprime run src/main.pp
```
'''
        readme.write_text(readme_content)

        click.echo(f"Created PolyPrime project: {project_name}")
        click.echo(f"  - {src_dir / 'main.pp'}")
        click.echo(f"  - {readme}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

@main.command()
def info():
    """Show information about PolyPrime"""
    click.echo("PolyPrime - The Multi-Paradigm Programming Language")
    click.echo(f"Version: {__version__}")
    click.echo("Author: Michael Benjamin Crowe")
    click.echo()
    click.echo("Features:")
    click.echo("  - Compile to Python")
    click.echo("  - Compile to JavaScript")
    click.echo("  - Simple, clean syntax")
    click.echo("  - Fast compilation")
    click.echo()
    click.echo("Usage:")
    click.echo("  polyprime compile <file> --target <language>")
    click.echo("  polyprime run <file>")
    click.echo("  polyprime init <project>")

if __name__ == '__main__':
    main()