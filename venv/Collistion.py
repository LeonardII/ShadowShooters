import pygame
import math
def intersects_circle(ray_dir, ray_pos, circle_pos, radius):
    print(ray_dir, ray_pos, circle_pos, radius)
    '''
    :param ray_dir: pygame.math.Vector2
    :param ray_pos: pygame.math.Vector2
    :param circle_pos: pygame.math.Vector2
    :param radius: float
    :return:
    '''
    f = ray_pos - circle_pos
    a = ray_dir.dot(ray_dir)
    b = 2 * f.dot(ray_dir)
    c = f.dot(f) - radius*radius

    discriminant = b * b - 4 * a * c
    if discriminant < 0:
        return False

    discriminant = math.sqrt(discriminant)

    t1 = (-b - discriminant) / (2 * a)

    t2 = (-b + discriminant) / (2 * a)
    if t1<0 and t2<0:
        return False

    return True