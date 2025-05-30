from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import google.generativeai as ai
import re
import ast
import json
from PIL import Image
import base64
from io import BytesIO
from dotenv import load_dotenv
import os


load_dotenv()


SERVER_URL = 'localhost'
PORT = '8900'
ENV = 'dev'
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')


ai.configure(api_key=GEMINI_API_KEY)
model = ai.GenerativeModel(model_name="gemini-1.5-flash")


class ImageInfo(BaseModel):
    image: str
    dict_of_vars: dict
    action: str


def process_image(img: Image, dict_of_vars: dict, action: str):
    dict_of_vars_to_str = json.dumps(dict_of_vars, ensure_ascii=False)
    
    if action == "Mathematics":
        prompt = (
            "You are given an image containing mathematical expressions, equations, or graphical problems. "
            "Solve them following the PEMDAS rule: Parentheses, Exponents, Multiplication/Division (left to right), "
            "and Addition/Subtraction (left to right). After solving, explain the steps taken to reach the solution in detail. "
            "The output must contain the final result as well as a step-by-step breakdown of how the solution was reached.\n\n"
            
            "Example:\n"
            "Q1. 2 + 3 * 4 => (3 * 4) = 12; 2 + 12 = 14.\n"
            "Explanation:\n"
            "1. First, multiply 3 by 4 to get 12.\n"
            "2. Then, add 2 to 12 to get 14.\n"
            "3.Final result: 14.\n\n"

            "Q2. 2 + 3 + 5 * 4 - 8 / 2 => (5 * 4) = 20; (8 / 2) = 4; (2 + 3) = 5; 5 + 20 = 25; 25 - 4 = 21.\n"
            "Explanation:\n"
            "1. First, multiply 5 by 4 to get 20.\n"
            "2. Then, divide 8 by 2 to get 4.\n"
            "3. Add 2 and 3 to get 5.\n"
            "4. Now, add 5 and 20 to get 25.\n"
            "5. Finally, subtract 4 from 25 to get 21.\n"
            "6.Final result: 21.\n\n"

            f"Use the following dictionary of user-assigned variables if any appear in the expression: {dict_of_vars_to_str}.\n"
            "Escape characters like \\f and \\n should be written as \\\\f and \\\\n.\n"
            "DO NOT USE backticks or Markdown formatting. Ensure all dictionary keys and values are properly quoted for easy parsing with Python's ast.literal_eval.\n"
        )

    elif action == "Aptitude":
        prompt = (
            "You are an expert at solving all logical reasoning problems especially pattern-based reasoning problems. When presented with an image containing mathematical patterns, number series, or logical puzzles, analyze and solve them using the following structured approach:"

            "PROBLEM TYPES:"
            "1. Matrix Patterns:"
            "   - Grid arrangements with numbers/symbols"
            "   - Missing number in a cell"
            "   - Pattern follows row/column-wise operations"

            "2. Number Series:"
            "   - Linear/geometric progressions"
            "   - Mixed operations series"
            "   - Pattern-based sequences"

            "3. Circular/Geometric Arrangements:"
            "   - Numbers arranged in circles/shapes"
            "   - Relationship between adjacent numbers"
            "   - Center-to-outer patterns"

            "SOLUTION APPROACH:"

            "1. Pattern Identification:"
            "   - Examine relationships between given numbers"
            "   - Check basic operations (±, ×, ÷)"
            "   - Look for squares, cubes, or special sequences"
            "   - Consider position-based patterns"

            "2. Pattern Verification:"
            "   - Test pattern on known values"
            "   - Verify pattern works for all given examples"
            "   - Check for multiple possible patterns"

            "3. Solution Generation:"
            "   - Apply verified pattern to find missing value"
            "   - Double-check calculation"
            "   - Verify answer matches given options (if provided)"

            "OUTPUT FORMAT:"
            "Return a DICT with the following structure:"
            "{"
            "    'pattern_type': 'type of pattern identified',"
            "    'pattern_rules': ['rule1', 'rule2', ...],"
            "    'solution_steps': ["
            "        'step1: examination of values',"
            "        'step2: pattern identification',"
            "        'step3: verification',"
            "        'step4: final calculation'"
            "    ],"
            "    'missing_value': 'calculated answer',"
            "    'verification': 'how answer fits pattern',"
            "    'alternatives_considered': ['other patterns checked']"
            "}"

            "Examples:"  
            "eXAMPLE #1: \"3 4 5\""
            "	     \"6 8 10\""
            "	     \"7 24 25\""
            "	     \"12 ? 13\""  
            "\"Formula: Sum of the squares of the first two columns = Square of the third column.\""  
            "\"1st Row: 3² + 4² = 5² → 9 + 16 = 25 → 25 = 25 (LHS = RHS)\""  
            "\"2nd Row: 6² + 8² = 10² → 36 + 64 = 100 → 100 = 100 (LHS = RHS)\""  
            "\"3rd Row: 7² + 24² = 25² → 49 + 576 = 625 → 625 = 625 (LHS = RHS)\""  
            "\"4th Row: 12² + ?² = 13² → 144 + ?² = 169 → ?² = 169 - 144 → ?² = 25 → ? = √25 = 5\""  
            "\"So 5 is the correct Answer.\""

            "Example 2: For a number series problem like:"  
            "\"Given series: 2, 4, 9, 20, 40, ?\""

            "Solution:"  
            "\"Step 1: Analyze the differences between consecutive terms:\""
            "\"4 - 2 = 2\""
            "\"9 - 4 = 5\""
            "\"20 - 9 = 11\""
            "\"40 - 20 = 20\""

            "\"Observation: The differences are increasing as follows: 2, 5, 11, 20.\""

            "\"Step 2: Analyze the differences of these increments:\""
            "\"5 - 2 = 3\""
            "\"11 - 5 = 6\""
            "\"20 - 11 = 9\""

            "\"Observation: The differences (3, 6, 9) are increasing by 3 each time, suggesting a quadratic progression in the differences.\""

            "\"Step 3: Predict the next difference:\""
            "\"The next difference will be 20 + 12 = 32.\""

            "\"Step 4: Calculate the next term:\""
            "\"40 + 32 = 72.\""

            "\"Final Answer: The next number in the series is 72.\""

            "\"Verification: Using the identified quadratic progression in differences, the series matches perfectly: 2, 4, 9, 20, 40, 72.\""

            "IMPORTANT RULES:"
            "1. Always check multiple possible patterns"
            "2. Verify pattern works for all given examples"
            "3. Consider both simple and complex relationships"
            "4. Look for patterns in multiple directions"
            "5. Test answer in context of full pattern"
            "6. Consider special mathematical properties (squares, primes, etc.)"
            "7. For options-based questions, verify only one answer fits pattern"

            "Note: If multiple valid patterns exist, list all possibilities and explain why one particular solution is most likely correct based on the given options or context."
        )
    else:
        prompt = "Solve the problem in the image systematically."

    try:
        response = model.generate_content([prompt, img])
        print("Raw response:", response.text)
        
        
        text = response.text.strip()
        
        
        steps = []
        final_result = None
        
        
        step_matches = re.finditer(r'(\d+)\.\s*([^\n]+)', text)
        for match in step_matches:
            steps.append(match.group(2).strip())
        
        
        final_match = re.search(r'Final Result:?\s*(\d+(?:\.\d+)?)', text)
        if final_match:
            final_result = final_match.group(1)
        
        
        answer = {
            'solution': final_result,
            'steps': steps,
            'explanation': text,
            'assign': False
        }
        print(answer)
        return [answer]  

    except Exception as error:
        print(f"Error processing image: {error}")
        return [{
            'error': str(error),
            'solution': 'Error in processing',
            'explanation': 'An error occurred while processing the response',
            'assign': False
        }]


router = APIRouter()

@router.post('')
async def run(data: ImageInfo):
    
    image_data = base64.b64decode(data.image.split(",")[1])
    image_bytes = BytesIO(image_data)
    
    
    image = Image.open(image_bytes)
    responses = process_image(image, dict_of_vars=data.dict_of_vars, action=data.action)
    
    
    data_list = []
    for response in responses:
        data_list.append(response)
    
    return {
        "message": "Image processed",
        "data": data_list,
        "status": "success"
    }


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/")
async def health():
    return {"message": "server is running fine andi...!"}


app.include_router(router, prefix="/calculate", tags=["calculate"])


if __name__ == "__main__":
    uvicorn.run("canvas:app", host=SERVER_URL, port=int(PORT), reload=(ENV == "dev"))