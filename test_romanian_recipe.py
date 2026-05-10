"""Test recipe parser with Romanian recipes."""
from app.services.recipe_parser import RecipeParser


def test_romanian_recipe():
    """Test Romanian recipe parsing."""
    parser = RecipeParser()
    
    # Test Romanian recipe
    caption_ro = """
Plăcintă cu mere delicioasă! 🥧

Ingrediente:
- 500g făină
- 250g unt
- 3 ouă
- 100g zahăr
- 5-6 mere
- 1 linguriță scorțișoară
- 1 plic praf de copt
- Un praf de sare

Mod de preparare:
1. Amestecă făina cu praful de copt și sare
2. Adaugă untul rece tăiat cubulețe
3. Încorporează ouăle și zahărul
4. Frământă aluatul până devine omogen
5. Taie merele felii subțiri
6. Presară scorțișoara peste mere
7. Întinde aluatul în tavă
8. Așează merele deasupra
9. Coace 40 minute la 180°C
10. Servește caldă cu zahăr pudră

Poftă bună! 😋
    """
    
    result = parser.parse_recipe(caption_ro)
    
    print("=" * 60)
    print("TEST REȚETĂ ROMÂNEASCĂ")
    print("=" * 60)
    print(f"\nEste rețetă: {result['is_recipe']}")
    print(f"\nIngrediente găsite: {len(result['ingredients'])}")
    for i, ing in enumerate(result['ingredients'], 1):
        print(f"  {i}. {ing}")
    
    print(f"\nPași găsiți: {len(result['directions'])}")
    for i, dir in enumerate(result['directions'], 1):
        print(f"  {i}. {dir}")
    
    print("\n" + "=" * 60)
    
    # Test mixed Romanian/English
    caption_mixed = """
Sarmale tradiționale 🥟

Ingrediente:
- 1kg carne tocată (pork)
- 500g orez
- 2 cepe mari
- Foi de varză murată
- Sare, piper
- Smântână pentru servit

Preparare:
1. Călește ceapa în ulei
2. Mix carnea cu orezul și ceapa
3. Season cu sare și piper
4. Învăluie în frunze de varză
5. Pune în oală și fierbe 2 ore
6. Servește cu smântână
    """
    
    result2 = parser.parse_recipe(caption_mixed)
    
    print("\nTEST REȚETĂ MIXTĂ (RO/EN)")
    print("=" * 60)
    print(f"\nEste rețetă: {result2['is_recipe']}")
    print(f"Ingrediente: {len(result2['ingredients'])}")
    print(f"Pași: {len(result2['directions'])}")
    print("=" * 60)


if __name__ == '__main__':
    test_romanian_recipe()
