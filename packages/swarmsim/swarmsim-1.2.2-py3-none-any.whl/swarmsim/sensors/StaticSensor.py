from ..sensors.AbstractSensor import AbstractSensor


class StaticSensor(AbstractSensor):
    def __init__(self, parent=None):
        super(StaticSensor, self).__init__(parent=parent)
        self.current_state = 0

    def step(self, population):
        pass

    def draw(self, screen, zoom=1.0):
        pass
