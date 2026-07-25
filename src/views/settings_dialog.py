from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QComboBox, QCheckBox, QSpinBox, QDoubleSpinBox,
    QGroupBox, QFormLayout, QTabWidget, QWidget, QMessageBox, QProgressBar
)
from PySide6.QtCore import Qt, QThread, Signal
from controllers.ollama_client import OllamaClient

class TestConnectionThread(QThread):
    finished_signal = Signal(bool, str, list)

    def __init__(self, base_url):
        super().__init__()
        self.base_url = base_url

    def run(self):
        try:
            client = OllamaClient(self.base_url)
            success, message = client.test_connection()
            if success:
                models = client.list_models()
                model_names = [m.get('name', '') for m in models]
                self.finished_signal.emit(True, message, model_names)
            else:
                self.finished_signal.emit(False, message, [])
        except Exception as e:
            self.finished_signal.emit(False, str(e), [])

class SettingsDialog(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.setWindowTitle('设置')
        self.settings = settings
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.tab_widget = QTabWidget()

        appearance_tab = self.createAppearanceTab()
        save_tab = self.createSaveTab()
        output_tab = self.createOutputTab()
        ollama_tab = self.createOllamaTab()

        self.tab_widget.addTab(appearance_tab, '外观')
        self.tab_widget.addTab(save_tab, '保存')
        self.tab_widget.addTab(output_tab, '输出')
        self.tab_widget.addTab(ollama_tab, '本地 Ollama')

        layout.addWidget(self.tab_widget)

        button_layout = QHBoxLayout()
        self.btn_ok = QPushButton('确定')
        self.btn_ok.clicked.connect(self.accept)
        self.btn_cancel = QPushButton('取消')
        self.btn_cancel.clicked.connect(self.reject)

        button_layout.addWidget(self.btn_ok)
        button_layout.addWidget(self.btn_cancel)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def createAppearanceTab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        appearance_group = QGroupBox('外观设置')
        form_layout = QFormLayout()

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(['dark', 'light'])
        self.theme_combo.setCurrentText(self.settings.theme)

        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setValue(self.settings.font_size)

        self.language_combo = QComboBox()
        self.language_combo.addItems(['zh', 'en'])
        self.language_combo.setCurrentText(self.settings.language)

        form_layout.addRow('主题:', self.theme_combo)
        form_layout.addRow('字体大小:', self.font_size_spin)
        form_layout.addRow('语言:', self.language_combo)
        appearance_group.setLayout(form_layout)
        layout.addWidget(appearance_group)
        layout.addStretch()

        widget.setLayout(layout)
        return widget

    def createSaveTab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        save_group = QGroupBox('保存设置')
        form_layout = QFormLayout()

        self.auto_save_check = QCheckBox()
        self.auto_save_check.setChecked(self.settings.auto_save)

        self.auto_backup_check = QCheckBox()
        self.auto_backup_check.setChecked(self.settings.auto_backup)

        self.backup_interval_spin = QSpinBox()
        self.backup_interval_spin.setRange(1, 240)
        self.backup_interval_spin.setValue(self.settings.backup_interval)

        form_layout.addRow('自动保存:', self.auto_save_check)
        form_layout.addRow('自动备份:', self.auto_backup_check)
        form_layout.addRow('备份间隔(小时):', self.backup_interval_spin)
        save_group.setLayout(form_layout)
        layout.addWidget(save_group)
        layout.addStretch()

        widget.setLayout(layout)
        return widget

    def createOutputTab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        output_group = QGroupBox('输出设置')
        form_layout = QFormLayout()

        self.output_format_combo = QComboBox()
        self.output_format_combo.addItems(['english', 'chinese', 'both'])
        self.output_format_combo.setCurrentText(self.settings.default_output_format)

        self.show_mode_combo = QComboBox()
        self.show_mode_combo.addItems(['english', 'chinese', 'both'])
        self.show_mode_combo.setCurrentText(self.settings.show_mode)

        form_layout.addRow('默认输出格式:', self.output_format_combo)
        form_layout.addRow('显示模式:', self.show_mode_combo)
        output_group.setLayout(form_layout)
        layout.addWidget(output_group)
        layout.addStretch()

        widget.setLayout(layout)
        return widget

    def createOllamaTab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        config_group = QGroupBox('Ollama 服务配置')
        form_layout = QFormLayout()

        self.ollama_enabled_check = QCheckBox('启用本地 Ollama')
        self.ollama_enabled_check.setChecked(self.settings.ollama_enabled)

        self.ollama_url_edit = QLineEdit()
        self.ollama_url_edit.setText(self.settings.ollama_base_url)
        self.ollama_url_edit.setPlaceholderText('http://localhost:11434')

        self.test_conn_btn = QPushButton('测试连接')
        self.test_conn_btn.clicked.connect(self.testOllamaConnection)

        self.test_status_label = QLabel('')

        form_layout.addRow('', self.ollama_enabled_check)
        form_layout.addRow('服务地址:', self.ollama_url_edit)
        form_layout.addRow('', self.test_conn_btn)
        form_layout.addRow('状态:', self.test_status_label)
        config_group.setLayout(form_layout)
        layout.addWidget(config_group)

        model_group = QGroupBox('模型设置')
        model_layout = QFormLayout()

        self.model_combo = QComboBox()
        if self.settings.ollama_model:
            self.model_combo.addItem(self.settings.ollama_model)
            self.model_combo.setCurrentText(self.settings.ollama_model)

        self.refresh_models_btn = QPushButton('刷新模型列表')
        self.refresh_models_btn.clicked.connect(self.refreshModelList)

        model_layout.addRow('选择模型:', self.model_combo)
        model_layout.addRow('', self.refresh_models_btn)
        model_group.setLayout(model_layout)
        layout.addWidget(model_group)

        info_group = QGroupBox('说明')
        info_layout = QVBoxLayout()
        info_label = QLabel(
            '• 支持局域网内任意 Ollama 服务\n'
            '• 填写 IP 地址即可连接（如 http://192.168.1.100:11434）\n'
            '• 所有模型可通过 /api/tags 自动获取\n'
            '• 生成内容完全本地运行，不依赖外网'
        )
        info_label.setWordWrap(True)
        info_layout.addWidget(info_label)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def testOllamaConnection(self):
        base_url = self.ollama_url_edit.text().strip()
        if not base_url:
            QMessageBox.warning(self, '提示', '请先填写服务地址')
            return

        self.test_conn_btn.setEnabled(False)
        self.test_status_label.setText('正在连接...')

        self.test_thread = TestConnectionThread(base_url)
        self.test_thread.finished_signal.connect(self.onTestConnectionFinished)
        self.test_thread.start()

    def onTestConnectionFinished(self, success, message, models):
        self.test_conn_btn.setEnabled(True)

        if success:
            self.test_status_label.setText(message)
            self.test_status_label.setStyleSheet('color: #00aa00;')

            self.model_combo.clear()
            for model_name in models:
                self.model_combo.addItem(model_name)

            if self.settings.ollama_model and self.settings.ollama_model in models:
                self.model_combo.setCurrentText(self.settings.ollama_model)

            QMessageBox.information(self, '连接成功', message)
        else:
            self.test_status_label.setText('连接失败')
            self.test_status_label.setStyleSheet('color: #ff0000;')
            QMessageBox.critical(self, '连接失败', message)

    def refreshModelList(self):
        base_url = self.ollama_url_edit.text().strip()
        if not base_url:
            QMessageBox.warning(self, '提示', '请先填写服务地址')
            return

        try:
            client = OllamaClient(base_url)
            models = client.list_models()

            self.model_combo.clear()
            for model in models:
                self.model_combo.addItem(model.get('name', ''))

            if self.settings.ollama_model:
                index = self.model_combo.findText(self.settings.ollama_model)
                if index >= 0:
                    self.model_combo.setCurrentIndex(index)

            QMessageBox.information(self, '刷新成功', f'已获取 {len(models)} 个模型')
        except Exception as e:
            QMessageBox.critical(self, '刷新失败', str(e))

    def getSettings(self):
        return {
            'theme': self.theme_combo.currentText(),
            'font_size': self.font_size_spin.value(),
            'language': self.language_combo.currentText(),
            'auto_save': self.auto_save_check.isChecked(),
            'auto_backup': self.auto_backup_check.isChecked(),
            'backup_interval': self.backup_interval_spin.value(),
            'default_output_format': self.output_format_combo.currentText(),
            'show_mode': self.show_mode_combo.currentText(),
            'ollama_enabled': self.ollama_enabled_check.isChecked(),
            'ollama_base_url': self.ollama_url_edit.text().strip(),
            'ollama_model': self.model_combo.currentText()
        }
