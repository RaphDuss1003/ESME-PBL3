from PyQt5.QtWidgets import QApplication
import sys
from Engine.Interface.interface import Interface


def main():
	app = QApplication(sys.argv)
	window = Interface()
	window.show()
	sys.exit(app.exec_())


if __name__ == '__main__':
	main()

