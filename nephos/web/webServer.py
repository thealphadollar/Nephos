"""
This Starts the Web Server that will listen for requests
Plus this is where the fun begins for the web part :))
"""
from .info_panel import create_app

APP = create_app()

if __name__ == "__main__":
    APP.run()
