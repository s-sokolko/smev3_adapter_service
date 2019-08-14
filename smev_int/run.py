from smev_int.core import app
import smev_int.views  # noqua


if __name__ == "__main__":
    app.run(host=app.Config.HOST, port=app.Config.PORT, debug=True)