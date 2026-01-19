from src.utils.logger import setup_logger
from typing import List, Dict
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from config.settings import settings

logger = setup_logger(
    name="question_generator",
    log_dir="logs/question_generator_agent",
)

class QuestionGenerator:
    """Generate interview questions based on candidate profile."""
    
    def __init__(self):
        """Initialize question generator."""
        self.llm = self._initialize_llm()
        self.question_types = settings.get('interview.question_types')
        self.min_questions = settings.get('interview.min_questions',5)
        self.max_questions = settings.get('interview.max_questions',15)
    
    def _initialize_llm(self):
        """Initialize LLM based on configuration."""
        provider = settings.get('llm.provider', 'groq')
        
        if provider == 'groq':
            api_key = settings.groq_api_key
            if not api_key:
                raise ValueError("GROQ_API_KEY not found in environment variables")
            
            return ChatGroq(
                api_key=api_key,
                model=settings.get('llm.model', 'mixtral-8x7b-32768'),
                temperature=settings.get('llm.temperature', 0.7),
                max_tokens=settings.get('llm.max_tokens', 2048)
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    def generate_questions(
        self,
        candidate_info: Dict,
        role: str,
        num_questions: int = None
    ) -> List[Dict[str, str]]:
        """
        Generate interview questions based on candidate profile.
        
        Args:
            candidate_info: Dictionary containing candidate information
            role: Role being applied for
            num_questions: Number of questions to generate
            
        Returns:
            List of question dictionaries with type and text
        """
        if num_questions is None:
            num_questions = self.max_questions
        
        num_questions = max(self.min_questions, min(num_questions, self.max_questions))
        
        logger.info(f"Generating {num_questions} questions for role: {role}")
        
        # Determine difficulty level based on experience
        experience_years = candidate_info.get('experience_years', 0)
        difficulty = self._determine_difficulty(experience_years)
        
        # Create prompt
        prompt = self._create_question_prompt(
            candidate_info,
            role,
            difficulty,
            num_questions
        )
        
        # Generate questions
        try:
            response = self.llm.invoke(prompt)
            questions = self._parse_questions(response.content)
            
            logger.info(f"Generated {len(questions)} questions")
            return questions
            
        except Exception as e:
            logger.error(f"Error generating questions: {e}")
            # Return fallback questions
            return self._get_fallback_questions(role, num_questions)
    
    def _determine_difficulty(self, experience_years: int) -> str:
        """Determine difficulty level based on experience."""
        difficulty_levels = settings.get('interview.difficulty_levels', {})
        
        for level, (min_exp, max_exp) in difficulty_levels.items():
            if min_exp <= experience_years < max_exp:
                return level
        
        return 'mid'
    
    def _create_question_prompt(
        self,
        candidate_info: Dict,
        role: str,
        difficulty: str,
        num_questions: int
    ) -> str:
        """Create prompt for question generation."""
        skills = ', '.join(candidate_info.get('skills', []))
        experience = candidate_info.get('experience_years', 'unknown')
        education = ', '.join(candidate_info.get('education', []))
        
        prompt = f"""
You are an expert interviewer specializing in the role of **{role}**.

IMPORTANT RULES (MUST FOLLOW):
- If the role is NON-TECHNICAL (e.g. Hotel Management, Operations, HR, Sales, Marketing),
  ALL questions must be practical, real-world, and domain-specific.
- Questions MUST reflect how this job is actually performed in the real world.

Candidate Profile:
- Role: {role}
- Experience Level: {experience} years
- Skills: {skills}
- Education: {education}
- Difficulty Level: {difficulty}

Question Types to Generate:
{', '.join(self.question_types)}

STRUCTURE REQUIREMENTS:
- Group questions by type (ALL technical together, ALL behavioral together, etc.)
- Generate EXACTLY {num_questions} questions total
- Distribute questions evenly across question types

QUESTION TYPE GUIDELINES:
- Technical:
  - Must be domain-specific to {role}
  - Example:
    - Hotel Management → guest handling, operations, staff coordination, crisis handling
    - Marketing → campaign strategy, analytics interpretation
    - ML Engineer → model evaluation, deployment, data issues
- Behavioral:
  - Past experiences, teamwork, conflict, leadership
- Situational:
  - “What would you do if…” real workplace scenarios
- Experience-based:
  - Deep dive into candidate’s past roles, responsibilities, decisions

FORMAT (STRICT):
1. [Technical]
   Question: <question text>
   Evaluating: <skill or competency>

2. [Behavioral]
   Question: <question text>
   Evaluating: <skill or competency>

QUALITY BAR:
- Questions must be realistic, job-relevant, and interview-ready
- Avoid generic or textbook questions
- NO coding / NO algorithms unless role demands it
"""

        return prompt
    
    def _parse_questions(self, response_text: str) -> List[Dict[str, str]]:
        questions = []
        current = None

        for raw_line in response_text.splitlines():
            line = raw_line.strip()

            if not line:
                continue

            # 1. New question block
            if line[0].isdigit() and "[" in line and "]" in line:
                if current:
                    questions.append(current)

                q_type = line[line.find("[") + 1 : line.find("]")].lower()

                current = {
                    "type": q_type,
                    "question": "",
                    "evaluating": "",
                }
                continue

            if not current:
                continue

            # 2. Question text (support multiple formats)
            if line.lower().startswith("question:"):
                current["question"] = line.split(":", 1)[1].strip()

            elif line.lower().startswith("q:"):
                current["question"] = line.split(":", 1)[1].strip()

            # 3. Evaluating line
            elif line.lower().startswith("evaluating:"):
                current["evaluating"] = line.split(":", 1)[1].strip()

            # 4. Fallback: plain sentence line
            elif not current["question"] and len(line) > 10:
                current["question"] = line

        if current:
            questions.append(current)

        return questions

    
    def _get_fallback_questions(self, role: str, num_questions: int) -> List[Dict[str, str]]:
        """Get fallback questions if generation fails."""
        fallback = [
            {
                'type': 'experience_based',
                'question': f'Tell me about your experience relevant to the {role} position.',
                'evaluating': 'Relevant experience and communication skills'
            },
            {
                'type': 'technical',
                'question': 'What technical skills do you consider your strongest, and can you provide an example of how you\'ve used them?',
                'evaluating': 'Technical competency and practical application'
            },
            {
                'type': 'behavioral',
                'question': 'Describe a challenging project you worked on. What was your role and how did you overcome obstacles?',
                'evaluating': 'Problem-solving and resilience'
            },
            {
                'type': 'situational',
                'question': 'How would you approach learning a new technology or framework required for this role?',
                'evaluating': 'Learning ability and adaptability'
            },
            {
                'type': 'behavioral',
                'question': 'Tell me about a time when you had to work with a difficult team member. How did you handle it?',
                'evaluating': 'Interpersonal skills and conflict resolution'
            },
        ]
        
        return fallback[:num_questions]