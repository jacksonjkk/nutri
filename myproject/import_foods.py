import os
import django
import csv

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from aiagent.models import FoodItem

def import_csv(file_path):
    print(f"Reading {file_path}...")
    with open(file_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        count = 0
        FoodItem.objects.all().delete() # Clear existing to avoid duplicates during sync
        
        for row in reader:
            # Handle list fields
            health_tags = row['health_tags'].split('|') if row['health_tags'] else []
            allergens = row['allergens'].split('|') if row['allergens'] else []
            
            # Create FoodItem
            FoodItem.objects.create(
                name=row['food_name'],
                category=row['category'],
                serving_size_grams=float(row['serving_size_grams'] or 100),
                calories=float(row['calories_per_100g'] or 0),
                protein=float(row['protein_g'] or 0),
                carbs=float(row['carbohydrates_g'] or 0),
                fat=float(row['fat_g'] or 0),
                fiber=float(row['fiber_g'] or 0),
                sugar=float(row['sugar_g'] or 0),
                sodium=float(row['sodium_mg'] or 0),
                iron=float(row['iron_mg'] or 0),
                calcium=float(row['calcium_mg'] or 0),
                glycemic_index=float(row['glycemic_index'] or 0),
                is_processed=row['is_processed'].lower() == 'true',
                region=row['region_common'],
                season=row['seasonal_availability'],
                health_tags=health_tags,
                allergens=allergens,
                price=float(row['estimated_cost_ugx'] or 0),
                preparation=row.get('preparation', '')
            )
            count += 1
    
    print(f"Successfully imported {count} food items.")

def import_ugandan_foods():
    """Entry point for Render build command"""
    # Use absolute path to be safe on Render
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(base_dir, 'ugdataset (1).csv')
    
    if os.path.exists(csv_path):
        import_csv(csv_path)
    else:
        print(f"❌ Error: CSV not found at {csv_path}")

if __name__ == "__main__":
    import_ugandan_foods()
