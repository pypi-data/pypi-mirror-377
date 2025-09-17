pi=3.14159265359

def area_of_cube(side: float) -> float:
    return 6 * (side * side)
def area_of_cuboid(length: float, breadth: float, height: float) -> float:
    return 2 * (length * breadth + breadth * height + height * length)
def area_of_cylinder(radius: float, height: float) -> float:
    return 2 * pi * radius * (radius + height)

def area_of_cone(radius: float, slant_height: float) -> float:
    return pi * radius * (radius + slant_height)

def area_of_sphere(radius: float) -> float:
    return 4 * pi * radius * radius
