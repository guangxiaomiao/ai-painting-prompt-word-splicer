from PySide6.QtWidgets import (
    QTreeView, QMenu, QInputDialog, QMessageBox, 
    QHeaderView, QStyledItemDelegate
)
from PySide6.QtCore import Qt, QSize, QAbstractItemModel, QModelIndex
from PySide6.QtGui import QIcon, QFont
from models import Category

class CategoryTreeModel(QAbstractItemModel):
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.root_item = None
        self.load_data()
    
    def load_data(self):
        self.beginResetModel()
        categories = self.data_manager.get_all_categories()
        self.root_item = CategoryTreeNode(None, None)
        self.build_tree(categories)
        self.endResetModel()
    
    def build_tree(self, categories):
        category_map = {}
        
        for cat in categories:
            node = CategoryTreeNode(cat, self.root_item)
            category_map[cat.id] = node
        
        for cat in categories:
            if cat.parent_id and cat.parent_id in category_map:
                parent_node = category_map[cat.parent_id]
                category_map[cat.id].setParent(parent_node)
                parent_node.addChild(category_map[cat.id])
            else:
                self.root_item.addChild(category_map[cat.id])
    
    def index(self, row, column, parent=QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        
        if not parent.isValid():
            parent_item = self.root_item
        else:
            parent_item = parent.internalPointer()
        
        child_item = parent_item.child(row)
        if child_item:
            return self.createIndex(row, column, child_item)
        return QModelIndex()
    
    def parent(self, index):
        if not index.isValid():
            return QModelIndex()
        
        child_item = index.internalPointer()
        parent_item = child_item.parent
        
        if parent_item == self.root_item:
            return QModelIndex()
        
        return self.createIndex(parent_item.row(), 0, parent_item)
    
    def rowCount(self, parent=QModelIndex()):
        if parent.column() > 0:
            return 0
        
        if not parent.isValid():
            parent_item = self.root_item
        else:
            parent_item = parent.internalPointer()
        
        return parent_item.childCount()
    
    def columnCount(self, parent=QModelIndex()):
        return 1
    
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        
        item = index.internalPointer()
        
        if role == Qt.DisplayRole:
            name = item.category.name_cn if item.category.name_cn else item.category.name
            return name
        
        elif role == Qt.DecorationRole:
            if item.hasChildren():
                return QIcon.fromTheme('folder-open' if item.category.expanded else 'folder')
            return QIcon.fromTheme('tag')
        
        elif role == Qt.UserRole:
            return item.category.id
        
        return None
    
    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled
    
    def addCategory(self, name, name_cn=None, parent_id=None):
        parent_item = None
        if parent_id:
            for i in range(self.root_item.childCount()):
                child = self.root_item.child(i)
                if child.category.id == parent_id:
                    parent_item = child
                    break
        
        category = self.data_manager.add_category(name, name_cn, parent_id)
        
        node = CategoryTreeNode(category, parent_item or self.root_item)
        if parent_item:
            parent_item.addChild(node)
            row = parent_item.childCount() - 1
            parent_index = self.createIndex(parent_item.row(), 0, parent_item)
        else:
            self.root_item.addChild(node)
            row = self.root_item.childCount() - 1
            parent_index = QModelIndex()
        
        self.beginInsertRows(parent_index, row, row)
        self.endInsertRows()
    
    def removeCategory(self, index):
        item = index.internalPointer()
        category_id = item.category.id
        
        self.beginRemoveRows(index.parent(), index.row(), index.row())
        parent_item = item.parent()
        parent_item.removeChild(index.row())
        self.data_manager.delete_category(category_id)
        self.endRemoveRows()
    
    def renameCategory(self, index, new_name):
        item = index.internalPointer()
        self.data_manager.update_category(item.category.id, name=new_name)
        self.dataChanged.emit(index, index)
    
    def getCategoryId(self, index):
        if index.isValid():
            return index.data(Qt.UserRole)
        return None

class CategoryTreeNode:
    def __init__(self, category, parent=None):
        self.category = category
        self.parent = parent
        self.children = []
    
    def addChild(self, child):
        self.children.append(child)
    
    def removeChild(self, row):
        del self.children[row]
    
    def child(self, row):
        return self.children[row]
    
    def childCount(self):
        return len(self.children)
    
    def row(self):
        if self.parent:
            return self.parent.children.index(self)
        return 0
    
    def setParent(self, parent):
        self.parent = parent
    
    def hasChildren(self):
        return len(self.children) > 0

class CategoryTreeView(QTreeView):
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.model = CategoryTreeModel(data_manager)
        self.setModel(self.model)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)
        self.setHeaderHidden(True)
        self.expanded.connect(self.onExpanded)
        self.collapsed.connect(self.onCollapsed)
    
    def showContextMenu(self, point):
        index = self.indexAt(point)
        menu = QMenu(self)
        
        menu.addAction('新建分类', lambda: self.addCategory())
        menu.addAction('重命名', lambda: self.renameCategory(index))
        menu.addAction('删除', lambda: self.deleteCategory(index))
        menu.addSeparator()
        menu.addAction('刷新', lambda: self.model.load_data())
        
        menu.exec(self.mapToGlobal(point))
    
    def addCategory(self):
        name, ok = QInputDialog.getText(self, '新建分类', '请输入分类名称:')
        if ok and name:
            name_cn, ok_cn = QInputDialog.getText(self, '中文名称', '请输入中文名称(可选):')
            self.model.addCategory(name, name_cn if ok_cn else None)
    
    def renameCategory(self, index):
        if not index.isValid():
            return
        
        old_name = index.data(Qt.DisplayRole)
        new_name, ok = QInputDialog.getText(self, '重命名', '请输入新名称:', text=old_name)
        if ok and new_name:
            self.model.renameCategory(index, new_name)
    
    def deleteCategory(self, index):
        if not index.isValid():
            return
        
        name = index.data(Qt.DisplayRole)
        reply = QMessageBox.question(self, '删除确认', f'确定要删除分类 "{name}" 吗？')
        if reply == QMessageBox.Yes:
            self.model.removeCategory(index)
    
    def onExpanded(self, index):
        item = index.internalPointer()
        if item and item.category:
            self.data_manager.update_category(item.category.id, expanded=True)
    
    def onCollapsed(self, index):
        item = index.internalPointer()
        if item and item.category:
            self.data_manager.update_category(item.category.id, expanded=False)
    
    def refresh(self):
        self.model.load_data()
    
    def getSelectedCategoryId(self):
        indexes = self.selectedIndexes()
        if indexes:
            return self.model.getCategoryId(indexes[0])
        return None
