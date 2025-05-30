from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import litellm
from enum import Enum
from dotenv import load_dotenv

from crewai import Agent, Task, Crew, Process

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
os.environ["GEMINI_API_KEY"] = API_KEY

class StudyAidType(Enum):
    CHEAT_SHEET = "cheat sheet"
    COMMON_MISTAKES = "common mistakes"
    MEMORY_TRICKS = "memory tricks"
    QUICK_DEFINITIONS = "quick definitions"
    FORMULAS = "formulas"
    CONCEPT_MAP = "concept map"
    PRACTICE_QUESTIONS = "practice questions"
    SUMMARY_NOTES = "summary notes"

class StudyAidCreator:
    def __init__(self, llm):
        """
        Initialize the StudyAidCreator with a language model.
        
        Args:
            llm: The language model to use for the agents
        """
        self.llm = llm
        
    def create_agents(self):
        """Create and return the agents for the study aid creation process"""
        researcher = Agent(
            role="Content Researcher",
            goal="Research accurate information for exam topics",
            backstory="Academic researcher specialized in finding high-quality educational information with expertise in retrieving the most relevant facts for quick exam preparation.",
            llm=self.llm,
            verbose=True
        )
        
        creator = Agent(
            role="Study Aid Creator",
            goal="Create concise and effective study materials for last-minute exam preparation",
            backstory="Experienced educator who creates easy-to-understand study content optimized for quick memorization and review.",
            llm=self.llm,
            verbose=True
        )
        
        reviewer = Agent(
            role="Education Quality Reviewer",
            goal="Ensure materials are accurate, clear, and effective for exam preparation",
            backstory="Former education examiner who ensures content is accurate, concise, and formatted for maximum retention.",
            llm=self.llm,
            verbose=True
        )
        
        return [researcher, creator, reviewer]
    
    def create_tasks(self, topic: str, aid_type: StudyAidType, agents: list):
        """
        Create tasks for the study aid creation process
        
        Args:
            topic: The academic topic to create materials for
            aid_type: The type of study aid from StudyAidType enum
            agents: List of agents [researcher, creator, reviewer]
        
        Returns:
            List of tasks
        """
        # Create specific instructions based on aid type
        research_instructions = self._get_research_instructions(aid_type, topic)
        creation_instructions = self._get_creation_instructions(aid_type, topic)
        review_instructions = self._get_review_instructions(aid_type, topic)
        
        research_task = Task(
            description=f"Research the topic '{topic}' for creating a '{aid_type.value}'.\n{research_instructions}",
            expected_output="Comprehensive research notes containing key information needed for the specific study aid type.",
            agent=agents[0]  # researcher
        )
        
        create_task = Task(
            description=f"Create a {aid_type.value} for '{topic}' based on the research.\n{creation_instructions}",
            expected_output=f"A well-structured {aid_type.value} with essential information, formatted for easy reading and quick review.",
            agent=agents[1],  # creator
            context=[research_task]
        )
        
        review_task = Task(
            description=f"Review and improve the {aid_type.value} for accuracy, clarity, and effectiveness.\n{review_instructions}",
            expected_output="A polished final study aid that is accurate, clear, and optimized for last-minute exam preparation.",
            agent=agents[2],  # reviewer
            context=[create_task]
        )
        
        return [research_task, create_task, review_task]
    
    def _get_research_instructions(self, aid_type: StudyAidType, topic: str) -> str:
        """Get specific research instructions based on aid type"""
        instructions = {
            StudyAidType.CHEAT_SHEET: "Identify core concepts, key definitions, important formulas, and critical facts that must be included in a one-page cheat sheet.",
            StudyAidType.COMMON_MISTAKES: "Research typical errors students make when working with this topic, misconceptions, and frequently confused concepts.",
            StudyAidType.MEMORY_TRICKS: "Find or create effective mnemonics, analogies, and memory aids that help recall complex information.",
            StudyAidType.QUICK_DEFINITIONS: "Gather concise, accurate definitions for all key terms and concepts in the topic.",
            StudyAidType.FORMULAS: "Compile all relevant formulas, equations, and mathematical relationships, with brief contextual notes.",
            StudyAidType.CONCEPT_MAP: "Identify key concepts and their relationships to create a visual hierarchy of information.",
            StudyAidType.PRACTICE_QUESTIONS: "Find common exam question patterns and develop representative questions that test understanding.",
            StudyAidType.SUMMARY_NOTES: "Identify the most important information to condense into concise, memorable notes."
        }
        return instructions.get(aid_type, "Research the essential information about this topic.")
    
    def _get_creation_instructions(self, aid_type: StudyAidType, topic: str) -> str:
        """Get specific creation instructions based on aid type"""
        instructions = {
            StudyAidType.CHEAT_SHEET: "Create a single-page, highly condensed overview with bullet points, brief definitions, and essential formulas. Use clear headings and visual organization.",
            StudyAidType.COMMON_MISTAKES: "Create a list of common errors with correct alternatives. Explain why each mistake occurs and how to avoid it.",
            StudyAidType.MEMORY_TRICKS: "Develop memorable acronyms, rhymes, visual associations, and other memory aids. Explain how each mnemonic maps to the actual content.",
            StudyAidType.QUICK_DEFINITIONS: "Create a glossary of terms with extremely concise but accurate definitions. Organize alphabetically or by concept clusters.",
            StudyAidType.FORMULAS: "Create a well-organized formula sheet with clear labels. Include units, variables definitions, and brief usage notes where needed.",
            StudyAidType.CONCEPT_MAP: "Create a hierarchical diagram showing relationships between concepts. Use arrows, colors, and minimal text for clarity.",
            StudyAidType.PRACTICE_QUESTIONS: "Create practice questions with brief solutions that target key concepts. Include a mix of recall and application questions.",
            StudyAidType.SUMMARY_NOTES: "Create concise notes that capture the essential knowledge in a structured, easy-to-review format."
        }
        return instructions.get(aid_type, "Create a concise and effective study aid focused on essential information.")
    
    def _get_review_instructions(self, aid_type: StudyAidType, topic: str) -> str:
        """Get specific review instructions based on aid type"""
        instructions = {
            StudyAidType.CHEAT_SHEET: "Ensure all essential information is included without excess detail. Check for clear organization and readability at a glance.",
            StudyAidType.COMMON_MISTAKES: "Verify accuracy of both common errors and corrections. Ensure explanations are clear and helpful.",
            StudyAidType.MEMORY_TRICKS: "Test each mnemonic for effectiveness and accuracy. Ensure they truly help recall the correct information.",
            StudyAidType.QUICK_DEFINITIONS: "Check definitions for accuracy and conciseness. Ensure no essential terms are missing.",
            StudyAidType.FORMULAS: "Verify all formulas for accuracy. Check that variable definitions and context notes are clear.",
            StudyAidType.CONCEPT_MAP: "Ensure relationships are accurately represented and the visual organization enhances understanding.",
            StudyAidType.PRACTICE_QUESTIONS: "Check questions and answers for accuracy. Ensure they target the most exam-relevant content.",
            StudyAidType.SUMMARY_NOTES: "Check for completeness of essential concepts while maintaining brevity. Ensure clear organization."
        }
        return instructions.get(aid_type, "Ensure the study aid is accurate, concise, and effectively serves last-minute exam preparation.")
    
    def create_crew(self, topic: str, aid_type_str: str):
        """
        Create a complete crew for generating the study aid
        
        Args:
            topic: The academic topic to create materials for
            aid_type_str: String representation of the study aid type
            
        Returns:
            CrewAI Crew object ready to kickoff
        """
        # Convert string to enum (with fallback)
        try:
            aid_type = next(t for t in StudyAidType if t.value == aid_type_str.lower())
        except StopIteration:
            # Default to cheat sheet if not found
            aid_type = StudyAidType.CHEAT_SHEET
            
        agents = self.create_agents()
        tasks = self.create_tasks(topic, aid_type, agents)
        
        crew = Crew(
            agents=agents,
            tasks=tasks,
            verbose=True,
            process=Process.sequential
        )
        
        return crew

