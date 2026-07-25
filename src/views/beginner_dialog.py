from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QComboBox,
    QListWidget, QListWidgetItem, QSplitter, QWidget, QGroupBox,
    QMessageBox, QLineEdit, QCheckBox, QProgressBar, QTextEdit
)
from PySide6.QtCore import Qt, Signal
from models import Session, Category, Prompt


ARCHITECTURE_SEGMENT_CATEGORY_MAP = {
    '画质前缀': ['画质', '画风', '艺术家'],
    'LoRA': ['Lora', 'LoRA', 'lora'],
    '主体角色': ['人物'],
    '外貌细节': ['发型', '服装', '眼睛', '外貌', '装饰'],
    '场景': ['背景', '天气', '场景'],
    '动作/姿势': ['动作', '姿势'],
    '性行为细节': ['NSFW', 'nsfw'],
    '表情/R18': ['NSFW', 'nsfw', '表情'],
    '权重加强': [],
}


BEGINNER_ARCHITECTURES = {
    '标准9段架构 (推荐)': [
        {'name': '画质前缀', 'enabled': True, 'example': 'masterpiece, best quality, highres'},
        {'name': 'LoRA', 'enabled': True, 'example': '<lora:xxx:1>'},
        {'name': '主体角色', 'enabled': True, 'example': '1girl, solo'},
        {'name': '外貌细节', 'enabled': True, 'example': 'long hair, blue eyes'},
        {'name': '场景', 'enabled': True, 'example': 'forest, nature'},
        {'name': '动作/姿势', 'enabled': True, 'example': 'standing, looking at viewer'},
        {'name': '性行为细节', 'enabled': False, 'example': 'sex, vaginal'},
        {'name': '表情/R18', 'enabled': False, 'example': 'ahegao, blush'},
        {'name': '权重加强', 'enabled': True, 'example': '(word:1.2)'},
    ],
    '基础画质+角色': [
        {'name': '画质前缀', 'enabled': True, 'example': 'masterpiece, best quality'},
        {'name': '主体角色', 'enabled': True, 'example': '1girl, solo'},
        {'name': '外貌细节', 'enabled': True, 'example': 'long hair, blue eyes'},
        {'name': '场景', 'enabled': True, 'example': 'simple background'},
    ],
    'R18专用架构': [
        {'name': '画质前缀', 'enabled': True, 'example': 'masterpiece, best quality'},
        {'name': 'LoRA', 'enabled': True, 'example': '<lora:xxx:1>'},
        {'name': '主体角色', 'enabled': True, 'example': '1girl, solo'},
        {'name': '外貌细节', 'enabled': True, 'example': 'long hair, blue eyes, nude'},
        {'name': '场景', 'enabled': True, 'example': 'bedroom, on bed'},
        {'name': '动作/姿势', 'enabled': True, 'example': 'spread legs, missionary'},
        {'name': '性行为细节', 'enabled': True, 'example': 'sex, vaginal, penetration'},
        {'name': '表情/R18', 'enabled': True, 'example': 'ahegao, blush, orgasm'},
        {'name': '权重加强', 'enabled': True, 'example': '(word:1.3)'},
    ],
    '极简架构': [
        {'name': '画质前缀', 'enabled': True, 'example': 'masterpiece, best quality'},
        {'name': '主体角色', 'enabled': True, 'example': '1girl, solo'},
    ],
}


