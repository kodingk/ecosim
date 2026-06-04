from scenes.title import TitleScene
from simulator import Simulator

if __name__ == "__main__":
    app = Simulator()
    app.run(TitleScene(app))
