"""CLI wrapper around the workflow orchestrator."""

from __future__ import annotations

from pathlib import Path

from backend.app.workflow import WorkflowArtifacts, analyze_inputs


def run_job_readiness_engine_orchestrator(
    resume_pdf_path: str,
    job_description: str,
    *,
    plan_output_path: str | Path | None = "study_plan.md",
) -> str:
    """Execute the full workflow via the workflow orchestrator."""

    print("✨ Starting Job Readiness Intelligence Engine Workflow...")
    try:
        artifacts: WorkflowArtifacts = analyze_inputs(
            resume_pdf_path=resume_pdf_path,
            job_description_text=job_description,
            plan_output_path=plan_output_path,
        )
    except Exception as exc:  # pragma: no cover - CLI helper
        print(f"Workflow failed: {exc}")
        return "Workflow failed."

    print("\n--- Outputs ---")
    print(f"Resume XML length: {len(artifacts.resume_xml)} characters")
    print(f"Job skills extracted: {len(artifacts.job_skills)}")
    print(f"Resume skills scored: {len(artifacts.resume_skills)}")
    print(f"Gap XML length: {len(artifacts.skill_gap_xml)} characters")
    if artifacts.study_plan:
        print("Study plan generated successfully.\n")
        if artifacts.plan_path:
            print(f"Study plan saved to: {artifacts.plan_path}\n")
        return artifacts.study_plan
    return "Workflow completed but no study plan was produced."


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    RESUME_PDF_PATH = "/Users/alexandresepulvedadedietrich/Documents/Columbia/Fall_Term/AI_eng_apps/Resume-Readiness-Intelligence-Engine/demo/resume_parsing/Resume_ASDD_CSxCU.pdf"
    JOB_DESCRIPTION_TEXT = """
    [url : https://www.linkedin.com/jobs/view/4314428489/?alternateChannel=search&refId=9u3sk8i%2BeQIlSVBrpYxESQ%3D%3D&trackingId=Get6L8t577ywsT%2BWJ1ymUA%3D%3D]

    About the job
    Kensho is S&P Global’s hub for AI innovation and transformation. With expertise in machine learning, natural language processing, and data discovery, we develop and deploy novel solutions to innovate and drive progress at S&P Global and its customers worldwide. Kensho's solutions and research focus on business and financial generative AI applications, agents, data retrieval APIs, data extraction, and much more.

    At Kensho, we hire talented people and give them the autonomy and support needed to build amazing technology and products. We collaborate using our teammates' diverse perspectives to solve hard problems. Our communication with one another is open, honest, and efficient. We dedicate time and resources to explore new ideas, but always rooted in engineering best practices. As a result, we can innovate rapidly to produce technology that is scalable, robust, and useful.

    Kensho is looking for ML Engineer interns to join the group of Machine Learning Engineers working on developing a cutting-edge GenAI platform, LLM-powered applications, and fundamental AI toolkit solutions such as Kensho Extract. We are looking for talented people who share our passion for bringing robust, scalable, and highly accurate ML solutions to production.

    Are you looking to leverage your teammates' diverse perspectives to solve hard problems? If so, we would love to help you excel here at Kensho. You will be working on a team with experienced engineers and have an opportunity to learn and grow. We take pride in our team-based, tightly-knit startup Kenshin community that provides our employees with a collaborative, communicative environment that allows us to tackle the biggest challenges in data. In addition, as an intern you will have the opportunity to attend technical and non-technical discussions as well as company wide social events.

    We value in-person collaboration, therefore interns are required to work out of the Cambridge HQ or our New York City office!

    Technologies & Tools We Use

    Agentic systems: Agentic Orchestration, Deep Research, Information Retrieval, LLM code generation, LLM tool utilization, Multi-turn Conversationality, Textual RAG systems
    Core ML/AI: DGL, GNNs, HuggingFace, LangGraph, LightGBM, PyTorch, SKLearn, Transformers, XGBoost
    Data Exploration and Visualization: Jupyter, Matplotlib, Pandas, Weights & Biases, Gradio, Streamlit
    Data Management and Storage: AWS Athena, DVC, LabelBox, OpenSearch, Postgres/Pgvector, S3, SQLite
    Deployment & MLOps: Arize, AWS, Amazon EKS, DeepSpeed, Containerization, Grafana, Jenkins, LangFuse, LiteLLM, Ray, vLLM

    What You’ll Do

    Apply advanced NLP techniques to extract insights from large proprietary unstructured and structured datasets
    Design, build, and maintain scalable production-ready ML systems
    Participate in the ML model lifecycle, from problem framing to training, deployment, and monitoring in production
    Partner with our ML Operations team to deliver solutions for automating the ML model lifecycle, from technical design to implementation
    Work in a cross-functional team of ML Engineers, Product Managers, Designers, Backend & Frontend Engineers who are passionate about delivering exceptional products

    What We Look For

    Outstanding people come from all different backgrounds, and we’re always interested in meeting talented people! Therefore, we do not require any particular credential or experience. If our work seems exciting to you, and you feel that you could excel in this position, we’d love to hear from you. That said, most successful candidates will fit the following profile, which reflects both our technical needs and team culture:

    Pursuing a bachelor's degree or higher with relevant classwork or internships in Machine Learning
    Experience in designing and iterating on agentic systems, understanding user interactions, and evaluating agent performance to enhance user experiences.
    Experience with advanced machine learning methods
    Statistical knowledge, intuition, and experience modeling real data
    Expertise in Python and Python-based ML frameworks (e.g.,LangGraph, Pydantic AI, PyTorch)
    Demonstrated effective coding, documentation, and communication habits
    Strong communication skills and the ability to effectively express even complicated methods and results to a broad, often non-technical, audience 

    """
    final_output = run_job_readiness_engine_orchestrator(RESUME_PDF_PATH, JOB_DESCRIPTION_TEXT,
                                                         plan_output_path="/Users/alexandresepulvedadedietrich/Documents/Columbia/Fall_Term/AI_eng_apps/Resume-Readiness-Intelligence-Engine/demo/study_plan.md")
    print("\n==============================================")
    print("🚀 FINAL PERSONALIZED STUDY PLAN OUTPUT:")
    print("==============================================")
    print(final_output)
    print("==============================================")
