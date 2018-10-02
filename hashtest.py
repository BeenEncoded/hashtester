import sys, hashalgo

from hashalgo import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt

class input_widget(QWidget):
    def __init__(self, parent):
        super(input_widget, self).__init__(parent)
        self.setLayout(self._input_layout())
    
    def _input_layout(self):
        self.hash_textbox = QLineEdit()
        self.test_button = QPushButton("Test a File Against this Hash")
        self.result_label = QLabel("No Match!")

        self.hash_labels = []
        for e in hash_function_t:
            self.hash_labels.append(QLabel(""))
            self.hash_labels[e].setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
        
        layout = QVBoxLayout()
        layout.addWidget(self.hash_textbox)
        layout.addWidget(self.test_button)
        layout.addWidget(self.result_label)

        for e in hash_function_t:
            layout.addLayout(self._label_hash(e.name, self.hash_labels[e]))

        self.test_button.clicked.connect(self._test)
        return layout

    def _label_hash(self, hashname, label):
        l = QHBoxLayout()
        l.addWidget(QLabel(hashname + ": "))
        l.addWidget(label)
        return l
    
    def _test(self):
        h = hash_function_data()
        h.target = QFileDialog.getOpenFileName()[0]
        print("Target: " + h.target)
        thash = ""
        self.result_label.setText("No Match.")
        for e in hash_function_t:
            h.function_type = e
            thash = generate_hash(h)
            self.hash_labels[e].setText(thash)
            if(thash == self.hash_textbox.text()):
                self.result_label.setText("MATCH!")
    
    def _connect_slots(self):
        pass

class main_window(QMainWindow):
    def __init__(self, parent):
        super(main_window, self).__init__(parent)
        self.setCentralWidget(input_widget(self))

def main(argv):
    app = QApplication(argv)
    window = main_window(None)
    window.show()
    return app.exec()

if(__name__ == "__main__"):
    sys.exit(main(sys.argv))