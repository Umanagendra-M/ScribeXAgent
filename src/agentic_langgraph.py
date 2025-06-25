from langgraph.graph import StateGraph, START,END
from langchain_ollama import ChatOllama
from typing import List,TypedDict
from pydantic import BaseModel, Field, validator

import os
from langchain.prompts import PromptTemplate

class GraphState(TypedDict):
    messages: List[dict]
    transcript: str

    
# Define the function that calls the local LLaMA model
def soap_model(state: GraphState):
    llm = ChatOllama(model="llama3.2:latest")



    soap_prompt = f"""You are a cautious SOAP generator bot. You have the transcript below from a conversation between a doctor and patient.

    Transcript:
    {transcript}

    Create a SOAP note from this. Make it precise and accurate. If any section lacks information, explicitly state that."""
    try:
        response = llm.invoke([{"role": "user", "content": soap_prompt}])
        print("Generated SOAP:", response.content)
    except Exception as e:
        print("LLM call failed:", e)
        return {"messages": state["messages"] + [{"role": "system", "content": f"Error: {str(e)}"}]}

    return {
        "messages": state["messages"] + [{"role": "assistant", "content": response.content}]
    }
def review_model(state: GraphState):
    llm = ChatOllama(model="llama3.2:latest")
    review_prompt = f"""you are meticulous Medical reviewer bot.Take the review step by step.
    Below is the transcription of doctor patient conversation

    Transcript:
    {transcript}
    LLM generated SOAP_note:
    {state["messages"][-1]["content"]}
    
    can you compare the both transcript and SOAP note and add/remove the hallucinated content and regenerate the SOAP note followed by your comments at the end just stick to what is there already, every hallucination gives chance to suing the company.
    """
    try:
        response = llm.invoke([{"role": "user", "content": review_prompt}])
        print("Generated review content:", response.content)
    except Exception as e:
        print("LLM call failed:", e)
        return {"messages": state["messages"] + [{"role": "system", "content": f"Error: {str(e)}"}]}

    return {
        "messages": state["messages"] + [{"role": "assistant", "content": response.content}]
    }
# Test input
## step 1 
## process the wav file and convert it into a text transcription using whisper
## merge and preprocess the text data to make meaningful dialogue details
## pass this to LLM agent which answers the response in SOAP 
workflow=StateGraph(GraphState)
workflow.add_node("soap_call",soap_model)
workflow.add_node("review_call",review_model)

#########################################################
workflow.add_edge(START,"soap_call")
workflow.add_edge("soap_call","review_call")
workflow.add_edge("review_call",END)


with open("C:/Users/umall/Documents/github_projects/Agentic_ScribeX/data/formatted_transcript/Jane Doe_Dr. John Smith_2025-05-28.txt") as f:
    transcript = "".join(f.readlines()).strip()
flow = workflow.compile()


if not transcript:
    raise ValueError("Transcript is empty or not found.")
initial_state = {"messages": [],"transcript": transcript}
for w in flow.stream(initial_state):
    print(w)