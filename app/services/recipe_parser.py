"""Recipe parser service for extracting ingredients and directions from captions."""
import re
import json
import logging

logger = logging.getLogger(__name__)


class RecipeParser:
    """Parse recipes from Instagram captions in English and Romanian."""
    
    # Common ingredient keywords (English + Romanian)
    INGREDIENT_KEYWORDS = {
        # Proteins (English)
        'chicken', 'beef', 'pork', 'fish', 'salmon', 'tuna', 'shrimp', 'lamb',
        'turkey', 'bacon', 'sausage', 'tofu', 'eggs', 'egg',
        
        # Proteins (Romanian)
        'pui', 'pasăre', 'carne', 'vita', 'porc', 'peste', 'somon', 'ton',
        'creveți', 'crevete', 'miel', 'curcan', 'slănină', 'slanina', 'cârnat',
        'carnați', 'ouă', 'ou',
        
        # Dairy (English)
        'milk', 'cream', 'butter', 'cheese', 'yogurt', 'sour cream', 'mozzarella',
        'parmesan', 'cheddar', 'feta', 'ricotta', 'cream cheese',
        
        # Dairy (Romanian)
        'lapte', 'smântână', 'smantana', 'unt', 'brânză', 'branza', 'iaurt',
        'telemea', 'caș', 'cas', 'mozzarella', 'parmezan',
        
        # Vegetables (English)
        'onion', 'garlic', 'tomato', 'potato', 'carrot', 'celery', 'pepper',
        'bell pepper', 'jalapeño', 'mushroom', 'spinach', 'lettuce', 'cucumber',
        'zucchini', 'broccoli', 'cauliflower', 'corn', 'peas', 'beans',
        'green beans', 'asparagus', 'cabbage', 'kale', 'avocado', 'eggplant',
        
        # Vegetables (Romanian)
        'ceapă', 'ceapa', 'usturoi', 'roșie', 'rosie', 'roșii', 'rosii', 'tomate',
        'cartof', 'cartofi', 'morcov', 'morcovi', 'țelină', 'telina', 'ardei',
        'ardei gras', 'ciupercă', 'ciuperci', 'spanac', 'salată', 'salata',
        'castravete', 'castraveti', 'dovlecel', 'dovlecei', 'broccoli', 'conopidă',
        'conopida', 'porumb', 'mazăre', 'mazare', 'fasole', 'păstăi', 'pastai',
        'sparanghel', 'varză', 'varza', 'avocado', 'vinete', 'vânătă', 'vanata',
        
        # Fruits (English)
        'apple', 'banana', 'orange', 'lemon', 'lime', 'strawberry', 'blueberry',
        'raspberry', 'mango', 'pineapple', 'peach', 'pear', 'grape', 'cherry',
        'watermelon', 'melon',
        
        # Fruits (Romanian)
        'măr', 'mar', 'mere', 'banană', 'banana', 'portocală', 'portocala',
        'lămâie', 'lamâie', 'lamie', 'lime', 'căpșună', 'capsuna', 'căpșuni',
        'capsuni', 'afine', 'zmeură', 'zmeure', 'mango', 'ananas', 'piersică',
        'piersica', 'pară', 'para', 'strugure', 'struguri', 'cireașă', 'cirese',
        'pepene', 'pepene verde', 'pepene galben',
        
        # Grains & Pasta (English)
        'rice', 'pasta', 'noodles', 'flour', 'bread', 'tortilla', 'quinoa',
        'couscous', 'oats', 'spaghetti', 'penne', 'fusilli', 'macaroni',
        
        # Grains & Pasta (Romanian)
        'orez', 'paste', 'tăiței', 'taitei', 'făină', 'faina', 'pâine', 'paine',
        'quinoa', 'cuscus', 'ovăz', 'ovaz', 'fulgi', 'griș', 'gris', 'pesmet',
        
        # Seasonings & Spices (English)
        'salt', 'pepper', 'paprika', 'cumin', 'oregano', 'basil', 'thyme',
        'rosemary', 'parsley', 'cilantro', 'cinnamon', 'ginger', 'nutmeg',
        'turmeric', 'curry', 'chili', 'cayenne', 'vanilla', 'bay leaf',
        
        # Seasonings & Spices (Romanian)
        'sare', 'piper', 'boia', 'chimion', 'oregano', 'busuioc', 'cimbru',
        'rozmarin', 'pătrunjel', 'patrunjel', 'coriandru', 'scorțișoară',
        'scortisoara', 'ghimber', 'nucșoară', 'nucsoara', 'turmeric', 'curry',
        'chili', 'boia iute', 'vanilie', 'foi dafin', 'dafin',
        
        # Liquids & Oils (English)
        'oil', 'olive oil', 'vegetable oil', 'coconut oil', 'water', 'stock',
        'broth', 'chicken stock', 'beef stock', 'vegetable stock', 'wine',
        'vinegar', 'soy sauce', 'worcestershire', 'hot sauce', 'lemon juice',
        
        # Liquids & Oils (Romanian)
        'ulei', 'ulei măsline', 'ulei de măsline', 'ulei vegetal', 'ulei cocos',
        'apă', 'apa', 'bulion', 'zeamă', 'zeama', 'supă', 'supa', 'vin',
        'oțet', 'otet', 'sos soia', 'sos picant', 'suc lămâie', 'suc lamie',
        
        # Baking (English)
        'sugar', 'brown sugar', 'honey', 'maple syrup', 'baking powder',
        'baking soda', 'yeast', 'cocoa', 'chocolate', 'vanilla extract',
        
        # Baking (Romanian)
        'zahăr', 'zahar', 'zahăr brun', 'miere', 'sirop arțar', 'praf copt',
        'bicarbonat', 'drojdie', 'cacao', 'ciocolată', 'ciocolata', 'esență',
        'esenta', 'vanilie',
        
        # Condiments (English)
        'mayonnaise', 'mustard', 'ketchup', 'relish', 'pesto', 'salsa',
        
        # Condiments (Romanian)
        'maioneză', 'maioneza', 'muștar', 'mustar', 'ketchup', 'pesto',
        
        # Nuts & Seeds (English)
        'almonds', 'walnuts', 'pecans', 'peanuts', 'cashews', 'pistachios',
        'sesame seeds', 'sunflower seeds', 'chia seeds', 'flax seeds',
        
        # Nuts & Seeds (Romanian)
        'migdale', 'nuci', 'alune', 'caju', 'fistic', 'susan', 'semințe',
        'seminte', 'floarea soarelui', 'chia', 'in',
    }
    
    # Measurement units (English + Romanian)
    UNITS = {
        # English
        'cup', 'cups', 'tbsp', 'tablespoon', 'tablespoons', 'tsp', 'teaspoon',
        'teaspoons', 'oz', 'ounce', 'ounces', 'lb', 'pound', 'pounds', 'g',
        'gram', 'grams', 'kg', 'kilogram', 'kilograms', 'ml', 'milliliter',
        'milliliters', 'l', 'liter', 'liters', 'pinch', 'dash', 'handful',
        'clove', 'cloves', 'piece', 'pieces', 'slice', 'slices', 'can', 'cans',
        'package', 'packages', 'jar', 'jars', 'bunch', 'head', 'stalk', 'stalks',
        
        # Romanian
        'cană', 'cana', 'căni', 'cani', 'lingură', 'lingura', 'linguri',
        'linguriță', 'lingurita', 'lingurite', 'kg', 'kilogram', 'grame', 'gr',
        'litru', 'litri', 'ml', 'mililitru', 'mililitri', 'praf', 'vârf',
        'varf', 'cățel', 'catel', 'catei', 'bucată', 'bucata', 'bucăți',
        'bucati', 'felie', 'felii', 'conservă', 'conserva', 'cutie', 'borcan',
        'legătură', 'legatura', 'ciorchine', 'tulpină', 'tulpina',
    }
    
    # Direction keywords (English + Romanian)
    DIRECTION_KEYWORDS = {
        # English
        'cook', 'bake', 'fry', 'boil', 'simmer', 'roast', 'grill', 'sauté',
        'mix', 'stir', 'whisk', 'blend', 'combine', 'add', 'pour', 'heat',
        'preheat', 'chop', 'dice', 'slice', 'mince', 'cut', 'peel', 'drain',
        'rinse', 'season', 'marinate', 'coat', 'spread', 'layer', 'fold',
        'beat', 'knead', 'roll', 'shape', 'form', 'place', 'arrange', 'cover',
        'refrigerate', 'freeze', 'cool', 'serve', 'garnish', 'sprinkle',
        'reduce', 'thicken', 'brown', 'caramelize', 'toast', 'broil', 'steam',
        
        # Romanian
        'gătește', 'gateste', 'gătim', 'gatim', 'coace', 'prăjește', 'prajeste',
        'fierbe', 'fierte', 'dă', 'da', 'pune', 'fierbi', 'rumenește', 'rumeneste',
        'frigem', 'amestecă', 'amesteca', 'mestecă', 'mesteca', 'bate', 'mixează',
        'mixeaza', 'combină', 'combina', 'adaugă', 'adauga', 'toarnă', 'toarna',
        'încălzește', 'incalzeste', 'preîncălzește', 'preincalzeste', 'toacă',
        'toaca', 'cubulețe', 'cubulete', 'felii', 'taie', 'curăță', 'curata',
        'scurge', 'clătește', 'clateste', 'condimentează', 'condimenteaza',
        'marinează', 'marineaza', 'învăluie', 'invaluie', 'întinde', 'intinde',
        'așează', 'aseaza', 'aranjează', 'aranjeaza', 'acoperă', 'acopera',
        'răcește', 'raceste', 'îngheață', 'ingheata', 'servește', 'serveste',
        'presară', 'presara', 'reduce', 'îngroașă', 'ingroasa', 'caramelizează',
        'caramelizeaza', 'prăjim', 'prajim', 'abur',
    }
    
    # Recipe indicators (English + Romanian)
    RECIPE_INDICATORS = {
        # English
        'recipe', 'ingredients', 'directions', 'instructions', 'how to make',
        'preparation', 'method', 'steps', 'cooking', 'you will need',
        
        # Romanian
        'rețetă', 'reteta', 'ingrediente', 'instrucțiuni', 'instructiuni',
        'mod de preparare', 'preparare', 'pași', 'pasi', 'etape', 'cum se face',
        'cum se prepară', 'cum se prepara', 'ai nevoie', 'necesare',
    }
    
    def parse_recipe(self, caption):
        """
        Parse recipe from caption text.
        
        Args:
            caption: Instagram post caption text
            
        Returns:
            dict: {
                'is_recipe': bool,
                'ingredients': list,
                'directions': list
            }
        """
        if not caption:
            return {'is_recipe': False, 'ingredients': [], 'directions': []}
        
        caption_lower = caption.lower()
        
        # Check if this looks like a recipe
        is_recipe = self._is_recipe(caption_lower)
        
        if not is_recipe:
            return {'is_recipe': False, 'ingredients': [], 'directions': []}
        
        # Extract ingredients and directions
        ingredients = self._extract_ingredients(caption)
        directions = self._extract_directions(caption)
        
        return {
            'is_recipe': True,
            'ingredients': ingredients,
            'directions': directions
        }
    
    def _is_recipe(self, caption_lower):
        """Check if caption appears to be a recipe."""
        # Look for recipe indicators (English & Romanian)
        has_indicator = any(indicator in caption_lower for indicator in self.RECIPE_INDICATORS)
        
        # Count ingredient keywords
        ingredient_count = sum(1 for ing in self.INGREDIENT_KEYWORDS if ing in caption_lower)
        
        # Count direction keywords
        direction_count = sum(1 for dir in self.DIRECTION_KEYWORDS if dir in caption_lower)
        
        # Recipe if it has indicator OR multiple ingredients + directions
        return has_indicator or (ingredient_count >= 3 and direction_count >= 2)
    
    def _extract_ingredients(self, caption):
        """Extract ingredients from caption."""
        ingredients = []
        lines = caption.split('\n')
        
        # Find ingredients section (English & Romanian markers)
        in_ingredients_section = False
        ingredient_markers = ['ingredient', 'you will need', 'you\'ll need', 'ingrediente', 'ai nevoie', 'necesare']
        direction_markers = ['direction', 'instruction', 'method', 'preparation', 'steps', 
                           'instrucțiuni', 'instructiuni', 'mod de preparare', 'preparare', 'pași', 'pasi', 'etape']
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Check if we're entering ingredients section
            if any(marker in line_lower for marker in ingredient_markers):
                in_ingredients_section = True
                continue
            
            # Check if we're leaving ingredients section
            if in_ingredients_section and any(marker in line_lower for marker in direction_markers):
                in_ingredients_section = False
                break  # Stop processing once we leave ingredients
            
            # Skip empty lines
            if not line.strip():
                continue
            
            # Extract ingredient if it matches pattern or has keywords
            if in_ingredients_section:
                # Clean the line
                ingredient = self._clean_ingredient_line(line)
                if ingredient and not self._is_direction(ingredient.lower()):
                    ingredients.append(ingredient)
            else:
                # Look for bullet points or numbered items with ingredients
                if self._looks_like_ingredient_line(line_lower):
                    ingredient = self._clean_ingredient_line(line)
                    if ingredient and not self._is_direction(ingredient.lower()):
                        ingredients.append(ingredient)
        
        # If no structured ingredients found, extract from keywords
        if not ingredients:
            ingredients = self._extract_by_keywords(caption, self.INGREDIENT_KEYWORDS)
        
        return ingredients[:20]  # Limit to 20 ingredients
    
    def _is_direction(self, text):
        """Check if text is likely a direction, not an ingredient."""
        # Check if starts with action verb
        words = text.split()
        if words and words[0] in self.DIRECTION_KEYWORDS:
            return True
        return False
    
    def _extract_directions(self, caption):
        """Extract cooking directions from caption."""
        directions = []
        lines = caption.split('\n')
        
        # Direction markers (English & Romanian)
        direction_markers = ['direction', 'instruction', 'method', 'preparation', 'steps', 'how to',
                           'instrucțiuni', 'instructiuni', 'mod de preparare', 'preparare', 
                           'pași', 'pasi', 'etape', 'cum se face', 'cum se prepară', 'cum se prepara']
        end_markers = ['note:', 'tip:', 'notă:', 'nota:', 'sfat:', '#', '@', 'enjoy', 'serve', 'poftă', 'pofta']
        
        # Find directions section
        in_directions_section = False
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Check if we're entering directions section
            if any(marker in line_lower for marker in direction_markers):
                in_directions_section = True
                continue
            
            # Check if we're leaving directions section
            if in_directions_section and any(marker in line_lower for marker in end_markers):
                # Allow 'serve'/'servește' as a direction if it's a full sentence
                if ('serve' in line_lower or 'servește' in line_lower or 'serveste' in line_lower) and len(line.split()) > 3:
                    direction = self._clean_direction_line(line)
                    if direction:
                        directions.append(direction)
                continue
            
            # Skip empty lines
            if not line.strip():
                continue
            
            # Extract direction if it looks like one
            if in_directions_section:
                direction = self._clean_direction_line(line)
                if direction:
                    directions.append(direction)
            else:
                # Look for numbered steps or action verbs
                if self._looks_like_direction_line(line_lower):
                    direction = self._clean_direction_line(line)
                    if direction:
                        directions.append(direction)
        
        # If no structured directions found, extract sentences with action verbs
        if not directions:
            directions = self._extract_by_action_verbs(caption)
        
        return directions[:15]  # Limit to 15 steps
    
    def _clean_ingredient_line(self, line):
        """Clean and format ingredient line."""
        # Remove bullet points, numbers, emojis
        cleaned = re.sub(r'^[-•*→➡️▪️▫️⭐️✓✔️☑️\d\.)\s]+', '', line)
        cleaned = cleaned.strip()
        
        # Remove trailing emojis
        cleaned = re.sub(r'[👌👍❤️💚💛🧡💙💜🖤🤍🤎💗💖💕💓💞💝💟❣️💌]', '', cleaned)
        cleaned = cleaned.strip()
        
        # Must have at least one ingredient keyword or unit
        if len(cleaned) > 3 and (
            any(ing in cleaned.lower() for ing in self.INGREDIENT_KEYWORDS) or
            any(unit in cleaned.lower() for unit in self.UNITS)
        ):
            return cleaned
        
        return None
    
    def _clean_direction_line(self, line):
        """Clean and format direction line."""
        # Remove step numbers
        cleaned = re.sub(r'^(step\s*)?[-•*→➡️\d\.)\s]+', '', line, flags=re.IGNORECASE)
        cleaned = cleaned.strip()
        
        # Remove trailing emojis
        cleaned = re.sub(r'[👌👍❤️💚💛🧡💙💜🖤🤍🤎💗💖💕💓💞💝💟❣️💌]', '', cleaned)
        cleaned = cleaned.strip()
        
        # Must contain action verb and be substantial
        if len(cleaned) > 10 and any(verb in cleaned.lower() for verb in self.DIRECTION_KEYWORDS):
            # Capitalize first letter
            cleaned = cleaned[0].upper() + cleaned[1:] if len(cleaned) > 1 else cleaned.upper()
            return cleaned
        
        return None
    
    def _looks_like_ingredient_line(self, line):
        """Check if line looks like an ingredient."""
        # Has bullet point or number
        if re.match(r'^[-•*→➡️▪️▫️\d\.)\s]+', line):
            # Contains ingredient keyword or unit
            return any(ing in line for ing in self.INGREDIENT_KEYWORDS) or \
                   any(unit in line for unit in self.UNITS)
        return False
    
    def _looks_like_direction_line(self, line):
        """Check if line looks like a direction/step."""
        # Numbered step
        if re.match(r'^\d+[\.)]\s+', line):
            return any(verb in line for verb in self.DIRECTION_KEYWORDS)
        
        # Starts with action verb
        first_word = line.split()[0].lower() if line.split() else ''
        return first_word in self.DIRECTION_KEYWORDS
    
    def _extract_by_keywords(self, caption, keywords):
        """Extract items that contain specific keywords."""
        items = []
        lines = caption.split('\n')
        
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in keywords):
                cleaned = self._clean_ingredient_line(line)
                if cleaned and len(cleaned) > 3:
                    items.append(cleaned)
        
        return items
    
    def _extract_by_action_verbs(self, caption):
        """Extract sentences with cooking action verbs."""
        directions = []
        
        # Split by periods or newlines
        sentences = re.split(r'[.\n]', caption)
        
        for sentence in sentences:
            sentence = sentence.strip()
            sentence_lower = sentence.lower()
            
            # Check if sentence has action verb
            if any(verb in sentence_lower for verb in self.DIRECTION_KEYWORDS):
                cleaned = self._clean_direction_line(sentence)
                if cleaned and len(cleaned) > 15:  # Substantial instruction
                    directions.append(cleaned)
        
        return directions