class PromptListItemWidget(QWidget):
    def __init__(self, english, chinese, category_name, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(0)

        en_label = QLabel(english)
        en_label.setStyleSheet('font-weight: bold; color: #0066cc;')
        layout.addWidget(en_label)

        cn_text = chinese if chinese else '无翻译'
        if category_name:
            cn_text = f'{cn_text}  [{category_name}]'
        cn_label = QLabel(cn_text)
        cn_label.setStyleSheet('color: #666; font-size: 11px;')
        layout.addWidget(cn_label)

        self.setLayout(layout)


class BeginnerModeDialog(QDialog):
    promptGenerated = Signal(str)

    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.setWindowTitle('新人模式 - 引导式提示词生成')
        self.resize(1000, 650)
        self.current_arch_name = '标准9段架构 (推荐)'
        self.segments = []
        self.current_segment_index = 0
        self.selected_prompts = {}
        self.all_categories = []
        self.initUI()
        self.loadArchitectures()
        self.loadCategories()
        self.refreshSegmentView()

    def initUI(self):
        layout = QVBoxLayout()

        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel('选择架构:'))
        self.arch_combo = QComboBox()
        self.arch_combo.currentTextChanged.connect(self.onArchitectureChanged)
        top_layout.addWidget(self.arch_combo, 1)
        self.new_arch_btn = QPushButton('新建自定义架构')
        self.new_arch_btn.clicked.connect(self.createCustomArchitecture)
        top_layout.addWidget(self.new_arch_btn)
        layout.addLayout(top_layout)

        self.progress_bar = QProgressBar()
        self.progress_bar.setFormat('第 %v / %m 段')
        layout.addWidget(self.progress_bar)

        info_layout = QHBoxLayout()
        self.segment_label = QLabel('当前段: -')
        self.segment_label.setStyleSheet('font-size: 14px; font-weight: bold; color: #0066cc;')
        info_layout.addWidget(self.segment_label)
        info_layout.addStretch()
        self.example_label = QLabel('示例: -')
        self.example_label.setStyleSheet('color: #888; font-style: italic;')
        info_layout.addWidget(self.example_label)
        layout.addLayout(info_layout)

        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel('分类筛选:'))
        self.category_filter = QComboBox()
        self.category_filter.addItem('推荐分类 (自动)', None)
        self.category_filter.currentIndexChanged.connect(self.refreshPromptList)
        filter_layout.addWidget(self.category_filter, 1)
        filter_layout.addWidget(QLabel('搜索:'))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText('搜索词条...')
        self.search_edit.textChanged.connect(self.refreshPromptList)
        filter_layout.addWidget(self.search_edit, 1)
        layout.addLayout(filter_layout)

        splitter = QSplitter(Qt.Horizontal)

        prompt_group = QGroupBox('可选词条 (双击或点击"添加"加入)')
        prompt_layout = QVBoxLayout()
        self.prompt_list = QListWidget()
        self.prompt_list.itemDoubleClicked.connect(self.addSelectedPrompt)
        prompt_layout.addWidget(self.prompt_list)
        prompt_btn_layout = QHBoxLayout()
        self.add_btn = QPushButton('→ 添加')
        self.add_btn.clicked.connect(self.addSelectedPrompt)
        prompt_btn_layout.addWidget(self.add_btn)
        self.add_random_btn = QPushButton('随机一条')
        self.add_random_btn.clicked.connect(self.addRandomPrompt)
        prompt_btn_layout.addWidget(self.add_random_btn)
        prompt_layout.addLayout(prompt_btn_layout)
        prompt_group.setLayout(prompt_layout)
        splitter.addWidget(prompt_group)

        selected_group = QGroupBox('当前段已选词条')
        selected_layout = QVBoxLayout()
        self.selected_list = QListWidget()
        self.selected_list.itemDoubleClicked.connect(self.removeSelectedPrompt)
        selected_layout.addWidget(self.selected_list)
        sel_btn_layout = QHBoxLayout()
        self.remove_btn = QPushButton('← 移除')
        self.remove_btn.clicked.connect(self.removeSelectedPrompt)
        sel_btn_layout.addWidget(self.remove_btn)
        self.clear_segment_btn = QPushButton('清空当前段')
        self.clear_segment_btn.clicked.connect(self.clearCurrentSegment)
        sel_btn_layout.addWidget(self.clear_segment_btn)
        selected_layout.addLayout(sel_btn_layout)
        selected_group.setLayout(selected_layout)
        splitter.addWidget(selected_group)

        preview_group = QGroupBox('最终提示词预览 (所有段按架构顺序拼接)')
        preview_layout = QVBoxLayout()
        self.preview_edit = QTextEdit()
        self.preview_edit.setReadOnly(True)
        preview_layout.addWidget(self.preview_edit)
        preview_group.setLayout(preview_layout)
        splitter.addWidget(preview_group)

        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)
        splitter.setStretchFactor(2, 2)
        layout.addWidget(splitter, 1)

        nav_layout = QHBoxLayout()
        self.prev_btn = QPushButton('◀ 上一段')
        self.prev_btn.clicked.connect(self.prevSegment)
        nav_layout.addWidget(self.prev_btn)
        self.next_btn = QPushButton('下一段 ▶')
        self.next_btn.clicked.connect(self.nextSegment)
        nav_layout.addWidget(self.next_btn)
        self.skip_btn = QPushButton('跳过此段')
        self.skip_btn.clicked.connect(self.skipSegment)
        nav_layout.addWidget(self.skip_btn)
        nav_layout.addStretch()
        self.finish_btn = QPushButton('完成并生成')
        self.finish_btn.setStyleSheet('background-color: #4CAF50; color: white; font-weight: bold; padding: 6px 20px;')
        self.finish_btn.clicked.connect(self.finishAndGenerate)
        nav_layout.addWidget(self.finish_btn)
        self.cancel_btn = QPushButton('取消')
        self.cancel_btn.clicked.connect(self.reject)
        nav_layout.addWidget(self.cancel_btn)
        layout.addLayout(nav_layout)

        self.setLayout(layout)

    def loadArchitectures(self):
        self.arch_combo.clear()
        self.arch_combo.addItems(list(BEGINNER_ARCHITECTURES.keys()))
        self.onArchitectureChanged(self.arch_combo.currentText())

    def loadCategories(self):
        try:
            self.all_categories = self.data_manager.get_all_categories()
        except Exception:
            self.all_categories = []

        current_text = self.category_filter.blockSignals(True)
        self.category_filter.clear()
        self.category_filter.addItem('推荐分类 (自动)', None)
        for cat in self.all_categories:
            display_name = cat.name_cn if cat.name_cn else cat.name
            self.category_filter.addItem(display_name, cat.id)
        self.category_filter.blockSignals(current_text)

    def onArchitectureChanged(self, name):
        if not name:
            return
        self.current_arch_name = name
        arch = BEGINNER_ARCHITECTURES.get(name, BEGINNER_ARCHITECTURES['标准9段架构 (推荐)'])
        self.segments = [s.copy() for s in arch if s.get('enabled', True)]
        if not self.segments:
            self.segments = [s.copy() for s in arch]
        self.current_segment_index = 0
        self.selected_prompts = {i: [] for i in range(len(self.segments))}
        self.progress_bar.setMaximum(len(self.segments))
        self.refreshSegmentView()

    def createCustomArchitecture(self):
        from PySide6.QtWidgets import QInputDialog
        names = list(BEGINNER_ARCHITECTURES.keys())
        name, ok = QInputDialog.getItem(self, '基于现有架构创建', '选择基础架构:', names, 0, False)
        if not ok:
            return
        new_name, ok = QInputDialog.getText(self, '新架构名称', '输入新架构名称:')
        if not ok or not new_name.strip():
            return
        new_name = new_name.strip()
        if new_name in BEGINNER_ARCHITECTURES:
            QMessageBox.warning(self, '提示', '架构名称已存在')
            return
        BEGINNER_ARCHITECTURES[new_name] = [s.copy() for s in BEGINNER_ARCHITECTURES[name]]
        self.arch_combo.addItem(new_name)
        self.arch_combo.setCurrentText(new_name)

    def refreshSegmentView(self):
        if not self.segments:
            self.segment_label.setText('无可用段')
            self.example_label.setText('')
            self.progress_bar.setValue(0)
            return
        seg = self.segments[self.current_segment_index]
        self.segment_label.setText(
            f'第 {self.current_segment_index + 1}/{len(self.segments)} 段: {seg["name"]}'
        )
        self.example_label.setText(f'示例: {seg.get("example", "")}')
        self.progress_bar.setValue(self.current_segment_index + 1)
        self.prev_btn.setEnabled(self.current_segment_index > 0)
        self.next_btn.setEnabled(self.current_segment_index < len(self.segments) - 1)
        self.refreshCategoryFilter()
        self.refreshPromptList()
        self.refreshSelectedList()
        self.refreshPreview()

    def refreshCategoryFilter(self):
        seg = self.segments[self.current_segment_index]
        seg_name = seg['name']
        recommended = ARCHITECTURE_SEGMENT_CATEGORY_MAP.get(seg_name, [])

        current_text = self.category_filter.blockSignals(True)
        self.category_filter.clear()
        self.category_filter.addItem('推荐分类 (自动)', None)
        self.category_filter.addItem('全部分类', 'all')
        for cat in self.all_categories:
            display_name = cat.name_cn if cat.name_cn else cat.name
            is_recommended = any(
                rec.lower() in (cat.name or '').lower() or rec.lower() in (cat.name_cn or '').lower()
                for rec in recommended
            )
            prefix = '★ ' if is_recommended else '  '
            self.category_filter.addItem(prefix + display_name, cat.id)
        self.category_filter.blockSignals(current_text)

    def refreshPromptList(self):
        self.prompt_list.clear()
        seg = self.segments[self.current_segment_index]
        seg_name = seg['name']
        recommended = ARCHITECTURE_SEGMENT_CATEGORY_MAP.get(seg_name, [])
        keyword = self.search_edit.text().strip().lower()
        filter_data = self.category_filter.currentData()

        try:
            session = Session()
            query = session.query(Prompt).filter(Prompt.enabled == True)

            if filter_data == 'all':
                pass
            elif filter_data is None:
                if recommended:
                    from sqlalchemy import or_
                    conditions = []
                    for cat in self.all_categories:
                        if any(
                            rec.lower() in (cat.name or '').lower() or rec.lower() in (cat.name_cn or '').lower()
                            for rec in recommended
                        ):
                            conditions.append(Prompt.category_id == cat.id)
                    if conditions:
                        query = query.filter(or_(*conditions))
            else:
                query = query.filter(Prompt.category_id == filter_data)

            if keyword:
                from sqlalchemy import or_
                query = query.filter(
                    or_(
                        Prompt.english.like(f'%{keyword}%'),
                        Prompt.chinese.like(f'%{keyword}%')
                    )
                )

            prompts = query.limit(500).all()
            session.close()

            for p in prompts:
                cat_name = ''
                if p.category:
                    cat_name = p.category.name_cn or p.category.name or ''
                display = f'{p.english}'
                if p.chinese:
                    display += f'  |  {p.chinese}'
                if cat_name:
                    display += f'  [{cat_name}]'
                item = QListWidgetItem(display)
                item.setData(Qt.UserRole, {
                    'english': p.english,
                    'chinese': p.chinese or '',
                    'category': cat_name,
                    'weight': p.weight if p.weight else 1.0
                })
                self.prompt_list.addItem(item)

            if self.prompt_list.count() == 0:
                empty_item = QListWidgetItem('（无匹配词条，可跳过此段或手动输入）')
                empty_item.setFlags(Qt.NoItemFlags)
                self.prompt_list.addItem(empty_item)

        except Exception as e:
            QMessageBox.warning(self, '错误', f'加载词条失败: {str(e)}')

    def refreshSelectedList(self):
        self.selected_list.clear()
        selected = self.selected_prompts.get(self.current_segment_index, [])
        for p in selected:
            item = QListWidgetItem(p['english'])
            if p.get('chinese'):
                item.setToolTip(p['chinese'])
            self.selected_list.addItem(item)

    def refreshPreview(self):
        parts = []
        for i, seg in enumerate(self.segments):
            selected = self.selected_prompts.get(i, [])
            if selected:
                words = []
                for p in selected:
                    en = p['english']
                    weight = p.get('weight', 1.0)
                    if weight and weight != 1.0:
                        words.append(f'({en}:{weight})')
                    else:
                        words.append(en)
                parts.append(', '.join(words))

        if parts:
            self.preview_edit.setPlainText(', '.join(parts))
        else:
            self.preview_edit.setPlainText('（尚未选择任何词条）')

    def addSelectedPrompt(self):
        items = self.prompt_list.selectedItems()
        if not items:
            return
        for item in items:
            data = item.data(Qt.UserRole)
            if not data:
                continue
            existing = self.selected_prompts.setdefault(self.current_segment_index, [])
            if not any(p['english'] == data['english'] for p in existing):
                existing.append(data)
        self.refreshSelectedList()
        self.refreshPreview()

    def addRandomPrompt(self):
        import random
        count = self.prompt_list.count()
        if count == 0:
            return
        idx = random.randint(0, count - 1)
        item = self.prompt_list.item(idx)
        data = item.data(Qt.UserRole)
        if not data:
            return
        existing = self.selected_prompts.setdefault(self.current_segment_index, [])
        if not any(p['english'] == data['english'] for p in existing):
            existing.append(data)
        self.refreshSelectedList()
        self.refreshPreview()

    def removeSelectedPrompt(self):
        items = self.selected_list.selectedItems()
        if not items:
            return
        row = self.selected_list.row(items[0])
        selected = self.selected_prompts.get(self.current_segment_index, [])
        if 0 <= row < len(selected):
            del selected[row]
        self.refreshSelectedList()
        self.refreshPreview()

    def clearCurrentSegment(self):
        self.selected_prompts[self.current_segment_index] = []
        self.refreshSelectedList()
        self.refreshPreview()

    def prevSegment(self):
        if self.current_segment_index > 0:
            self.current_segment_index -= 1
            self.refreshSegmentView()

    def nextSegment(self):
        if self.current_segment_index < len(self.segments) - 1:
            self.current_segment_index += 1
            self.refreshSegmentView()
        else:
            self.finishAndGenerate()

    def skipSegment(self):
        self.selected_prompts[self.current_segment_index] = []
        if self.current_segment_index < len(self.segments) - 1:
            self.current_segment_index += 1
            self.refreshSegmentView()
        else:
            self.finishAndGenerate()

    def finishAndGenerate(self):
        parts = []
        for i, seg in enumerate(self.segments):
            selected = self.selected_prompts.get(i, [])
            if selected:
                words = []
                for p in selected:
                    en = p['english']
                    weight = p.get('weight', 1.0)
                    if weight and weight != 1.0:
                        words.append(f'({en}:{weight})')
                    else:
                        words.append(en)
                parts.append(', '.join(words))

        if not parts:
            QMessageBox.warning(self, '提示', '请至少选择一个词条')
            return

        final_prompt = ', '.join(parts)
        self.promptGenerated.emit(final_prompt)
        QMessageBox.information(
            self, '生成完成',
            f'已按 "{self.current_arch_name}" 架构生成提示词:\n\n{final_prompt[:200]}{"..." if len(final_prompt) > 200 else ""}\n\n已添加到编辑器，可复制使用。'
        )
        self.accept()

    def getFinalPrompt(self):
        parts = []
        for i, seg in enumerate(self.segments):
            selected = self.selected_prompts.get(i, [])
            if selected:
                words = []
                for p in selected:
                    en = p['english']
                    weight = p.get('weight', 1.0)
                    if weight and weight != 1.0:
                        words.append(f'({en}:{weight})')
                    else:
                        words.append(en)
                parts.append(', '.join(words))
        return ', '.join(parts) if parts else ''
