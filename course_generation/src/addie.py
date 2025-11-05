from src.services.llm import client, async_client
from src.utils import fast_search, async_fast_search
from typing import Optional, Dict
# New imports for checkpointing
import os
import json
import hashlib
import asyncio
from typing import Any

class Analyze:
    """
    Analyze phase of the ADDIE model.
    Receive information about the special course and return:
    - Objectives definition
    - Audience analysis
    - Resource assessment 
    """
    
    def __init__(self, client = client, async_client = async_client):
        self.client = client
        self.async_client = async_client

    # Single-step research to align all analysis attributes
    def build_shared_research_context(
        self,
        course_name: str,
        course_description: str,
        learning_objectives: str,
    ) -> str:
        query = f"""
        Research to inform Objectives, Audience, and Resource assessment for a course.
        Course Name: {course_name}
        Course Description: {course_description}
        Initial Learning Objectives: {learning_objectives}
        Include: domain trends, learner personas, prerequisite skills, common pitfalls, accessibility, tooling/platforms, datasets, standards, and best practices.
        """
        return fast_search(query)

    async def async_build_shared_research_context(
        self,
        course_name: str,
        course_description: str,
        learning_objectives: str,
    ) -> str:
        query = f"""
        Research to inform Objectives, Audience, and Resource assessment for a course.
        Course Name: {course_name}
        Course Description: {course_description}
        Initial Learning Objectives: {learning_objectives}
        Include: domain trends, learner personas, prerequisite skills, common pitfalls, accessibility, tooling/platforms, datasets, standards, and best practices.
        """
        return await async_fast_search(query)

    def analyze_course(
        self,
        course_name: str,
        course_description: str,
        learning_objectives: str,
        do_research: bool = True,
    ) -> str:
        """
        Analyze the course information and return the analysis.
        """
        if not do_research:
            prompt = f"""
            You are an expert instructional designer. 
            Analyze the following course information and provide a detailed analysis including:
            - Objectives definition
            - Audience analysis
            - Resource assessment 

            Course Name: {course_name}
            Course Description: {course_description}
            Learning Objectives: {learning_objectives}

            Provide your analysis in a structured format.
            """
            response = self.client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {"role": "system", "content": "You are an expert instructional designer."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.7,
            )
            return response.choices[0].message.content
        else:
            query = f"""
            Analyze the following course information and provide a detailed analysis including:
            - Objectives definition
            - Audience analysis
            - Resource assessment
            Course Name: {course_name}
            Course Description: {course_description}
            Learning Objectives: {learning_objectives}
            """
            context = fast_search(
                query
            )
            prompt = f"""
            You are an expert instructional designer.
            Analyze the following course information and additional research context to provide a detailed analysis including:
            - Objectives definition
            - Audience analysis
            - Resource assessment
            Course Name: {course_name}
            Course Description: {course_description}
            Learning Objectives: {learning_objectives}
            Additional Context: {context}
            Provide your analysis in a structured format.
            """
            response = self.client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {"role": "system", "content": "You are an expert instructional designer."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.7,
            )
            return response.choices[0].message.content

    # Aligned generation using a single shared context for all three attributes
    def analyze_all_aligned(
        self,
        course_name: str,
        course_description: str,
        learning_objectives: str,
        do_research: bool = True,
    ) -> Dict[str, str]:
        shared_context = (
            self.build_shared_research_context(course_name, course_description, learning_objectives)
            if do_research else ""
        )
        objectives = self.analyze_objectives(
            course_name, course_description, learning_objectives, do_research=False, shared_context=shared_context
        )
        audience = self.analyze_audience(
            course_name, course_description, learning_objectives, do_research=False, shared_context=shared_context
        )
        resources = self.analyze_resources(
            course_name, course_description, learning_objectives, do_research=False, shared_context=shared_context
        )
        combined = f"Objectives:\n{objectives}\n\nAudience:\n{audience}\n\nResources:\n{resources}"
        return {
            "objectives": objectives,
            "audience": audience,
            "resources": resources,
            "combined": combined,
            "shared_context": shared_context,
        }

    async def async_analyze_all_aligned(
        self,
        course_name: str,
        course_description: str,
        learning_objectives: str,
        do_research: bool = True,
    ) -> Dict[str, str]:
        shared_context = (
            await self.async_build_shared_research_context(course_name, course_description, learning_objectives)
            if do_research else ""
        )
        objectives = await self.async_analyze_objectives(
            course_name, course_description, learning_objectives, do_research=False, shared_context=shared_context
        )
        audience = await self.async_analyze_audience(
            course_name, course_description, learning_objectives, do_research=False, shared_context=shared_context
        )
        resources = await self.async_analyze_resources(
            course_name, course_description, learning_objectives, do_research=False, shared_context=shared_context
        )
        combined = f"Objectives:\n{objectives}\n\nAudience:\n{audience}\n\nResources:\n{resources}"
        return {
            "objectives": objectives,
            "audience": audience,
            "resources": resources,
            "combined": combined,
            "shared_context": shared_context,
        }

    def analyze_objectives(
        self,
        course_name: str,
        course_description: str,
        learning_objectives: str,
        do_research: bool = True,
        shared_context: Optional[str] = None,
    ) -> str:
        query = f"Define clear learning objectives for a course.\nCourse: {course_name}\nDesc: {course_description}\nInitial Objectives: {learning_objectives}"
        context = shared_context if shared_context is not None else (fast_search(query) if do_research else "")
        prompt = f"""
        You are an expert instructional designer.
        Only produce the Objectives definition for the course.
        Be concise and structured (bulleted list with measurable outcomes).
        Course Name: {course_name}
        Course Description: {course_description}
        Provided Learning Objectives: {learning_objectives}
        Additional Context: {context}
        """
        response = self.client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": "You are an expert instructional designer."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=800,
            temperature=0.5,
        )
        return response.choices[0].message.content

    async def async_analyze_objectives(
        self,
        course_name: str,
        course_description: str,
        learning_objectives: str,
        do_research: bool = True,
        shared_context: Optional[str] = None,
    ) -> str:
        query = f"Define clear learning objectives for a course.\nCourse: {course_name}\nDesc: {course_description}\nInitial Objectives: {learning_objectives}"
        context = shared_context if shared_context is not None else (await async_fast_search(query) if do_research else "")
        prompt = f"""
        You are an expert instructional designer.
        Only produce the Objectives definition for the course.
        Be concise and structured (bulleted list with measurable outcomes).
        Course Name: {course_name}
        Course Description: {course_description}
        Provided Learning Objectives: {learning_objectives}
        Additional Context: {context}
        """
        response = await self.async_client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": "You are an expert instructional designer."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=800,
            temperature=0.5,
        )
        return response.choices[0].message.content

    def analyze_audience(
        self,
        course_name: str,
        course_description: str,
        learning_objectives: str,
        do_research: bool = True,
        shared_context: Optional[str] = None,
    ) -> str:
        query = f"Analyze target learners for a course.\nCourse: {course_name}\nDesc: {course_description}\nObjectives: {learning_objectives}"
        context = shared_context if shared_context is not None else (fast_search(query) if do_research else "")
        prompt = f"""
        You are an expert instructional designer.
        Only produce the Audience analysis (prior knowledge, roles, motivations, constraints, accessibility).
        Use concise bullets.
        Course Name: {course_name}
        Course Description: {course_description}
        Learning Objectives: {learning_objectives}
        Additional Context: {context}
        """
        response = self.client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": "You are an expert instructional designer."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=800,
            temperature=0.5,
        )
        return response.choices[0].message.content

    async def async_analyze_audience(
        self,
        course_name: str,
        course_description: str,
        learning_objectives: str,
        do_research: bool = True,
        shared_context: Optional[str] = None,
    ) -> str:
        query = f"Analyze target learners for a course.\nCourse: {course_name}\nDesc: {course_description}\nObjectives: {learning_objectives}"
        context = shared_context if shared_context is not None else (await async_fast_search(query) if do_research else "")
        prompt = f"""
        You are an expert instructional designer.
        Only produce the Audience analysis (prior knowledge, roles, motivations, constraints, accessibility).
        Use concise bullets.
        Course Name: {course_name}
        Course Description: {course_description}
        Learning Objectives: {learning_objectives}
        Additional Context: {context}
        """
        response = await self.async_client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": "You are an expert instructional designer."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=800,
            temperature=0.5,
        )
        return response.choices[0].message.content

    def analyze_resources(
        self,
        course_name: str,
        course_description: str,
        learning_objectives: str,
        do_research: bool = True,
        shared_context: Optional[str] = None,
    ) -> str:
        query = f"Identify resources for a course (tools, platforms, time, SMEs, datasets, references).\nCourse: {course_name}\nDesc: {course_description}\nObjectives: {learning_objectives}"
        context = shared_context if shared_context is not None else (fast_search(query) if do_research else "")
        prompt = f"""
        You are an expert instructional designer.
        Only produce the Resource assessment (people, content, tools, budget/time, risks).
        Use concise bullets grouped by category.
        Course Name: {course_name}
        Course Description: {course_description}
        Learning Objectives: {learning_objectives}
        Additional Context: {context}
        """
        response = self.client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": "You are an expert instructional designer."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=900,
            temperature=0.5,
        )
        return response.choices[0].message.content

    async def async_analyze_resources(
        self,
        course_name: str,
        course_description: str,
        learning_objectives: str,
        do_research: bool = True,
        shared_context: Optional[str] = None,
    ) -> str:
        query = f"Identify resources for a course (tools, platforms, time, SMEs, datasets, references).\nCourse: {course_name}\nDesc: {course_description}\nObjectives: {learning_objectives}"
        context = shared_context if shared_context is not None else (await async_fast_search(query) if do_research else "")
        prompt = f"""
        You are an expert instructional designer.
        Only produce the Resource assessment (people, content, tools, budget/time, risks).
        Use concise bullets grouped by category.
        Course Name: {course_name}
        Course Description: {course_description}
        Learning Objectives: {learning_objectives}
        Additional Context: {context}
        """
        response = await self.async_client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": "You are an expert instructional designer."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=900,
            temperature=0.5,
        )
        return response.choices[0].message.content
        
    async def async_analyze_course(
        self,
        course_name: str,
        course_description: str,
        learning_objectives: str,
        do_research: bool = True,
    ) -> str:
        """
        Asynchronously analyze the course information and return the analysis.
        """
        if not do_research:
            prompt = f"""
            You are an expert instructional designer. 
            Analyze the following course information and provide a detailed analysis including:
            - Objectives definition
            - Audience analysis
            - Resource assessment 

            Course Name: {course_name}
            Course Description: {course_description}
            Learning Objectives: {learning_objectives}

            Provide your analysis in a structured format.
            """
            response = await self.async_client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {"role": "system", "content": "You are an expert instructional designer."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.7,
            )
            return response.choices[0].message.content
        else:
            query = f"""
            Analyze the following course information and provide a detailed analysis including:
            - Objectives definition
            - Audience analysis
            - Resource assessment
            Course Name: {course_name}
            Course Description: {course_description}
            Learning Objectives: {learning_objectives}
            """
            context = await async_fast_search(
                query
            )
            prompt = f"""
            You are an expert instructional designer.
            Analyze the following course information and additional research context to provide a detailed analysis including:
            - Objectives definition
            - Audience analysis
            - Resource assessment
            Course Name: {course_name}
            Course Description: {course_description}
            Learning Objectives: {learning_objectives}
            Additional Context: {context}
            Provide your analysis in a structured format.
            """
            response = await self.async_client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {"role": "system", "content": "You are an expert instructional designer."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.7,
            )
            return response.choices[0].message.content
        

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

    def design_course(
        self,
        analysis: str,
    ) -> str:
        """ 
        Design the course based on the analysis and return the design.
        """
        prompt = f"""
        You are an expert instructional designer. 
        Based on the following analysis, design a detailed course plan including:
        - Syllabus design
        - Slide planning
        - Assessment planning

        Analysis: {analysis}

        Provide your design in a structured format.
        """
        response = self.client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": "You are an expert instructional designer."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.7,
        )
        return response.choices[0].message.content

    def design_syllabus(self, analysis: str) -> str:
        prompt = f"""
        You are an expert instructional designer.
        Only produce the Syllabus design: modules/chapters, brief descriptions, prerequisites, estimated durations.
        Keep it concise and structured.
        Analysis: {analysis}
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

    async def async_design_syllabus(self, analysis: str) -> str:
        prompt = f"""
        You are an expert instructional designer.
        Only produce the Syllabus design: modules/chapters, brief descriptions, prerequisites, estimated durations.
        Keep it concise and structured.
        Analysis: {analysis}
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

    def plan_slides(self, analysis: str) -> str:
        prompt = f"""
        You are an expert instructional designer.
        Only produce Slide planning: per module key slides, titles, 3-5 bullets per slide, visuals suggestions.
        Keep it concise and structured.
        Analysis: {analysis}
        """
        response = self.client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": "You are an expert instructional designer."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=1500,
            temperature=0.6,
        )
        return response.choices[0].message.content

    async def async_plan_slides(self, analysis: str) -> str:
        prompt = f"""
        You are an expert instructional designer.
        Only produce Slide planning: per module key slides, titles, 3-5 bullets per slide, visuals suggestions.
        Keep it concise and structured.
        Analysis: {analysis}
        """
        response = await self.async_client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": "You are an expert instructional designer."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=1500,
            temperature=0.6,
        )
        return response.choices[0].message.content

    def plan_assessments(self, analysis: str) -> str:
        prompt = f"""
        You are an expert instructional designer.
        Only produce Assessment planning: per module formative checks and summative items, rubric outlines, mapping to objectives.
        Keep it concise and structured.
        Analysis: {analysis}
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
        Only produce Assessment planning: per module formative checks and summative items, rubric outlines, mapping to objectives.
        Keep it concise and structured.
        Analysis: {analysis}
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
        Based on the following analysis, design a detailed course plan including:
        - Syllabus design
        - Slide planning
        - Assessment planning

        Analysis: {analysis}

        Provide your design in a structured format.
        """
        response = await self.async_client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": "You are an expert instructional designer."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.7,
        )
        return response.choices[0].message.content
    

