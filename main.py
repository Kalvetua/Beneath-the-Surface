# Local
from game import Game

def main():
    g = Game()
    while g.run_application:
        g.current_menu.menu_sequence()
        g.level_sequence()

if __name__ == '__main__':
    main()