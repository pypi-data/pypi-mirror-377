from dataclasses import dataclass
from Moon.python.Vectors import Vector2f
from Moon.python.Rendering.Shapes import *
from Moon.python.Rendering.Sprites import *
from Moon.python.Rendering.Vertexes import *
from Moon.python.Rendering.RenderStates import RenderStates, BlendMode
import random

import math

def CREATE_CIRCLE_TEXTURE(resolution: int = 100, approximation: int = 60) -> RenderTexture:
    texture = RenderTexture().create(resolution, resolution)
    texture.clear(COLOR_TRANSPARENT)
    circle = CircleShape(approximation)

    circle.set_position(resolution // 2, resolution // 2)
    circle.set_origin_radius(resolution // 2)
    circle.set_color(COLOR_WHITE)

    texture.draw(circle)
    texture.display()
    return texture

def CREATE_RECTANGLE_TEXTURE(resolution: int = 100) -> RenderTexture:
    texture = RenderTexture().create(resolution, resolution)
    texture.clear(COLOR_TRANSPARENT)
    rect = RectangleShape(resolution, resolution)
    rect.set_position(0, 0)
    rect.set_color(COLOR_WHITE)
    texture.draw(rect)
    texture.display()
    return texture

def CREATE_LIGHT_TEXTURE(resolution: int = 100, layers: int = 20, approximation: int = 30) -> RenderTexture:
    texture = RenderTexture().create(resolution, resolution)
    texture.clear(COLOR_TRANSPARENT)
    
    center = resolution / 2
    max_radius = center
    
    for i in range(layers):
        radius = max_radius * (layers - i) / layers
        brightness = int(255 * (layers - i) / layers)
        
        circle = CircleShape(approximation)
        circle.set_position(center, center)
        circle.set_origin_radius(radius)
        circle.set_color(Color(255 - brightness, 255 - brightness, 255 - brightness, 255))
        
        texture.draw(circle)
    
    texture.display()
    return texture

TEXTURE_CIRCLE = CREATE_CIRCLE_TEXTURE().get_texture()
TEXTURE_RECT = CREATE_RECTANGLE_TEXTURE(10).get_texture()
TEXTURE_LIGHT_CIRCLE = CREATE_LIGHT_TEXTURE(approximation=30, resolution=100, layers=20).get_texture()


class ParticleTextureAtlas:
    def __init__(self):
        self.__texture = RenderTexture().create(1, 1)
        self.__height = 0
        self.__width = 0
        self.__first_init = True

        self.__poses = {}
        
        

    def add_texture(self, texture: Texture, identifier: str | int):
        texture_size = texture.get_size().xy
        
        # Сохраняем старый атлас
        old_atlas = self.__texture.get_texture() if not self.__first_init else None
        
        self.__height = max(self.__height, texture_size[1])
        self.__width += texture_size[0]

        # Создаем новый атлас
        self.__texture = RenderTexture().create(self.__width, self.__height)
        self.__texture.clear(COLOR_TRANSPARENT)
        
        # Перерисовываем старый атлас на новый
        if old_atlas:
            old_sprite = BaseSprite.FromTexture(old_atlas)
            self.__texture.draw(old_sprite)
        
        # Добавляем новую текстуру
        sprite = BaseSprite.FromTexture(texture)
        sprite.set_position(self.__width - texture_size[0], 0)
        self.__texture.draw(sprite)
        self.__texture.display()
        
        self.__first_init = False
        self.__poses[identifier] = [self.__width - texture_size[0], 0, *texture_size]

    def get_poses(self):
        return self.__poses
    
    def get_render_texture(self) -> RenderTexture:
        print(self.__texture.get_size())
        return self.__texture
    
      
DEFAULT_TEXTURE_ATLAS = ParticleTextureAtlas()
DEFAULT_TEXTURE_ATLAS.add_texture(TEXTURE_CIRCLE, 'circle')
DEFAULT_TEXTURE_ATLAS.add_texture(TEXTURE_RECT, 'rect')
DEFAULT_TEXTURE_ATLAS.add_texture(TEXTURE_LIGHT_CIRCLE, 'light_circle')
        


@dataclass
class ParticleShapes:
    Circle = 0
    Rectangle = 1
    LightCircle = 2
    Sprite = 3

class CPU_Particle:
    def __init__(self, pos: Vector2f = Vector2f(0, 0), 
                      speed: Vector2f = Vector2f(0, 0), 
                      color: Color = COLOR_WHITE, 
                      size: float = 10,
                      resize: float = -1,
                      shape: ParticleShapes = ParticleShapes.Circle):
        self.position = pos
        self.speed = speed
        self.max_speed = 10
        self.min_speed = 5
        self.speed = speed
        self.spreading_angle = 0
        self.angular_distribution_area = 10

        self.resistance = 0.99
        
        # Параметры вращения
        self.rotation = 0.0
        self.rotation_speed = 0.0
        self.min_rotation_speed = -5.0
        self.max_rotation_speed = 5.0
        
        # Параметры размера
        self.min_size = size
        self.max_size = size
        
        # Параметры вращения вектора скорости
        self.velocity_rotation_speed = 0.0
        self.min_velocity_rotation_speed = 0.0
        self.max_velocity_rotation_speed = 0.0

        self.color = color
        self.size = size
        self.shape = shape
        self.resize = resize

        if self.shape == ParticleShapes.Circle:
            self.texture = TEXTURE_CIRCLE
        if self.shape == ParticleShapes.Rectangle:
            self.texture = TEXTURE_RECT
        if self.shape == ParticleShapes.LightCircle:
            self.texture = TEXTURE_LIGHT_CIRCLE

    def copy(self):
        np = CPU_Particle(Vector2f(self.position.x, self.position.y), 
                       Vector2f(self.speed.x, self.speed.y), 
                       self.color, self.size, self.resize, self.shape)
        np.max_speed = self.max_speed
        np.min_speed = self.min_speed
        np.spreading_angle = self.spreading_angle
        np.angular_distribution_area = self.angular_distribution_area
        np.texture = self.texture
        np.resistance = self.resistance
        np.rotation = self.rotation
        np.rotation_speed = self.rotation_speed
        np.min_rotation_speed = self.min_rotation_speed
        np.max_rotation_speed = self.max_rotation_speed
        np.min_size = self.min_size
        np.max_size = self.max_size
        np.velocity_rotation_speed = self.velocity_rotation_speed
        np.min_velocity_rotation_speed = self.min_velocity_rotation_speed
        np.max_velocity_rotation_speed = self.max_velocity_rotation_speed
        return np
        

class CPU_ParticleEmitters:
    class Point:
        def __init__(self, position: Vector2f):
            self.position = position

    class Rect:
        def __init__(self, position: Vector2f, width: float = 1, height: float = 1):
            self.position = position
            self.width = width
            self.height = height

    class Circle:
        def __init__(self, positiom: Vector2f, radius: float = 1):
            self.position = positiom
            self.radius = radius

class CPU_ParticleSystem:
    def __init__(self):
        self.particles: list[CPU_Particle] = []
        self.vertices = VertexArray().set_primitive_type(VertexArray.PrimitiveType.QUADS)

        self.atlas = DEFAULT_TEXTURE_ATLAS.get_render_texture().get_texture()
        self.render_states = RenderStates()
        self.render_states.set_texture(self.atlas)
        
        # Переменные для emit_per_time
        self.emission_timers = {}
        
        # Кэшируем координаты текстур
        poses = DEFAULT_TEXTURE_ATLAS.get_poses()
        self.circle_coords = poses['circle']
        self.rect_coords = poses['rect']
        self.light_coords = poses['light_circle']

        self.lightning = False
    
    def _construct_particle(self, particle: CPU_Particle, emitter: CPU_ParticleEmitters) -> CPU_Particle:
        p = particle.copy()
        if isinstance(emitter, CPU_ParticleEmitters.Point):
            p.position = Vector2f(emitter.position.x, emitter.position.y)
        if isinstance(emitter, CPU_ParticleEmitters.Rect):
            p.position = Vector2f(emitter.position.x + random.uniform(0, emitter.width), emitter.position.y + random.uniform(0, emitter.height))
        if isinstance(emitter, CPU_ParticleEmitters.Circle):
            p.position = emitter.position + Vector2f(0, random.uniform(0, emitter.radius)).rotate_at(random.uniform(0, 360))
            
        p.speed = Vector2f(0, random.uniform(p.min_speed, p.max_speed)).set_angle(p.spreading_angle + random.uniform(-p.angular_distribution_area / 2, p.angular_distribution_area / 2))
        p.rotation_speed = random.uniform(p.min_rotation_speed, p.max_rotation_speed)
        p.size = random.uniform(p.min_size, p.max_size)
        p.velocity_rotation_speed = random.uniform(p.min_velocity_rotation_speed, p.max_velocity_rotation_speed)
        return p

    def emit(self, particle: CPU_Particle, emitter: CPU_ParticleEmitters, count: int = 1):
        for _ in range(count):
            self.particles.append(self._construct_particle(particle, emitter))



    def update(self, render_time: float = 1):
        self.vertices.clear()
        alive_particles = []
        
        for p in self.particles:
            p.speed *= (p.resistance ** render_time)
            p.rotation += p.rotation_speed * render_time
            
            # Вращаем вектор скорости
            if p.velocity_rotation_speed != 0:
                current_angle = p.speed.get_angle()
                p.speed.set_angle(current_angle + p.velocity_rotation_speed * render_time)
            
            p.position += p.speed * render_time
            p.size += p.resize * render_time
            
            if p.size <= 0:
                continue
                
            alive_particles.append(p)
            
            x, y = p.position.x, p.position.y
            half = p.size * 0.5
            
            # Используем кэшированные координаты
            if p.shape == ParticleShapes.Circle:
                coords = self.circle_coords
            elif p.shape == ParticleShapes.LightCircle:
                coords = self.light_coords
            elif p.shape == ParticleShapes.Rectangle:
                coords = self.rect_coords
            
            # Вычисляем повернутые вершины
            
            cos_r = math.cos(math.radians(p.rotation))
            sin_r = math.sin(math.radians(p.rotation))
            
            # Координаты вершин относительно центра
            vertices_local = [(-half, -half), (half, -half), (half, half), (-half, half)]
            
            for i, (lx, ly) in enumerate(vertices_local):
                # Поворачиваем вершину
                rx = lx * cos_r - ly * sin_r
                ry = lx * sin_r + ly * cos_r
                
                # Переносим в мировые координаты
                world_x = x + rx
                world_y = y + ry
                
                # Координаты текстуры
                tex_coords = [
                    Vector2f(coords[0], coords[1]),
                    Vector2f(coords[0] + coords[2], coords[1]),
                    Vector2f(coords[0] + coords[2], coords[1] + coords[3]),
                    Vector2f(coords[0], coords[1] + coords[3])
                ]
                
                self.vertices.append(Vertex(Vector2f(world_x, world_y), p.color, tex_coords[i]))
        
        self.particles = alive_particles
    
    def render(self, window):
        self.render_states.set_blend_mode(BlendMode.Add())
        window.draw(self.vertices, self.render_states)

    def special_draw(self, window, attr = None):
        if isinstance(attr, RenderStates):
            attr.set_texture(self.atlas)
            window.draw(self.vertices, attr)
        else:
            if self.lightning:
                window.draw(self.vertices, self.render_states.set_blend_mode(BlendMode.Add()))
            else:
                window.draw(self.vertices, self.render_states)

    def get_ptr(self) -> Self:
        return self
    
    def emit_per_time(self, particle: CPU_Particle, emitter: CPU_ParticleEmitters, 
                      interval_seconds: float, count: int = 1, render_time: float = 1.0, 
                      emitter_id: str = "default"):
        if emitter_id not in self.emission_timers:
            self.emission_timers[emitter_id] = 0.0
        
        self.emission_timers[emitter_id] += render_time
        
        if self.emission_timers[emitter_id] >= interval_seconds:
            self.emit(particle, emitter, count)
            self.emission_timers[emitter_id] = 0.0