class Develop:
    """
    Develop phase of the ADDIE model.
    Receive design information and return materials for each chapter:
    - Script
    - Slide
    - Assessment questions
    """

    def __init__(self, client = client, async_client = async_client):
        self.client = client
        self.async_client = async_client
    def develop_course(
        self,
        design: str,
    ) -> str:
        """
        Develop the course materials based on the design and return the materials.
        """
        prompt = f"""
        You are an expert instructional designer. 
        Based on the following design, develop detailed course materials for each chapter including:
        - Script
        - Slide
        - Assessment questions

        Design: {design}

        Provide your materials in a structured format.
        """
        response = self.client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": "You are an expert instructional designer."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.7,
        )
        return response.choices[0].message.content

    def develop_chapter_script(self, design: str, chapter_title: str) -> str:
        prompt = f"""
        You are an expert instructional designer.
        Only produce the Script for the chapter: "{chapter_title}".
        Include speaking notes, key explanations, and timing cues.
        Use concise sections.
        Design: {design}
        """
        response = self.client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": "You are an expert instructional designer."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=1500,
            temperature=0.6,
        )
        return response.choices[0].message.content

    async def async_develop_chapter_script(self, design: str, chapter_title: str) -> str:
        prompt = f"""
        You are an expert instructional designer.
        Only produce the Script for the chapter: "{chapter_title}".
        Include speaking notes, key explanations, and timing cues.
        Use concise sections.
        Design: {design}
        """
        response = await self.async_client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": "You are an expert instructional designer."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=1500,
            temperature=0.6,
        )
        return response.choices[0].message.content

    def develop_chapter_slides(self, design: str, chapter_title: str) -> str:
        prompt = f"""
        You are an expert instructional designer.
        Only produce the Slides outline for the chapter: "{chapter_title}".
        Provide slide titles, 3-5 bullets each, and visual/diagram suggestions.
        Design: {design}
        """
        response = self.client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": "You are an expert instructional designer."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=1500,
            temperature=0.6,
        )
        return response.choices[0].message.content

        # Async variant
    async def async_develop_chapter_slides(self, design: str, chapter_title: str) -> str:
        prompt = f"""
        You are an expert instructional designer.
        Only produce the Slides outline for the chapter: "{chapter_title}".
        Provide slide titles, 3-5 bullets each, and visual/diagram suggestions.
        Design: {design}
        """
        response = await self.async_client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": "You are an expert instructional designer."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=1500,
            temperature=0.6,
        )
        return response.choices[0].message.content

    def develop_chapter_assessment(self, design: str, chapter_title: str) -> str:
        prompt = f"""
        You are an expert instructional designer.
        Only produce the Assessment questions for the chapter: "{chapter_title}".
        Include a mix of item types (MCQ, short answer, practical task), answer keys, and mapping to objectives.
        Design: {design}
        """
        response = self.client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": "You are an expert instructional designer."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=1500,
            temperature=0.6,
        )
        return response.choices[0].message.content

    async def async_develop_chapter_assessment(self, design: str, chapter_title: str) -> str:
        prompt = f"""
        You are an expert instructional designer.
        Only produce the Assessment questions for the chapter: "{chapter_title}".
        Include a mix of item types (MCQ, short answer, practical task), answer keys, and mapping to objectives.
        Design: {design}
        """
        response = await self.async_client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": "You are an expert instructional designer."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=1500,
            temperature=0.6,
        )
        return response.choices[0].message.content
    
    async def async_develop_course(
        self,
        design: str,
    ) -> str:
        """
        Asynchronously develop the course materials based on the design and return the materials.
        """
        prompt = f"""
        You are an expert instructional designer. 
        Based on the following design, develop detailed course materials for each chapter including:
        - Script
        - Slide
        - Assessment questions

        Design: {design}

        Provide your materials in a structured format.
        """
        response = await self.async_client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": "You are an expert instructional designer."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.7,
        )
        return response.choices[0].message.content

