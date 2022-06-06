import pygame_gui as pg_gui

import objects
from consts import *
from graph import Graph

pg.init()


def _fix_pos(v: pg.Vector2) -> pg.Vector2:
    return v - pg.Vector2(1, 1) * (CELL_SIZE // 2)


def mex(a: list):
    if not a:
        return 1
    a.sort()
    if a[0] > 1:
        return 1
    if len(a) == 1:
        return a[0] + 1
    for i in range(len(a) - 1):
        if a[i] + 1 != a[i + 1]:
            return a[i] + 1
    return a[-1] + 1


class Game:
    ADD_NODE_MOD = 1
    ADD_EDGE_MOD = 2
    ADD_DIRECTED_EDGE_MOD = 3
    REMOVE_MOD = 4

    MODES = {ADD_NODE_MOD: "Добавить вершину", ADD_EDGE_MOD: "Добавить дугу", REMOVE_MOD: "Удалить"}

    def __init__(self):
        self.edges_group = None
        self.nodes_group = None
        self.current_node_number = None
        self.objects_group = None
        self.running = False
        self.selected_nodes = []
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption("Discrete Math")
        self.clock = pg.time.Clock()
        self.mode = self.ADD_NODE_MOD
        self.checking_result = False
        self.result_edges = None
        self.states = []
        self.current_state = 0
        self.message = ""
        self.message_time = ""
        self.algorithm = "Эйлеров путь(цикл)"
        self.ui_manager = pg_gui.UIManager((WIDTH, HEIGHT), theme_path="theme.json")
        self.directed = False

        self.load_settings()

    def load_settings(self):
        self.running = False
        self.objects_group = pg.sprite.Group()
        self.nodes_group = pg.sprite.Group()
        self.edges_group = pg.sprite.Group()
        self.current_node_number = 1

        self.load_objects()

    def load_objects(self):
        self._load_gui()

    def _load_gui(self):
        y = 30
        self.add_node_button = pg_gui.elements.UIButton(relative_rect=pg.Rect((WIDTH - 220, y), (200, 25)),
                                                        text="Вершина",
                                                        manager=self.ui_manager)
        self.edge_type_drop_down = pg_gui.elements.UIDropDownMenu(options_list=["Неориентированный",
                                                                                "Ориентированный"],
                                                                  starting_option="Неориентированный",
                                                                  relative_rect=pg.Rect((WIDTH - 220, y + 30),
                                                                                        (200, 25)),
                                                                  manager=self.ui_manager,
                                                                  object_id=pg_gui.core.ObjectID(
                                                                      object_id="#alg_drop_down",
                                                                      class_id="@drop_down"))
        self.add_edge_button = pg_gui.elements.UIButton(relative_rect=pg.Rect((WIDTH - 220, y + 60), (200, 25)),
                                                        text="Дуга",
                                                        manager=self.ui_manager)
        self.remove_button = pg_gui.elements.UIButton(relative_rect=pg.Rect((WIDTH - 220, y + 90), (200, 25)),
                                                      text="Удалить",
                                                      manager=self.ui_manager)
        self.clear_button = pg_gui.elements.UIButton(relative_rect=pg.Rect((WIDTH - 220, y + 120), (200, 25)),
                                                     text="Очистить",
                                                     manager=self.ui_manager)
        self.algorithm_dropdown_menu = pg_gui.elements.UIDropDownMenu(
            options_list=["Эйлеров путь(цикл)", "Гамильтонов цикл",
                          "Гамильтонов путь"],
            starting_option="Эйлеров путь(цикл)",
            relative_rect=pg.Rect((WIDTH - 220, y + 180),
                                  (200, 25)),
            manager=self.ui_manager,
            object_id=pg_gui.core.ObjectID(
                object_id="#alg_drop_down",
                class_id="@drop_down"))
        self.run_algorithm_button = pg_gui.elements.UIButton(relative_rect=pg.Rect((WIDTH - 220, y + 210), (200, 25)),
                                                             text="Запустить алгоритм",
                                                             manager=self.ui_manager)
        self.state_scroll = pg_gui.elements.UIHorizontalSlider(relative_rect=pg.Rect((WIDTH - 220, 270), (200, 25)),
                                                               start_value=0, value_range=(0, 0), visible=False,
                                                               manager=self.ui_manager)

    def check_events(self):
        for event in pg.event.get():
            if event.type == pg_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.add_node_button:
                    self.set_mode(self.ADD_NODE_MOD)
                elif event.ui_element == self.add_edge_button:
                    self.set_mode(self.ADD_EDGE_MOD)
                elif event.ui_element == self.remove_button:
                    self.set_mode(self.REMOVE_MOD)
                elif event.ui_element == self.clear_button:
                    self.clear()
                elif event.ui_element == self.run_algorithm_button:
                    self.run_algorithm()

            if event.type == pg_gui.UI_DROP_DOWN_MENU_CHANGED:
                if event.ui_element == self.algorithm_dropdown_menu:
                    self.algorithm = event.text
                elif event.ui_element == self.edge_type_drop_down:
                    if event.text == "Неориентированный":
                        self.directed = False
                    else:
                        self.directed = True
                    self._default_state()
                    self._destroy_all_edges()

            if event.type == pg.QUIT:
                self.running = False
            elif event.type == pg.MOUSEBUTTONUP:
                x, y = pg.mouse.get_pos()
                if x < WIDTH - 220:  # чтобы нельзя было поставить вершину рядом с кнопками
                    if event.button == LMB:
                        v = pg.Vector2(x, y)
                        if self.mode == self.ADD_NODE_MOD:
                            colliders = list(
                                filter(lambda obj: obj.rect.collidepoint(pg.mouse.get_pos()), self.nodes_group))
                            if not colliders:
                                self.current_node_number = mex([int(node.number) for node in self.nodes_group])
                                node = objects.Node(*v, self.current_node_number)
                                self.add_node(node)
                                self.selected_nodes.clear()
                        elif self.mode == self.ADD_EDGE_MOD or self.mode == self.ADD_DIRECTED_EDGE_MOD:
                            colliders = list(
                                filter(lambda obj: obj.rect.collidepoint(pg.mouse.get_pos()), self.nodes_group))
                            if colliders:
                                node = colliders[0]
                                self.select_node(node)
                        elif self.mode == self.REMOVE_MOD:
                            colliders = list(
                                filter(lambda obj: obj.rect.collidepoint(pg.mouse.get_pos()), self.objects_group))
                            for collider in colliders:
                                collider.destroy()

            elif event.type == pg.KEYUP:
                if event.key == pg.K_1:
                    self.set_mode(self.ADD_NODE_MOD)
                elif event.key == pg.K_2:
                    self.set_mode(self.ADD_EDGE_MOD)
                elif event.key == pg.K_3:
                    self.set_mode(self.REMOVE_MOD)
                elif event.key == pg.K_RETURN:
                    self.run_algorithm()
                elif event.key == pg.K_ESCAPE:
                    self._default_state()
                elif event.key == pg.K_RIGHT and self.checking_result:
                    if self.states:
                        if self.current_state + 1 < len(self.states):
                            self.current_state += 1
                            self.state_scroll.set_current_value(self.current_state)
                elif event.key == pg.K_LEFT and self.checking_result:
                    if self.states:
                        if self.current_state - 1 >= 0:
                            self.current_state -= 1
                            self.state_scroll.set_current_value(self.current_state)

            self.ui_manager.process_events(event)

    def clear(self):
        self._default_state()
        for obj in self.objects_group:
            obj.destroy()

    def _default_state(self):
        self.state_scroll.hide()
        for node in self.selected_nodes:
            node.unselect()
        self.selected_nodes.clear()
        for edge in self.edges_group:
            edge.default()
        self.checking_result = False
        self.states = []
        self.current_state = 0
        self.message = ""
        self.message_time = ""

    def set_state(self, state: dict):
        yellow_nodes = state["yellow_nodes"]
        red_nodes = state["red_nodes"]
        red_edges = state["red_edges"]
        green_nodes = state["green_nodes"]
        green_edges = state["green_edges"]
        for node in self.nodes_group:
            if node.number in yellow_nodes:
                node.color = pg.Color("#FFFF80")
            if node.number in red_nodes:
                node.color = pg.Color("#FF3812")
            if node.number in green_nodes:
                node.color = pg.Color("#8FFEAB")
        for edge in self.edges_group:
            if (edge.node1.number, edge.node2.number) in red_edges \
                    or (edge.node2.number, edge.node1.number) in red_edges:
                edge.color = pg.Color("#FF3812")
            if (edge.node1.number, edge.node2.number) in green_edges \
                    or (edge.node2.number, edge.node1.number) in green_edges:
                edge.color = pg.Color("#008D00")

        edges = set(self.edges_group)
        for i in range(len(green_nodes) - 1):
            for edge in self.edges_group:
                if edge.node1.number == green_nodes[i] and edge.node2.number == green_nodes[i + 1]:
                    edge.set_direction(edge.node1, edge.node2)
                    edges.remove(edge)
                elif edge.node2.number == green_nodes[i] and edge.node1.number == green_nodes[i + 1]:
                    edge.set_direction(edge.node2, edge.node1)
                    edges.remove(edge)
        if green_nodes:
            for edge in edges:
                edge.current_directed = False

    def run_algorithm(self):
        import time
        self._default_state()
        graph = Graph(self.directed)
        for edge in self.edges_group:
            graph.add_edge(edge.node1.number, edge.node2.number, edge.directed)
        states = []
        start_time = time.time()
        if self.algorithm == "Эйлеров путь(цикл)":
            if graph.check_euler_path():
                states = graph.find_euler_path()
            else:
                self.message = f"{self.algorithm} не существует"
                return
        elif self.algorithm == "Гамильтонов цикл":
            states = graph.hamilton_cycle()
            if not states[-1]["green_nodes"]:
                self.message = f"{self.algorithm} не существует"
                return
        elif self.algorithm == "Гамильтонов путь":
            states = graph.hamilton_path()
            if not states[-1]["green_nodes"]:
                self.message = f"{self.algorithm} не существует"
                return
        result_time = time.time() - start_time
        self.checking_result = True
        self.states = states
        self.set_state(self.states[0])
        self.message = f"{self.algorithm}: " + " ".join(states[-1]["green_nodes"])
        self.message_time = f"Время работы: {round(result_time * 1000, 3)} мс"
        self._set_up_state_scroll()

    def _set_up_state_scroll(self):
        self.state_scroll.kill()
        self.state_scroll = pg_gui.elements.UIHorizontalSlider(relative_rect=pg.Rect((WIDTH - 220, 270), (200, 25)),
                                                               start_value=0, value_range=(0, len(self.states) - 1),
                                                               manager=self.ui_manager,
                                                               object_id=pg_gui.core.ObjectID(class_id="@scroll",
                                                                                              object_id="#state_scroll"))

    def set_mode(self, mode):
        self.mode = mode

    def add_node(self, node):
        self._default_state()
        self.objects_group.add(node)
        self.nodes_group.add(node)

    def select_node(self, node):
        node.select()
        self.selected_nodes.append(node)

    def _check_collisions(self):
        for i, object1 in enumerate(list(self.objects_group)[:-1]):
            for object2 in list(self.objects_group)[i + 1:]:
                if object1.rect.colliderect(object2.rect):
                    object1.collision(object2)
                    object2.collision(object1)

    def _update_objects(self):

        self._check_collisions()

        if self.checking_result:
            self.set_state(self.states[self.state_scroll.current_value])
            self.current_state = self.state_scroll.current_value

        for obj in self.objects_group:
            obj.update()

        if len(self.selected_nodes) == 2:  # набралось 2 выбранные вершины
            node1, node2 = self.selected_nodes
            node1.unselect()
            node2.unselect()
            self.selected_nodes = []

            if node1 != node2:
                self.add_edge(node1, node2, self.directed)

    def _default_objects(self):
        for obj in self.objects_group:
            obj.default()

    def _destroy_all_edges(self):
        for edge in self.edges_group:
            edge.destroy()

    def add_edge(self, node1: objects.Node, node2: objects.Node, directed: bool):
        if not node1.has_neighbour(node2):
            self._default_state()
            edge = objects.Edge(node1, node2, directed)
            node1.add_neighbour(node2, edge)
            can_go = True
            if directed:
                can_go = False
            node2.add_neighbour(node1, edge, can_go)
            self.objects_group.add(edge)
            self.edges_group.add(edge)

    def _render_objects(self):
        self.objects_group.draw(self.screen)
        self.ui_manager.draw_ui(self.screen)
        self._print_mode()
        self._print_message()

    def _print_mode(self):
        font = pg.font.SysFont("arial", 12)
        color = pg.Color("#44455B")
        text_mode = font.render(f"Режим: {self.MODES[self.mode]}", True, color)
        self.screen.blit(text_mode, (WIDTH - 220, 10))

    def _print_message(self):
        font = pg.font.SysFont("arial", 12)
        color = pg.Color("#44455B")
        text_message = font.render(self.message, True, color)
        text_time = font.render(self.message_time, True, color)
        self.screen.blit(text_message, (WIDTH - 220, 300))
        self.screen.blit(text_time, (WIDTH - 220, 320))

    def run(self):
        self.running = True
        while self.running:
            time_delta = self.clock.tick(FPS) / 1000

            self._default_objects()

            self.check_events()

            self._update_objects()

            self.screen.fill(SCREEN_COLOR)

            self.ui_manager.update(time_delta)

            self._render_objects()

            pg.display.flip()

        pg.quit()


if __name__ == '__main__':
    game = Game()
    game.run()
