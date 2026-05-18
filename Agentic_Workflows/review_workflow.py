from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from typing import TypedDict, Literal
from dotenv import load_dotenv
import os
from pydantic import BaseModel, Field

load_dotenv(override=True)


def get_groq_llm():
    return ChatOpenAI(
        model= "openai/gpt-oss-120b",
        base_url= "https://api.groq.com/openai/v1",
        api_key= os.getenv("GROQ_API_KEY"),
        max_tokens= 1000
    )

llm= get_groq_llm()

from pydantic import BaseModel, Field


class SentimentSchema(BaseModel):
    sentiment: Literal["positive", "negative"]= Field(description= "Sentiment of the review")
	
class DiagnosisSchema(BaseModel):
    issue_type: Literal["UX/UI", "Performace", "Bug", "Support", "Other"]= Field(description= "The category of issue mentioned in the review")
    tone: Literal["angry", "frustated", "disappointed", "calm"]= Field(description= "The emotional tone expressed by the user in review")
    urgency: Literal["low", "Medium", "High"]= Field(description= "How urgent or critical the issue appears to be")


structured_model_1= llm.with_structured_output(SentimentSchema)
structured_model_2= llm.with_structured_output(DiagnosisSchema)

class ReviewState(TypedDict):
    review: str
    sentiment: Literal["positive", "negative"]
    diagnosis: dict
    response: str
	
def find_sentiment(state: ReviewState):
    prompt= f'For the following review, find out the sentiment: {state["review"]}'
    sentiment= structured_model_1.invoke(prompt).sentiment

    return {'sentiment': sentiment}
    
    
	
## helper function:

def check_sentiment(state:ReviewState) -> Literal["positive_response", "run_diagnosis"]:
    if state['sentiment']=='positive':
        return 'positive_response'
    else:
        return 'run_diagnosis'
		
		
def positive_response(state:ReviewState):
    prompt= f'Write a warm thank you message in your response based on the review of the user: {state['review']}'
    response= llm.invoke(prompt).content

    return {'response': response}
	

def run_diagnosis(state: ReviewState):

    prompt= f"""
    Diagnose this negative review: \n
    {state['review']}    
    """
    raw_response= structured_model_2.invoke(prompt)

    return {'diagnosis': raw_response.model_dump()}
    
    
def negative_response(state: ReviewState):

    diagnosis= state['diagnosis']

    prompt= f"""You are a support assistant.
    The user had a {diagnosis['issue_type']}, sounded {diagnosis['tone']}, and marked urgency as: {diagnosis['urgency']}.
    Write an empathetic, helpful response message.

    """

    response= llm.invoke(prompt).content

    return {'response': response}


graph= StateGraph(ReviewState)

graph.add_node('find_sentiment', find_sentiment)
graph.add_node('positive_response', positive_response)
graph.add_node('run_diagnosis', run_diagnosis)
graph.add_node('negative_response', negative_response)

graph.add_edge(START, 'find_sentiment')
graph.add_conditional_edges('find_sentiment', check_sentiment)
graph.add_edge("positive_response", END)

graph.add_edge('run_diagnosis', "negative_response")
graph.add_edge("negative_response", END)

workflow= graph.compile()


def main():
    initial_state = {
        'review': "Extremely satisfied"
    }

    final_state = workflow.invoke(initial_state)
    print("Final State Output:")
    print(final_state)

if __name__ == "__main__":
    main()