# Define the custom LLM class for CrewAI
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

# Create Pydantic models for request/response validation
class StudyAidRequest(BaseModel):
    topic: str
    aid_type: str

class StudyAidResponse(BaseModel):
    result: str
    aid_type: str
    topic: str

# Initialize FastAPI app
app = FastAPI(
    title="Study Aid Generator API",
    description="An API that generates different types of study aids for various academic topics",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.post("/generate-study-aid", response_model=StudyAidResponse)
async def generate_study_aid(request: StudyAidRequest):
    """
    Generate a study aid for a specific topic and type.
    
    - **topic**: The academic topic to create materials for
    - **aid_type**: Type of study aid (e.g., "cheat sheet", "common mistakes", "memory tricks")
    """
    # Validate inputs
    if not request.topic.strip():
        raise HTTPException(status_code=400, detail="Topic cannot be empty")
    
    # Initialize our LLM
    llm = GeminiLLM()
    
    try:
        # Create the study aid system
        study_aid_system = StudyAidCreator(llm)
        
        # Create and run the crew
        crew = study_aid_system.create_crew(request.topic, request.aid_type)
        result = crew.kickoff()
        
        # Extract the result as a string
        if hasattr(result, 'raw'):
            result_str = result.raw
        else:
            # Fallback to string conversion if .raw doesn't exist
            result_str = str(result)
        
        # Return the response
        return StudyAidResponse(
            result=result_str,
            aid_type=request.aid_type,
            topic=request.topic
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating study aid: {str(e)}")
    

    
@app.get("/aid-types")
async def get_aid_types():
    """Get all available study aid types"""
    return {
        "aid_types": [aid_type.value for aid_type in StudyAidType]
    }

@app.get("/")
async def root():
    """Root endpoint to check if the API is running"""
    return {
        "message": "Study Aid Generator API is running",
        "version": "1.0.0",
        "usage": "POST to /generate-study-aid with topic and aid_type",
        "available_aid_types": [aid_type.value for aid_type in StudyAidType]
    }


import uvicorn
    # Run the FastAPI app with uvicorn
uvicorn.run(app, host="localhost", port=8006)
