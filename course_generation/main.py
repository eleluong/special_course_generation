from dotenv import load_dotenv

load_dotenv()
from src.addie import ADDIE

addie = ADDIE()
# result = addie.generate_course(
#     course_name="Agile and Scrum",
#     course_description="Introduce approachs to project management along with hands on exercises and real life case studies and practices.",
#     learning_objectives="Understand Agile principles, Implement Scrum framework, Apply Agile practices in real-world scenarios",
#     do_research=True,
#     use_checkpoint=True
# )


# # IT Project management concepts course for non IT professionals
# result = addie.generate_course(
#     course_name="IT Project Management for Non-IT Professionals",
#     course_description="This course introduces non-IT professionals to the fundamental concepts and practices of IT project management, enabling them to effectively collaborate with IT teams and contribute to project success.",
#     learning_objectives="Understand key IT project management concepts, Learn the project lifecycle, Develop skills to work effectively with IT teams",
#     do_research=True,
#     use_checkpoint=True
# )

# Marketing fundamental for non marketing professionals
course_result = addie.generate_course(
    course_name="Marketing Fundamentals for Non-Marketing Professionals",
    course_description="This course provides non-marketing professionals with a comprehensive understanding of fundamental marketing concepts, strategies, and tools to enhance their ability to contribute to marketing efforts within their organizations.",
    learning_objectives="Understand basic marketing principles, Learn about market research and consumer behavior, Develop skills in digital marketing and social media strategies",
    do_research=True,
    use_checkpoint=True
)

modules = addie.develop_modules_materials(
    course_name="Marketing Fundamentals for Non-Marketing Professionals",
    course_description="This course provides non-marketing professionals with a comprehensive understanding of fundamental marketing concepts, strategies, and tools to enhance their ability to contribute to marketing efforts within their organizations.",
    learning_objectives="Understand basic marketing principles, Learn about market research and consumer behavior, Develop skills in digital marketing and social media strategies",
    do_research=True,
    use_checkpoint=True
)



print(modules)