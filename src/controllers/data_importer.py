import json
import csv
import requests
from models import Session, Category, Prompt

DANBOORU_CATEGORY_MAP = {
    0: ('general', '通用'),
    1: ('artist', '艺术家'),
    3: ('copyright', '版权'),
    4: ('character', '角色'),
    5: ('quality', '画质'),
    6: ('meta', '元数据'),
    7: ('species', '物种'),
    8: ('invalid', '无效'),
}

class DataImporter:
    def __init__(self):
        self.session = Session()
    
    def _get_or_create_category(self, name, name_cn=None):
        category = self.session.query(Category).filter(Category.name == name).first()
        if not category:
            category = Category(name=name, name_cn=name_cn or name)
            self.session.add(category)
            self.session.flush()
        return category
    
    def _prompt_exists(self, english):
        return self.session.query(Prompt).filter(Prompt.english == english).first() is not None
    
    def import_e621_tags(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for tag in data.get('tags', []):
            name = tag.get('name')
            category_name = tag.get('category')
            
            if not name:
                continue
            
            if self._prompt_exists(name):
                continue
            
            category = self._get_or_create_category(category_name, category_name)
            
            prompt = Prompt(
                english=name,
                chinese=tag.get('name_cn'),
                note=tag.get('description'),
                category_id=category.id
            )
            self.session.add(prompt)
        
        self.session.commit()
    
    def import_danbooru_tags(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for tag in data.get('tags', []):
            name = tag.get('name')
            category = tag.get('category')
            
            if not name:
                continue
            
            category_name = DANBOORU_CATEGORY_MAP.get(category, ('general', '通用'))[0]
            category_cn = DANBOORU_CATEGORY_MAP.get(category, ('general', '通用'))[1]
            
            if self._prompt_exists(name):
                continue
            
            cat = self._get_or_create_category(category_name, category_cn)
            
            prompt = Prompt(
                english=name,
                chinese=tag.get('chinese'),
                note=tag.get('description'),
                category_id=cat.id
            )
            self.session.add(prompt)
        
        self.session.commit()
    
    def import_danbooru_csv(self, filepath):
        count = 0
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            
            for row in reader:
                if len(row) < 2:
                    continue
                
                english = row[0].strip()
                if not english:
                    continue
                
                if self._prompt_exists(english):
                    continue
                
                category_id = int(row[1]) if len(row) > 1 and row[1].isdigit() else 0
                aliases = row[3].strip() if len(row) > 3 else None
                chinese = row[4].strip() if len(row) > 4 else None
                category_cn = row[5].strip() if len(row) > 5 else None
                
                cat_info = DANBOORU_CATEGORY_MAP.get(category_id, ('general', '通用'))
                category_name = cat_info[0]
                category_display = category_cn if category_cn else cat_info[1]
                
                cat = self._get_or_create_category(category_name, category_display)
                
                prompt = Prompt(
                    english=english,
                    chinese=chinese,
                    aliases=aliases,
                    category_id=cat.id
                )
                self.session.add(prompt)
                count += 1
        
        self.session.commit()
        return count
    
    def import_danbooru_zh_csv(self, filepath, default_category='general'):
        count = 0
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            
            for row in reader:
                if len(row) < 2:
                    continue
                
                english = row[0].strip()
                if not english:
                    continue
                
                if self._prompt_exists(english):
                    continue
                
                chinese_part = row[1].strip() if len(row) > 1 else None
                chinese = chinese_part
                category_cn = None
                
                if chinese_part and '|' in chinese_part:
                    parts = chinese_part.split('|', 1)
                    chinese = parts[0]
                    category_cn = parts[1] if len(parts) > 1 else None
                
                cat_name = default_category
                if category_cn:
                    for cat_id, (en_name, cn_name) in DANBOORU_CATEGORY_MAP.items():
                        if category_cn in cn_name or cn_name in category_cn:
                            cat_name = en_name
                            break
                
                cat = self._get_or_create_category(cat_name, category_cn or cat_name)
                
                prompt = Prompt(
                    english=english,
                    chinese=chinese,
                    category_id=cat.id
                )
                self.session.add(prompt)
                count += 1
        
        self.session.commit()
        return count
    
    def import_csv(self, filepath, english_column=0, chinese_column=1, category_column=None, tag_column=None):
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            try:
                next(reader)
            except StopIteration:
                return
            
            for row in reader:
                if len(row) <= english_column:
                    continue
                
                english = row[english_column].strip()
                if not english:
                    continue
                
                chinese = row[chinese_column].strip() if len(row) > chinese_column else None
                category_name = row[category_column].strip() if category_column and len(row) > category_column else 'default'
                tags = row[tag_column].strip() if tag_column and len(row) > tag_column else None
                
                if self._prompt_exists(english):
                    continue
                
                category = self._get_or_create_category(category_name, category_name)
                
                prompt = Prompt(
                    english=english,
                    chinese=chinese,
                    tags=tags,
                    category_id=category.id
                )
                self.session.add(prompt)
        
        self.session.commit()
    
    def import_txt(self, filepath, separator='\n', category_name='default'):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        items = content.split(separator)
        
        category = self._get_or_create_category(category_name, category_name)
        
        for item in items:
            item = item.strip()
            if not item:
                continue
            
            parts = item.split('|')
            english = parts[0].strip()
            
            if self._prompt_exists(english):
                continue
            
            chinese = parts[1].strip() if len(parts) > 1 else None
            note = parts[2].strip() if len(parts) > 2 else None
            
            prompt = Prompt(
                english=english,
                chinese=chinese,
                note=note,
                category_id=category.id
            )
            self.session.add(prompt)
        
        self.session.commit()
    
    def import_json(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        category_map = {}
        
        if 'categories' in data:
            for cat_data in data['categories']:
                existing = self.session.query(Category).filter(Category.name == cat_data['name']).first()
                if existing:
                    category_map[cat_data['id']] = existing.id
                else:
                    cat = Category.from_dict(cat_data)
                    self.session.add(cat)
                    self.session.flush()
                    category_map[cat_data['id']] = cat.id
        
        if 'prompts' in data:
            for prompt_data in data['prompts']:
                if prompt_data.get('category_id') in category_map:
                    prompt_data['category_id'] = category_map[prompt_data['category_id']]
                
                if self._prompt_exists(prompt_data['english']):
                    continue
                
                prompt = Prompt.from_dict(prompt_data)
                self.session.add(prompt)
        
        self.session.commit()
    
    def detect_csv_format(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            try:
                first_row = next(reader)
            except StopIteration:
                return 'unknown'
            
            if len(first_row) >= 6:
                if first_row[1].isdigit() and int(first_row[1]) in DANBOORU_CATEGORY_MAP:
                    return 'danbooru'
            
            if len(first_row) == 2 and '|' in first_row[1]:
                return 'danbooru_zh'
            
            return 'standard'
    
    def close(self):
        self.session.close()
