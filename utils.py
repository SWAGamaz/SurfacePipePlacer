from math import pi, cos, sin
from mathutils import Vector

def find_best_points(p1, p2, outer_radius, global_vertices):
    # Вычислите направление от P1 к P2
    direction = (p2 - p1).normalized()

    # Получите перпендикулярное направление к направлению P1-P2 (в плоскости XY)
    perpendicular = Vector((-direction.y, direction.x, 0))

    # Вычислите приближенное идеальное местоположение для P3
    ideal_position = (p1 + p2) / 2 + perpendicular * ((p2 - p1).length * (3 ** 0.5 / 2))

    # Ищем наиболее подходящие вершины для каждой из позиций
    suitable_vertices = [v for v in global_vertices if not any(is_intersecting(v[0], pos, outer_radius) for pos in [p1, p2])]

    if not suitable_vertices:
        return None

    # Находим вершину, наиболее близкую к идеальной позиции
    best_vert = min(suitable_vertices, key=lambda v: (v[0] - ideal_position).length)

    # Идеальное местоположение для четвёртой точки (противоположная сторона от третьей точки)
    fourth_ideal_position = (p1 + p2) / 2 - perpendicular * ((p2 - p1).length * (3 ** 0.5 / 2))
    
    suitable_vertices_for_fourth = [v for v in global_vertices if not any(is_intersecting(v[0], pos, outer_radius) for pos in [p1, p2, best_vert[0]])]
    
    if not suitable_vertices_for_fourth:
        return best_vert[0], None
    
    best_vert_for_fourth = min(suitable_vertices_for_fourth, key=lambda v: (v[0] - fourth_ideal_position).length)
    
    return best_vert[0], best_vert_for_fourth[0]


def is_intersecting(pipe_position, new_position, outer_radius):
    """Проверка пересечения новой трубки с уже размещенной."""
    distance = (pipe_position - new_position).length
    return distance < outer_radius * 2


def find_potential_position(previous_positions, global_vertices, outer_radius):
    """Находит потенциальную позицию для новой трубки."""
    ideal_distance = outer_radius * 2
    tolerance = 0.01

    best_vert = None
    best_distance_diff = float('inf')
    for vert, normal in global_vertices:
        suitable = all([(vert - pos).length > ideal_distance - tolerance and
                        (vert - pos).length < ideal_distance + tolerance for pos in previous_positions])
        if not suitable:
            continue
        distance_diff = abs((vert - previous_positions[-1]).length - ideal_distance)
        if distance_diff < best_distance_diff:
            best_vert = vert
            best_distance_diff = distance_diff

    return best_vert