class ADDIE:
    """
    Full ADDIE model for course generation.
    Combines Analyze, Design, and Develop phases.
    """
    def __init__(self, client = client, async_client = async_client, checkpoint_dir: Optional[str] = None):
        self.analyze = Analyze(client, async_client)
        self.design = Design(client, async_client)
        self.develop = Develop(client, async_client)
        # New: checkpoint directory
        self.checkpoint_dir = checkpoint_dir or ".addie_checkpoints"

    # New: checkpoint helpers
    def _make_checkpoint_key(
        self,
        course_name: str,
        course_description: str,
        learning_objectives: str,
        do_research: bool,
        stage: str,
    ) -> str:
        payload = {
            "course_name": course_name,
            "course_description": course_description,
            "learning_objectives": learning_objectives,
            "do_research": do_research,
            "stage": stage,
            "version": 1,  # bump if the payload shape changes
        }
        blob = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
        return hashlib.sha256(blob).hexdigest()[:16]

    def _checkpoint_path(self, key: str, stage: str, checkpoint_dir: Optional[str] = None) -> str:
        # Kept for backward compatibility (JSON paths); no longer used for .md artifacts.
        directory = checkpoint_dir or self.checkpoint_dir
        os.makedirs(directory, exist_ok=True)
        return os.path.join(directory, f"{stage}-{key}.json")

    def _load_checkpoint(self, path: str) -> Optional[Any]:
        # Kept for backward compatibility
        if not os.path.exists(path):
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                saved = json.load(f)
            return saved.get("data")
        except Exception:
            return None

    def _save_checkpoint(self, path: str, data: Any) -> None:
        # Kept for backward compatibility
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"data": data}, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    # New: .md-based helpers
    def _sanitize_course_name(self, name: str) -> str:
        s = "".join(c if c.isalnum() or c in ("-", "_") else "-" for c in (name or "").strip())
        s = "-".join(filter(None, s.split("-")))
        return s[:80] or "course"

    def _course_dir(self, course_name: str, key: str, checkpoint_dir: Optional[str] = None) -> str:
        base = checkpoint_dir or self.checkpoint_dir
        os.makedirs(base, exist_ok=True)
        folder = f"{self._sanitize_course_name(course_name)}-{key}"
        path = os.path.join(base, folder)
        os.makedirs(path, exist_ok=True)
        return path

    def _read_md(self, path: str) -> Optional[str]:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception:
                return None
        return None

    def _write_md(self, path: str, content: str) -> None:
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(str(content or ""))
        except Exception:
            pass

    def generate_course(
        self,
        course_name: str,
        course_description: str,
        learning_objectives: str,
        do_research: bool = True,
        use_checkpoint: bool = True,
        checkpoint_dir: Optional[str] = None,
    ) -> dict:
        """
        Generate analysis and design parts separately and return a structured dict.
        Uses single-step research for aligned analysis when do_research=True.
        Saves each artifact to Markdown in a course-named folder.
        """
        key = self._make_checkpoint_key(course_name, course_description, learning_objectives, do_research, stage="parts")
        course_path = self._course_dir(course_name, key, checkpoint_dir)

        # New: attempt to load all artifacts from .md files
        if use_checkpoint:
            files = {
                "objectives": os.path.join(course_path, "objectives.md"),
                "audience": os.path.join(course_path, "audience.md"),
                "resources": os.path.join(course_path, "resources.md"),
                "combined": os.path.join(course_path, "analysis_combined.md"),
                "syllabus": os.path.join(course_path, "syllabus.md"),
                "slides_plan": os.path.join(course_path, "slides_plan.md"),
                "assessment_plan": os.path.join(course_path, "assessment_plan.md"),
            }
            if all(os.path.exists(p) for p in files.values()):
                return {
                    "analysis": {
                        "objectives": self._read_md(files["objectives"]) or "",
                        "audience": self._read_md(files["audience"]) or "",
                        "resources": self._read_md(files["resources"]) or "",
                        "combined": self._read_md(files["combined"]) or "",
                    },
                    "design": {
                        "syllabus": self._read_md(files["syllabus"]) or "",
                        "slides_plan": self._read_md(files["slides_plan"]) or "",
                        "assessment_plan": self._read_md(files["assessment_plan"]) or "",
                    },
                }

        # ...existing generation flow...
        if do_research:
            aligned = self.analyze.analyze_all_aligned(
                course_name, course_description, learning_objectives, do_research=True
            )
            objectives = aligned["objectives"]
            audience = aligned["audience"]
            resources = aligned["resources"]
            analysis_combined = aligned["combined"]
        else:
            objectives = self.analyze.analyze_objectives(course_name, course_description, learning_objectives, do_research=False)
            audience = self.analyze.analyze_audience(course_name, course_description, learning_objectives, do_research=False)
            resources = self.analyze.analyze_resources(course_name, course_description, learning_objectives, do_research=False)
            analysis_combined = f"Objectives:\n{objectives}\n\nAudience:\n{audience}\n\nResources:\n{resources}"

        syllabus = self.design.design_syllabus(analysis_combined)
        slides_plan = self.design.plan_slides(analysis_combined)
        assessment_plan = self.design.plan_assessments(analysis_combined)

        result = {
            "analysis": {
                "objectives": objectives,
                "audience": audience,
                "resources": resources,
                "combined": analysis_combined,
            },
            "design": {
                "syllabus": syllabus,
                "slides_plan": slides_plan,
                "assessment_plan": assessment_plan,
            },
        }

        # New: save artifacts as .md
        if use_checkpoint:
            self._write_md(os.path.join(course_path, "objectives.md"), objectives)
            self._write_md(os.path.join(course_path, "audience.md"), audience)
            self._write_md(os.path.join(course_path, "resources.md"), resources)
            self._write_md(os.path.join(course_path, "analysis_combined.md"), analysis_combined)
            self._write_md(os.path.join(course_path, "syllabus.md"), syllabus)
            self._write_md(os.path.join(course_path, "slides_plan.md"), slides_plan)
            self._write_md(os.path.join(course_path, "assessment_plan.md"), assessment_plan)

        return result

    async def async_generate_course(
        self,
        course_name: str,
        course_description: str,
        learning_objectives: str,
        do_research: bool = True,
        use_checkpoint: bool = True,
        checkpoint_dir: Optional[str] = None,
    ) -> dict:
        """
        Async variant using single-step research for aligned analysis when do_research=True.
        Saves each artifact to Markdown in a course-named folder.
        """
        key = self._make_checkpoint_key(course_name, course_description, learning_objectives, do_research, stage="parts")
        course_path = self._course_dir(course_name, key, checkpoint_dir)

        # New: attempt to load all artifacts from .md files
        if use_checkpoint:
            files = {
                "objectives": os.path.join(course_path, "objectives.md"),
                "audience": os.path.join(course_path, "audience.md"),
                "resources": os.path.join(course_path, "resources.md"),
                "combined": os.path.join(course_path, "analysis_combined.md"),
                "syllabus": os.path.join(course_path, "syllabus.md"),
                "slides_plan": os.path.join(course_path, "slides_plan.md"),
                "assessment_plan": os.path.join(course_path, "assessment_plan.md"),
            }
            if all(os.path.exists(p) for p in files.values()):
                return {
                    "analysis": {
                        "objectives": self._read_md(files["objectives"]) or "",
                        "audience": self._read_md(files["audience"]) or "",
                        "resources": self._read_md(files["resources"]) or "",
                        "combined": self._read_md(files["combined"]) or "",
                    },
                    "design": {
                        "syllabus": self._read_md(files["syllabus"]) or "",
                        "slides_plan": self._read_md(files["slides_plan"]) or "",
                        "assessment_plan": self._read_md(files["assessment_plan"]) or "",
                    },
                }

        # ...existing generation flow...
        if do_research:
            aligned = await self.analyze.async_analyze_all_aligned(
                course_name, course_description, learning_objectives, do_research=True
            )
            objectives = aligned["objectives"]
            audience = aligned["audience"]
            resources = aligned["resources"]
            analysis_combined = aligned["combined"]
        else:
            objectives = await self.analyze.async_analyze_objectives(course_name, course_description, learning_objectives, do_research=False)
            # Fixed: call async analysis on self.analyze
            audience = await self.analyze.async_analyze_audience(course_name, course_description, learning_objectives, do_research=False)
            resources = await self.analyze.async_analyze_resources(course_name, course_description, learning_objectives, do_research=False)
            analysis_combined = f"Objectives:\n{objectives}\n\nAudience:\n{audience}\n\nResources:\n{resources}"

        syllabus = await self.design.async_design_syllabus(analysis_combined)
        slides_plan = await self.design.async_plan_slides(analysis_combined)
        assessment_plan = await self.design.async_plan_assessments(analysis_combined)

        result = {
            "analysis": {
                "objectives": objectives,
                "audience": audience,
                "resources": resources,
                "combined": analysis_combined,
            },
            "design": {
                "syllabus": syllabus,
                "slides_plan": slides_plan,
                "assessment_plan": assessment_plan,
            },
        }

        # New: save artifacts as .md
        if use_checkpoint:
            self._write_md(os.path.join(course_path, "objectives.md"), objectives)
            self._write_md(os.path.join(course_path, "audience.md"), audience)
            self._write_md(os.path.join(course_path, "resources.md"), resources)
            self._write_md(os.path.join(course_path, "analysis_combined.md"), analysis_combined)
            self._write_md(os.path.join(course_path, "syllabus.md"), syllabus)
            self._write_md(os.path.join(course_path, "slides_plan.md"), slides_plan)
            self._write_md(os.path.join(course_path, "assessment_plan.md"), assessment_plan)

        return result

