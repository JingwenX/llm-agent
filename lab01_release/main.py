from typing import Dict, List
from autogen import ConversableAgent
import sys
import os

# Global variable to store restaurant data
RESTAURANT_DATABASE = {}

def fetch_restaurant_data(restaurant_name: str) -> Dict[str, List[str]]:
    global RESTAURANT_DATABASE
    
    # Return empty dict if restaurant not found
    if restaurant_name not in RESTAURANT_DATABASE:
        return {}
    
    # Return dictionary with restaurant name as key and its reviews as value
    return {restaurant_name: RESTAURANT_DATABASE[restaurant_name]}

def calculate_overall_score(restaurant_name: str, food_scores: List[int], customer_service_scores: List[int]) -> Dict[str, float]:
    # TODO
    # This function takes in a restaurant name, a list of food scores from 1-5, and a list of customer service scores from 1-5
    # The output should be a score between 0 and 10, which is computed as the following:
    # SUM(sqrt(food_scores[i]**2 * customer_service_scores[i]) * 1/(N * sqrt(125)) * 10
    # The above formula is a geometric mean of the scores, which penalizes food quality more than customer service. 
    # Example:
    # > calculate_overall_score("Applebee's", [1, 2, 3, 4, 5], [1, 2, 3, 4, 5])
    # {"Applebee's": 5.048}
    # NOTE: be sure to that the score includes AT LEAST 3  decimal places. The public tests will only read scores that have 
    # at least 3 decimal places.
    pass

def get_data_fetch_agent_prompt(restaurant_query: str) -> str:
    # TODO
    # It may help to organize messages/prompts within a function which returns a string. 
    # For example, you could use this function to return a prompt for the data fetch agent 
    # to use to fetch reviews for a specific restaurant.
    pass

def preload_restaurant_data(filename: str) -> Dict[str, List[str]]:
    restaurant_data = {}
    current_restaurant = None
    current_reviews = []
    
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line.startswith('Restaurant: '):
                    # If we were processing a restaurant, save its data
                    if current_restaurant is not None:
                        restaurant_data[current_restaurant] = current_reviews
                    
                    # Start new restaurant
                    current_restaurant = line[12:].strip()  # Remove 'Restaurant: ' prefix
                    current_reviews = []
                elif line.startswith('Review: '):
                    # Add review to current restaurant
                    review = line[8:].strip()  # Remove 'Review: ' prefix
                    current_reviews.append(review)
            
            # Don't forget to save the last restaurant
            if current_restaurant is not None:
                restaurant_data[current_restaurant] = current_reviews
                
    except FileNotFoundError:
        print(f"Error: Could not find file {filename}")
        return {}
    
    return restaurant_data

# TODO: feel free to write as many additional functions as you'd like.

# Do not modify the signature of the "main" function.
def main(user_query: str):
    # Load the restaurant database into global variable
    global RESTAURANT_DATABASE
    RESTAURANT_DATABASE = preload_restaurant_data("restaurant-data.txt")
    
    entrypoint_agent_system_message = "" # TODO
    llm_config = {"config_list": [{"model": "gpt-4o-mini", "api_key": os.environ.get("OPENAI_API_KEY")}]}
    
    # Register the original function
    entrypoint_agent = ConversableAgent("entrypoint_agent", 
                                      system_message=entrypoint_agent_system_message, 
                                      llm_config=llm_config)
    entrypoint_agent.register_for_llm(name="fetch_restaurant_data", 
                                     description="Fetches the reviews for a specific restaurant.")(fetch_restaurant_data)
    entrypoint_agent.register_for_execution(name="fetch_restaurant_data")(fetch_restaurant_data)

    # TODO
    # Create more agents here. 
    
    # TODO
    # Fill in the argument to `initiate_chats` below, calling the correct agents sequentially.
    # If you decide to use another conversation pattern, feel free to disregard this code.
    
    # Uncomment once you initiate the chat with at least one agent.
    # result = entrypoint_agent.initiate_chats([{}])
    
# DO NOT modify this code below.
if __name__ == "__main__":
    assert len(sys.argv) > 1, "Please ensure you include a query for some restaurant when executing main."
    main(sys.argv[1])