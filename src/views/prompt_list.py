from PySide6.QtWidgets import (
    QTableView, QMenu, QInputDialog, QMessageBox, 
    QHeaderView, QCheckBox, QStyledItemDelegate, QWidget
)
from PySide6.QtCore import Qt, QSize, QAbstractTableModel
from PySide6.QtGui import QFont, QColor
from models import Prompt

class PromptTableModel(QAbstractTableModel):
    COLUMNS = ['english', 'chinese', 'favorite', 'enabled']
    
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.prompts = []
        self.category_id = None
        self.show_mode = 'english'
    
    def setCategory(self, category_id):
        self.category_id = category_id
        self.load_data()
    
    def load_data(self):
        self.beginResetModel()
        if self.category_id:
            self.prompts = self.data_manager.get_prompts_by_category(self.category_id)
        else:
            self.prompts = []
        self.endResetModel()
    
    def setShowMode(self, mode):
        self.show_mode = mode
        self.dataChanged.emit(self.index(0, 0), self.index(self.rowCount() - 1, self.columnCount() - 1))
    
    def rowCount(self, parent=None):
        return len(self.prompts)
    
    def columnCount(self, parent=None):
        return 4
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            headers = ['提示词', '中文', '收藏', '启用']
            return headers[section]
        return None
    
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        
        row = index.row()
        col = index.column()
        prompt = self.prompts[row]
        
        if role == Qt.DisplayRole:
            if col == 0:
                if self.show_mode == 'chinese':
                    return prompt.chinese or prompt.english
                elif self.show_mode == 'both':
                    return f'{prompt.english} ({prompt.chinese})' if prompt.chinese else prompt.english
                else:
                    return prompt.english
            elif col == 1:
                return prompt.chinese or ''
            elif col == 2:
                return ''
            elif col == 3:
                return ''
        
        elif role == Qt.CheckStateRole:
            if col == 2:
                return Qt.Checked if prompt.favorite else Qt.Unchecked
            elif col == 3:
                return Qt.Checked if prompt.enabled else Qt.Unchecked
        
        elif role == Qt.UserRole:
            return prompt.id
        
        return None
    
    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid():
            return False
        
        row = index.row()
        col = index.column()
        prompt = self.prompts[row]
        
        if role == Qt.CheckStateRole:
            if col == 2:
                self.data_manager.update_prompt(prompt.id, favorite=(value == Qt.Checked))
            elif col == 3:
                self.data_manager.update_prompt(prompt.id, enabled=(value == Qt.Checked))
            self.dataChanged.emit(index, index)
            return True
        
        return False
    
    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        
        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable
        
        if index.column() in [2, 3]:
            flags |= Qt.ItemIsUserCheckable
        
        return flags
    
    def getPromptId(self, index):
        if index.isValid():
            return index.data(Qt.UserRole)
        return None
    
    def getPrompt(self, index):
        if index.isValid():
            return self.prompts[index.row()]
        return None
    
    def search(self, keyword):
        if not keyword:
            self.load_data()
            return
        
        all_prompts = self.data_manager.search_prompts(keyword)
        if self.category_id:
            self.prompts = [p for p in all_prompts if p.category_id == self.category_id]
        else:
            self.prompts = all_prompts
        
        self.beginResetModel()
        self.endResetModel()

class CheckBoxDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        checkbox = QCheckBox(parent)
        return checkbox
    
    def setEditorData(self, editor, index):
        value = index.data(Qt.CheckStateRole)
        editor.setChecked(value == Qt.Checked)
    
    def setModelData(self, editor, model, index):
        model.setData(index, Qt.Checked if editor.isChecked() else Qt.Unchecked, Qt.CheckStateRole)

class PromptTableView(QTableView):
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.model = PromptTableModel(data_manager)
        self.setModel(self.model)
        
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)
        
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setItemDelegateForColumn(2, CheckBoxDelegate())
        self.setItemDelegateForColumn(3, CheckBoxDelegate())
        
        self.doubleClicked.connect(self.onDoubleClicked)
    
    def showContextMenu(self, point):
        index = self.indexAt(point)
        menu = QMenu(self)
        
        menu.addAction('添加到编辑器', lambda: self.emitAddPrompt(index))
        menu.addAction('编辑', lambda: self.editPrompt(index))
        menu.addAction('删除', lambda: self.deletePrompt(index))
        menu.addSeparator()
        menu.addAction('添加新Prompt', lambda: self.addPrompt())
        
        menu.exec(self.mapToGlobal(point))
    
    def emitAddPrompt(self, index):
        if index.isValid():
            prompt = self.model.getPrompt(index)
            if prompt:
                self.parent().addPromptToEditor(prompt)
    
    def editPrompt(self, index):
        if not index.isValid():
            return
        
        prompt = self.model.getPrompt(index)
        
        english, ok = QInputDialog.getText(self, '编辑Prompt', '英文:', text=prompt.english)
        if not ok:
            return
        
        chinese, ok = QInputDialog.getText(self, '编辑Prompt', '中文:', text=prompt.chinese or '')
        if not ok:
            chinese = prompt.chinese
        
        note, ok = QInputDialog.getText(self, '编辑Prompt', '备注:', text=prompt.note or '')
        if not ok:
            note = prompt.note
        
        self.data_manager.update_prompt(
            prompt.id,
            english=english,
            chinese=chinese,
            note=note
        )
        self.model.load_data()
    
    def deletePrompt(self, index):
        if not index.isValid():
            return
        
        prompt = self.model.getPrompt(index)
        reply = QMessageBox.question(self, '删除确认', f'确定要删除 "{prompt.english}" 吗？')
        if reply == QMessageBox.Yes:
            self.data_manager.delete_prompt(prompt.id)
            self.model.load_data()
    
    def addPrompt(self):
        if not self.model.category_id:
            QMessageBox.warning(self, '警告', '请先选择一个分类')
            return
        
        english, ok = QInputDialog.getText(self, '添加Prompt', '请输入英文Prompt:')
        if not ok or not english:
            return
        
        chinese, ok = QInputDialog.getText(self, '添加Prompt', '请输入中文翻译(可选):')
        if not ok:
            chinese = None
        
        note, ok = QInputDialog.getText(self, '添加Prompt', '请输入备注(可选):')
        if not ok:
            note = None
        
        self.data_manager.add_prompt(
            english=english,
            chinese=chinese,
            note=note,
            category_id=self.model.category_id
        )
        self.model.load_data()
    
    def onDoubleClicked(self, index):
        self.emitAddPrompt(index)
    
    def setCategory(self, category_id):
        self.model.setCategory(category_id)
    
    def setShowMode(self, mode):
        self.model.setShowMode(mode)
    
    def search(self, keyword):
        self.model.search(keyword)
    
    def refresh(self):
        self.model.load_data()
