from main import preload_restaurant_data, fetch_restaurant_data, RESTAURANT_DATABASE
import os

def test_restaurant_data():
    global RESTAURANT_DATABASE
    
    print("Current working directory:", os.getcwd())
    print("Attempting to load restaurant data...")
    
    try:
        RESTAURANT_DATABASE = preload_restaurant_data("restaurant-data.txt")
        print("File opened successfully")
    except Exception as e:
        print(f"Error loading file: {e}")
        return
    
    # Comment out or remove the breakpoint
    # breakpoint()  # Stop here to inspect RESTAURANT_DATABASE
    
    # Print total number of restaurants
    print(f"\nTotal restaurants loaded: {len(RESTAURANT_DATABASE)}")
    
    # Print first restaurant and its reviews
    if RESTAURANT_DATABASE:
        first_restaurant = next(iter(RESTAURANT_DATABASE))
        print(f"\nExample restaurant: {first_restaurant}")
        print(f"Number of reviews: {len(RESTAURANT_DATABASE[first_restaurant])}")
        print("First review:", RESTAURANT_DATABASE[first_restaurant][0])
        
        # Test fetch_restaurant_data function
        result = fetch_restaurant_data(first_restaurant)
        print(f"\nFetch result for {first_restaurant}:")
        print(f"Found: {len(result[first_restaurant])} reviews")
        
        # Test with non-existent restaurant
        fake_result = fetch_restaurant_data("NonExistentRestaurant")
        print("\nFetch result for non-existent restaurant:")
        print(fake_result)

if __name__ == "__main__":
    print("Testing restaurant data functionality...")
    test_restaurant_data() 