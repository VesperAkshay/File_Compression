from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

class Dashboard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()

        # Dashboard title
        self.dashboard_label = QLabel('Dashboard Overview')
        self.dashboard_label.setStyleSheet("font-family: 'Fira Code'; font-size: 18px; color: #333;")
        self.layout.addWidget(self.dashboard_label)

        # Example content
        self.dashboard_info = QLabel('Here you can see an overview of your application.')
        self.dashboard_info.setStyleSheet("font-family: 'Fira Code'; font-size: 14px; color: #333;")
        self.layout.addWidget(self.dashboard_info)

        # Add more detailed information or controls here

        self.setLayout(self.layout) 