# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=os.getenv("DEBUG"))


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
