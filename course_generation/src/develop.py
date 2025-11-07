from src.services.llm import client, async_client
from src.utils import fast_search, async_fast_search
from typing import Optional, Dict

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
            max_tokens=5000,
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
            max_tokens=5000,
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
            max_tokens=5000,
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
            max_tokens=5000,
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
            max_tokens=5000,
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
            max_tokens=5000,
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
            max_tokens=5000,
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
            max_tokens=5000,
            temperature=0.7,
        )
        return response.choices[0].message.content