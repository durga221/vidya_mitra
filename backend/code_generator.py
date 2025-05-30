
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import re
import os
from typing import Dict, Any, List
from crewai import Agent, Task, Crew, Process
import litellm
from datetime import datetime

os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY")


app = FastAPI(title="CrewAI Code Generator API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

class GeminiLLM:
    def __init__(self, model_name="gemini/gemini-2.0-flash-lite"):
        self.model_name = model_name
    
    def generate(self, messages):
        response = litellm.completion(
            model=self.model_name,
            messages=messages
        )
        return response.choices[0].message.content
        
    def chat(self, messages):
        return self.generate(messages)


llm = GeminiLLM()


code_generator = Agent(
    role="Code Generator",
    goal="Generate functional code based on user requirements",
    backstory="""Experienced programmer fluent in multiple programming languages.
    Creates functional code that addresses user requirements directly.""",
    llm=llm,
    verbose=True
)

code_optimizer = Agent(
    role="Code Optimizer",
    goal="Optimize and improve the generated code",
    backstory="""Expert in code optimization and best practices.
    Takes existing code and improves its efficiency, readability, and maintainability.""",
    llm=llm,
    verbose=True
)

def create_crew(user_prompt):
    """Create and return a CrewAI Crew with all agents and tasks."""
    
    generate_code_task = Task(
        description=f"Generate code that satisfies this user request: '{user_prompt}'",
        expected_output="""
        Clean, well-documented code that fulfills the user's requirements.
        The code should be functional and address all aspects of the user's request.
        """,
        agent=code_generator
    )

    optimize_code_task = Task(
        description="Optimize and improve the generated code. Also provide an explanation of how the code works.",
        expected_output="""
        Optimized version of the code with:
        - Improved efficiency
        - Better readability
        - Following best practices
        - Added error handling where appropriate
        Also include an explanation of how the code works and why certain decisions were made.
        """,
        agent=code_optimizer,
        context=[generate_code_task]
    )
    
    crew = Crew(
        agents=[
            code_generator,
            code_optimizer
        ],
        tasks=[
            generate_code_task,
            optimize_code_task
        ],
        verbose=True,
        process=Process.sequential
    )
    return crew

def generate_optimized_code(user_prompt):
    crew = create_crew(user_prompt)
    result = crew.kickoff()
    
   
    if hasattr(result, 'raw_output'):
        result_text = result.raw_output
    elif hasattr(result, 'output'):
        result_text = result.output
    else:
        
        result_text = str(result)
    
    
    code_pattern = re.compile(r'```(?:python|java|javascript|cpp|c|html|css)?\n(.*?)```', re.DOTALL)
    code_matches = code_pattern.findall(result_text)
    
   
    if not code_matches:
        code_blocks = [result_text]
    else:
        code_blocks = code_matches
    
   
    explanation = "Code explanation not provided."
    if code_matches:
        last_code = code_matches[-1]
        last_code_pos = result_text.rfind(last_code) + len(last_code) + 3  
        if last_code_pos < len(result_text):
            explanation = result_text[last_code_pos:].strip()
    
    
    messages = [
        {
            "role": "user",
            "content": user_prompt,
            "timestamp": datetime.now().isoformat()
        },
        {
            "role": "system",
            "content": "Code generation complete.",
            "timestamp": datetime.now().isoformat()
        }
    ]
    
    return {
        "code_blocks": code_blocks,
        "explanation": explanation,
        "messages": messages
    }


class PromptRequest(BaseModel):
    prompt: str


class Message(BaseModel):
    role: str
    content: str
    timestamp: str


class CodeResponse(BaseModel):
    code_blocks: List[str]
    explanation: str
    messages: List[Message]

@app.post("/generate-code/", response_model=CodeResponse)
async def generate_code(request: PromptRequest):
    try:
        if not request.prompt or request.prompt.strip() == "":
            raise HTTPException(status_code=400, detail="Prompt cannot be empty")
        
        result = generate_optimized_code(request.prompt)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating code: {str(e)}")

@app.get("/health/")
async def health_check():
    return {"status": "healthy"}

import uvicorn
uvicorn.run(app, host="localhost", port=8008)
