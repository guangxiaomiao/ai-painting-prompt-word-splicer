from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QComboBox, QToolBar, QStatusBar, QSplitter
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QAction

class MainToolbar(QToolBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMovable(False)
        
        self.action_new_category = QAction(QIcon.fromTheme('folder-new'), '新建分类', self)
        self.action_new_prompt = QAction(QIcon.fromTheme('document-new'), '新建Prompt', self)
        self.action_import = QAction(QIcon.fromTheme('document-import'), '导入', self)
        self.action_export = QAction(QIcon.fromTheme('document-export'), '导出', self)
        self.action_beginner = QAction(QIcon.fromTheme('go-next'), '新人模式', self)
        self.action_random = QAction(QIcon.fromTheme('dice'), '随机生成', self)
        self.action_settings = QAction(QIcon.fromTheme('settings'), '设置', self)
        
        self.addActions([
            self.action_new_category,
            self.action_new_prompt,
            self.action_import,
            self.action_export,
            self.action_beginner,
            self.action_random,
            self.action_settings
        ])
        
        self.addSeparator()
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText('搜索...')
        self.addWidget(self.search_edit)
        
        self.show_mode_combo = QComboBox()
        self.show_mode_combo.addItems(['英文', '中文', '英文+中文'])
        self.addWidget(QLabel('显示:'))
        self.addWidget(self.show_mode_combo)

class MainStatusBar(QStatusBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.label_prompt_count = QLabel('Prompt: 0')
        self.label_category_count = QLabel('分类: 0')
        self.label_status = QLabel('就绪')
        
        self.addWidget(self.label_category_count)
        self.addWidget(self.label_prompt_count)
        self.addWidget(self.label_status)
    
    def updateCounts(self, category_count, prompt_count):
        self.label_category_count.setText(f'分类: {category_count}')
        self.label_prompt_count.setText(f'Prompt: {prompt_count}')
    
    def setStatus(self, text):
        self.label_status.setText(text)
