from dotenv import load_dotenv

load_dotenv()
from src.addie import ADDIE

addie = ADDIE()
result = addie.generate_course(
    course_name="Agile and Scrum",
    course_description="Introduce approachs to project management along with hands on exercises and real life case studies and practices.",
    learning_objectives="Understand Agile principles, Implement Scrum framework, Apply Agile practices in real-world scenarios",
    do_research=True,
    use_checkpoint=True
)


print(result)