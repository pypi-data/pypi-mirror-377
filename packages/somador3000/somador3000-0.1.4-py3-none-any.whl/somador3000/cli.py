import click
from .functions import soma_3_mil


@click.command()
@click.argument('numero', type=float)
def main(numero):
    """Calcula o número passado mais 3000"""
    resultado = soma_3_mil(numero)
    click.echo(f"O resultado de {numero} + 3000 é: {resultado}")


if __name__ == '__main__':
    main()
