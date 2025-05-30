from crewai import Agent, Task, Crew, Process
import os
from crewai_tools import SerperDevTool, WebsiteSearchTool
import litellm

# Set API keys
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyAfvi6jTzKOBMZLA4eebmf7-5swapUr5dA") 
SERPER_API_KEY = os.environ.get("SERPER_API_KEY", "b8d0a8d68ec30023aaf5fa6e8504aa9d975639b2")


# Initialize search tools
serper_tool = SerperDevTool()
web_search_tool = WebsiteSearchTool()

class GeminiLLM:
    """Wrapper for the Gemini model integration with CrewAI"""
    
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

# Initialize Gemini LLM
llm = GeminiLLM()

class AdvancedContentGenerator:
    """Enhanced class to generate educational content based on topic and user level"""
    
    def __init__(self):
        self.agents = self._create_agents()
    
    def _create_agents(self):
        """Initialize a team of specialized agents"""
        
        # Research agent to gather information from the web
        research_agent = Agent(
            role="Educational Researcher",
            goal="Find comprehensive information on educational topics",
            backstory="You are an expert researcher who can find reliable information on any topic, adapting the depth based on the learner's level.",
            tools=[serper_tool, web_search_tool],
            llm=llm,
            verbose=True
        )
        
        # Content creator to synthesize information
        content_creator = Agent(
            role="Content Synthesizer",
            goal="Create clear, structured educational content adapted to the learner's level",
            backstory="You transform raw research into well-organized educational materials that match the user's knowledge level.",
            llm=llm,
            verbose=True
        )
        
        # Visual elements specialist
        visual_specialist = Agent(
            role="Visual Content Specialist",
            goal="Identify and describe necessary visual elements for educational content",
            backstory="You identify what diagrams, flowcharts, images, and visual aids would enhance learning for a specific topic and user level.",
            tools=[serper_tool],
            llm=llm,
            verbose=True
        )
        
        # Mathematical/Technical specialist
        technical_specialist = Agent(
            role="Technical Content Specialist",
            goal="Provide accurate technical details and equations appropriate for the user's level",
            backstory="You ensure all technical content, including equations, formulas, and technical concepts, are accurate and presented at the right level of complexity.",
            llm=llm,
            verbose=True
        )
        
        # Educational adaptation specialist
        adaptation_specialist = Agent(
            role="Educational Adaptation Specialist",
            goal="Adapt content to match the learner's level perfectly",
            backstory="You are an expert in educational psychology who knows how to present the same information differently for beginners, intermediate, and advanced learners.",
            llm=llm,
            verbose=True
        )
        
        return {
            "researcher": research_agent,
            "content_creator": content_creator,
            "visual_specialist": visual_specialist,
            "technical_specialist": technical_specialist,
            "adaptation_specialist": adaptation_specialist
        }
    
    def generate_content(self, topic, level):
        """Extract content related to the given topic adapted to user level"""
        
        # Validate user level
        valid_levels = ["beginner", "intermediate", "advanced"]
        if level.lower() not in valid_levels:
            return f"Error: Level must be one of {valid_levels}"
        
        # Task 1: Research the topic
        research_task = Task(
            description=f"""
            Research the topic: '{topic}' thoroughly with focus on a {level} level understanding.
            """,
            expected_output="""
            A comprehensive research report containing:
            - Key concepts and definitions suited to the user's level
            - Important principles with appropriate depth
            - Examples tailored to the specified level
            - Practical applications with relevant complexity
            - References to reliable sources
            """,
            agent=self.agents["researcher"]
        )
        
        # Task 2: Identify necessary visual elements
        visual_task = Task(
            description=f"""
            Identify and describe visual elements needed to explain '{topic}' to a {level} learner.
            """,
            expected_output="""
            A detailed plan for visual elements including:
            - Descriptions of necessary diagrams and flowcharts
            - Specifications for helpful images
            - Details on graphs and charts needed
            - Labels and annotations for each visual
            """,
            agent=self.agents["visual_specialist"],
            context=[research_task]
        )
        
        # Task 3: Provide technical/mathematical content
        technical_task = Task(
            description=f"""
            Provide technical details for '{topic}' appropriate for a {level} learner.
            """,
            expected_output="""
            Technical content including:
            - Relevant equations and formulas with explanations
            - Technical terms defined at appropriate level
            - Mathematical derivations as needed
            - Code examples if applicable
            """,
            agent=self.agents["technical_specialist"],
            context=[research_task]
        )
        
        # Task 4: Adapt content to user level
        adaptation_task = Task(
            description=f"""
            Analyze all gathered information about '{topic}' and determine the optimal presentation for a {level} learner.
            """,
            expected_output="""
            A detailed adaptation plan including:
            - Core concepts with appropriate depth
            - Content progression strategy
            - Integration points for visuals and technical content
            - Effective analogies and examples for this level
            """,
            agent=self.agents["adaptation_specialist"],
            context=[research_task, visual_task, technical_task]
        )
        
        # Task 5: Structure and organize the complete content
        content_task = Task(
            description=f"""
            Create comprehensive educational content about '{topic}' for a {level} learner.
            """,
            expected_output="""
            Complete educational content including:
            - Level-appropriate introduction and overview
            - Core concepts with explanations at correct depth
            - Integrated descriptions of visual elements
            - Technical content with appropriate complexity
            - Practical examples tailored to level
            """,
            agent=self.agents["content_creator"],
            context=[research_task, visual_task, technical_task, adaptation_task]
        )
        
        # Create and execute the crew workflow
        crew = Crew(
            agents=list(self.agents.values()),
            tasks=[research_task, visual_task, technical_task, adaptation_task, content_task],
            verbose=True,
            process=Process.sequential
        )
        
        # Execute and return results
        result = crew.kickoff()
        
        # Return the final output
        if hasattr(result, 'raw_output'):
            return result.raw_output
        elif hasattr(result, 'output'):
            return result.output
        else:
            return str(result)

# Example usage
def get_educational_content(topic, level):
    """Get educational content for a specified topic at the requested level"""
    generator = AdvancedContentGenerator()
    return generator.generate_content(topic, level)

if __name__ == "__main__":
    # Get topic and level from user
    user_topic = input("Enter the educational topic you want to learn about: ")
    user_level = input("Enter your knowledge level (beginner, intermediate, advanced): ")
    
    # Generate and display content
    content = get_educational_content(user_topic, user_level)
    print(f"\nEducational Content on: {user_topic} (Level: {user_level})")
    print("-" * 50)
    print(content)