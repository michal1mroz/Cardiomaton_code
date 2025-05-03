from utils.data_reader import *


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    automaton = load_to_binary_array("resources/img_ccs/", 1500)

    automaton.draw()
