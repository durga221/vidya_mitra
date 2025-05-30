import os
import json
from datetime import datetime
from typing import Optional, Dict, Any, List


from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel


import google.generativeai as genai
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool
from dotenv import load_dotenv()


load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")


genai.configure(api_key=GEMINI_API_KEY)
os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY
os.environ["SERPER_API_KEY"] = SERPER_API_KEY


serper_tool = SerperDevTool()


app = FastAPI(title="Multilingual Agent Chatbot API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    query: str
    language: str = "English"
    api_key: Optional[str] = None
    debug: bool = False

class ChatResponse(BaseModel):
    response: str
    debug_info: Optional[Dict[str, Any]] = None

class DebugRequest(BaseModel):
    api_key: str



class ChatMemory:
    """A class to handle persistent chat memory across sessions using API key"""
    
    def __init__(self, api_key="default_api_key", memory_file="chat_memory.json"):
        self.api_key = api_key
        self.memory_file = memory_file
        self.memories = self._load_memories()
        
    def _load_memories(self):
        """Load existing memories from file"""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r') as f:
                    all_memories = json.load(f)
                
                # Return this API key's memories or create new entry
                return all_memories.get(self.api_key, {"session": {"messages": []}, "facts": []})
            else:
                return {"session": {"messages": []}, "facts": []}
        except Exception as e:
            print(f"Error loading memories: {str(e)}")
            return {"session": {"messages": []}, "facts": []}
    
    def _save_memories(self):
        """Save memories to file"""
        try:
            # Load all API keys' data first
            all_memories = {}
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r') as f:
                    all_memories = json.load(f)
            
            # Update this API key's data
            all_memories[self.api_key] = self.memories
            
            # Save back to file
            with open(self.memory_file, 'w') as f:
                json.dump(all_memories, f, indent=2)
        except Exception as e:
            print(f"Error saving memories: {str(e)}")
    
    def initialize_session(self, language):
        """Initialize or continue the existing session"""
        if "session" not in self.memories:
            self.memories["session"] = {
                "timestamp": datetime.now().isoformat(),
                "language": language,
                "messages": []
            }
        else:
            # Just update the language in case it changed
            self.memories["session"]["language"] = language
            
        self._save_memories()
    
    def add_message(self, role, content):
        """Add a message to the session"""
        self.memories["session"]["messages"].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self._save_memories()
    
    def add_fact(self, fact):
        """Add a fact about the user for long-term memory"""
        self.memories["facts"].append({
            "content": fact,
            "timestamp": datetime.now().isoformat()
        })
        self._save_memories()
    
    def get_session_history(self, limit=None):
        """Get the complete message history for the session with optional limit"""
        if limit is None:
            return self.memories["session"]["messages"]
        return self.memories["session"]["messages"][-limit:]
    
    def get_facts(self):
        """Get all facts about the user"""
        return self.memories["facts"]

    def get_formatted_memory_context(self, history_limit=None):
        """Format memory as context for the model with optional history limit"""
        context = "User's previous information:\n"
        
        # Add facts about the user
        if self.memories["facts"]:
            context += "Facts about the user:\n"
            for fact in self.memories["facts"]:
                context += f"- {fact['content']}\n"
            context += "\n"
        
        # Add conversation history with optional limit
        messages = self.get_session_history(history_limit)
        if len(messages) > 0:
            context += "Conversation history:\n"
            for msg in messages:
                context += f"{msg['role'].title()}: {msg['content']}\n"
        
        return context
    
    def get_recent_messages(self, count=5):
        """Get only the most recent messages"""
        messages = self.get_session_history()
        return messages[-count:] if len(messages) >= count else messages
    
    def search_memory(self, query, limit=10):
        """Semantic search of past messages based on relevance to the query"""
        messages = self.get_session_history()
        
        if not messages:
            return []
            
        
        system_prompt = """
        You are a memory retrieval expert. Rank the following conversation messages 
        by their relevance to the user's current query. Return a JSON list of 
        indices in order of relevance (most relevant first).
        """
        
        
        formatted_messages = "\n".join([
            f"[{i}] {msg['role'].title()}: {msg['content']}" 
            for i, msg in enumerate(messages)
        ])
        
        
        prompt = f"""
        User's current query: "{query}"
        
        Conversation messages:
        {formatted_messages}
        
        Return the indices of the most relevant messages as a JSON list, 
        ordered from most to least relevant. For example: [3, 1, 4]
        Only include indices that are genuinely relevant to the query.
        """
        
        
        try:
            llm = GeminiLLM()  
            response = llm.generate([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ])
            
            
            import re
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                indices = json.loads(json_match.group(0))
                
               
                results = []
                for idx in indices:
                    if 0 <= idx < len(messages):
                        results.append(messages[idx])
                        if len(results) >= limit:
                            break
                return results
        except Exception as e:
            print(f"Error in semantic search: {str(e)}")
        
        # Fallback to keyword search if semantic search fails
        return self._keyword_search(query, limit)

    def _keyword_search(self, query, limit=10):
        """Simple keyword-based search (fallback method)"""
        results = []
        messages = self.get_session_history()
        
        query_terms = query.lower().split()
        
        for msg in messages:
            content = msg['content'].lower()
           
            if any(term in content for term in query_terms):
                results.append(msg)
                if len(results) >= limit:
                    break
                    
        return results


class GeminiLLM:
    """Wrapper for the Gemini model integration with CrewAI"""
    
    def __init__(self, model_name="gemini/gemini-2.0-flash-lite"):
        self.model_name = model_name
        self.gemini_model = genai.GenerativeModel("gemini-2.0-flash-lite")
    
    def generate(self, messages):
        # Format messages for Gemini
        formatted_prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
        response = self.gemini_model.generate_content(formatted_prompt)
        return response.text
        
    def chat(self, messages):
        return self.generate(messages)


class MemoryRetrievalAgent:
    """Agent that determines whether and how to use memory based on the context"""
    
    def __init__(self, llm, memory):
        self.llm = llm
        self.memory = memory
        
    def analyze_query(self, query):
        """Analyze if the query requires memory lookup and how much history to retrieve"""
        
        system_prompt = """
        You are a memory retrieval expert. Your job is to analyze a user query and determine:
        1. Whether we need to search through past conversation history or if this is a standalone question
        2. Whether we need user facts/preferences from memory
        3. How many previous conversation turns we should include for context
        
        Respond with JSON in this exact format:
        {
            "needs_history": true/false,
            "needs_facts": true/false,
            "history_turns": <number of turns or "all">,
            "search_terms": ["list", "of", "relevant", "terms"],
            "explanation": "brief explanation of your decision"
        }
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"User query: {query}\nAnalyze this query and determine memory requirements:"}
        ]
        
        response = self.llm.generate(messages)
        
        try:
           
            import re
            json_match = re.search(r'({.*})', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                decision = json.loads(json_str)
                return decision
            else:
                
                return {
                    "needs_history": True,
                    "needs_facts": True,
                    "history_turns": 3,
                    "search_terms": query.split(),
                    "explanation": "Failed to parse decision, using default partial memory retrieval"
                }
        except Exception as e:
            print(f"Error parsing memory agent response: {str(e)}")
            
            return {
                "needs_history": True,
                "needs_facts": True,
                "history_turns": 3,
                "search_terms": query.split(),
                "explanation": "Error in parsing, using default partial memory retrieval"
            }
    
    def retrieve_relevant_memory(self, query):
        """Get the most relevant memory context based on the query"""
        
        decision = self.analyze_query(query)
        
        
        print(f"Memory retrieval decision: {decision['explanation']}")
        
        
        context = ""
        
        
        if decision["needs_facts"]:
            facts = self.memory.get_facts()
            if facts:
                context += "Facts about the user:\n"
                for fact in facts:
                    context += f"- {fact['content']}\n"
                context += "\n"
        
        
        if decision["needs_history"]:
            
            if decision["history_turns"] == "all":
                messages = self.memory.get_session_history()
            else:
                try:
                    turns = int(decision["history_turns"])
                    messages = self.memory.get_session_history(turns * 2) 
                except:
                    
                    messages = self.memory.get_recent_messages(6)
            
            #
            if messages:
                context += "Relevant conversation history:\n"
                for msg in messages:
                    context += f"{msg['role'].title()}: {msg['content']}\n"
            
            
            if decision.get("search_terms") and len(decision["search_terms"]) > 0:
                
                search_query = " ".join(decision["search_terms"])
                search_results = self.memory.search_memory(search_query)
                
                if search_results and len(search_results) > 0:
                    
                    unique_results = []
                    for msg in search_results:
                        if msg not in messages:  
                            unique_results.append(msg)
                    
                    if unique_results:
                        context += "\nAdditional relevant messages found in history:\n"
                        for msg in unique_results:
                            context += f"{msg['role'].title()}: {msg['content']}\n"
        
        return {
            "context": context,
            "decision": decision
        }


class MultilingualAgentChatbot:
    """Chatbot that intelligently uses conversation history and uses agents for complex queries"""
    
    def __init__(self, language="English", api_key=None):
       
        self.api_key = api_key or f"api_key_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.language = language
        self.memory = ChatMemory(api_key=self.api_key)
        self.memory.initialize_session(language)
        self.llm = GeminiLLM()
        
      
        self.memory_agent = MemoryRetrievalAgent(self.llm, self.memory)
        
        
        system_prompt = f"You are a multilingual chatbot. Respond to all my messages in {language}. Be friendly and helpful."
        welcome_message = f"I'll be your multilingual assistant, responding in {language}. How can I help you today?"
        
       
        self.memory.add_message("system", system_prompt)
        self.memory.add_message("assistant", welcome_message)
        
        
        self.response_agent = self._create_response_agent()
        
    def _create_response_agent(self):
        """Create a smart agent that can use web search when needed"""
        smart_agent = Agent(
            role=f"Multilingual {self.language} Assistant",
            goal=f"Provide accurate and helpful responses in {self.language} while maintaining conversation context",
            backstory=f"You are a knowledgeable assistant who responds in {self.language}. "
                      f"You first try to answer questions using your own knowledge. "
                      f"If you don't know the answer, you use web search to find information.",
            tools=[serper_tool],
            llm=self.llm,
            verbose=True
        )
        return smart_agent
    
    def extract_possible_facts(self, message):
        """Analyze user message to identify potential facts to remember"""
        system_prompt = """
        You are a memory extraction expert. Your job is to analyze a user message and extract
        important facts about the user that should be remembered for future reference.
        
        Examples of important facts:
        - Personal information (name, location, preferences)
        - Specific interests or hobbies
        - Important life events
        - Strong opinions or values
        
        Respond with a JSON array of extracted facts, or an empty array if none found:
        ["fact 1", "fact 2", ...]
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"User message: {message}\nExtract any important facts:"}
        ]
        
        try:
            response = self.llm.generate(messages)
            
            # Extract JSON array from response
            import re
            json_match = re.search(r'(\[.*\])', response, re.DOTALL)
            if json_match:
                facts = json.loads(json_match.group(1))
                return facts
        except Exception as e:
            print(f"Error in fact extraction: {str(e)}")
        
        
        facts = []
        
        
        if "my name is" in message.lower() or "i am called" in message.lower():
            facts.append(f"User's name mentioned in message: '{message}'")
        
        if "i like" in message.lower() or "i enjoy" in message.lower() or "i love" in message.lower():
            facts.append(f"User's preference mentioned: '{message}'")
            
        if "i live in" in message.lower() or "i'm from" in message.lower() or "i am from" in message.lower():
            facts.append(f"User's location mentioned: '{message}'")
            
        return facts
    
    def send_message(self, user_message):
        """Process user message and generate response using intelligent memory usage"""
     
        facts = self.extract_possible_facts(user_message)
        for fact in facts:
            self.memory.add_fact(fact)
        
        
        self.memory.add_message("user", user_message)
        
        # Use the memory agent to determine what memory is relevant
        memory_result = self.memory_agent.retrieve_relevant_memory(user_message)
        relevant_context = memory_result["context"]
        memory_decision = memory_result["decision"]
        
        # Log memory usage (for debugging)
        print(f"Memory usage: {memory_decision['explanation']}")
        
        # Always include at least the most recent messages for continuity
        recent_messages = ""
        last_few = self.memory.get_recent_messages(3)
        if last_few:
            recent_messages = "\nMost recent messages:\n"
            for msg in last_few:
                recent_messages += f"{msg['role'].title()}: {msg['content']}\n"
        
        # Determine if we should use web search based on the query
        system_prompt = """
        You are a query analysis expert. Analyze this user query and determine if it likely requires 
        recent information from the web or specialized knowledge that might benefit from web search.
        
        Respond with a simple "yes" or "no".
        """
        
        search_decision_messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"User query: {user_message}\nDoes this likely need web search?"}
        ]
        
        search_decision = "no"
        try:
            search_response = self.llm.generate(search_decision_messages)
            if "yes" in search_response.lower():
                search_decision = "yes"
        except:
            # Default to no if there's an error
            pass
        
        # Create a task for the agent
        response_task = Task(
            description=f"""
            You need to respond to the user's query in {self.language}.
            
            User's query: "{user_message}"
            
            {relevant_context}
            {recent_messages}
            
            First, try to answer the question based on what you know and the conversation context provided.
            {"If you're uncertain about the answer or the information might be outdated, use the SerperDevTool to search the web." if search_decision == "yes" else ""}
            
            Remember to always respond in {self.language}.
            """,
            expected_output=f"""
            A helpful and accurate response to the user's query in {self.language}.
            {"If web search was used, include a brief mention that you looked up the information." if search_decision == "yes" else ""}
            Ensure your response is consistent with any previous conversation context.
            """,
            agent=self.response_agent
        )
        
        # Execute the agent task
        crew = Crew(
            agents=[self.response_agent],
            tasks=[response_task],
            verbose=True,
            process=Process.sequential
        )
        
        result = crew.kickoff()
        
        # Extract response
        if hasattr(result, 'raw_output'):
            response = result.raw_output
        elif hasattr(result, 'output'):
            response = result.output
        else:
            response = str(result)
        
        # Add response to memory
        self.memory.add_message("assistant", response)
        
        return response
    
    def get_history(self):
        """Return the complete chat history"""
        return self.memory.get_session_history()
    
    def get_debug_info(self):
        """Return debug information about this chatbot instance"""
        facts = self.memory.get_facts()
        history = self.memory.get_session_history()
        
        return {
            "api_key": self.api_key,
            "language": self.language,
            "facts_count": len(facts),
            "conversation_turns": len(history) // 2,
            "recent_facts": [fact["content"] for fact in facts[-3:]] if facts else [],
            "recent_messages": [
                {"role": msg["role"], "content": msg["content"]} 
                for msg in self.memory.get_recent_messages(3)
            ]
        }

