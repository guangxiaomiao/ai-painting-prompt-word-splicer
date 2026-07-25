import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt, QTimer
from models import init_db, Session, Settings, Category, Prompt
from controllers import DataManager, RandomGenerator, DataImporter, BackupManager
from views import (
    CategoryTreeView, PromptTableView, PromptEditorPanel,
    MainToolbar, MainStatusBar, SettingsDialog,
    RandomGeneratorDialog, ImportDialog, OllamaAIPanel,
    BeginnerModeDialog
)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('绘画提示辅助器 v1.6 - 新人模式版')
        self.setGeometry(100, 100, 1400, 800)
        
        init_db()
        
        self.data_manager = DataManager()
        self.random_generator = RandomGenerator()
        self.data_importer = DataImporter()
        self.backup_manager = BackupManager()
        
        self.settings = self.data_manager.get_settings()
        
        self.initUI()
        self.loadDefaultData()
        
        self.auto_save_timer = QTimer()
        if self.settings.auto_save:
            self.auto_save_timer.start(60000)
        
        self.auto_backup_timer = QTimer()
        if self.settings.auto_backup:
            self.auto_backup_timer.start(self.settings.backup_interval * 3600000)
    
    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        self.toolbar = MainToolbar()
        self.addToolBar(self.toolbar)
        
        self.status_bar = MainStatusBar()
        self.setStatusBar(self.status_bar)
        
        splitter = QSplitter(Qt.Horizontal)
        
        self.category_tree = CategoryTreeView(self.data_manager)
        self.category_tree.setFixedWidth(200)
        self.category_tree.clicked.connect(self.onCategorySelected)
        
        self.prompt_list = PromptTableView(self.data_manager)
        self.prompt_list.doubleClicked.connect(self.onPromptDoubleClicked)
        
        self.editor_panel = PromptEditorPanel()

        self.ollama_panel = OllamaAIPanel(self.settings, self.data_manager)
        self.ollama_panel.setEditorCallback(self.appendTextToEditor)
        self.ollama_panel.setEditorTextGetter(self.getEditorText)

        right_splitter = QSplitter(Qt.Vertical)
        right_splitter.addWidget(self.editor_panel)
        right_splitter.addWidget(self.ollama_panel)
        right_splitter.setStretchFactor(0, 2)
        right_splitter.setStretchFactor(1, 3)

        splitter.addWidget(self.category_tree)
        splitter.addWidget(self.prompt_list)
        splitter.addWidget(right_splitter)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        splitter.setStretchFactor(2, 2)
        
        layout.addWidget(splitter)
        
        self.toolbar.action_new_category.triggered.connect(self.category_tree.addCategory)
        self.toolbar.action_new_prompt.triggered.connect(self.prompt_list.addPrompt)
        self.toolbar.action_import.triggered.connect(self.importData)
        self.toolbar.action_export.triggered.connect(self.exportData)
        self.toolbar.action_beginner.triggered.connect(self.openBeginnerMode)
        self.toolbar.action_random.triggered.connect(self.generateRandom)
        self.toolbar.action_settings.triggered.connect(self.showSettings)
        
        self.toolbar.search_edit.textChanged.connect(self.onSearch)
        self.toolbar.show_mode_combo.currentIndexChanged.connect(self.onShowModeChanged)
        
        self.applyTheme()
    
    def loadDefaultData(self):
        session = Session()
        
        if session.query(Category).count() == 0:
            categories = [
                {'name': '人物', 'name_cn': '人物'},
                {'name': '动作', 'name_cn': '动作'},
                {'name': '姿势', 'name_cn': '姿势'},
                {'name': '服装', 'name_cn': '服装'},
                {'name': '发型', 'name_cn': '发型'},
                {'name': '背景', 'name_cn': '背景'},
                {'name': '天气', 'name_cn': '天气'},
                {'name': '画质', 'name_cn': '画质'},
                {'name': '画风', 'name_cn': '画风'},
                {'name': '艺术家', 'name_cn': '艺术家'},
                {'name': 'Lora', 'name_cn': 'Lora'},
                {'name': 'NSFW', 'name_cn': 'NSFW'},
            ]
            
            for cat_data in categories:
                category = Category(name=cat_data['name'], name_cn=cat_data['name_cn'])
                session.add(category)
            
            session.flush()
            
            prompts_data = [
                ('masterpiece', '杰作', '画质', 1.0),
                ('best quality', '最佳质量', '画质', 1.0),
                ('high quality', '高质量', '画质', 0.9),
                ('1girl', '1个女孩', '人物', 1.0),
                ('solo', '单人', '人物', 0.9),
                ('smile', '微笑', '表情', 0.8),
                ('blue eyes', '蓝眼睛', '眼睛', 0.7),
                ('long hair', '长发', '发型', 0.8),
                ('short hair', '短发', '发型', 0.7),
                ('standing', '站立', '姿势', 0.8),
                ('sitting', '坐姿', '姿势', 0.7),
                ('running', '奔跑', '动作', 0.6),
                ('forest', '森林', '背景', 0.7),
                ('city', '城市', '背景', 0.7),
                ('sunny', '晴天', '天气', 0.8),
                ('rainy', '雨天', '天气', 0.6),
                ('anime style', '动漫风格', '画风', 0.9),
                ('realistic', '写实', '画风', 0.8),
            ]
            
            for english, chinese, cat_name, weight in prompts_data:
                category = session.query(Category).filter(Category.name == cat_name).first()
                if category:
                    prompt = Prompt(
                        english=english,
                        chinese=chinese,
                        category_id=category.id,
                        random_weight=weight,
                        enabled=True
                    )
                    session.add(prompt)
            
            session.commit()
        
        session.close()
        
        self.category_tree.refresh()
        self.updateStatus()
    
    def onCategorySelected(self, index):
        category_id = self.category_tree.getSelectedCategoryId()
        self.prompt_list.setCategory(category_id)
        self.updateStatus()
    
    def onPromptDoubleClicked(self, index):
        prompt = self.prompt_list.model.getPrompt(index)
        if prompt:
            self.editor_panel.addPrompt(prompt)
    
    def addPromptToEditor(self, prompt):
        self.editor_panel.addPrompt(prompt)

    def appendTextToEditor(self, text):
        current = self.editor_panel.toPlainText()
        if current:
            current += ', ' + text
        else:
            current = text
        self.editor_panel.setText(current)
    
    def getEditorText(self):
        return self.editor_panel.getText()
    
    def onSearch(self, text):
        self.prompt_list.search(text)
    
    def onShowModeChanged(self, index):
        modes = ['english', 'chinese', 'both']
        mode = modes[index]
        self.prompt_list.setShowMode(mode)
        self.data_manager.update_settings(show_mode=mode)
    
    def importData(self):
        dialog = ImportDialog()
        if dialog.exec():
            options = dialog.getOptions()
            
            path, _ = QFileDialog.getOpenFileName(self, '选择文件', '', 'All Files (*)')
            if not path:
                return
            
            try:
                if options['source'] == 'JSON文件':
                    self.data_importer.import_json(path)
                elif options['source'] == 'CSV文件':
                    fmt = self.data_importer.detect_csv_format(path)
                    if fmt == 'danbooru':
                        count = self.data_importer.import_danbooru_csv(path)
                        QMessageBox.information(self, '导入成功', f'Danbooru CSV导入成功，共导入 {count} 条')
                    elif fmt == 'danbooru_zh':
                        count = self.data_importer.import_danbooru_zh_csv(path)
                        QMessageBox.information(self, '导入成功', f'Danbooru中文CSV导入成功，共导入 {count} 条')
                    else:
                        self.data_importer.import_csv(path)
                        QMessageBox.information(self, '导入成功', 'CSV导入成功')
                    self.category_tree.refresh()
                    if self.category_tree.getSelectedCategoryId():
                        self.prompt_list.setCategory(self.category_tree.getSelectedCategoryId())
                    self.updateStatus()
                    return
                elif options['source'] == 'TXT文件':
                    self.data_importer.import_txt(path)
                elif options['source'] == 'e621标签':
                    self.data_importer.import_e621_tags(path)
                elif options['source'] == 'Danbooru标签':
                    self.data_importer.import_danbooru_tags(path)
                
                QMessageBox.information(self, '导入成功', '数据导入成功')
                self.category_tree.refresh()
                
                if self.category_tree.getSelectedCategoryId():
                    self.prompt_list.setCategory(self.category_tree.getSelectedCategoryId())
                
                self.updateStatus()
            except Exception as e:
                QMessageBox.critical(self, '导入失败', str(e))
    
    def exportData(self):
        from PySide6.QtWidgets import QInputDialog
        formats = ['JSON', 'CSV (标准格式)', 'CSV (Danbooru格式)', 'CSV (Danbooru中文格式)']
        fmt, ok = QInputDialog.getItem(self, '选择导出格式', '格式:', formats, 0, False)
        if not ok:
            return
        
        if fmt == 'JSON':
            path, _ = QFileDialog.getSaveFileName(self, '导出为JSON', '', 'JSON Files (*.json)')
            if path:
                self.data_manager.export_to_json(path)
                QMessageBox.information(self, '导出成功', '数据导出成功')
        else:
            path, _ = QFileDialog.getSaveFileName(self, '导出为CSV', '', 'CSV Files (*.csv)')
            if path:
                if fmt == 'CSV (Danbooru格式)':
                    self.data_manager.export_to_csv(path, 'danbooru')
                elif fmt == 'CSV (Danbooru中文格式)':
                    self.data_manager.export_to_csv(path, 'danbooru_zh')
                else:
                    self.data_manager.export_to_csv(path, 'standard')
                QMessageBox.information(self, '导出成功', '数据导出成功')
    
    def generateRandom(self):
        dialog = RandomGeneratorDialog(self.data_manager)
        if dialog.exec():
            category_ids = dialog.getSelectedCategories()
            count = dialog.getGenerateCount()
            
            results = []
            for _ in range(count):
                prompts = self.random_generator.generate(category_ids)
                results.append(prompts)
            
            if results:
                prompt_texts = [p.english for p in results[0]]
                self.editor_panel.setText(', '.join(prompt_texts))
    
    def openBeginnerMode(self):
        dialog = BeginnerModeDialog(self.data_manager, self)
        dialog.promptGenerated.connect(self.onBeginnerPromptGenerated)
        dialog.exec()
    
    def onBeginnerPromptGenerated(self, prompt_text):
        current = self.editor_panel.getText()
        if current:
            current += ', ' + prompt_text
        else:
            current = prompt_text
        self.editor_panel.setText(current)
        self.status_bar.setStatus('新人模式生成完成')
    
    def showSettings(self):
        dialog = SettingsDialog(self.settings)
        if dialog.exec():
            new_settings = dialog.getSettings()
            self.data_manager.update_settings(**new_settings)
            self.settings = self.data_manager.get_settings()
            self.ollama_panel.updateSettings(self.settings)
            self.applyTheme()
    
    def applyTheme(self):
        if self.settings.theme == 'dark':
            self.setStyleSheet('''
                QMainWindow { background-color: #2b2b2b; }
                QWidget { color: #ffffff; }
                QTreeView { background-color: #333333; alternate-background-color: #3a3a3a; }
                QTableView { background-color: #333333; alternate-background-color: #3a3a3a; }
                QTextEdit { background-color: #333333; }
                QToolBar { background-color: #333333; }
                QStatusBar { background-color: #333333; }
                QLineEdit { background-color: #333333; }
                QComboBox { background-color: #333333; }
                QPushButton { background-color: #444444; border: 1px solid #555555; }
                QPushButton:hover { background-color: #555555; }
            ''')
        else:
            self.setStyleSheet('')
    
    def updateStatus(self):
        categories = self.data_manager.get_all_categories()
        prompt_count = 0
        
        if self.category_tree.getSelectedCategoryId():
            prompts = self.data_manager.get_prompts_by_category(self.category_tree.getSelectedCategoryId())
            prompt_count = len(prompts)
        else:
            session = Session()
            prompt_count = session.query(Prompt).count()
            session.close()
        
        self.status_bar.updateCounts(len(categories), prompt_count)
    
    def closeEvent(self, event):
        if self.settings.auto_backup:
            db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'prompt_db.sqlite')
            self.backup_manager.create_backup(db_path)
        
        self.data_manager.close()
        self.random_generator.close()
        self.data_importer.close()
        
        event.accept()

class App(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.window = MainWindow()
        self.window.show()
