
# pip install -qU "langchain[anthropic]" to call the model

from langchain_groq import ChatGroq
#from dotenv import load_dotenv

import os

API_KEY = os.environ["GROQ_API_KEY"]


llm = ChatGroq(
    model = "llama-3.1-8b-instant",
    temperature=0,
    max_tokens=None,
 #   reasoning_format="parsed",
    timeout=None,
    max_retries=2,
)


practice_resume = """
                    HTML File:
                    <!DOCTYPE html>
            <html lang="en">
            <head>
            <meta charset="UTF-8" />
            <title>Sripad Karne - Resume</title>
            </head>
            <body>

            <h1>Sripad Karne</h1>
            <p>
            858-275-3303 | sk5695@columbia.edu | 
            <a href="https://linkedin.com/in/sripad-karne">linkedin.com/in/sripad-karne</a> | US Citizen
            </p>

            <h2>Education</h2>

            <h3>Columbia University — New York City, NY</h3>
            <p>Master of Science (M.S.) in Data Science — <strong>Expected Dec 2026</strong></p>

            <h3>University of California, San Diego — San Diego, CA</h3>
            <p>Bachelor of Science (B.S) in Cognitive Science (Machine Learning) — <strong>Sep 2021 – June 2025</strong></p>

            <h2>Experience</h2>

            <h3>Data Science & Machine Learning Intern — UC San Diego Health (San Diego, CA)</h3>
            <p><strong>May 2025 – Sep 2025</strong></p>
            <ul>
            <li>Processed and analyzed large-scale EHR datasets (>10 million patients) on Databricks using Spark SQL.</li>
            <li>Integrated clinical data across hospitals using ICD-10, CPT, and standardized terminologies.</li>
            <li>Built regression and classification tree models to identify risk factors and predict CKD progression.</li>
            <li>Developed XGBoost and Random Forest models for individualized risk trajectories for a clinical ML manuscript.</li>
            </ul>

            <h3>AI Intern — Machine Learning, Perception & Cognition Lab (San Diego, CA)</h3>
            <p><strong>June 2024 – Mar 2025</strong></p>
            <ul>
            <li>Built a scalable PyTorch-based video analytics pipeline to process 10+ TB of footage.</li>
            <li>Optimized open-vocabulary object prompts and improved detection throughput by 2.3×.</li>
            <li>Integrated ByteTrack, GroundingDINO, and YOLOWorld into a unified real-time multi-object tracking system.</li>
            <li>Designed a controllable image generation architecture with Diffusion Transformers and LLM-driven modules.</li>
            </ul>

            <h2>Publications</h2>
            <p>
            Hwang, H., Yoon, S., Karne, S., Boussina, A., & Sitapati, A. (pending).  
            <i>Machine learning–derived risk trajectory of chronic kidney disease and clinical implications after disease onset.</i>
            </p>

            <h2>Projects</h2>

            <h3>Job Readiness Intelligence Engine (Agentic AI + RAG Platform)</h3>
            <ul>
            <li>Built multi-agent system for résumé parsing, job fit analysis, and skill-gap detection.</li>
            <li>Implemented scalable retrieval pipeline using vector stores, embeddings, and ranked indexing.</li>
            <li>Developed adaptive LLM-generated practice questions with mastery tracking and difficulty adjustment.</li>
            </ul>

            <h3>Custom Built Wearable w/ Personalized Health AI Agent</h3>
            <ul>
            <li>Built Python-based AI system integrating 4+ sensors (HR, SpO₂, temperature, pressure).</li>
            <li>Created generative analytics pipeline using PyTorch + LangChain.</li>
            <li>Fine-tuned GPT-4 models on 100k+ physiological data points for trend modeling and insight generation.</li>
            </ul>

            <h2>Technical Skills</h2>

            <p><strong>Languages:</strong> Python, R, SQL, MATLAB</p>

            <p><strong>Frameworks & Libraries:</strong>  
            Databricks, PySpark, PyTorch, Transformers, CUDA, TensorFlow, Apache Spark, Pandas, NumPy, Scikit-learn, 
            XGBoost, RandomForest, AWS, GCP, Snowflake, Git, Docker, Linux, NLP, LLM, LangChain
            </p>

            <p><strong>Coursework:</strong>  
            AIoT, AI Algorithms, AI Engineering, Algorithms for Data Science, Advanced ML Methods, Modeling & Data Analysis,  
            Neural Networks & Deep Learning, Exploratory Data Analysis & Visualization, Business Analytics
            </p>

            </body>
            </html>


"""


