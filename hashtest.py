import sys, hashlib

from PyQt5.QtWidgets import *
from enum import IntEnum
from pathlib import Path
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

global_font = QFont("monospaced", 10)
result_font = QFont("monospaced", 14)

class hash_function_t(IntEnum):
    MD5 = 0
    SHA1 = 1
    SHA256 = 2
    SHA384 = 3
    SHA512 = 4

# Generates a tuple of hashes for the specified file.
# The tuple is such that you should be able to reference its members
# with hash_function_t.  Example:  hashes[hash_function_t.MD5] would be the md5
# hash.
def generate_hash(target):
    if(Path(target).is_file() == False):
        return None
    file = open(target, "rb").read()
    return (hashlib.md5(file).hexdigest(), \
            hashlib.sha1(file).hexdigest(), \
            hashlib.sha256(file).hexdigest(), \
            hashlib.sha384(file).hexdigest(), \
            hashlib.sha512(file).hexdigest())

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
            self.hash_labels[e].setFont(global_font)
            self.hash_labels[e].setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
        self.result_label.setFont(result_font)
        
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
        hashname_label = QLabel(hashname + ": ")
        hashname_label.setFont(global_font)
        l.addWidget(hashname_label)
        l.addWidget(label)
        return l
    
    def _test(self):
        self.result_label.setText("Please wait, reading file...")
        target = QFileDialog.getOpenFileName()[0]
        hashes = generate_hash(target)
        if(hashes is not None):
            self.result_label.setText("No Match.")
            for h in hash_function_t:
                if(hashes[h] == self.hash_textbox.text()):
                    self.result_label.setText("MATCH!")
                self.hash_labels[h].setText(hashes[h])
        else:
            self.result_label.setText("Canceled.")
            
    
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