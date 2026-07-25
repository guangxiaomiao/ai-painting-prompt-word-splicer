import random
from models import Session, Category, Prompt, RandomRule

class RandomGenerator:
    def __init__(self):
        self.session = Session()
    
    def generate(self, category_ids=None, custom_rules=None):
        result = []
        
        if category_ids is None:
            categories = self.session.query(Category).filter(Category.enabled == True).all()
            category_ids = [cat.id for cat in categories]
        
        for category_id in category_ids:
            rule = self.session.query(RandomRule).filter(RandomRule.category_id == category_id).first()
            
            if custom_rules and category_id in custom_rules:
                rule_data = custom_rules[category_id]
                mode = rule_data.get('mode', 'optional')
                min_count = rule_data.get('min_count', 0)
                max_count = rule_data.get('max_count', 1)
                probability = rule_data.get('probability', 1.0)
                use_weight = rule_data.get('use_weight', True)
            elif rule:
                mode = rule.mode
                min_count = rule.min_count
                max_count = rule.max_count
                probability = rule.probability
                use_weight = rule.use_weight
            else:
                mode = 'optional'
                min_count = 0
                max_count = 1
                probability = 1.0
                use_weight = True
            
            if mode == 'disabled':
                continue
            
            if random.random() > probability:
                continue
            
            prompts = self.session.query(Prompt).filter(
                Prompt.category_id == category_id,
                Prompt.enabled == True
            ).all()
            
            if not prompts:
                continue
            
            if mode == 'required':
                count = max(min_count, 1)
            else:
                count = random.randint(min_count, max_count)
            
            count = min(count, len(prompts))
            
            if use_weight:
                weights = [p.random_weight for p in prompts]
                selected = random.choices(prompts, weights=weights, k=count)
            else:
                selected = random.sample(prompts, min(count, len(prompts)))
            
            result.extend(selected)
        
        return result
    
    def generate_with_categories(self, categories_config):
        result = []
        
        for cat_name, config in categories_config.items():
            category = self.session.query(Category).filter(Category.name == cat_name).first()
            if not category:
                continue
            
            mode = config.get('mode', 'optional')
            min_count = config.get('min_count', 0)
            max_count = config.get('max_count', 1)
            probability = config.get('probability', 1.0)
            use_weight = config.get('use_weight', True)
            
            if mode == 'disabled':
                continue
            
            if random.random() > probability:
                continue
            
            prompts = self.session.query(Prompt).filter(
                Prompt.category_id == category.id,
                Prompt.enabled == True
            ).all()
            
            if not prompts:
                continue
            
            if mode == 'required':
                count = max(min_count, 1)
            else:
                count = random.randint(min_count, max_count)
            
            count = min(count, len(prompts))
            
            if use_weight:
                weights = [p.random_weight for p in prompts]
                selected = random.choices(prompts, weights=weights, k=count)
            else:
                selected = random.sample(prompts, min(count, len(prompts)))
            
            result.extend(selected)
        
        return result
    
    def close(self):
        self.session.close()
