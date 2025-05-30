
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import os
import re
import json
import multiprocessing
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from crewai import Agent, Task, Crew, Process as CrewProcess


os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY")

class GeminiLLM:
    def __init__(self, model_name="gemini/gemini-2.0-flash-lite"):
        self.model_name = model_name
    
    def generate(self, messages):
        import litellm
        response = litellm.completion(
            model=self.model_name,
            messages=messages
        )
        return response.choices[0].message.content
        
    def chat(self, messages):
        return self.generate(messages)

llm = GeminiLLM()


resource_planner = Agent(
    role="Learning Resource Planner",
    goal="Plan a comprehensive learning journey for any topic",
    backstory="""You are an expert education consultant with decades of experience
    designing personalized learning paths. You understand how different people
    learn and what combination of resources works best for different subjects.""",
    llm=llm,
    verbose=True
)

book_specialist = Agent(
    role="Book Specialist",
    goal="Find the most relevant and high-quality books on any subject",
    backstory="""You are a librarian and literary critic with comprehensive knowledge
    of academic and popular books across all fields. You can identify which books
    are foundational, which are cutting-edge, and which are most appropriate
    for different levels of expertise.""",
    llm=llm,
    verbose=True
)

online_course_expert = Agent(
    role="Online Course Expert",
    goal="Identify the best online courses and learning platforms for any topic",
    backstory="""You have personally reviewed thousands of online courses across
    major platforms like Coursera, Udemy, edX, and specialized learning sites.
    You understand which courses provide the best value, which have the best
    instructors, and which are most up-to-date.""",
    llm=llm,
    verbose=True
)

web_resource_curator = Agent(
    role="Web Resource Curator",
    goal="Curate the most valuable websites, blogs, and online communities for learning",
    backstory="""You are a digital librarian who specializes in finding high-quality
    web resources. You know which websites provide the most accurate information,
    which forums have the most helpful communities, and which blogs are written
    by genuine experts.""",
    llm=llm,
    verbose=True
)

video_content_researcher = Agent(
    role="Video Content Researcher",
    goal="Discover the best YouTube channels and video content for effective learning",
    backstory="""You are a media researcher who specializes in educational video content.
    You can identify which YouTube channels provide the clearest explanations,
    which have the most engaging teaching styles, and which cover topics most
    comprehensively.""",
    llm=llm,
    verbose=True
)

def create_learning_resources_crew(topic):
    """Create and return a CrewAI Crew with learning resource generation tasks."""
    
    # Task 1: Plan the learning journey
    plan_learning = Task(
        description=f"""
        Create a comprehensive learning plan for the topic: '{topic}'.
        Analyze what subtopics should be covered and in what order.
        Consider different learning styles and levels of expertise.
        Identify what mix of resources (books, courses, websites, videos) would be ideal.
        """,
        expected_output="""
        A detailed learning plan including:
        1. Key subtopics to master
        2. Suggested learning sequence
        3. Recommended mix of resource types
        4. Considerations for different learning styles
        """,
        agent=resource_planner
    )
    
    # Task 2: Research book recommendations
    research_books = Task(
        description=f"""
        Identify the 5 best books for learning about '{topic}'.
        For each book, provide:
        - Title (accurate and complete)
        - Author(s)
        - A compelling description explaining why this book is valuable
        
        Include a mix of:
        - Foundational/classic texts
        - Up-to-date resources
        - Books for beginners and advanced learners
        
        Format as valid JSON exactly like this:
        [
            {{
                "title": "Complete Book Title",
                "author": "Author Name",
                "description": "Description"
            }}
        ]
        """,
        expected_output="A list of 5 well-researched book recommendations in JSON format",
        agent=book_specialist,
        context=[plan_learning]
    )
    
    # Task 3: Research online courses
    research_courses = Task(
        description=f"""
        Identify the 5 best online courses for learning about '{topic}'.
        For each course, provide:
        - Platform (e.g., Coursera, Udemy, edX, etc.)
        - Course name (accurate and complete)
        - URL (if you are uncertain, provide the platform's homepage)
        - A compelling description of the course's value
        
        Include a mix of:
        - Free and paid options
        - Different difficulty levels
        - Self-paced and structured courses
        
        Format as valid JSON exactly like this:
        [
            {{
                "platform": "Platform Name",
                "course_name": "Complete Course Title",
                "url": "Course URL or Platform URL",
                "description": "Description"
            }}
        ]
        """,
        expected_output="A list of 5 well-researched online course recommendations in JSON format",
        agent=online_course_expert,
        context=[plan_learning]
    )
    
    # Task 4: Research websites and online resources
    research_websites = Task(
        description=f"""
        Identify the 5 best websites and online resources for learning about '{topic}'.
        For each website, provide:
        - Name of the website or resource
        - URL (if you are uncertain, provide a general description of how to find it)
        - A compelling description of why this resource is valuable
        
        Include a mix of:
        - Interactive learning platforms
        - Documentation sites
        - Blogs and articles
        - Communities and forums
        
        Format as valid JSON exactly like this:
        [
            {{
                "name": "Website or Resource Name",
                "url": "Website URL",
                "description": "Description"
            }}
        ]
        """,
        expected_output="A list of 5 well-researched website recommendations in JSON format",
        agent=web_resource_curator,
        context=[plan_learning]
    )
    
    # Task 5: Research YouTube channels and video content
    research_videos = Task(
        description=f"""
        Identify the 5 best YouTube channels and video content creators for learning about '{topic}'.
        For each channel, provide:
        - Channel name
        - URL (if you are uncertain, provide a general description of how to find it)
        - A compelling description of why this channel is valuable
        
        Include a mix of:
        - Channels with different teaching styles
        - Content for different difficulty levels
        - Both popular and lesser-known quality creators
        
        Format as valid JSON exactly like this:
        [
            {{
                "channel_name": "YouTube Channel Name",
                "url": "Channel URL",
                "description": "Description"
            }}
        ]
        """,
        expected_output="A list of 5 well-researched YouTube channel recommendations in JSON format",
        agent=video_content_researcher,
        context=[plan_learning]
    )
    
    # Task 6: Compile and finalize all resources
    compile_resources = Task(
        description=f"""
        Compile all the researched resources into a comprehensive learning guide for '{topic}'.
        Review all resources for quality and relevance.
        Ensure there's a good mix of resource types and difficulty levels.
        Format everything as a structured JSON object with sections for each resource type.
        
        The final JSON structure should be exactly:
        {{
            "learning_plan": "Overall learning strategy and approach",
            "books": [...book objects...],
            "online_courses": [...course objects...],
            "websites": [...website objects...],
            "youtube_channels": [...channel objects...]
        }}
        """,
        expected_output="A complete, well-structured learning resources guide in JSON format",
        agent=resource_planner,
        context=[plan_learning, research_books, research_courses, research_websites, research_videos]
    )
    
    # Create the crew
    crew = Crew(
        agents=[resource_planner, book_specialist, online_course_expert, 
                web_resource_curator, video_content_researcher],
        tasks=[plan_learning, research_books, research_courses, 
               research_websites, research_videos, compile_resources],
        verbose=True,
        process=CrewProcess.sequential  # Renamed to avoid conflict with multiprocessing.Process
    )
    
    return crew

