import sys, hashlib, os, threading, dataclasses

from PyQt5.QtWidgets import *
from enum import IntEnum
from pathlib import Path
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal, QObject
from PyQt5.QtGui import QFont

global_font = QFont("monospaced", 10)
result_font = QFont("monospaced", 14)
HASH_BLOCKSIZE = ((2**10) * 5) #10 Kb blocksize

class hash_function_t(IntEnum):
    MD5 = 0
    SHA1 = 1
    SHA256 = 2
    SHA384 = 3
    SHA512 = 4

@dataclasses.dataclass
class ProcessStatus:
    '''
    Stores a process' status
    '''
    percent: float = 0
    message: str = ""

class HashThread(threading.Thread):
    class guicom(QObject):
        updatestatus = pyqtSignal(ProcessStatus)
        finishedprocess = pyqtSignal()

    def __init__(self, target, blocksize=HASH_BLOCKSIZE):
        super(HashThread, self).__init__()
        self.status = ProcessStatus()
        self.target = target
        self.blocksize = blocksize
        self.hashes = None
        self.cancel = False

        self.com = HashThread.guicom()

    # Generates a tuple of hashes for the specified file.
    # The tuple is such that you should be able to reference its members
    # with hash_function_t.  Example:  hashes[hash_function_t.MD5] would be the md5
    # hash.
    def run(self):
        self.cancel = False
        if not os.path.isfile(self.target):
            return None
        hashes = [
            hashlib.md5(),
            hashlib.sha1(),
            hashlib.sha256(),
            hashlib.sha384(),
            hashlib.sha512()
        ]
        file_size = os.stat(self.target).st_size
        file_read = 0
        self.status.message = "Hashing..."
        self.status.percent = 0
        self._setstatus(self.status)
        with open(self.target, 'rb') as file:
            while not self.cancel:
                block = file.read(self.blocksize)
                file_read += len(block)
                self.status.percent = ((file_read * 100) / file_size)
                self._setstatus(self.status)
                if len(block) == 0:
                    break
                for h in hashes:
                    h.update(block)
        if not self.cancel:
            self.hashes = [h.hexdigest() for h in hashes]
        else:
            self.hashes = ["Canceled" for x in range(0, len(hashes))]
        self._finished()

    def _setstatus(self, status):
        self.com.updatestatus.emit(status)
    
    def _finished(self):
        self.com.finishedprocess.emit()

class input_widget(QWidget):
    def __init__(self, parent):
        super(input_widget, self).__init__(parent)
        self.setLayout(self._input_layout())
        self._connect_slots()
    
    def _input_layout(self):
        self.hash_textbox = QLineEdit()
        self.test_button = QPushButton("Test a File Against this Hash")
        self.result_label = QLabel("No Match!")
        self.progress_bar = QProgressBar()
        self.cancel_button = QPushButton("Cancel")

        self.hash_labels = []
        for e in hash_function_t:
            self.hash_labels.append(QLabel(""))
            self.hash_labels[e].setFont(global_font)
            self.hash_labels[e].setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
        self.result_label.setFont(result_font)
        
        layout = QVBoxLayout()
        button_layout = QHBoxLayout()
        layout.addWidget(self.hash_textbox)
        button_layout.addWidget(self.test_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.result_label)

        for e in hash_function_t:
            layout.addLayout(self._label_hash(e.name, self.hash_labels[e]))

        self._updateEnabledButtons()
        return layout

    def _label_hash(self, hashname, label):
        l = QHBoxLayout()
        hashname_label = QLabel(hashname + ": ")
        hashname_label.setFont(global_font)
        l.addWidget(hashname_label)
        l.addWidget(label)
        return l
    
    @pyqtSlot()
    def _updateEnabledButtons(self):
        if not hasattr(self, "hash_thread"):
            self.test_button.setEnabled(True)
            self.cancel_button.setEnabled(False)
        else:
            self.test_button.setEnabled(not self.hash_thread.isAlive())
            self.cancel_button.setEnabled(self.hash_thread.isAlive())

    @pyqtSlot(ProcessStatus)
    def _statusUpdate(self, status):
        self.progress_bar.setValue(status.percent)

    def run_hashes(self, target, blocksize=HASH_BLOCKSIZE):
        self.hash_thread = HashThread(target, blocksize)
        self.hash_thread.com.updatestatus.connect(self._statusUpdate)
        self.hash_thread.com.finishedprocess.connect(self._hashingFinished)
        self.hash_thread.start()
        self._updateEnabledButtons()

    @pyqtSlot()
    def _hashingFinished(self):
        self.hash_thread.join()
        self._updateEnabledButtons()
        if(self.hash_thread.hashes is not None):
            self.result_label.setText("No Match.")
            for h in hash_function_t:
                if(self.hash_thread.hashes[h] == self.hash_textbox.text()):
                    self.result_label.setText("MATCH!")
                self.hash_labels[h].setText(self.hash_thread.hashes[h])
        else:
            self.result_label.setText("Canceled.")

    @pyqtSlot()
    def _test(self):
        self.test_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.result_label.setText("Please wait, reading file...")
        target = QFileDialog.getOpenFileName()[0]
        self.run_hashes(target)
    
    @pyqtSlot()
    def _cancel_hash(self):
        self.hash_thread.cancel = True
        self._hashingFinished()

    def _connect_slots(self):
        self.test_button.clicked.connect(self._test)
        self.cancel_button.clicked.connect(self._cancel_hash)
        

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