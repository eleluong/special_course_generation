from src.services.llm import client, async_client
from src.utils import fast_search, async_fast_search
from typing import Optional, Dict
import json


class Design:
    """
    Design phase of the ADDIE model.
    Receive analysis information and return:
    - Syllabus design
    - Slide planning
    - Assessment planning
    """
    
    def __init__(self, client = client, async_client = async_client):
        self.client = client
        self.async_client = async_client
        
        # Predefined outline templates
        self.syllabus_template = """
## Course Syllabus

### Course Overview
| Attribute | Details |
|-----------|---------|
| **Duration** | [Total course length - weeks/hours] |
| **Format** | [Online/Hybrid/In-person] |
| **Prerequisites** | [Required prior knowledge/courses] |
| **Target Audience** | [Primary learner profile] |

### Module Structure

| Module | Title | Duration | Learning Outcomes | Prerequisites |
|--------|-------|----------|-------------------|---------------|
| 1 | [Module Title] | [Hours/weeks] | • [Outcome 1]<br>• [Outcome 2]<br>• [Outcome 3] | [Module requirements] |
| 2 | [Module Title] | [Hours/weeks] | • [Outcome 1]<br>• [Outcome 2]<br>• [Outcome 3] | [Module requirements] |
| 3 | [Module Title] | [Hours/weeks] | • [Outcome 1]<br>• [Outcome 2]<br>• [Outcome 3] | [Module requirements] |

### Course Schedule
| Timeframe | Coverage | Milestones |
|-----------|----------|------------|
| Week 1-2 | [Module coverage] | [Key deliverables] |
| Week 3-4 | [Module coverage] | [Key deliverables] |
| Week 5-6 | [Module coverage] | [Key deliverables] |
"""

        self.slides_template = """
## Slide Planning

### Module 1: [Module Title]
| Slide | Title | Bullets | Visual |
|-------|-------|---------|--------|
| 1 | [Slide Title] | • [Key point 1]<br>• [Key point 2]<br>• [Key point 3] | [Diagram/chart/image type] |
| 2 | [Slide Title] | • [Key point 1]<br>• [Key point 2]<br>• [Key point 3] | [Diagram/chart/image type] |
| 3 | [Slide Title] | • [Key point 1]<br>• [Key point 2]<br>• [Key point 3] | [Diagram/chart/image type] |

### Module 2: [Module Title]
| Slide | Title | Bullets | Visual |
|-------|-------|---------|--------|
| 1 | [Slide Title] | • [Key point 1]<br>• [Key point 2]<br>• [Key point 3] | [Diagram/chart/image type] |
| 2 | [Slide Title] | • [Key point 1]<br>• [Key point 2]<br>• [Key point 3] | [Diagram/chart/image type] |
| 3 | [Slide Title] | • [Key point 1]<br>• [Key point 2]<br>• [Key point 3] | [Diagram/chart/image type] |

### Module 3: [Module Title]
| Slide | Title | Bullets | Visual |
|-------|-------|---------|--------|
| 1 | [Slide Title] | • [Key point 1]<br>• [Key point 2]<br>• [Key point 3] | [Diagram/chart/image type] |
| 2 | [Slide Title] | • [Key point 1]<br>• [Key point 2]<br>• [Key point 3] | [Diagram/chart/image type] |
| 3 | [Slide Title] | • [Key point 1]<br>• [Key point 2]<br>• [Key point 3] | [Diagram/chart/image type] |

### Presentation Guidelines
| Aspect | Specification |
|--------|---------------|
| **Slide Design** | [Design principles and templates] |
| **Animation/Transitions** | [Recommended effects] |
| **Accessibility** | [Font sizes, color contrast requirements] |
| **Time per Slide** | [Recommended duration] |
"""

        self.assessment_template = """
## Assessment Planning

### Assessment Overview
| Attribute | Details |
|-----------|---------|
| **Assessment Philosophy** | [Formative vs summative approach] |
| **Grading Scale** | [Points, percentages, or letter grades] |
| **Objective Mapping** | [How assessments align to learning objectives] |
| **Feedback Timeline** | [Response time expectations] |

### Module 1: [Module Title]

#### Formative Assessments
| Assessment | Format | Duration | Objectives Measured | Weight |
|------------|--------|----------|-------------------|--------|
| [Assessment Name] | [Quiz/Discussion/Exercise] | [Time allocation] | [Specific learning outcomes] | [% of grade] |
| [Assessment Name] | [Quiz/Discussion/Exercise] | [Time allocation] | [Specific learning outcomes] | [% of grade] |

#### Summative Assessments
| Assessment | Format | Weight | Rubric Criteria |
|------------|--------|--------|-----------------|
| [Assignment Title] | [Project/Exam/Presentation] | [% of final grade] | • [Criteria 1]: [Performance levels]<br>• [Criteria 2]: [Performance levels]<br>• [Criteria 3]: [Performance levels] |

### Module 2: [Module Title]

#### Formative Assessments
| Assessment | Format | Duration | Objectives Measured | Weight |
|------------|--------|----------|-------------------|--------|
| [Assessment Name] | [Quiz/Discussion/Exercise] | [Time allocation] | [Specific learning outcomes] | [% of grade] |

#### Summative Assessments
| Assessment | Format | Weight | Rubric Criteria |
|------------|--------|--------|-----------------|
| [Assignment Title] | [Project/Exam/Presentation] | [% of final grade] | • [Criteria 1]: [Performance levels]<br>• [Criteria 2]: [Performance levels] |

### Final Assessment
| Component | Description | Weight | Evaluation Criteria |
|-----------|-------------|--------|-------------------|
| **Capstone Project** | [Project description] | [% of final grade] | [How it demonstrates mastery] |
| **Comprehensive Evaluation** | [How it ties everything together] | [% of final grade] | [Success indicators] |
"""

        self.combined_template = f"""
# Course Design Document

{self.syllabus_template}

{self.slides_template}

{self.assessment_template}
"""

    def design_course(
        self,
        analysis: str,
    ) -> str:
        """ 
        Design the course based on the analysis and return the design.
        """
        prompt = f"""
        You are an expert instructional designer. 
        Based on the following analysis, design a detailed course plan following this EXACT structure with properly formatted tables:

        {self.combined_template}

        Analysis: {analysis}

        Replace ALL bracketed placeholders with specific, detailed content based on the analysis. Maintain the markdown table formatting exactly as shown. Use bullet points within table cells where indicated (• symbol followed by <br> for line breaks).
        """
        response = self.client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": "You are an expert instructional designer."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=5000,
            temperature=0.7,
        )
        return response.choices[0].message.content

    def design_syllabus(self, analysis: str) -> str:
        prompt = f"""
        You are an expert instructional designer.
        Produce ONLY the Syllabus design following this EXACT table structure:

        {self.syllabus_template}

        Analysis: {analysis}
        
        Replace ALL bracketed placeholders with specific module information, durations, and prerequisites based on the analysis. Maintain the markdown table formatting exactly as shown with proper alignment.
        """
        response = self.client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": "You are an expert instructional designer."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=5000,
            temperature=0.5,
        )
        return response.choices[0].message.content

    async def async_design_syllabus(self, analysis: str) -> str:
        prompt = f"""
        You are an expert instructional designer.
        Produce ONLY the Syllabus design following this EXACT table structure:

        {self.syllabus_template}

        Analysis: {analysis}
        
        Replace ALL bracketed placeholders with specific module information, durations, and prerequisites based on the analysis. Maintain the markdown table formatting exactly as shown with proper alignment.
        """
        response = await self.async_client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": "You are an expert instructional designer."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=5000,
            temperature=0.5,
        )
        return response.choices[0].message.content

    def plan_slides(self, analysis: str) -> str:
        prompt = f"""
        You are an expert instructional designer.
        Produce ONLY the Slide planning following this EXACT table structure:

        {self.slides_template}

        Analysis: {analysis}
        
        Replace ALL bracketed placeholders with specific slide titles, 3-5 key points per slide using bullet format (• followed by <br>), and detailed visual suggestions. Maintain the markdown table formatting exactly as shown.
        """
        response = self.client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": "You are an expert instructional designer."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=5000,
            temperature=0.6,
        )
        return response.choices[0].message.content

    async def async_plan_slides(self, analysis: str) -> str:
        prompt = f"""
        You are an expert instructional designer.
        Produce ONLY the Slide planning following this EXACT table structure:

        {self.slides_template}

        Analysis: {analysis}
        
        Replace ALL bracketed placeholders with specific slide titles, 3-5 key points per slide using bullet format (• followed by <br>), and detailed visual suggestions. Maintain the markdown table formatting exactly as shown.
        """
        response = await self.async_client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": "You are an expert instructional designer."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=5000,
            temperature=0.6,
        )
        return response.choices[0].message.content

    def plan_assessments(self, analysis: str) -> str:
        prompt = f"""
        You are an expert instructional designer.
        Produce ONLY the Assessment planning following this EXACT table structure
        {self.assessment_template}
        Analysis: {analysis}
        Replace ALL bracketed placeholders with specific assessment names, formats, durations, objectives measured, weights, and rubric criteria based on the analysis. Maintain the markdown table formatting exactly as shown.
        """
        response = self.client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": "You are an expert instructional designer."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=1200,
            temperature=0.5,
        )
        return response.choices[0].message.content
    
    async def async_plan_assessments(self, analysis: str) -> str:
        prompt = f"""
        You are an expert instructional designer.
        Produce ONLY the Assessment planning following this EXACT table structure
        {self.assessment_template}
        Analysis: {analysis}
        Replace ALL bracketed placeholders with specific assessment names, formats, durations, objectives measured, weights, and rubric criteria based on the analysis. Maintain the markdown table formatting exactly as shown.
        """
        response = await self.async_client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": "You are an expert instructional designer."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=1200,
            temperature=0.5,
        )
        return response.choices[0].message.content

    async def async_design_course(
        self,
        analysis: str,
    ) -> str:
        """ 
        Asynchronously design the course based on the analysis and return the design.
        """
        prompt = f"""
        You are an expert instructional designer. 
        Based on the following analysis, design a detailed course plan following this EXACT structure with properly formatted tables:

        {self.combined_template}

        Analysis: {analysis}

        Replace ALL bracketed placeholders with specific, detailed content based on the analysis. Maintain the markdown table formatting exactly as shown. Use bullet points within table cells where indicated (• symbol followed by <br> for line breaks).
        """
        response = await self.async_client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": "You are an expert instructional designer."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=5000,
            temperature=0.7,
        )
        return response.choices[0].message.content
    
    def extract_modules_from_design_output(self, syllabus: str, slides: str, assessments: str) -> Dict[str, Dict[str, str]]:
        """
        Helper to extract individual module designs from combined syllabus, slides, and assessments text.
        Returns a dict mapping module titles to their design components.
        """
        shared_content = f"""Generated designs:
Syllabus: {syllabus}
Slides: {slides}
Assessments: {assessments}

Response template: [
    {{
        "module_title": "<Module Title>",
        "Scipt": "<Module Content>",
        "slides_plan": "<Module Slides Plan Content>",
        "assessment_plan": "<Module Assessment Plan Content>"
    }}
]
"""
        prompt = """
        You are an expert course designer skilled at breaking down course designs into individual module components.
        Given the combined syllabus, slide planning, and assessment planning, extract each module's title, content outline, slide plan, and assessment plan.
        Provide the response in the specified JSON format.
        """
        response = self.client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": "You are an expert course designer skilled at breaking down course designs into individual module components."},
                {"role": "user", "content": prompt + shared_content},
            ],
            max_tokens=3000,
            temperature=0.3,
        )
        modules_list = json.loads(response.choices[0].message.content.strip("```json").strip("```").strip())
        modules_array = []
        for module in modules_list:
            modules_array.append({
                "title": module["module_title"],
                "script": module["Scipt"],
                "slides_plan": module["slides_plan"],
                "assessment_plan": module["assessment_plan"],
            })

        return modules_array