# Store active chatbot instances
chatbot_instances = {}

def get_or_create_chatbot(api_key=None, language="English"):
    """Get an existing chatbot instance or create a new one"""
    
    if not api_key:
        api_key = f"default_api_key"
    
    
    if api_key not in chatbot_instances:
        chatbot_instances[api_key] = MultilingualAgentChatbot(language, api_key)
    elif chatbot_instances[api_key].language != language:
       
        chatbot_instances[api_key].language = language
        chatbot_instances[api_key].memory.initialize_session(language)
        
    return chatbot_instances[api_key]


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        
        chatbot = get_or_create_chatbot(request.api_key, request.language)
        
       
        response = chatbot.send_message(request.query)
        
        
        if request.debug:
            return ChatResponse(
                response=response,
                debug_info=chatbot.get_debug_info()
            )
        else:
            return ChatResponse(response=response)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing request: {str(e)}"
        )

@app.post("/add-fact")
async def add_fact(request: Request):
    data = await request.json()
    api_key = data.get("api_key", "default_api_key")
    fact = data.get("fact")
    
    if not fact:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Fact is required"
        )
    
  
    if api_key in chatbot_instances:
        chatbot = chatbot_instances[api_key]
        chatbot.memory.add_fact(fact)
        return {"success": True, "message": f"Fact added: {fact}"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active session found for this API key"
        )

@app.post("/debug", response_model=Dict[str, Any])
async def debug_endpoint(request: DebugRequest):
    api_key = request.api_key
    
    if api_key in chatbot_instances:
        return chatbot_instances[api_key].get_debug_info()
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active session found for this API key"
        )

@app.get("/")
async def root():
    return {"message": "Multilingual Agent Chatbot API is running. Send POST requests to /chat endpoint."}


import uvicorn
uvicorn.run(app, host="localhost", port=8001)
