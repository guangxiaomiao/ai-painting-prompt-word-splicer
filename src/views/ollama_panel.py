from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit,
    QComboBox, QLabel, QGroupBox, QSplitter, QCheckBox, QSpinBox,
    QLineEdit, QDialog, QDialogButtonBox, QListWidget, QListWidgetItem,
    QInputDialog
)
from PySide6.QtCore import Qt, QThread, Signal
from controllers.ollama_client import OllamaClient
import time

ARCHITECTURES = {
    '标准9段架构 (推荐)': [
        {'name': '画质前缀', 'key': 'quality', 'enabled': True, 'example': 'masterpiece, best quality, highres'},
        {'name': 'LoRA', 'key': 'lora', 'enabled': True, 'example': '<lora:xxx:1>'},
        {'name': '主体角色', 'key': 'character', 'enabled': True, 'example': '1girl, solo'},
        {'name': '外貌细节', 'key': 'appearance', 'enabled': True, 'example': 'long hair, blue eyes'},
        {'name': '场景', 'key': 'scene', 'enabled': True, 'example': 'forest, nature'},
        {'name': '动作/姿势', 'key': 'action', 'enabled': True, 'example': 'standing, looking at viewer'},
        {'name': '性行为细节', 'key': 'sexual', 'enabled': False, 'example': 'sex, vaginal'},
        {'name': '表情/R18', 'key': 'expression', 'enabled': False, 'example': 'ahegao, blush'},
        {'name': '权重加强', 'key': 'weight', 'enabled': True, 'example': '(word:1.2)'},
    ],
    '基础画质+角色': [
        {'name': '画质前缀', 'key': 'quality', 'enabled': True, 'example': 'masterpiece, best quality'},
        {'name': '主体角色', 'key': 'character', 'enabled': True, 'example': '1girl, solo'},
        {'name': '外貌细节', 'key': 'appearance', 'enabled': True, 'example': 'long hair, blue eyes'},
        {'name': '场景', 'key': 'scene', 'enabled': True, 'example': 'simple background'},
    ],
    'R18专用架构': [
        {'name': '画质前缀', 'key': 'quality', 'enabled': True, 'example': 'masterpiece, best quality'},
        {'name': 'LoRA', 'key': 'lora', 'enabled': True, 'example': '<lora:xxx:1>'},
        {'name': '主体角色', 'key': 'character', 'enabled': True, 'example': '1girl, solo'},
        {'name': '外貌细节', 'key': 'appearance', 'enabled': True, 'example': 'long hair, blue eyes, nude'},
        {'name': '场景', 'key': 'scene', 'enabled': True, 'example': 'bedroom, on bed'},
        {'name': '动作/姿势', 'key': 'action', 'enabled': True, 'example': 'spread legs, missionary'},
        {'name': '性行为细节', 'key': 'sexual', 'enabled': True, 'example': 'sex, vaginal, penetration'},
        {'name': '表情/R18', 'key': 'expression', 'enabled': True, 'example': 'ahegao, blush, orgasm'},
        {'name': '权重加强', 'key': 'weight', 'enabled': True, 'example': '(word:1.3)'},
    ],
    '极简架构': [
        {'name': '画质前缀', 'key': 'quality', 'enabled': True, 'example': 'masterpiece, best quality'},
        {'name': '主体角色', 'key': 'character', 'enabled': True, 'example': '1girl, solo'},
    ],
}

