#!/usr/bin/env python3

class Course:
    def __init__(self, nombre, duracion, link):
        self.nombre = nombre 
        self.duracion = duracion
        self.link = link

    def __repr__(self):
        return f"[+] Nombre del curso: {self.nombre}, duracion [{self.duracion}], link del video -> {self.link}"

courses = [
    Course("Como ser un lammer", 5, "https://test.test"),
    Course("Esto es un nuevo camino", 10, "https://test.test"),
    Course("El esfuerzo es la unica clave", 40, "https://test.test"),
]

def listar():
    for i in courses:
        print(i)


def buscar_nombre(nombre):
    for i in courses:
        if i.nombre == nombre:
            return i
        return None