def extract_json(text):
    """Extract valid JSON from text that might contain markdown or other content"""
    # Look for JSON blocks in markdown code blocks
    json_pattern = re.compile(r'```(?:json)?\s*([\s\S]*?)\s*```')
    match = json_pattern.search(text)
    
    if match:
        json_str = match.group(1)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass
    
    # Try to find JSON with curly braces if not in code blocks
    try:
        # Find the first { and the last }
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1 and end != 0:
            json_str = text[start:end]
            return json.loads(json_str)
    except (json.JSONDecodeError, ValueError):
        pass
    
    # Return the original text if no JSON could be extracted
    return {"error": "Could not extract valid JSON", "raw_text": text}

def generate_learning_resources(topic):
    """Generate learning resources for a specified topic"""
    crew = create_learning_resources_crew(topic)
    result = crew.kickoff()
    
    # Get the string output from the CrewOutput object
    if hasattr(result, 'raw_output'):
        result_text = result.raw_output
    elif hasattr(result, 'output'):
        result_text = result.output
    else:
        result_text = str(result)
    
    # Extract JSON from the result
    resources_data = extract_json(result_text)
    return resources_data

# Pydantic models
class TopicRequest(BaseModel):
    topic: str

class ResourcesResponse(BaseModel):
    learning_plan: str
    books: List[Dict[str, str]]
    online_courses: List[Dict[str, str]]
    websites: List[Dict[str, str]]
    youtube_channels: List[Dict[str, str]]

class ErrorResponse(BaseModel):
    error: str
    raw_text: Optional[str] = None


app = FastAPI(
    title="Learning Resources API",
    description="An AI-powered API that generates comprehensive learning resources for any topic",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

@app.post("/generate-resources", response_model=ResourcesResponse, responses={400: {"model": ErrorResponse}})
async def generate_resources(request: TopicRequest):
    """
    Generate comprehensive learning resources for the provided topic.
    
    The API will return:
    - A learning plan
    - Book recommendations
    - Online course recommendations
    - Website resources
    - YouTube channel recommendations
    """
    if not request.topic or len(request.topic.strip()) == 0:
        raise HTTPException(status_code=400, detail="Topic cannot be empty")
    
    try:
        
        result = generate_learning_resources(request.topic)
        
        
        if "error" in result and "raw_text" in result:
            raise HTTPException(status_code=400, detail=result)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while generating resources: {str(e)}")

@app.get("/")
async def root():
    """Welcome endpoint with API usage information"""
    return {
        "message": "Welcome to the Learning Resources API",
        "usage": "Send a POST request to /generate-resources with a JSON body containing a 'topic' field"
    }

# Main entry point fixed to handle multiprocessing correctly

import uvicorn
uvicorn.run(app, host="localhost", port=8000)


