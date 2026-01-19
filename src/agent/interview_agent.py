from src.utils.logger import setup_logger
from typing import TypedDict, Annotated, List, Dict
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from src.parsers.resume_parser import ResumeParser
from src.generators.question_generator import QuestionGenerator
from config.settings import settings
import operator

logger = setup_logger(
    name="interview_agent",
    log_dir="logs/interview_agent",
)

class InterviewState(TypedDict):
    resume_path: str
    candidate_info: Dict
    questions: List[Dict[str, str]]
    status: str
    error: str


class InterviewAgent:
    """
    Sequential Interview Question Generator Agent
    (No user answers, no interaction)
    """

    def __init__(self):
        self.resume_parser = ResumeParser()
        self.question_generator = QuestionGenerator()
        self.graph = self._build_graph()

    # =========================
    # GRAPH
    # =========================

    def _build_graph(self):
        workflow = StateGraph(InterviewState)

        workflow.add_node("parse_resume", self._parse_resume_node)
        workflow.add_node("generate_questions", self._generate_questions_node)

        workflow.set_entry_point("parse_resume")

        workflow.add_edge("parse_resume", "generate_questions")
        workflow.add_edge("generate_questions", END)

        return workflow.compile()

    # =========================
    # NODES
    # =========================

    def _parse_resume_node(self, state: InterviewState) -> InterviewState:
        logger.info("Node: Parsing resume")

        try:
            candidate_info = self.resume_parser.parse(state["resume_path"])

            # HARD STOP if OCR + PDF extraction failed
            if not candidate_info.get("raw_text"):
                state["status"] = "failed"
                state["error"] = "PDF not accessible or text extraction failed"
                return state

            state["candidate_info"] = candidate_info
            state["status"] = "resume_parsed"

        except Exception as e:
            logger.error(f"Resume parsing failed: {e}")
            state["status"] = "failed"
            state["error"] = str(e)

        return state

    def _generate_questions_node(self, state: InterviewState) -> InterviewState:
        logger.info("Node: Generating questions")

        try:
            candidate_info = state["candidate_info"]
            role = candidate_info.get("job_role", "General Candidate")

            questions = self.question_generator.generate_questions(
                candidate_info=candidate_info,
                role=role
            )

            state["questions"] = questions
            state["status"] = "completed"

        except Exception as e:
            logger.error(f"Question generation failed: {e}")
            state["status"] = "failed"
            state["error"] = str(e)

        return state

    # =========================
    # PUBLIC API
    # =========================

    def run(self, resume_path: str) -> Dict:
        logger.info("Starting Interview Question Generator Agent")

        initial_state: InterviewState = {
            "resume_path": resume_path,
            "candidate_info": {},
            "questions": [],
            "status": "initialized",
            "error": "",
        }

        final_state = self.graph.invoke(initial_state)

        return final_state