class OllamaGenerateThread(QThread):
    output_signal = Signal(str)
    progress_signal = Signal(str, int, int)
    finished_signal = Signal(list)
    error_signal = Signal(str)

    def __init__(self, base_url, model, prompts, system_prompt, stream=False, timeout=120, batch_interval=10):
        super().__init__()
        self.base_url = base_url
        self.model = model
        self.prompts = prompts if isinstance(prompts, list) else [prompts]
        self.system_prompt = system_prompt
        self.stream = stream
        self.timeout = timeout
        self.batch_interval = batch_interval
        self._is_running = True

    def run(self):
        try:
            client = OllamaClient(self.base_url, timeout=self.timeout)
            results = []
            total = len(self.prompts)
            
            for i, prompt in enumerate(self.prompts):
                if not self._is_running:
                    break
                    
                try:
                    if self.stream:
                        full_result = ''
                        def on_stream(content):
                            nonlocal full_result
                            full_result += content
                            self.output_signal.emit(content)
                        result = client.generate(
                            model=self.model,
                            prompt=prompt,
                            system=self.system_prompt if self.system_prompt else None,
                            stream=True,
                            callback=on_stream
                        )
                    else:
                        result = client.generate(
                            model=self.model,
                            prompt=prompt,
                            system=self.system_prompt if self.system_prompt else None,
                            stream=False
                        )
                        self.output_signal.emit(result)
                    
                    results.append(result)
                    self.progress_signal.emit(result, i + 1, total)
                    
                except Exception as e:
                    error_msg = f'[批次{i+1}错误] {str(e)}'
                    results.append(error_msg)
                    self.progress_signal.emit(error_msg, i + 1, total)
                
                if i < total - 1 and self.batch_interval > 0:
                    time.sleep(self.batch_interval)
            
            self.finished_signal.emit(results)
            
        except Exception as e:
            self.error_signal.emit(str(e))

    def stop(self):
        self._is_running = False

class ArchitectureEditDialog(QDialog):
    def __init__(self, arch_name, segments, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f'编辑架构 - {arch_name}')
        self.resize(500, 400)
        self.segments = [s.copy() for s in segments]
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        
        info_label = QLabel('调整各段顺序和启用状态：')
        layout.addWidget(info_label)
        
        self.list_widget = QListWidget()
        for seg in self.segments:
            item = QListWidgetItem(f'{"[x]" if seg["enabled"] else "[ ]"} {seg["name"]}')
            item.setData(Qt.UserRole, seg)
            self.list_widget.addItem(item)
        layout.addWidget(self.list_widget, 1)
        
        btn_layout = QHBoxLayout()
        up_btn = QPushButton('上移')
        up_btn.clicked.connect(self.moveUp)
        down_btn = QPushButton('下移')
        down_btn.clicked.connect(self.moveDown)
        toggle_btn = QPushButton('启用/禁用')
        toggle_btn.clicked.connect(self.toggleSegment)
        btn_layout.addWidget(up_btn)
        btn_layout.addWidget(down_btn)
        btn_layout.addWidget(toggle_btn)
        layout.addLayout(btn_layout)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def moveUp(self):
        row = self.list_widget.currentRow()
        if row > 0:
            item = self.list_widget.takeItem(row)
            self.list_widget.insertItem(row - 1, item)
            self.list_widget.setCurrentRow(row - 1)
    
    def moveDown(self):
        row = self.list_widget.currentRow()
        if row < self.list_widget.count() - 1:
            item = self.list_widget.takeItem(row)
            self.list_widget.insertItem(row + 1, item)
            self.list_widget.setCurrentRow(row + 1)
    
    def toggleSegment(self):
        row = self.list_widget.currentRow()
        if row >= 0:
            item = self.list_widget.item(row)
            seg = item.data(Qt.UserRole)
            seg['enabled'] = not seg['enabled']
            item.setText(f'{"[x]" if seg["enabled"] else "[ ]"} {seg["name"]}')
    
    def getSegments(self):
        result = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            seg = item.data(Qt.UserRole)
            result.append(seg)
        return result

