"""Test recipe parser."""
from app.services.recipe_parser import RecipeParser


def test_recipe_parser():
    """Test recipe parsing functionality."""
    parser = RecipeParser()
    
    # Test caption with clear recipe format
    caption = """
Delicious Chocolate Chip Cookies! 🍪

Ingredients:
- 2 cups flour
- 1 cup butter
- 3/4 cup brown sugar
- 2 eggs
- 1 tsp vanilla extract
- 1 tsp baking soda
- 2 cups chocolate chips
- Pinch of salt

Directions:
1. Preheat oven to 375°F
2. Mix butter and sugar until creamy
3. Beat in eggs and vanilla
4. Combine flour, baking soda, and salt
5. Stir into butter mixture
6. Fold in chocolate chips
7. Drop spoonfuls onto baking sheet
8. Bake for 10-12 minutes

Enjoy warm! 🔥
    """
    
    result = parser.parse_recipe(caption)
    
    print("=" * 60)
    print("RECIPE PARSER TEST")
    print("=" * 60)
    print(f"\nIs Recipe: {result['is_recipe']}")
    print(f"\nIngredients Found: {len(result['ingredients'])}")
    for i, ing in enumerate(result['ingredients'], 1):
        print(f"  {i}. {ing}")
    
    print(f"\nDirections Found: {len(result['directions'])}")
    for i, dir in enumerate(result['directions'], 1):
        print(f"  {i}. {dir}")
    
    print("\n" + "=" * 60)
    
    # Test non-recipe caption
    non_recipe = "Beautiful sunset at the beach! #vacation #sunset #relax"
    result2 = parser.parse_recipe(non_recipe)
    print("\nNon-Recipe Test:")
    print(f"Is Recipe: {result2['is_recipe']}")
    print("=" * 60)


if __name__ == '__main__':
    test_recipe_parser()
