from utils.data_reader import img_graph


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    automaton = img_graph("resources/CCS.png", 1500)

    automaton.draw()
