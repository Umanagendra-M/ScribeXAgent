from crewai import Agent, Task, Crew
import os
import re

from langchain_openai import ChatOpenAI
# Load transcript


# Load local LLM
os.environ["OPENAI_API_KEY"]="89g8df0gkjgjfe"

llm = ChatOpenAI(
    model="ollama/llama3.2:latest",  # or your preferred model
    base_url="http://localhost:11434/v1"  # Make sure Ollama is running
)
transcript_path = "C:/Users/umall/Documents/github_projects/ScribeX - Agentic/data/formatted_transcript/Jane Doe_Dr. John Smith_2025-05-28.txt"
assert os.path.exists(transcript_path), "Transcript file missing"

with open(transcript_path, "r") as f:
    transcript = f.read()
with open('C:/Users/umall/Documents/github_projects/ScribeX - Agentic/data/SOAP_NOTES/agentic.txt','r') as output:
    SOAP_note=output.readlines()
subjective_agent = Agent(name="Subjective Agent", llm=llm,role="Symptom gatherer", goal="Extract subjective symptoms", backstory="You are a compassionate medical assistant who specializes in capturing patients' subjective experiences. You are trained to interpret how patients describe their symptoms, including onset, duration, and intensity. You listen attentively and do not make assumptions — you only record what the patient says, in their own words where appropriate.")
objective_agent = Agent(name="Objective Agent", llm=llm,role="Observer", goal="Extract objective findings", backstory="You are a detail-oriented nurse practitioner who records clinical observations and vital signs. You only note down objective facts from the transcript, such as physical findings or measurements the doctor mentions. You avoid interpreting — your role is to report what was seen, heard, or measured.")
assessment_agent = Agent(name="Assessment Agent",llm=llm, role="Medical summarizer as per doctor patient conversation", goal="Generate assessment", backstory="You are a clinical reasoning expert trained in medical summarization. Based on both subjective and objective inputs, your job is to synthesize the doctor’s findings and form a clinical impression. You do not generate new diagnoses unless explicitly mentioned — instead, you summarize the condition and its likely cause based on the transcript.")
plan_agent = Agent(name="Plan Agent",llm=llm, role="Planner", goal="Suggest next steps as per doctor", backstory="You are a diligent junior physician who assists in treatment planning. You summarize what the doctor advised the patient, including medications, further tests, referrals, and follow-up plans. You do not invent new steps, only extract what was actually recommended in the transcript.")

validator_agent = Agent(name="Output file Agent",llm=llm, role="SOAP file validator", goal="check if the file has the SOAP format sections Subjective,objective,plan and assessment return yes if everything looks good else return no", backstory="you are a validator in SOAP format you validate the file and check if it has subjective,objective,plan,assessment section then mention yes otherwise no")


subjective_task=Task(
            description=f"""From this text:\n{transcript}\n\nWrite the SUBJECTIVE section in SOAP format. Only include symptoms the patient *explicitly described*. Use the patient’s words where appropriate. Do not assume or infer symptoms.If there is no clear subjective input, respond with: 'No subjective symptoms mentioned.'and add the dummy  SUBJECTIVE section Limit output to 3-5 bullet points or 100 words.""",
            agent=subjective_agent,
            expected_output="Subjective section capturing patient's symptoms and personal experience"
        )
objective_task=Task(
            description=f"""From this text:\n{transcript}\n\nWrite the OBJECTIVE section in SOAP format. Only include symptoms the patient *explicitly described*. Use the patient’s words or doctors words where appropriate. Do not assume or infer statements.If there is no clear objective input, respond with: 'No objective mentioned' and add the dummy  OBJECTIVE section and add the dummy  ASSESSMENT section Limit output to 3-5 bullet points or 100 words.""",
            agent=objective_agent,
            expected_output="Objective clinical observations and measurements from the doctor"
        )

assessment_task=Task(
            description=f"""From this text:\n{transcript}\n\nWrite the ASSESSMENT section in SOAP format. Only include symptoms the patient *explicitly described*. Use the doctor's words where appropriate. Do not assume or infer doctor statements.If there is no clear ASSESSMENT input, respond with: 'No ASSESSMENT mentioned.' and add the dummy  ASSESSMENT section Limit output to 3-5 bullet points or 100 words.""",
            agent=assessment_agent,
            expected_output="Doctor’s assessment or diagnosis of the condition"
        )
plan_task=Task(
            description=f"""From this text:\n{transcript}\n\nWrite the PLAN section in SOAP format. only include the plan the doctor *explicitly described*. Use the doctor's words where appropriate. Do not assume or infer statements.If there is no clear plan input, respond with: 'No plan mentioned.' and add the dummy  PLAN section Limit output to 3-5 bullet points or 100 words.""",
            agent=plan_agent,
            expected_output="Plan of care including prescriptions, tests, and follow-up instructions please be precise"
        )

# validator_task=Task(
#             description=f"""From this text:\n{SOAP_note}\n\nIf proper SOAP format mention 'Yes' otherwise 'No'""",
#             agent=validator_agent,
#             expected_output="If proper SOAP format mention 'Yes' otherwise 'No'"
#         )

validator_task=Task(
    description=f"""The following is a full SOAP note:\n\n{''.join(SOAP_note)}\n\nCheck if the note includes the four clearly labeled sections: Subjective, Objective, Assessment, and Plan. If all are present and non-empty, return exactly 'Yes'. Otherwise, return 'No'.""",
    agent=validator_agent,
    expected_output="Yes or No"
)
# 2. Define tasks for each agent

# 3. Run Crew
def run_agentic_soap():
    #[subjective_task, objective_task, assessment_task, plan_task]
    crew = Crew(tasks=[subjective_task, objective_task, assessment_task, plan_task], agents=[subjective_agent,objective_agent, assessment_agent, plan_agent])
    results = crew.kickoff()
    return results

def run_validation():

    crew_validator = Crew(tasks=[validator_task], agents=[validator_agent])
    validator= crew_validator.kickoff()
    return validator

    

if __name__=='__main__':
    for i in range(0,5):
        print("trial",i)
        soap_sections = run_agentic_soap()
        # with open("C:/Users/umall/Documents/github_projects/ScribeX - Agentic/data/SOAP_NOTES/agentic.txt", "w", encoding="utf-8") as f:
        #     for section in soap_sections:
        #         if section[0]=='raw':
        #             f.write(section[1])
        with open("C:/Users/umall/Documents/github_projects/ScribeX - Agentic/data/SOAP_NOTES/agentic.txt", "w", encoding="utf-8") as f:
            for section_name, section_text in soap_sections:
                if section_name=='raw':
                    f.write(f"{section_name.upper()}:\n{section_text.strip()}\n\n")
        validator_result=run_validation()
        print("validator resault",validator_result,type(validator_result))
        if 'Yes' in validator_result :
            #soap_sections = run_agentic_soap()
            # Save to file or display
            break
            
        