class OllamaAIPanel(QWidget):
    def __init__(self, settings, data_manager=None, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.data_manager = data_manager
        self.is_generating = False
        self.current_architecture = '标准9段架构 (推荐)'
        self.custom_architectures = {}
        self.editor_text_getter = None
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        top_group = QGroupBox('AI 提示词助手 (SD 1.5 优化版)')
        top_layout = QVBoxLayout()

        arch_layout = QHBoxLayout()
        arch_layout.addWidget(QLabel('架构:'))
        self.arch_combo = QComboBox()
        self.arch_combo.addItems(list(ARCHITECTURES.keys()))
        self.arch_combo.currentTextChanged.connect(self.onArchitectureChanged)
        arch_layout.addWidget(self.arch_combo, 1)
        self.edit_arch_btn = QPushButton('编辑')
        self.edit_arch_btn.clicked.connect(self.editArchitecture)
        arch_layout.addWidget(self.edit_arch_btn)
        top_layout.addLayout(arch_layout)

        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel('功能:'))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems([
            '生成提示词',
            '优化提示词',
            '扩写提示词',
            '翻译成英文',
            '翻译成中文',
            '修复编辑器词条(文件提交)',
            '自定义'
        ])
        mode_layout.addWidget(self.mode_combo, 1)
        top_layout.addLayout(mode_layout)

        ctx_layout = QHBoxLayout()
        self.use_context_cb = QCheckBox('使用词库上下文')
        self.use_context_cb.setChecked(True)
        ctx_layout.addWidget(self.use_context_cb)
        ctx_layout.addWidget(QLabel('数量:'))
        self.context_count_spin = QSpinBox()
        self.context_count_spin.setRange(10, 50)
        self.context_count_spin.setValue(40)
        self.context_count_spin.setMaximumWidth(70)
        ctx_layout.addWidget(self.context_count_spin)
        ctx_layout.addWidget(QLabel('超时:'))
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(60, 300)
        self.timeout_spin.setValue(120)
        self.timeout_spin.setMaximumWidth(70)
        self.timeout_spin.setSuffix('秒')
        ctx_layout.addWidget(self.timeout_spin)
        ctx_layout.addStretch()
        top_layout.addLayout(ctx_layout)

        stream_layout = QHBoxLayout()
        self.use_stream_cb = QCheckBox('流式输出')
        self.use_stream_cb.setChecked(False)
        stream_layout.addWidget(self.use_stream_cb)
        stream_layout.addWidget(QLabel('批次间隔:'))
        self.batch_interval_spin = QSpinBox()
        self.batch_interval_spin.setRange(5, 60)
        self.batch_interval_spin.setValue(10)
        self.batch_interval_spin.setMaximumWidth(70)
        self.batch_interval_spin.setSuffix('秒')
        stream_layout.addWidget(self.batch_interval_spin)
        stream_layout.addStretch()
        top_layout.addLayout(stream_layout)

        input_group = QGroupBox('输入（每行一个需求，将自动分批处理）')
        input_layout = QVBoxLayout()
        self.input_edit = QTextEdit()
        self.input_edit.setPlaceholderText('请输入要处理的内容...（支持多行，每行一个需求）')
        self.input_edit.setMinimumHeight(100)
        input_layout.addWidget(self.input_edit)
        input_group.setLayout(input_layout)
        top_layout.addWidget(input_group)

        btn_layout = QHBoxLayout()
        self.generate_btn = QPushButton('生成')
        self.generate_btn.clicked.connect(self.generate)
        self.stop_btn = QPushButton('停止')
        self.stop_btn.clicked.connect(self.stopGenerate)
        self.stop_btn.setEnabled(False)
        self.pause_btn = QPushButton('暂停')
        self.pause_btn.clicked.connect(self.pauseGenerate)
        self.pause_btn.setEnabled(False)
        btn_layout.addWidget(self.generate_btn)
        btn_layout.addWidget(self.stop_btn)
        btn_layout.addWidget(self.pause_btn)
        top_layout.addLayout(btn_layout)

        self.status_label = QLabel('就绪')
        self.status_label.setStyleSheet('color: #666; font-size: 12px;')
        top_layout.addWidget(self.status_label)

        top_group.setLayout(top_layout)
        layout.addWidget(top_group)

        output_group = QGroupBox('输出')
        output_layout = QVBoxLayout()
        self.output_edit = QTextEdit()
        self.output_edit.setReadOnly(True)
        self.output_edit.setMinimumHeight(150)
        output_layout.addWidget(self.output_edit)

        output_btn_layout = QHBoxLayout()
        self.copy_btn = QPushButton('复制结果')
        self.copy_btn.clicked.connect(self.copyResult)
        self.append_btn = QPushButton('添加到编辑器')
        self.append_btn.clicked.connect(self.appendToEditor)
        self.clear_btn = QPushButton('清空')
        self.clear_btn.clicked.connect(self.clearOutput)
        output_btn_layout.addWidget(self.copy_btn)
        output_btn_layout.addWidget(self.append_btn)
        output_btn_layout.addWidget(self.clear_btn)
        output_layout.addLayout(output_btn_layout)

        output_group.setLayout(output_layout)
        layout.addWidget(output_group, 1)

        self.setLayout(layout)
        self.setMinimumWidth(350)
    
    def getCurrentArchitecture(self):
        if self.current_architecture in self.custom_architectures:
            return self.custom_architectures[self.current_architecture]
        return ARCHITECTURES.get(self.current_architecture, ARCHITECTURES['标准9段架构 (推荐)'])
    
    def onArchitectureChanged(self, name):
        self.current_architecture = name
        arch = self.getCurrentArchitecture()
        seg_names = ' → '.join([s['name'] for s in arch if s['enabled']])
        self.status_label.setText(f'当前架构: {seg_names}')
    
    def editArchitecture(self):
        arch = self.getCurrentArchitecture()
        dialog = ArchitectureEditDialog(self.current_architecture, arch, self)
        if dialog.exec() == QDialog.Accepted:
            new_segments = dialog.getSegments()
            if self.current_architecture in ARCHITECTURES:
                custom_name = f'自定义-{self.current_architecture}'
                self.custom_architectures[custom_name] = new_segments
                if self.arch_combo.findText(custom_name) == -1:
                    self.arch_combo.addItem(custom_name)
                self.arch_combo.setCurrentText(custom_name)
                self.current_architecture = custom_name
            else:
                self.custom_architectures[self.current_architecture] = new_segments
            seg_names = ' → '.join([s['name'] for s in new_segments if s['enabled']])
            self.status_label.setText(f'架构已更新: {seg_names}')

    def getSystemPrompt(self):
        mode = self.mode_combo.currentText()
        arch = self.getCurrentArchitecture()
        enabled_segs = [s for s in arch if s['enabled']]
        seg_desc = '\n'.join([f'  {i+1}. {s["name"]}：{s.get("example", "")}' for i, s in enumerate(enabled_segs)])
        seg_order = ' + '.join([s['name'] for s in enabled_segs])
        
        base_prompts = {
            '生成提示词': f'''你是一个专业的 Stable Diffusion 1.5 提示词生成专家。
请根据用户的描述，严格按照以下架构顺序生成 SD 1.5 格式的高质量提示词。

【提示词架构顺序】
{seg_order}

【各段说明】
{seg_desc}

SD 1.5 提示词格式要求：
1. 全部使用英文单词/短语，用逗号分隔
2. 严格按照上面的架构顺序排列，不要打乱顺序
3. 权重格式：(单词:权重)，例如 (masterpiece:1.2), (blue eyes:1.1)
4. 权重范围 0.0~2.0，默认 1.0 时不加括号
5. 只输出提示词本身，不要解释、不要编号、不要换行
6. 各段之间自然过渡，用逗号连接

输出示例：
masterpiece, best quality, highres, <lora:example:1>, 1girl, solo, long hair, blue eyes, fox ears, forest background, sunlight, standing, looking at viewer, (smile:1.2)''',
            '优化提示词': f'''你是一个专业的 Stable Diffusion 1.5 提示词优化专家。
请优化用户提供的提示词，使其更符合 SD 1.5 的最佳实践，并严格按照以下架构重新组织。

【提示词架构顺序】
{seg_order}

【各段说明】
{seg_desc}

优化要求：
1. 保持英文，用逗号分隔
2. 增加画质前缀（masterpiece, best quality 等）
3. 严格按照架构顺序重新组织所有词条
4. 补充各段缺失的细节
5. 重要的词加权重，格式：(单词:1.2)
6. 去掉冗余和重复的词
7. 只输出优化后的提示词，不要解释''',
            '扩写提示词': f'''你是一个专业的 Stable Diffusion 1.5 提示词扩写助手。
请扩写用户提供的简短提示词，增加丰富的细节，并严格按照以下架构组织。

【提示词架构顺序】
{seg_order}

【各段说明】
{seg_desc}

扩写要求：
1. 保持英文，用逗号分隔
2. 增加画质词：masterpiece, best quality
3. 为每个架构段补充合适的细节
4. 严格按照架构顺序排列
5. 只输出扩写后的提示词，不要解释''',
            '翻译成英文': '''请将用户输入的中文翻译成 Stable Diffusion 1.5 风格的英文提示词。

翻译要求：
1. 使用 SD 常用的英文绘画术语
2. 用逗号分隔
3. 按重要性排序
4. 只输出英文翻译结果，不要解释''',
            '翻译成中文': '''请将用户输入的 Stable Diffusion 1.5 英文提示词翻译成中文。

翻译要求：
1. 准确翻译每个词汇
2. 保持逗号分隔格式
3. 只输出中文翻译结果，不要解释''',
            '修复编辑器词条(文件提交)': f'''你是一个专业的 Stable Diffusion 1.5 提示词架构修复专家。
用户已从编辑器中将所有已加入的词条通过文件方式提交给你，你的任务是将这些词条严格按照以下架构重新组织修复。

【提示词架构顺序】
{seg_order}

【各段说明】
{seg_desc}

【修复规则】
1. 仔细分析用户提交的文件中的所有词条
2. 将每个词条归入最合适的架构段
3. 严格按照上述架构顺序重新排列所有词条
4. 去除重复词条
5. 保留原始词条内容，不要随意修改英文单词
6. 权重格式：(单词:权重)，默认 1.0 不加括号
7. 各段之间用逗号连接
8. 只输出修复后的完整提示词，不要解释、不要编号、不要换行
9. 如果某段没有对应词条，可以省略该段

【输出格式】
画质词, LoRA, 主体角色, 外貌细节, 场景, 动作姿势, (可选)性行为, (可选)表情, 权重加强''',
            '自定义': ''
        }
        return base_prompts.get(mode, '')
    
    def getContextPrompt(self):
        if not self.use_context_cb.isChecked() or not self.data_manager:
            return ''
        
        try:
            count = self.context_count_spin.value()
            context = self.data_manager.get_prompt_context_for_ai(limit=count)
            if context:
                arch = self.getCurrentArchitecture()
                seg_names = [s['name'] for s in arch if s['enabled']]
                return f'''\n\n以下是用户词库中的参考词条，生成时请优先参考这些词条的风格，尽量从词库中选择合适的词：
--- 词库参考 ---
{context}
--- 参考结束 ---
请基于以上词库参考和架构({', '.join(seg_names)})生成提示词。只输出英文绘画tag，禁止多余描述、换行、注释。'''
        except Exception:
            pass
        return ''

    def generate(self):
        if not self.settings.ollama_enabled:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, '提示', '请先在设置中启用本地 Ollama')
            return

        if not self.settings.ollama_model:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, '提示', '请先在设置中选择模型')
            return

        mode = self.mode_combo.currentText()

        if mode == '修复编辑器词条(文件提交)':
            self._generateFromFileSubmission()
            return

        input_text = self.input_edit.toPlainText().strip()
        if not input_text:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, '提示', '请输入内容')
            return

        prompts = [p.strip() for p in input_text.split('\n') if p.strip()]
        if not prompts:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, '提示', '请输入有效内容')
            return

        self.is_generating = True
        self.is_paused = False
        self.generate_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.pause_btn.setEnabled(True)
        self.output_edit.clear()

        system_prompt = self.getSystemPrompt()
        context_prompt = self.getContextPrompt()
        full_system_prompt = system_prompt + context_prompt if context_prompt else system_prompt

        timeout = self.timeout_spin.value()
        use_stream = self.use_stream_cb.isChecked()
        batch_interval = self.batch_interval_spin.value()

        self.status_label.setText(f'处理中... (0/{len(prompts)})')
        self.status_label.setStyleSheet('color: #009900; font-size: 12px;')

        self.generate_thread = OllamaGenerateThread(
            base_url=self.settings.ollama_base_url,
            model=self.settings.ollama_model,
            prompts=prompts,
            system_prompt=full_system_prompt,
            stream=use_stream,
            timeout=timeout,
            batch_interval=batch_interval
        )
        self.generate_thread.output_signal.connect(self.onStreamOutput)
        self.generate_thread.progress_signal.connect(self.onProgress)
        self.generate_thread.finished_signal.connect(self.onGenerateFinished)
        self.generate_thread.error_signal.connect(self.onGenerateError)
        self.generate_thread.start()

    def _generateFromFileSubmission(self):
        """文件提交模式：将编辑器中的词条写入临时文件，再提交给 AI 进行架构修复"""
        from PySide6.QtWidgets import QMessageBox, QFileDialog
        import os
        import tempfile
        import json

        editor_text = ''
        if hasattr(self, 'editor_text_getter') and self.editor_text_getter:
            try:
                editor_text = self.editor_text_getter() or ''
            except Exception:
                pass

        if not editor_text:
            if not self.input_edit.toPlainText().strip():
                QMessageBox.warning(
                    self, '提示',
                    '编辑器中没有词条，且输入框也为空。\n请先在编辑器中添加词条，或在输入框中粘贴词条。'
                )
                return
            editor_text = self.input_edit.toPlainText().strip()

        words = [w.strip() for w in editor_text.replace('\n', ',').split(',') if w.strip()]
        if not words:
            QMessageBox.warning(self, '提示', '未解析到任何词条')
            return

        temp_dir = os.path.join(tempfile.gettempdir(), 'prompt_generator')
        os.makedirs(temp_dir, exist_ok=True)
        temp_file = os.path.join(temp_dir, 'editor_prompts_submit.json')

        try:
            file_data = {
                'source': 'editor',
                'total_count': len(words),
                'architecture': self.current_architecture,
                'segments': [s['name'] for s in self.getCurrentArchitecture() if s['enabled']],
                'prompts': words,
                'submitted_at': __import__('datetime').datetime.now().isoformat()
            }
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(file_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            QMessageBox.critical(self, '错误', f'写入临时文件失败: {str(e)}')
            return

        try:
            with open(temp_file, 'r', encoding='utf-8') as f:
                file_content = f.read()
        except Exception as e:
            QMessageBox.critical(self, '错误', f'读取临时文件失败: {str(e)}')
            return

        prompt_text = f'''以下是用户从编辑器提交的词条文件内容（JSON格式），包含 {len(words)} 个词条。
请仔细阅读文件内容，将这些词条严格按照当前架构重新组织修复。

【提交的文件内容】
{file_content}

【任务】
1. 解析文件中的 prompts 字段，获取所有词条
2. 按 "{self.current_architecture}" 架构顺序重新组织这些词条
3. 去除重复词条
4. 只输出修复后的英文提示词，用逗号分隔，不要解释，不要换行'''

        self.is_generating = True
        self.is_paused = False
        self.generate_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.pause_btn.setEnabled(True)
        self.output_edit.clear()
        self.output_edit.insertPlainText(f'[文件提交模式] 已将 {len(words)} 个词条写入临时文件:\n{temp_file}\n正在提交给 AI 进行架构修复...\n\n')

        system_prompt = self.getSystemPrompt()
        timeout = self.timeout_spin.value()
        use_stream = self.use_stream_cb.isChecked()
        batch_interval = self.batch_interval_spin.value()

        self.status_label.setText(f'文件提交处理中... ({len(words)} 条词条)')
        self.status_label.setStyleSheet('color: #009900; font-size: 12px;')

        self.generate_thread = OllamaGenerateThread(
            base_url=self.settings.ollama_base_url,
            model=self.settings.ollama_model,
            prompts=[prompt_text],
            system_prompt=system_prompt,
            stream=use_stream,
            timeout=timeout,
            batch_interval=batch_interval
        )
        self.generate_thread.output_signal.connect(self.onStreamOutput)
        self.generate_thread.progress_signal.connect(self.onProgress)
        self.generate_thread.finished_signal.connect(self.onGenerateFinished)
        self.generate_thread.error_signal.connect(self.onGenerateError)
        self.generate_thread.start()

    def onStreamOutput(self, content):
        self.output_edit.insertPlainText(content)

    def onProgress(self, result, current, total):
        self.status_label.setText(f'处理中... ({current}/{total})')
        self.output_edit.insertPlainText('\n--- 分割线 ---\n')

    def onGenerateFinished(self, results):
        self.is_generating = False
        self.generate_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.pause_btn.setEnabled(False)
        self.status_label.setText(f'完成 (共{len(results)}条)')
        self.status_label.setStyleSheet('color: #009900; font-size: 12px;')
        self.output_edit.insertPlainText('\n========== 全部完成 ==========\n')

    def onGenerateError(self, error):
        self.is_generating = False
        self.generate_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.pause_btn.setEnabled(False)
        self.status_label.setText('发生错误')
        self.status_label.setStyleSheet('color: #FF0000; font-size: 12px;')
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.critical(self, '生成失败', error)

    def stopGenerate(self):
        if self.generate_thread and self.generate_thread.isRunning():
            self.generate_thread.stop()
            self.generate_thread.terminate()
            self.is_generating = False
            self.generate_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.pause_btn.setEnabled(False)
            self.status_label.setText('已停止')
            self.status_label.setStyleSheet('color: #FF6600; font-size: 12px;')
            self.output_edit.insertPlainText('\n========== 已停止 ==========\n')

    def pauseGenerate(self):
        if hasattr(self, 'is_paused'):
            if self.is_paused:
                self.is_paused = False
                self.pause_btn.setText('暂停')
                self.status_label.setText('继续处理...')
            else:
                self.is_paused = True
                self.pause_btn.setText('继续')
                self.status_label.setText('已暂停，等待30秒...')
                time.sleep(30)
                if hasattr(self, 'is_paused') and self.is_paused:
                    self.is_paused = False
                    self.pause_btn.setText('暂停')
                    self.status_label.setText('继续处理...')

    def copyResult(self):
        text = self.output_edit.toPlainText()
        if text:
            from PySide6.QtWidgets import QApplication
            QApplication.clipboard().setText(text)

    def appendToEditor(self):
        text = self.output_edit.toPlainText()
        if text:
            if hasattr(self, 'editor_callback') and self.editor_callback:
                self.editor_callback(text)

    def clearOutput(self):
        self.output_edit.clear()
        self.status_label.setText('就绪')
        self.status_label.setStyleSheet('color: #666; font-size: 12px;')

    def setEditorCallback(self, callback):
        self.editor_callback = callback

    def setEditorTextGetter(self, getter):
        self.editor_text_getter = getter

    def updateSettings(self, settings):
        self.settings = settings
