from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QComboBox, QGroupBox, QFormLayout
)
from PySide6.QtCore import Qt

class ImportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('导入数据')
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        
        source_group = QGroupBox('导入来源')
        form_layout = QFormLayout()
        
        self.source_combo = QComboBox()
        self.source_combo.addItems(['JSON文件', 'CSV文件', 'TXT文件', 'e621标签', 'Danbooru标签'])
        
        form_layout.addRow('来源类型:', self.source_combo)
        source_group.setLayout(form_layout)
        layout.addWidget(source_group)
        
        options_group = QGroupBox('导入选项')
        form_layout2 = QFormLayout()
        
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(['合并', '覆盖', '追加'])
        
        form_layout2.addRow('导入模式:', self.mode_combo)
        options_group.setLayout(form_layout2)
        layout.addWidget(options_group)
        
        button_layout = QHBoxLayout()
        self.btn_browse = QPushButton('浏览')
        self.btn_ok = QPushButton('确定')
        self.btn_ok.clicked.connect(self.accept)
        self.btn_cancel = QPushButton('取消')
        self.btn_cancel.clicked.connect(self.reject)
        
        button_layout.addWidget(self.btn_browse)
        button_layout.addWidget(self.btn_ok)
        button_layout.addWidget(self.btn_cancel)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def getOptions(self):
        return {
            'source': self.source_combo.currentText(),
            'mode': self.mode_combo.currentText()
        }
