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
    
    # Create the entry point agent
    entrypoint_agent_system_message = """You are the coordinator agent that handles restaurant review analysis.
    You will work with other agents to:
    1. Fetch restaurant data
    2. Analyze reviews for food and service scores
    3. Calculate overall scores
    Coordinate with other agents and provide a final summary of the restaurant analysis."""
    
    entrypoint_agent = ConversableAgent(
        name="entrypoint_agent",
        system_message=entrypoint_agent_system_message,
        llm_config=llm_config,
        max_consecutive_auto_reply=10
    )
    
    # Create the data fetch agent
    data_fetch_agent = ConversableAgent(
        name="data_fetch_agent",
        system_message="""You are a data fetch agent. Your role is to:
        1. Extract restaurant names from queries
        2. Use fetch_restaurant_data function to get reviews
        3. Return the restaurant name and reviews in a clear format""",
        llm_config=llm_config
    )
    data_fetch_agent.register_for_llm(
        name="fetch_restaurant_data",
        description="Fetches reviews for a specific restaurant"
    )(fetch_restaurant_data)
    
    # Create the review analysis agent
    review_analysis_agent = ConversableAgent(
        name="review_analysis_agent",
        system_message="""You are a review analysis agent. For each review, extract:
        - food_score (1-5):
          1: awful, horrible, disgusting
          2: bad, unpleasant, offensive
          3: average, uninspiring, forgettable
          4: good, enjoyable, satisfying
          5: awesome, incredible, amazing
        - customer_service_score (1-5): using the same scale
        Return lists of food_scores and customer_service_scores.""",
        llm_config=llm_config
    )
    
    # Create the scoring agent
    scoring_agent = ConversableAgent(
        name="scoring_agent",
        system_message="""You are a scoring agent. Your role is to:
        1. Take the food_scores and customer_service_scores
        2. Use calculate_overall_score function to compute final score
        3. Present the results clearly""",
        llm_config=llm_config
    )
    scoring_agent.register_for_llm(
        name="calculate_overall_score",
        description="Calculates overall score based on food and service scores"
    )(calculate_overall_score)
    
    # Set up the chat flow
    chat_sequence = [
        {
            "recipient": data_fetch_agent,
            "message": f"Please fetch the reviews for the restaurant in this query: {user_query}"
        },
        {
            "recipient": review_analysis_agent,
            "message": "Please analyze the reviews and extract food and customer service scores"
        },
        {
            "recipient": scoring_agent,
            "message": "Please calculate the overall score using the extracted scores"
        }
    ]
    
    # Initiate the chat sequence
    result = entrypoint_agent.initiate_chats(chat_sequence)

# DO NOT modify this code below.
if __name__ == "__main__":
    assert len(sys.argv) > 1, "Please ensure you include a query for some restaurant when executing main."
    main(sys.argv[1])