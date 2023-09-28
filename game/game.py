from typing import Optional

import pygame

from game.utils.game_status_handler import GameStatusHandler
from game.utils.fen import FenConverter
from models.figure import Figure
from game.board import Board


class Game:
    """
    Contains all information about the game. Keeps the game running.
    """

    def __init__(self):
        pygame.init()
        self.FPS = 40
        self.clock = pygame.time.Clock()

        self.selected_figure: Optional[Figure] = None
        self.keep_doing = True

        self.board = Board(self)

        self.turn = 1
        # self.figures = FenConverter.fen_converter(self, "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")
        self.figures = FenConverter.fen_converter(self, "8/8/7k/8/8/8/1K1R4/6R1")

    def run(self):
        """Starts and runs the game."""
        while self.keep_doing:
            self.clock.tick(self.FPS)
            self.draw()
            self.process_events()
            self.handle_game_status()

        pygame.quit()

    def draw(self):
        """Draws all objects and images in the game."""
        self.board.draw()

    def process_events(self):
        """Processes all possible user interactions (events) during the game."""
        for event in pygame.event.get():
            self.process_exit_event(event)
            self.process_mouse_button_down_event(event)

    def process_exit_event(self, event):
        """
        Process an event in case user closes the application.
        :param event: pygame event
        """
        if event.type == pygame.QUIT:
            self.keep_doing = False

    def process_mouse_button_down_event(self, event):
        """
        Processes all possible events in case the user presses the left mouse button. It can either be figure selection,
        figure deselection or moving the figure.
        :param event: pygame event
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = self.board.convert_mouse_coordinates_to_board_coordinates(pygame.mouse.get_pos())
            self.figure_selection_events(mouse_x, mouse_y)
            if self.selected_figure is not None:
                self.selected_figure.move(mouse_x, mouse_y)

    def figure_selection_events(self, mouse_x, mouse_y):
        """
        By the given coordinates of the mouse during a click checks if the user was selecting or deselecting the figure
        and does necessary operations respectively.
        :param mouse_x: x coordinate of the mouse
        :param mouse_y: y coordinate of the mouse
        """
        if self.selected_figure is None:
            self.handling_figure_selection(mouse_x, mouse_y)
        else:
            self.handling_figure_deselection(mouse_x, mouse_y)

    def handling_figure_deselection(self, mouse_x, mouse_y):
        """
        By the given coordinates of the mouse during a click checks if the user was deselecting a figure.
        :param mouse_x: x coordinate of the mouse
        :param mouse_y: y coordinate of the mouse
        """
        if mouse_x == self.selected_figure.x and mouse_y == self.selected_figure.y:
            self.selected_figure.deselect()
            self.selected_figure = None

    def handling_figure_selection(self, mouse_x, mouse_y):
        """
        By the given coordinates of the mouse during a click checks if the user was deselecting a figure.
        :param mouse_x: x coordinate of the mouse
        :param mouse_y: y coordinate of the mouse
        """
        figure = self.get_figure_in_coords((mouse_x, mouse_y))
        if figure is not None and figure.color == self.turn:
            self.selected_figure = figure
            figure.select()

    def get_figure_in_coords(self, coords):
        """
        Looks whether there is a figure in the given coordinates.
        :param coords: coordinates to check in.
        :return: figure if there is any in the given coordinates, None if not.
        """
        for figure in self.figures:
            if figure.x == coords[0] and figure.y == coords[1]:
                return figure
        return None

    def is_mate(self):
        """
        :return: True if the game has reached checkmate, False if not.
        """
        arrangement = GameStatusHandler(self.figures)
        return arrangement.is_mate(0) or arrangement.is_mate(1)

    def is_check(self):
        """
        :return: True if any side is in check right now, False if not.
        """
        arrangement = GameStatusHandler(self.figures)
        return arrangement.is_check(0) or arrangement.is_check(1)

    def is_stalemate(self):
        """
        :return: True if the game has reached stalemate, False if not.
        """
        arrangement = GameStatusHandler(self.figures)
        return arrangement.is_stalemate(0) or arrangement.is_stalemate(1)

    def handle_game_status(self):
        """
        Checks if game has reached checkmate or stalemate and ends it if necessary.
        """
        if self.is_mate():
            self.keep_doing = False
            self.board.draw()
            self.board.draw_result("checkmate")
        if self.is_stalemate():
            self.keep_doing = False
            self.board.draw()
            self.board.draw_result("stalemate")