messages = [
    (
        "system",
        """
        Your task is to be extract data science skills from the resume you receieve, which will be in html format, and to
        give a skill score between 1-5 for each skill, with 1 being little to no skill, to 5 being advaned in that skill.
        Make sure there are no repeats, and that the skills you extract will be no greater than 3 words long. Don't
        provide any notes or anything else, just the skills. 


        For example:
        <!DOCTYPE html>
        <html lang="en">
        <head>
        <meta charset="UTF-8">
        <title>Practice Data Science Resume</title>
        </head>
        <body>

        <h1>John Doe</h1>
        <p>
        New York, NY • johndoe@gmail.com • (555) 123-4567 • 
        <a href="https://linkedin.com/in/johndoe">linkedin.com/in/johndoe</a> • 
        <a href="https://github.com/johndoe">github.com/johndoe</a>
        </p>

        <h2>Education</h2>

        <h3>Columbia University — New York, NY</h3>
        <p>Master of Science in Data Science — <strong>Expected May 2026</strong></p>
        <p><strong>Relevant Coursework:</strong> Machine Learning, Deep Learning, Databases, Statistical Modeling, Algorithms for Data Science</p>

        <h3>University of Michigan — Ann Arbor, MI</h3>
        <p>Bachelor of Science in Computer Science — <strong>May 2024</strong></p>
        <p><strong>Key Coursework:</strong> Data Structures, Probability & Statistics, Linear Algebra, Applied Regression</p>

        <h2>Experience</h2>

        <h3>Data Science Intern — Spotify (New York, NY)</h3>
        <p><strong>June 2025 – Aug 2025</strong></p>
        <ul>
        <li>Built predictive models for listener churn using XGBoost and logistic regression.</li>
        <li>Developed PySpark pipelines to process 400M+ streaming records, improving ETL speed by 35%.</li>
        <li>Designed A/B tests for recommendation features; computed uplift metrics.</li>
        <li>Created Tableau dashboards for engagement and retention trends.</li>
        </ul>

        <h3>Machine Learning Research Assistant — University of Michigan</h3>
        <p><strong>Jan 2023 – May 2024</strong></p>
        <ul>
        <li>Implemented BERT-based NLP model for sentiment analysis of social media posts.</li>
        <li>Improved F1 score by 12% via hyperparameter tuning and domain-specific pretraining.</li>
        <li>Performed topic modeling with LDA and dataset labeling.</li>
        <li>Automated data cleaning and preprocessing workflows in Python.</li>
        </ul>

        <h3>Data Analyst Intern — BlueWave Analytics</h3>
        <p><strong>June 2023 – Aug 2023</strong></p>
        <ul>
        <li>Built SQL queries and dashboards to analyze customer lifecycle trends.</li>
        <li>Conducted cohort analyses and segmentation with k-means clustering.</li>
        <li>Automated weekly reporting pipelines using Python and Pandas.</li>
        </ul>

        <h2>Projects</h2>

        <h3>Music Genre Classifier — Python & TensorFlow</h3>
        <ul>
        <li>Built a CNN for classifying 10 music genres using 50k+ audio spectrograms.</li>
        <li>Achieved 88% accuracy and deployed via Flask API.</li>
        <li>Used data augmentation to improve robustness.</li>
        </ul>

        <h3>Price Optimization Engine — Python & Scikit-learn</h3>
        <ul>
        <li>Designed a price-elasticity model using ridge regression and random forest.</li>
        <li>Built a scenario simulation tool for revenue predictions under different pricing strategies.</li>
        </ul>

        <h2>Technical Skills</h2>

        <p><strong>Languages:</strong> Python, SQL, R, Java</p>
        <p><strong>Libraries:</strong> NumPy, Pandas, Scikit-learn, PyTorch, TensorFlow, Matplotlib, Seaborn</p>
        <p><strong>Tools:</strong> AWS, Databricks, Spark, Airflow, Docker, Git, Tableau, PowerBI</p>
        <p><strong>Concepts:</strong> Machine Learning, Deep Learning, Statistics, NLP, Time Series, Experiment Design</p>

        </body>
        </html>



        Output:
        "Machine Learning": 4,
        "Deep Learning": 4,
        "Statistical Modeling": 4,
        "Data Structures": 3,
        "Linear Algebra": 3,
        "Probability Statistics": 4,
        "Applied Regression": 4,
        "XGBoost": 4,
        "Logistic Regression": 4,
        "PySpark": 4,
        "A/B Testing": 4,
        "Tableau": 3,
        "BERT NLP": 4,
        "Sentiment Analysis": 3,
        "Hyperparameter Tuning": 3,
        "Topic Modeling": 3,
        "Data Cleaning": 4,
        "Cross Validation": 4,
        "SQL Queries": 4,
        "Cohort Analysis": 3,
        "K Means": 3,
        "Dashboards": 3,
        "CNN Models": 4,
        "TensorFlow": 4,
        "PyTorch": 3,
        "Flask API": 2,
        "Data Augmentation": 3,
        "Ridge Regression": 3,
        "Random Forest": 4,
        "Spark": 4,
        "Airflow": 2,
        "Docker": 2,
        "Git": 3,
        "AWS": 2,
        "PowerBI": 2,
        "Time Series": 2,
        "Experiment Design": 4
        
        """
    ),
    ("user"), practice_resume
]
ai_msg = llm.invoke(messages)

print(ai_msg.content)

