
import findskillgap, ragretrieval, skillextractor, studyplangenerator




skills = skillextractor(resume, job_desc)
gaps = findskillgap(skills)
docs = ragretrieval(gaps)
study_plan = studyplangenerator(docs, skills)
