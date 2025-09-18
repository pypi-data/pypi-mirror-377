# HACK4IO Academy Courses Library 

Una biblioteca Python para consulrar cursos de la academia Hack4U.

## Cursos disponibles:
-Introduccion a linux [15 horas]
-Personalizacion de linux [3 horas]
-Introduccion al Hacking [53 horas]

## Instalacion

Instala el paquete usando `pip3`:

```python3
pip3 install hack4u_bichos
```


## Uso basico

### Listar todos los cursos

```python
from hack4u import list_courses

for course in list_courses():
    print(course)
```

### Obtener un curso por nombre

```python
from hack4u import get_course_by_name

course = get_course_by_name("Introduccion a Linux")
print(course)
```

### Calcular duracion total de los cursos

```python
from hack4u import total_duration

print(f"Duracion total: {total_dutation()} horas")
```
