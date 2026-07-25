import json
import os
import csv
from datetime import datetime
from models import Session, Category, Prompt, Template, TemplateItem, RandomRule, Settings

class DataManager:
    def __init__(self):
        self.session = Session()
    
    def get_all_categories(self):
        return self.session.query(Category).order_by(Category.order).all()
    
    def get_category_by_id(self, category_id):
        return self.session.query(Category).get(category_id)
    
    def add_category(self, name, name_cn=None, parent_id=None, order=0):
        category = Category(name=name, name_cn=name_cn, parent_id=parent_id, order=order)
        self.session.add(category)
        self.session.commit()
        return category
    
    def update_category(self, category_id, **kwargs):
        category = self.session.query(Category).get(category_id)
        if category:
            for key, value in kwargs.items():
                setattr(category, key, value)
            self.session.commit()
        return category
    
    def delete_category(self, category_id):
        category = self.session.query(Category).get(category_id)
        if category:
            self.session.delete(category)
            self.session.commit()
    
    def get_prompts_by_category(self, category_id):
        return self.session.query(Prompt).filter(Prompt.category_id == category_id, Prompt.enabled == True).all()
    
    def get_prompt_by_id(self, prompt_id):
        return self.session.query(Prompt).get(prompt_id)
    
    def add_prompt(self, english, chinese=None, note=None, category_id=None, **kwargs):
        prompt = Prompt(english=english, chinese=chinese, note=note, category_id=category_id, **kwargs)
        self.session.add(prompt)
        self.session.commit()
        return prompt
    
    def update_prompt(self, prompt_id, **kwargs):
        prompt = self.session.query(Prompt).get(prompt_id)
        if prompt:
            for key, value in kwargs.items():
                setattr(prompt, key, value)
            self.session.commit()
        return prompt
    
    def delete_prompt(self, prompt_id):
        prompt = self.session.query(Prompt).get(prompt_id)
        if prompt:
            self.session.delete(prompt)
            self.session.commit()
    
    def search_prompts(self, keyword, fields=['english', 'chinese', 'note', 'tags']):
        query = self.session.query(Prompt)
        conditions = []
        for field in fields:
            if field == 'english':
                conditions.append(Prompt.english.like(f'%{keyword}%'))
            elif field == 'chinese':
                conditions.append(Prompt.chinese.like(f'%{keyword}%'))
            elif field == 'note':
                conditions.append(Prompt.note.like(f'%{keyword}%'))
            elif field == 'tags':
                conditions.append(Prompt.tags.like(f'%{keyword}%'))
        
        if conditions:
            from sqlalchemy import or_
            query = query.filter(or_(*conditions))
        
        return query.all()
    
    def get_all_templates(self):
        return self.session.query(Template).all()
    
    def add_template(self, name, name_cn=None, description=None):
        template = Template(name=name, name_cn=name_cn, description=description)
        self.session.add(template)
        self.session.commit()
        return template
    
    def add_template_item(self, template_id, prompt_id, order=0, weight=None):
        item = TemplateItem(template_id=template_id, prompt_id=prompt_id, order=order, weight=weight)
        self.session.add(item)
        self.session.commit()
        return item
    
    def get_random_rule(self, category_id):
        return self.session.query(RandomRule).filter(RandomRule.category_id == category_id).first()
    
    def set_random_rule(self, category_id, mode='optional', min_count=0, max_count=1, probability=1.0, use_weight=True):
        rule = self.session.query(RandomRule).filter(RandomRule.category_id == category_id).first()
        if rule:
            rule.mode = mode
            rule.min_count = min_count
            rule.max_count = max_count
            rule.probability = probability
            rule.use_weight = use_weight
        else:
            rule = RandomRule(
                category_id=category_id,
                mode=mode,
                min_count=min_count,
                max_count=max_count,
                probability=probability,
                use_weight=use_weight
            )
            self.session.add(rule)
        self.session.commit()
        return rule
    
    def get_settings(self):
        return self.session.query(Settings).first()
    
    def update_settings(self, **kwargs):
        settings = self.session.query(Settings).first()
        if settings:
            settings.update_from_dict(kwargs)
            self.session.commit()
        return settings
    
    def export_to_json(self, filepath):
        data = {
            'version': '2.0',
            'exported_at': datetime.now().isoformat(),
            'categories': [],
            'prompts': [],
            'templates': [],
            'random_rules': []
        }
        
        categories = self.get_all_categories()
        for cat in categories:
            data['categories'].append(cat.to_dict())
        
        prompts = self.session.query(Prompt).all()
        for prompt in prompts:
            data['prompts'].append(prompt.to_dict())
        
        templates = self.get_all_templates()
        for template in templates:
            data['templates'].append(template.to_dict())
        
        rules = self.session.query(RandomRule).all()
        for rule in rules:
            data['random_rules'].append(rule.to_dict())
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def import_from_json(self, filepath, mode='merge'):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        category_map = {}
        if 'categories' in data:
            for cat_data in data['categories']:
                existing = self.session.query(Category).filter(Category.name == cat_data['name']).first()
                if existing:
                    if mode == 'merge':
                        existing.name_cn = cat_data.get('name_cn', existing.name_cn)
                        existing.order = cat_data.get('order', existing.order)
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
                
                existing = self.session.query(Prompt).filter(Prompt.english == prompt_data['english']).first()
                if existing:
                    if mode == 'merge':
                        existing.chinese = prompt_data.get('chinese', existing.chinese)
                        existing.note = prompt_data.get('note', existing.note)
                        existing.tags = prompt_data.get('tags', existing.tags)
                        existing.weight = prompt_data.get('weight', existing.weight)
                        existing.prompt_type = prompt_data.get('prompt_type', existing.prompt_type)
                else:
                    prompt = Prompt.from_dict(prompt_data)
                    self.session.add(prompt)
        
        self.session.commit()
    
    def export_to_csv(self, filepath, format_type='standard'):
        prompts = self.session.query(Prompt).all()
        
        with open(filepath, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            
            if format_type == 'danbooru':
                for p in prompts:
                    category = self.session.query(Category).get(p.category_id)
                    cat_name = category.name if category else 'general'
                    cat_id = 0
                    for cid, (en_name, _) in {0: ('general', ''), 1: ('artist', ''), 3: ('copyright', ''), 4: ('character', ''), 5: ('quality', '')}.items():
                        if en_name == cat_name:
                            cat_id = cid
                            break
                    writer.writerow([
                        p.english,
                        cat_id,
                        0,
                        p.aliases or '',
                        p.chinese or '',
                        category.name_cn if category else ''
                    ])
            elif format_type == 'danbooru_zh':
                for p in prompts:
                    category = self.session.query(Category).get(p.category_id)
                    cat_cn = category.name_cn if category and category.name_cn else ''
                    chinese_with_cat = f"{p.chinese or ''}|{cat_cn}" if cat_cn else (p.chinese or '')
                    writer.writerow([p.english, chinese_with_cat])
            else:
                writer.writerow(['english', 'chinese', 'category', 'tags', 'note', 'weight'])
                for p in prompts:
                    category = self.session.query(Category).get(p.category_id)
                    cat_name = category.name if category else ''
                    writer.writerow([
                        p.english,
                        p.chinese or '',
                        cat_name,
                        p.tags or '',
                        p.note or '',
                        p.weight or 1.0
                    ])
    
    def get_prompt_context_for_ai(self, keyword=None, category_id=None, limit=50):
        query = self.session.query(Prompt).filter(Prompt.enabled == True)
        
        if keyword:
            from sqlalchemy import or_
            query = query.filter(
                or_(
                    Prompt.english.like(f'%{keyword}%'),
                    Prompt.chinese.like(f'%{keyword}%'),
                    Prompt.tags.like(f'%{keyword}%')
                )
            )
        
        if category_id:
            query = query.filter(Prompt.category_id == category_id)
        
        prompts = query.limit(limit).all()
        
        lines = []
        for p in prompts:
            category = self.session.query(Category).get(p.category_id)
            cat_name = category.name if category else ''
            weight_str = f", weight: {p.weight}" if p.weight and p.weight != 1.0 else ""
            lines.append(f"- {p.english} ({p.chinese or '无翻译'}) [{cat_name}]{weight_str}")
        
        return "\n".join(lines)
    
    def get_all_prompts_summary(self):
        categories = self.get_all_categories()
        result = []
        
        for cat in categories:
            count = self.session.query(Prompt).filter(Prompt.category_id == cat.id, Prompt.enabled == True).count()
            if count > 0:
                prompts = self.session.query(Prompt).filter(
                    Prompt.category_id == cat.id,
                    Prompt.enabled == True
                ).limit(20).all()
                prompt_list = ', '.join([p.english for p in prompts])
                result.append(f"[{cat.name_cn or cat.name}] (共{count}条) 示例: {prompt_list}")
        
        return "\n".join(result)
    
    def close(self):
        self.session.close()
