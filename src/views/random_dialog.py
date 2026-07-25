from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QListWidget, QCheckBox, QGroupBox, QFormLayout, QSpinBox,
    QDoubleSpinBox, QComboBox
)
from PySide6.QtCore import Qt

class RandomGeneratorDialog(QDialog):
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.setWindowTitle('随机生成')
        self.data_manager = data_manager
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        
        categories = self.data_manager.get_all_categories()
        self.category_checkboxes = {}
        
        for category in categories:
            checkbox = QCheckBox(category.name_cn if category.name_cn else category.name)
            checkbox.setChecked(True)
            checkbox.setProperty('category_id', category.id)
            self.category_checkboxes[category.id] = checkbox
            layout.addWidget(checkbox)
        
        options_group = QGroupBox('生成选项')
        form_layout = QFormLayout()
        
        self.count_spin = QSpinBox()
        self.count_spin.setRange(1, 10)
        self.count_spin.setValue(1)
        
        form_layout.addRow('生成数量:', self.count_spin)
        options_group.setLayout(form_layout)
        layout.addWidget(options_group)
        
        button_layout = QHBoxLayout()
        self.btn_generate = QPushButton('生成')
        self.btn_generate.clicked.connect(self.accept)
        self.btn_cancel = QPushButton('取消')
        self.btn_cancel.clicked.connect(self.reject)
        
        button_layout.addWidget(self.btn_generate)
        button_layout.addWidget(self.btn_cancel)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def getSelectedCategories(self):
        return [cb.property('category_id') for cb in self.category_checkboxes.values() if cb.isChecked()]
    
    def getGenerateCount(self):
        return self.count_spin.value()
