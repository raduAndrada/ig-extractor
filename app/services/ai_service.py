"""AI service for automatic categorization and tagging."""
from typing import List, Dict, Tuple
from flask import current_app
import re
import logging

logger = logging.getLogger(__name__)


class AIService:
    """Service for AI-powered post categorization and tagging."""
    
    def __init__(self):
        """Initialize AI service based on configuration."""
        self.provider = current_app.config.get('AI_PROVIDER', 'openai')
        
        if self.provider == 'openai':
            self._init_openai()
        elif self.provider == 'local':
            self._init_local_models()
    
    def _init_openai(self):
        """Initialize OpenAI client."""
        try:
            import openai
            api_key = current_app.config.get('OPENAI_API_KEY')
            if api_key and api_key != 'your-openai-api-key-here':
                self.client = openai.OpenAI(api_key=api_key)
                self.model = "gpt-4o-mini"  # Cheaper, faster model
                logger.info("OpenAI initialized")
            else:
                logger.warning("OpenAI API key not configured, using keyword-based")
                self.client = None
        except ImportError:
            logger.warning("OpenAI package not installed, using keyword-based")
            self.client = None
    
    def _init_local_models(self):
        """Initialize local models (CLIP, BLIP)."""
        try:
            from transformers import pipeline
            # Use zero-shot classification for categories
            self.classifier = pipeline("zero-shot-classification", 
                                      model="facebook/bart-large-mnli")
            logger.info("Local models initialized")
        except ImportError:
            logger.warning("Transformers package not installed, using keyword-based")
            self.classifier = None
    
    def suggest_categories(self, post, available_categories: List[str]) -> List[Tuple[str, float]]:
        """Suggest categories for a post.
        
        Args:
            post: Post object to categorize
            available_categories: List of available category names
            
        Returns:
            List of tuples (category_name, confidence_score)
        """
        if not available_categories:
            return []
        
        # Try AI methods first
        if self.provider == 'openai' and self.client:
            suggestions = self._suggest_with_openai(post, available_categories)
            if suggestions:
                return suggestions
        elif self.provider == 'local' and hasattr(self, 'classifier') and self.classifier:
            suggestions = self._suggest_with_local(post, available_categories)
            if suggestions:
                return suggestions
        
        # Fallback to keyword matching
        return self._suggest_with_keywords(post, available_categories)
    
    def _suggest_with_openai(self, post, categories: List[str]) -> List[Tuple[str, float]]:
        """Use OpenAI to suggest categories.
        
        Args:
            post: Post object
            categories: Available categories
            
        Returns:
            List of (category, confidence) tuples
        """
        try:
            caption = post.caption or "No caption"
            username = post.owner_username or "Unknown"
            
            prompt = f"""Given this Instagram post, suggest which categories fit best.

Post by: @{username}
Caption: {caption[:500]}

Available categories: {', '.join(categories)}

Return up to 3 best matching categories with confidence scores (0-1).
Format: category_name:confidence
Example: Food:0.95
Travel:0.7

Only return categories from the available list. If no good match, return NONE."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that categorizes Instagram posts accurately."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.3
            )
            
            result = response.choices[0].message.content.strip()
            
            if result == "NONE":
                return []
            
            # Parse response
            suggestions = []
            for line in result.split('\n'):
                if ':' in line:
                    try:
                        cat, conf = line.strip().split(':')
                        cat = cat.strip()
                        conf = float(conf.strip())
                        if cat in categories and 0 <= conf <= 1:
                            suggestions.append((cat, conf))
                    except:
                        continue
            
            logger.info(f"OpenAI suggestions for post {post.id}: {suggestions}")
            return suggestions[:3]
            
        except Exception as e:
            logger.error(f"OpenAI categorization failed: {e}")
            return []
    
    def _suggest_with_local(self, post, categories: List[str]) -> List[Tuple[str, float]]:
        """Use local zero-shot classification to suggest categories.
        
        Args:
            post: Post object
            categories: Available categories
            
        Returns:
            List of (category, confidence) tuples
        """
        try:
            caption = post.caption or f"Post by {post.owner_username}"
            
            # Use zero-shot classification
            result = self.classifier(caption, categories, multi_label=True)
            
            # Combine results
            suggestions = []
            for label, score in zip(result['labels'], result['scores']):
                if score > 0.3:  # Only include if confidence > 30%
                    suggestions.append((label, score))
            
            logger.info(f"Local model suggestions for post {post.id}: {suggestions}")
            return suggestions[:3]
            
        except Exception as e:
            logger.error(f"Local categorization failed: {e}")
            return []
    
    def _suggest_with_keywords(self, post, categories: List[str]) -> List[Tuple[str, float]]:
        """Keyword-based category suggestion (fallback).
        
        Args:
            post: Post object
            categories: Available categories
            
        Returns:
            List of (category, confidence) tuples
        """
        suggestions = []
        caption = (post.caption or '').lower()
        username = (post.owner_username or '').lower()
        
        # Define keyword mappings (you can customize these!)
        keyword_map = {
            'food': ['food', 'recipe', 'cooking', 'delicious', 'yummy', 'eat', 'dinner', 'lunch', 'breakfast', 'restaurant', 'chef'],
            'travel': ['travel', 'trip', 'vacation', 'adventure', 'explore', 'journey', 'wanderlust', 'beach', 'mountain', 'city'],
            'fashion': ['fashion', 'style', 'outfit', 'ootd', 'clothes', 'dress', 'shoes', 'accessories', 'look'],
            'fitness': ['fitness', 'workout', 'gym', 'exercise', 'training', 'health', 'fit', 'muscle', 'cardio'],
            'art': ['art', 'artist', 'painting', 'drawing', 'creative', 'design', 'illustration', 'artwork'],
            'photography': ['photo', 'photography', 'photographer', 'camera', 'shot', 'portrait', 'landscape'],
            'nature': ['nature', 'natural', 'wildlife', 'outdoor', 'forest', 'garden', 'plant', 'flower', 'tree'],
            'inspiration': ['inspiration', 'motivate', 'quote', 'wisdom', 'inspire', 'goals', 'success'],
            'humor': ['funny', 'lol', 'meme', 'hilarious', 'comedy', 'laugh', 'joke'],
            'technology': ['tech', 'technology', 'gadget', 'software', 'code', 'programming', 'ai', 'digital'],
            'music': ['music', 'song', 'band', 'concert', 'musician', 'guitar', 'piano', 'singing'],
            'pet': ['dog', 'cat', 'pet', 'puppy', 'kitten', 'animal', 'cute'],
        }
        
        # Check each category
        for category in categories:
            category_lower = category.lower()
            
            # Direct match
            if category_lower in caption or category_lower in username:
                suggestions.append((category, 0.8))
                continue
            
            # Keyword match
            if category_lower in keyword_map:
                keywords = keyword_map[category_lower]
                matches = sum(1 for kw in keywords if kw in caption)
                if matches > 0:
                    # Confidence based on number of matching keywords
                    confidence = min(0.5 + (matches * 0.1), 0.9)
                    suggestions.append((category, confidence))
        
        # Sort by confidence
        suggestions.sort(key=lambda x: x[1], reverse=True)
        
        logger.info(f"Keyword suggestions for post {post.id}: {suggestions[:3]}")
        return suggestions[:3]
    
    def extract_tags(self, post) -> List[str]:
        """Extract relevant tags from post caption and content.
        
        Args:
            post: Post object
            
        Returns:
            List of suggested tags
        """
        tags = []
        caption = post.caption or ''
        
        # Extract hashtags (already present)
        hashtags = re.findall(r'#(\w+)', caption)
        tags.extend(hashtags)
        
        # Extract @mentions as potential tags
        mentions = re.findall(r'@(\w+)', caption)
        
        # Common keywords (without stopwords)
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                     'of', 'with', 'by', 'from', 'is', 'was', 'are', 'were', 'this', 'that'}
        
        # Extract common words (3+ chars, not stopwords)
        words = re.findall(r'\b[a-zA-Z]{3,}\b', caption.lower())
        keywords = [w for w in words if w not in stopwords and not w.startswith('http')]
        
        # Count word frequency
        word_freq = {}
        for word in keywords:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Add most common words as tags (if they appear 2+ times)
        common_words = [word for word, count in word_freq.items() if count >= 2]
        tags.extend(common_words[:5])
        
        # Add media type as tag
        if post.media_type:
            tags.append(post.media_type)
        
        # Remove duplicates and limit
        tags = list(set(tags))[:15]
        
        logger.info(f"Extracted tags for post {post.id}: {tags}")
        return tags
    
    def batch_suggest_categories(self, posts, available_categories: List[str]) -> Dict[int, List[Tuple[str, float]]]:
        """Suggest categories for multiple posts.
        
        Args:
            posts: List of Post objects
            available_categories: Available category names
            
        Returns:
            Dict mapping post.id to list of (category, confidence) tuples
        """
        results = {}
        
        for i, post in enumerate(posts):
            try:
                suggestions = self.suggest_categories(post, available_categories)
                results[post.id] = suggestions
                
                # Log progress
                if (i + 1) % 10 == 0:
                    logger.info(f"Processed {i + 1}/{len(posts)} posts")
                    
            except Exception as e:
                logger.error(f"Failed to categorize post {post.id}: {e}")
                results[post.id] = []
        
        return results
    
    def batch_extract_tags(self, posts) -> Dict[int, List[str]]:
        """Extract tags for multiple posts.
        
        Args:
            posts: List of Post objects
            
        Returns:
            Dict mapping post.id to list of tag names
        """
        results = {}
        
        for i, post in enumerate(posts):
            try:
                tags = self.extract_tags(post)
                results[post.id] = tags
                
                if (i + 1) % 10 == 0:
                    logger.info(f"Extracted tags for {i + 1}/{len(posts)} posts")
                    
            except Exception as e:
                logger.error(f"Failed to extract tags for post {post.id}: {e}")
                results[post.id] = []
        
        return results
