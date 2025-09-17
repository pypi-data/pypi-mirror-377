from dpgtheminator.controller import Controller


def load(theme: str):
    controller = Controller()
    controller.load(theme)
    return controller
