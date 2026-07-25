from PySide6.QtWidgets import (
    QTextEdit, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QMenu, QMessageBox, QInputDialog, QSplitter
)
from PySide6.QtCore import Qt, QMimeData, QByteArray
from PySide6.QtGui import QTextCursor, QKeySequence
from models import Prompt
import json

class PromptEditor(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)
        self.setPlaceholderText('点击或拖拽Prompt到这里...')
        self.prompt_items = []
    
    def showContextMenu(self, point):
        cursor = self.cursorForPosition(point)
        self.setTextCursor(cursor)
        
        menu = QMenu(self)
        
        menu.addAction('删除选中', lambda: self.deleteSelected())
        menu.addAction('清空', lambda: self.clear())
        menu.addSeparator()
        menu.addAction('复制', lambda: self.copy(), QKeySequence.Copy)
        menu.addAction('剪切', lambda: self.cut(), QKeySequence.Cut)
        menu.addAction('粘贴', lambda: self.paste(), QKeySequence.Paste)
        menu.addSeparator()
        menu.addAction('去重', lambda: self.removeDuplicates())
        menu.addAction('排序', lambda: self.sortPrompts())
        
        menu.exec(self.mapToGlobal(point))
    
    def deleteSelected(self):
        cursor = self.textCursor()
        if cursor.hasSelection():
            cursor.removeSelectedText()
    
    def removeDuplicates(self):
        text = self.toPlainText()
        items = [item.strip() for item in text.split(',') if item.strip()]
        unique_items = list(dict.fromkeys(items))
        self.setPlainText(', '.join(unique_items))
    
    def sortPrompts(self):
        text = self.toPlainText()
        items = [item.strip() for item in text.split(',') if item.strip()]
        items.sort()
        self.setPlainText(', '.join(items))
    
    def addPrompt(self, prompt):
        current_text = self.toPlainText().strip()
        if current_text:
            new_text = f'{current_text}, {prompt.english}'
        else:
            new_text = prompt.english
        
        self.setPlainText(new_text)
        self.prompt_items.append(prompt)
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('application/json'):
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        if event.mimeData().hasFormat('application/json'):
            data = json.loads(event.mimeData().data('application/json').data().decode())
            for item in data.get('prompts', []):
                current_text = self.toPlainText().strip()
                if current_text:
                    new_text = f'{current_text}, {item}'
                else:
                    new_text = item
                self.setPlainText(new_text)
            event.acceptProposedAction()

class PromptEditorPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self.editor = PromptEditor()
        self.layout.addWidget(self.editor)
        
        toolbar = QHBoxLayout()
        
        self.btn_copy = QPushButton('复制到剪贴板')
        self.btn_copy.clicked.connect(self.copyToClipboard)
        
        self.btn_save_txt = QPushButton('保存TXT')
        self.btn_save_txt.clicked.connect(self.saveAsTxt)
        
        self.btn_save_json = QPushButton('保存JSON')
        self.btn_save_json.clicked.connect(self.saveAsJson)
        
        self.btn_clear = QPushButton('清空')
        self.btn_clear.clicked.connect(self.editor.clear)
        
        toolbar.addWidget(self.btn_copy)
        toolbar.addWidget(self.btn_save_txt)
        toolbar.addWidget(self.btn_save_json)
        toolbar.addWidget(self.btn_clear)
        
        self.layout.addLayout(toolbar)
    
    def copyToClipboard(self):
        text = self.editor.toPlainText()
        from PySide6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
    
    def saveAsTxt(self):
        from PySide6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getSaveFileName(self, '保存为TXT', '', 'Text Files (*.txt)')
        if path:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(self.editor.toPlainText())
    
    def saveAsJson(self):
        from PySide6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getSaveFileName(self, '保存为JSON', '', 'JSON Files (*.json)')
        if path:
            text = self.editor.toPlainText()
            items = [item.strip() for item in text.split(',') if item.strip()]
            data = {'prompts': items, 'generated_at': 'now'}
            
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
    
    def getText(self):
        return self.editor.toPlainText()
    
    def setText(self, text):
        self.editor.setPlainText(text)
    
    def addPrompt(self, prompt):
        self.editor.addPrompt(prompt)
