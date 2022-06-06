import math

from consts import *


def distance(v1, v2):
    v = v2 - v1
    return math.sqrt(v.dot(v))


class Basic(pg.sprite.Sprite):
    WIDTH, HEIGHT = 64, 64
    COLOR = (0, 0, 0)

    def __init__(self, x, y):
        pg.sprite.Sprite.__init__(self)

        self.image = self._render_image()

        self.rect = self.image.get_rect(center=(x, y))
        self.rect.x, self.rect.y = x - self.WIDTH // 2, y - self.HEIGHT // 2
        self.pos = pg.math.Vector2(self.rect.x, self.rect.y)

        self._load_settings()

    def _render_image(self) -> pg.Surface:
        return self._get_image()

    def _get_image(self):
        return pg.Surface([self.WIDTH, self.HEIGHT], pg.SRCALPHA)

    def _load_settings(self):
        pass

    def collision(self, obj):
        pass

    def destroy(self):
        self.kill()


class Node(Basic):
    WIDTH, HEIGHT = 64, 64
    MAIN_COLOR = pg.Color("#FFFFFF")
    BORDER_COLOR = pg.Color("#D9D7D7")
    SELECTED_COLOR = pg.Color("#F0F0F0")
    RADIUS = WIDTH // 2 - 2

    def __init__(self, x, y, number):
        self.number = str(number)

        self.neighbours = set()
        self.edges = dict()
        self.color = self.MAIN_COLOR
        self.selected = False
        super().__init__(x, y)

    def default(self):
        if not self.selected:
            self.color = self.MAIN_COLOR

    def _render_image(self) -> pg.Surface:
        image = self._get_image()
        center = self.WIDTH // 2
        pg.draw.circle(image, self.BORDER_COLOR, (center, center), self.RADIUS)
        pg.draw.circle(image, self.color, (center, center), (self.WIDTH - 10) // 2)
        return image

    def select(self):
        self.color = self.SELECTED_COLOR
        self.selected = True
        # self.selecting_color = self.SELECTED_COLOR

    def unselect(self):
        self.color = self.MAIN_COLOR
        self.selected = False
        # self.selecting_color = self.BORDER_COLOR

    def add_neighbour(self, node, edge, can_go=True):
        self.neighbours.add(node)
        self.edges[node] = (edge, can_go)

    def has_neighbour(self, node) -> bool:
        return node in self.neighbours

    def remove_neighbour(self, node):
        if node in self.neighbours:
            self.neighbours.remove(node)
            self.edges.pop(node)

    def update(self):
        self.image = self._render_image()
        font_optima = pg.font.SysFont("arial", 36)
        color = pg.Color("#658EA9")
        text_number = font_optima.render(self.number, True, color)
        self.image.blit(text_number, (18, 14))

    def destroy(self):
        for neighbour in self.neighbours.copy():
            self.edges[neighbour][0].destroy()
        self.neighbours.clear()
        self.kill()


class Edge(Basic):
    WIDTH = WIDTH
    HEIGHT = HEIGHT
    COLOR = pg.Color("#4E4F50")

    def __init__(self, node1: Node, node2: Node, directed=False):
        self.node1 = node1
        self.node2 = node2
        self.directed = directed
        self.color = self.COLOR

        self.current_node1 = node1
        self.current_node2 = node2
        self.current_directed = directed

        pg.sprite.Sprite.__init__(self)

        self.image = pg.Surface([self.WIDTH, self.HEIGHT], pg.SRCALPHA)

        self._draw_arrow(node1, node2, directed)

    def update(self):
        self.image = pg.Surface([self.WIDTH, self.HEIGHT], pg.SRCALPHA)
        self._draw_arrow(self.current_node1, self.current_node2, self.current_directed)

    def default(self):
        self.color = self.COLOR
        self.current_node1 = self.node1
        self.current_node2 = self.node2
        self.current_directed = self.directed

    def set_direction(self, start: Node, end: Node):
        self.current_node1 = start
        self.current_node2 = end
        self.current_directed = True

    def _draw_arrow(self, start: Node, end: Node, directed=False):
        if directed:
            triangle_rad = 5
        else:
            triangle_rad = 0
        start_v, end_v = start.pos + pg.Vector2(1, 1) * start.RADIUS, end.pos + pg.Vector2(1, 1) * end.RADIUS
        r = start.RADIUS
        v = end_v - start_v
        v = v.normalize()
        start = start_v + v * start.RADIUS
        end = end_v - v * end.RADIUS
        rect_line = pg.draw.line(self.image, self.color, start, end, 3)
        rotation = math.degrees(math.atan2(start.y - end.y, end.x - start.x)) + 90
        rect_polygon = pg.draw.polygon(self.image, self.color, (
            (end.x + triangle_rad * math.sin(math.radians(rotation)),
             end.y + triangle_rad * math.cos(math.radians(rotation))), (
                end.x + triangle_rad * math.sin(math.radians(rotation - 120)),
                end.y + triangle_rad * math.cos(math.radians(rotation - 120))), (
                end.x + triangle_rad * math.sin(math.radians(rotation + 120)),
                end.y + triangle_rad * math.cos(math.radians(rotation + 120)))))
        rect = rect_line.union(rect_polygon)
        self.image = self.image.subsurface(rect)
        self.rect = rect

    def destroy(self):
        self.node1.remove_neighbour(self.node2)
        self.node2.remove_neighbour(self.node1)
        self.kill()
