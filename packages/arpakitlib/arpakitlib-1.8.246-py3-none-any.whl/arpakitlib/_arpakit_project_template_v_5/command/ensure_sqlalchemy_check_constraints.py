from arpakitlib.ensure_sqlalchemy_check_constraints import ensure_sqlalchemy_check_constraints
from project.core.setup_logging import setup_logging


def __command():
    setup_logging()
    ensure_sqlalchemy_check_constraints()


if __name__ == '__main__':
    __command()
