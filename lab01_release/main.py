from typing import Dict, List
from autogen import ConversableAgent
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Global variable to store restaurant data
RESTAURANT_DATABASE = {}

def fetch_restaurant_data(restaurant_name: str) -> Dict[str, List[str]]:
    # Mock data for Applebee's with three reviews using different score keywords
    mock_data = {
        "Applebee's": [
            "The food at Applebee's was average, with nothing particularly standout on the menu. However, the customer service was good, with attentive waitstaff and quick service.",
            "The food was bad, with uninspiring flavors and presentation. But the customer service was incredible, with staff going above and beyond expectations.",
            "The food quality was satisfying for a casual dinner. Unfortunately, the customer service was unpleasant, with long wait times and inattentive staff."
        ]
    }
    
    # Return mock data if restaurant is Applebee's
    if restaurant_name == "Applebee's":
        return mock_data
    
    # Use global database for other restaurants
    global RESTAURANT_DATABASE
    if restaurant_name not in RESTAURANT_DATABASE:
        return {}
    
    return {restaurant_name: RESTAURANT_DATABASE[restaurant_name]}

def calculate_overall_score(restaurant_name: str, food_scores: List[int], customer_service_scores: List[int]) -> Dict[str, float]:
    if not food_scores or not customer_service_scores:
        return {restaurant_name: 0.000}
    
    N = len(food_scores)
    total_score = 0
    for i in range(N):
        total_score += (food_scores[i]**2 * customer_service_scores[i])**0.5 * (1/(N * (125**0.5))) * 10
        
    return {restaurant_name: round(total_score, 3)}

def get_data_fetch_agent_prompt(restaurant_query: str) -> str:
    return f"""You are a data fetch agent. Your task is to extract the restaurant name from the query and fetch its reviews.
    Query: {restaurant_query}
    Please extract the restaurant name and use the fetch_restaurant_data function to get the reviews.
    Return the restaurant name and its reviews in a clear format."""

def preload_restaurant_data(filename: str) -> Dict[str, List[str]]:
    restaurant_data = {}
    
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if not line:  # Skip empty lines
                    continue
                    
                # Split on first period to separate restaurant name and review
                parts = line.split('. ', 1)  # Split on first occurrence of '. '
                if len(parts) == 2:
                    restaurant_name = parts[0]
                    review = parts[1]
                    
                    # Initialize list if restaurant not seen before
                    if restaurant_name not in restaurant_data:
                        restaurant_data[restaurant_name] = []
                        
                    # Add review to restaurant's list
                    restaurant_data[restaurant_name].append(review)
                
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
    
    llm_config = {"config_list": [{"model": "gpt-4o-mini", "api_key": os.environ.get("OPENAI_API_KEY")}]}

    # Create the code executor agent
    code_executor = ConversableAgent(
        name="code_executor",
        llm_config=False,  # No LLM needed for execution
        code_execution_config={
            "work_dir": "workspace",  # Directory for code execution
            "use_docker": False,  # Don't use Docker for isolation
        }
    )

    # Create the code writer agent
    code_writer = ConversableAgent(
        name="code_writer",
        system_message="""You write code to analyze restaurant reviews. Available functions:
        
        fetch_restaurant_data(restaurant_name: str) -> Dict[str, List[str]]
        - Gets reviews for a restaurant
        - Input: restaurant name as string
        - Returns: Dictionary with restaurant name and list of reviews

        calculate_overall_score(restaurant_name: str, food_scores: List[int], customer_service_scores: List[int]) -> Dict[str, float]
        - Calculates overall score from food and service scores (returns score out of 10)
        - Input: restaurant name, list of food scores (1-5), list of service scores (1-5)
        - Returns: Dictionary with restaurant name and final score (0-10)

        Scoring rules for reviews:
        - Score 1/5: awful, horrible, disgusting
        - Score 2/5: bad, unpleasant, offensive
        - Score 3/5: average, uninspiring, forgettable
        - Score 4/5: good, enjoyable, satisfying
        - Score 5/5: awesome, incredible, amazing

        Call calculate_overall_score only ONCE with the final scores.""",
        llm_config=llm_config
    )

    # Register functions for both LLM use and execution
    code_writer.register_for_llm(
        name="fetch_restaurant_data",
        description="Gets reviews for a restaurant. Input: restaurant_name (string)"
    )(fetch_restaurant_data)

    code_writer.register_for_llm(
        name="calculate_overall_score", 
        description="Calculates overall score from food and service scores"
    )(calculate_overall_score)

    code_executor.register_for_execution(
        name="fetch_restaurant_data"
    )(fetch_restaurant_data)

    code_executor.register_for_execution(
        name="calculate_overall_score"
    )(calculate_overall_score)

    # Start the conversation
    result = code_executor.initiate_chat(
        code_writer,
        message=f"Please analyze this restaurant query: {user_query}. First use fetch_restaurant_data to get reviews for the restaurant name, then analyze the reviews to extract food and service scores (1-5), and finally use calculate_overall_score to get the final score."
    )
    print(result)

# DO NOT modify this code below.
if __name__ == "__main__":
    assert len(sys.argv) > 1, "Please ensure you include a query for some restaurant when executing main."
    main(sys.argv[1])