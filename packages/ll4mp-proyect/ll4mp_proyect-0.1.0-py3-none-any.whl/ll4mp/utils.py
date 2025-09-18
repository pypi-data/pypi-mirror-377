
from .courses import courses

def horas_totales():
    return sum(i.duracion for i in courses)

