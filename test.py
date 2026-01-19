# # #Test Resume Parser
# from src.parsers.resume_parser import ResumeParser
# from pprint import pprint

# resume_path = "/Users/shriyansh/Documents/Finomics/Task_2/AI-Interview-Question-Generator/test/Umang Supplychain Analyst Resume.pdf"

# # parser = ResumeParser()
# # result = parser.parse(resume_path)

# # pprint(result)



# # Test Generator
# from src.parsers.resume_parser import ResumeParser
# from src.generators.question_generator import QuestionGenerator

# def main():
#     # 1. Parse resume
#     parser = ResumeParser()
#     candidate_info = parser.parse(
#         resume_path
#     )

#     # 2. Initialize question generator
#     generator = QuestionGenerator()

#     # 3. Generate questions
#     questions = generator.generate_questions(
#         candidate_info=candidate_info,
#         role=candidate_info["job_role"],
#         num_questions=7
#     )

#     # 4. Print results
#     print("\n===== GENERATED INTERVIEW QUESTIONS =====\n")
#     for i, q in enumerate(questions, 1):
#         print(f"{i}. [{q['type'].upper()}]")
#         print(f"Q: {q['question']}")
#         print(f"Evaluating: {q['evaluating']}\n")

# if __name__ == "__main__":
#     main()


# Test Interview Agent
from src.agent.interview_agent import InterviewAgent

def main():
    agent = InterviewAgent()

    # -------- INPUT --------
    resume_path = "/Users/shriyansh/Documents/Finomics/Task_2/AI-Interview-Question-Generator/test/Umang Supplychain Analyst Resume.pdf"
    # change path if needed

    # -------- RUN AGENT --------
    result = agent.run(resume_path)

    print("\n===== AGENT STATUS =====")
    print("Status:", result["status"])

    if result["status"] != "completed":
        print("Error:", result.get("error"))
        return

    # -------- SUMMARY --------
    candidate = result["candidate_info"]

    print("\n===== CANDIDATE SUMMARY =====")
    print("Name:", candidate.get("name"))
    print("Role:", candidate.get("job_role"))
    print("Experience:", candidate.get("experience"))
    print("Skills:", ", ".join(candidate.get("skills", [])))

    # -------- QUESTIONS --------
    print("\n===== GENERATED INTERVIEW QUESTIONS =====")
    for i, q in enumerate(result["questions"], 1):
        print(f"\n{i}. [{q['type'].upper()}]")
        print("Q:", q["question"])
        print("Evaluating:", q["evaluating"])


if __name__ == "__main__":
    main()
