""" Project designed by:
Department of Computer Science,
University of Toronto

=== Module Description ===
This module contains the code to run the treemap visualisation program.
It is responsible for initializing an instance of AbstractTree (using a
concrete subclass, of course), rendering it to the user using pygame,
and detecting user events like mouse clicks and key presses and responding
to them.
"""
import pygame
from tree_data import FileSystemTree
from population import PopulationTree


# Screen dimensions and coordinates
ORIGIN = (0, 0)
WIDTH = 1024  # default 1024
HEIGHT = 768  # default 768
FONT_HEIGHT = 30                       # The height of the text display.
TREEMAP_HEIGHT = HEIGHT - FONT_HEIGHT  # The height of the treemap display.

# Font to use for the treemap program.
FONT_FAMILY = 'Consolas'


def run_visualisation(tree):
    """Display an interactive graphical display of the given tree's treemap.

    @type tree: AbstractTree
    @rtype: None
    """
    # Setup pygame
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    # Render the initial display of the static treemap.
    render_display(screen, tree, '')

    # Start an event loop to respond to events.
    event_loop(screen, tree)


def render_display(screen, tree, text):
    """Render a treemap and text display to the given screen.

    @type screen: pygame.Surface
    @type tree: AbstractTree
    @type text: str
        The text to render.
    @rtype: None
    """
    # First, clear the screen
    pygame.draw.rect(screen, pygame.color.THECOLORS['black'],
                     (0, 0, WIDTH, HEIGHT))

    treemap = tree.generate_treemap((0, 0, WIDTH, TREEMAP_HEIGHT))
    for file in treemap:
        pygame.draw.rect(screen, file[1], file[0])

    _render_text(screen, text)

    # This must be called *after* all other pygame functions have run.
    pygame.display.flip()


def _render_text(screen, text):
    """Render text at the bottom of the display.

    @type screen: pygame.Surface
    @type text: str
    @rtype: None
    """
    # The font we want to use
    font = pygame.font.SysFont(FONT_FAMILY, FONT_HEIGHT - 8)
    text_surface = font.render(text, 1, pygame.color.THECOLORS['white'])

    # Where to render the text_surface
    text_pos = (0, HEIGHT - FONT_HEIGHT + 4)
    screen.blit(text_surface, text_pos)


def event_loop(screen, tree):
    """Respond to events (mouse clicks, key presses) and update the display.

    Note: loop ends when the user closes the window.

    @type screen: pygame.Surface
    @type tree: AbstractTree
    @rtype: None
    """
    selected_leaf = None
    path = ''
    size = ''

    while True:
        # Wait for an event
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            return

        treemap = tree.generate_treemap((0, 0, WIDTH, TREEMAP_HEIGHT))
        if event.type == pygame.MOUSEBUTTONUP \
                and tree.get_leaf(event.pos, treemap) is not None:
            clicked = tree.get_leaf(event.pos, treemap)

            if clicked is not selected_leaf and event.button == 1:
                selected_leaf = clicked
                path = selected_leaf.get_path()
                size = '      (' + str(selected_leaf.data_size) + ')'
            elif clicked is selected_leaf and event.button == 1:
                selected_leaf, path, size = None, '', ''
            elif clicked is not selected_leaf and event.button == 3:
                clicked.delete()
            elif clicked is selected_leaf and event.button == 3:
                selected_leaf.delete()
                selected_leaf, path, size = None, '', ''
            render_display(screen, tree, path + size)

        if event.type == pygame.KEYUP and selected_leaf is not None:
            if event.key == pygame.K_UP:
                selected_leaf.change_size('+')
            elif event.key == pygame.K_DOWN:
                selected_leaf.change_size('-')
            size = '      (' + str(selected_leaf.data_size) + ')'
            render_display(screen, tree, path + size)


def run_treemap_file_system(path):
    """Run a treemap visualisation for the given path's file structure.

    Precondition: <path> is a valid path to a file or folder.

    @type path: str
    @rtype: None
    """
    file_tree = FileSystemTree(path)
    run_visualisation(file_tree)


def run_treemap_population():
    """Run a treemap visualisation for World Bank population data.

    @rtype: None
    """
    pop_tree = PopulationTree(True)
    run_visualisation(pop_tree)


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config='pylintrc.txt')

    #
    run_treemap_population()
