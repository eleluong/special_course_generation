from src.services.llm import client, async_client
from src.utils import fast_search, async_fast_search
from typing import Optional, Dict
import os
import hashlib

class Develop:
    """
    Develop phase of the ADDIE model.
    Receive module design information and return materials for each module:
    - Script
    - Slide
    - Assessment questions
    """

    def __init__(self, client = client, async_client = async_client, checkpoint_dir: Optional[str] = None):
        self.client = client
        self.async_client = async_client
        # Structured templates for consistency (modeled after Analyze quality)
        self.script_template = """
## Module Script

### Overview
- Topic: [Module topic]
- Duration: [Minutes]
- Learning Objectives Addressed: [List or IDs]

### Sections
1. [Section Title]
- Key Points:
  - [Point 1]
  - [Point 2]
- Explanation:
  [Short narrative with concise explanations]
- Example/Demo:
  [Concrete example or demo outline]
- Engagement Prompt:
  [Question or quick activity]
- Timing: [Minutes]

2. [Section Title]
- Key Points:
  - [Point 1]
  - [Point 2]
- Explanation:
  [Short narrative]
- Example/Demo:
  [Example]
- Engagement Prompt:
  [Prompt]
- Timing: [Minutes]

### Closing
- Recap:
  - [Bullet 1]
  - [Bullet 2]
- Transition/Next Steps:
  [What comes next in the course]
- Assessment Prep:
  [What learners should be ready to demonstrate]
"""
        self.slides_template = """
## Presentation Plan

### Slide List
1. Title: [Slide title]
- Bullets:
  - [3–5 concise bullets]
- Visual/Diagram:
  [Visual concept or diagram idea]
- Speaker Notes:
  [Key talking points, not full script]

2. Title: [Slide title]
- Bullets:
  - [3–5 concise bullets]
- Visual/Diagram:
  [Visual idea]
- Speaker Notes:
  [Talking points]

### Visual Guidelines
- Color/Contrast:
  [Accessibility considerations]
- Font/Size:
  [Readable sizes]
- Diagram Conventions:
  [How to represent concepts]

### Timing Plan
- Total Slides: [Count]
- Estimated Duration: [Minutes]
- Pace Notes:
  [Where to pause, ask, or switch modalities]
"""
        self.assessment_template = """
## Assessment Package

### Blueprint
| Objective | Item Type | Count | Cognitive Level | Notes |
|-----------|-----------|-------|------------------|-------|
| [Objective 1] | [MCQ/Short/Practical] | [#] | [Remember/Apply/Analyze/Create] | [Notes] |
| [Objective 2] | [Type] | [#] | [Level] | [Notes] |

### Questions
1. Type: [MCQ]
- Stem: [Question]
- Options: [A], [B], [C], [D]
- Answer: [Correct option]
- Rationale: [Why correct; why others are wrong]
- Alignment: [Objective ID]

2. Type: [Short Answer]
- Prompt: [Open-ended question]
- Expected Key Points: [Bullet points]
- Alignment: [Objective ID]

3. Type: [Practical Task]
- Task: [Hands-on task]
- Submission: [What to submit]
- Rubric:
  - Criteria: [Criterion 1] — [Weights]
  - Criteria: [Criterion 2] — [Weights]
- Alignment: [Objective ID]

### Alignment Matrix
| Assessment Item | Objective | Related Script Section | Related Slide |
|-----------------|-----------|------------------------|---------------|
| Q1 | [Objective] | [Section] | [Slide #] |
| Q2 | [Objective] | [Section] | [Slide #] |
"""
        # Renamed: Module Design template for generating "design" input to Develop phase
        self.module_design_template = """
## Module Design

### Metadata
- Course: [Course name]
- Module Title: [Title]
- Estimated Duration: [Minutes]
- Audience/Prerequisites: [Brief]

### Learning Objectives
- [Objective 1 (measurable verb + condition/criterion)]
- [Objective 2]
- [Objective 3]

### Content Outline
1. [Section Title] — [Minutes]
- Key Points: [3–5 bullets]
- Examples/Demos: [Brief]
- Activity/Engagement: [Brief]
- Materials: [Links/tools]

2. [Section Title] — [Minutes]
- Key Points: [Bullets]
- Activity/Engagement: [Brief]
- Materials: [Links/tools]

### Slide Plan Summary
- Slide Groups: [Mapping of sections -> slide ranges]
- Visuals/Diagrams: [Recommended visuals]

### Assessment Alignment
- Item Map: [Objective -> items/types]
- Practical/Project: [If any]
- Rubric Highlights: [Criteria + weights]

### Accessibility & Risks
- Accessibility Considerations: [Bullets]
- Common Misconceptions: [Bullets]
- Mitigations: [Bullets]

### References/Resources
- [Short list]
"""
        # New: checkpoint directory for Develop artifacts
        self.checkpoint_dir = checkpoint_dir or ".develop_checkpoints"

    # --- Research helpers (shared context similar to Analyze) ---
    def build_shared_research_context(
        self,
        module_title: str,
        design: str,
        course_name: Optional[str] = None,
    ) -> str:
        query = f"""
        Research to inform Script, Presentation Plan, and Assessment for a single module.
        Course Name: {course_name or "[unspecified]"}
        Module Title: {module_title}
        Module Design/Outline: {design}
        Include: domain trends, prerequisite skills, common misconceptions, accessibility, recommended visuals/diagrams, best assessment practices, datasets/tools, standards/terminology.
        """
        return fast_search(query)

    async def async_build_shared_research_context(
        self,
        module_title: str,
        design: str,
        course_name: Optional[str] = None,
    ) -> str:
        query = f"""
        Research to inform Script, Presentation Plan, and Assessment for a single module.
        Course Name: {course_name or "[unspecified]"}
        Module Title: {module_title}
        Module Design/Outline: {design}
        Include: domain trends, prerequisite skills, common misconceptions, accessibility, recommended visuals/diagrams, best assessment practices, datasets/tools, standards/terminology.
        """
        return await async_fast_search(query)

    # Helper to accept a file path or raw text
    def _ensure_text(self, maybe_text_or_path: str) -> str:
        if not isinstance(maybe_text_or_path, str):
            return str(maybe_text_or_path)
        try:
            if os.path.exists(maybe_text_or_path) and os.path.isfile(maybe_text_or_path):
                with open(maybe_text_or_path, "r", encoding="utf-8") as f:
                    return f.read()
        except Exception:
            pass
        return maybe_text_or_path

    # New: checkpoint helpers (md-based)
    def _sanitize_name(self, name: Optional[str]) -> str:
        s = "".join(c if c.isalnum() or c in ("-", "_") else "-" for c in (name or "").strip())
        s = "-".join(filter(None, s.split("-")))
        return s[:80] or "item"

    def _make_develop_key(
        self,
        course_name: Optional[str],
        module_title: str,
        design_or_inputs_hash: str,
        do_research: bool,
        stage: str,
    ) -> str:
        payload = {
            "course_name": course_name or "",
            "module_title": module_title,
            "inputs": design_or_inputs_hash,
            "do_research": do_research,
            "stage": stage,
            "version": 1,
        }
        blob = str(payload).encode("utf-8")
        return hashlib.sha256(blob).hexdigest()[:16]

    def _artifact_dir(
        self,
        course_name: Optional[str],
        module_title: str,
        key: str,
        checkpoint_dir: Optional[str] = None,
    ) -> str:
        base = checkpoint_dir or self.checkpoint_dir
        os.makedirs(base, exist_ok=True)
        course_slug = self._sanitize_name(course_name or "course")
        module_slug = self._sanitize_name(module_title)
        path = os.path.join(base, f"{course_slug}-{module_slug}-{key}")
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

    # --- Orchestrated module development (script -> slides -> assessment) ---
    def develop_module(
        self,
        design: str,
        module_title: str,
        do_research: bool = True,
        course_name: Optional[str] = None,
        use_checkpoint: bool = True,
        checkpoint_dir: Optional[str] = None,
    ) -> Dict[str, str]:
        # New: checkpoint read for module artifacts
        art_dir = None
        script_path = slides_path = assess_path = combined_path = shared_ctx_path = None
        if use_checkpoint:
            design_hash = hashlib.sha256(design.encode("utf-8")).hexdigest()[:16]
            key = self._make_develop_key(course_name, module_title, design_hash, do_research, stage="develop")
            art_dir = self._artifact_dir(course_name, module_title, key, checkpoint_dir)
            script_path = os.path.join(art_dir, "script.md")
            slides_path = os.path.join(art_dir, "slides.md")
            assess_path = os.path.join(art_dir, "assessment.md")
            combined_path = os.path.join(art_dir, "combined.md")
            shared_ctx_path = os.path.join(art_dir, "shared_context.md")
            if all(os.path.exists(p) for p in [script_path, slides_path, assess_path, combined_path, shared_ctx_path]):
                return {
                    "script": self._read_md(script_path) or "",
                    "slides": self._read_md(slides_path) or "",
                    "assessment": self._read_md(assess_path) or "",
                    "combined": self._read_md(combined_path) or "",
                    "shared_context": self._read_md(shared_ctx_path) or "",
                }

        shared_context = (
            self.build_shared_research_context(module_title, design, course_name) if do_research else ""
        )
        script = self.develop_module_script(
            design, module_title, do_research=False, shared_context=shared_context
        )
        slides = self.develop_module_slides(
            design, module_title, script=script, do_research=False, shared_context=shared_context
        )
        assessment = self.develop_module_assessment(
            design, module_title, script=script, slides=slides, do_research=False, shared_context=shared_context
        )
        combined = f"Script:\n{script}\n\nSlides:\n{slides}\n\nAssessment:\n{assessment}"

        # New: checkpoint save
        if use_checkpoint and art_dir:
            self._write_md(script_path, script)
            self._write_md(slides_path, slides)
            self._write_md(assess_path, assessment)
            self._write_md(combined_path, combined)
            self._write_md(shared_ctx_path, shared_context)

        return {
            "script": script,
            "slides": slides,
            "assessment": assessment,
            "combined": combined,
            "shared_context": shared_context,
        }

    async def async_develop_module(
        self,
        design: str,
        module_title: str,
        do_research: bool = True,
        course_name: Optional[str] = None,
        use_checkpoint: bool = True,
        checkpoint_dir: Optional[str] = None,
    ) -> Dict[str, str]:
        # New: checkpoint read for module artifacts
        art_dir = None
        script_path = slides_path = assess_path = combined_path = shared_ctx_path = None
        if use_checkpoint:
            design_hash = hashlib.sha256(design.encode("utf-8")).hexdigest()[:16]
            key = self._make_develop_key(course_name, module_title, design_hash, do_research, stage="develop")
            art_dir = self._artifact_dir(course_name, module_title, key, checkpoint_dir)
            script_path = os.path.join(art_dir, "script.md")
            slides_path = os.path.join(art_dir, "slides.md")
            assess_path = os.path.join(art_dir, "assessment.md")
            combined_path = os.path.join(art_dir, "combined.md")
            shared_ctx_path = os.path.join(art_dir, "shared_context.md")
            if all(os.path.exists(p) for p in [script_path, slides_path, assess_path, combined_path, shared_ctx_path]):
                return {
                    "script": self._read_md(script_path) or "",
                    "slides": self._read_md(slides_path) or "",
                    "assessment": self._read_md(assess_path) or "",
                    "combined": self._read_md(combined_path) or "",
                    "shared_context": self._read_md(shared_ctx_path) or "",
                }

        shared_context = (
            await self.async_build_shared_research_context(module_title, design, course_name) if do_research else ""
        )
        script = await self.async_develop_module_script(
            design, module_title, do_research=False, shared_context=shared_context
        )
        slides = await self.async_develop_module_slides(
            design, module_title, script=script, do_research=False, shared_context=shared_context
        )
        assessment = await self.async_develop_module_assessment(
            design, module_title, script=script, slides=slides, do_research=False, shared_context=shared_context
        )
        combined = f"Script:\n{script}\n\nSlides:\n{slides}\n\nAssessment:\n{assessment}"

        # New: checkpoint save
        if use_checkpoint and art_dir:
            self._write_md(script_path, script)
            self._write_md(slides_path, slides)
            self._write_md(assess_path, assessment)
            self._write_md(combined_path, combined)
            self._write_md(shared_ctx_path, shared_context)

        return {
            "script": script,
            "slides": slides,
            "assessment": assessment,
            "combined": combined,
            "shared_context": shared_context,
        }

    # --- Updated per-artifact generators (use templates + shared_context) ---
    def develop_module_script(
        self,
        design: str,
        module_title: str,
        do_research: bool = True,
        shared_context: Optional[str] = None,
    ) -> str:
        context = shared_context if shared_context is not None else (fast_search(
            f"Best practices and key content for module '{module_title}'. Outline: {design}"
        ) if do_research else "")
        prompt = f"""
        You are an expert instructional designer.
        Produce ONLY the Script for the module: "{module_title}" using this EXACT structure:

        {self.script_template}

        Module Design/Outline: {design}
        Additional Context: {context}

        Replace bracketed placeholders with specific, concise, and measurable content.
        Maintain the markdown structure exactly as shown.
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

    async def async_develop_module_script(
        self,
        design: str,
        module_title: str,
        do_research: bool = True,
        shared_context: Optional[str] = None,
    ) -> str:
        context = shared_context if shared_context is not None else (await async_fast_search(
            f"Best practices and key content for module '{module_title}'. Outline: {design}"
        ) if do_research else "")
        prompt = f"""
        You are an expert instructional designer.
        Produce ONLY the Script for the module: "{module_title}" using this EXACT structure:

        {self.script_template}

        Module Design/Outline: {design}
        Additional Context: {context}

        Replace bracketed placeholders with specific, concise, and measurable content.
        Maintain the markdown structure exactly as shown.
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

    def develop_module_slides(
        self,
        design: str,
        module_title: str,
        script: Optional[str] = None,
        do_research: bool = True,
        shared_context: Optional[str] = None,
    ) -> str:
        context = shared_context if shared_context is not None else (fast_search(
            f"Effective slide planning for module '{module_title}'. Outline: {design}"
        ) if do_research else "")
        prompt = f"""
        You are an expert instructional designer.
        Produce ONLY the Presentation Plan (slides outline) for the module: "{module_title}" using this EXACT structure:

        {self.slides_template}

        Module Design/Outline: {design}
        Previous Output - Script: {script or "[not provided]"}
        Additional Context: {context}

        Replace bracketed placeholders with specific slide titles, bullets, visuals, and notes.
        Maintain the markdown structure exactly as shown.
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

    async def async_develop_module_slides(
        self,
        design: str,
        module_title: str,
        script: Optional[str] = None,
        do_research: bool = True,
        shared_context: Optional[str] = None,
    ) -> str:
        context = shared_context if shared_context is not None else (await async_fast_search(
            f"Effective slide planning for module '{module_title}'. Outline: {design}"
        ) if do_research else "")
        prompt = f"""
        You are an expert instructional designer.
        Produce ONLY the Presentation Plan (slides outline) for the module: "{module_title}" using this EXACT structure:

        {self.slides_template}

        Module Design/Outline: {design}
        Previous Output - Script: {script or "[not provided]"}
        Additional Context: {context}

        Replace bracketed placeholders with specific slide titles, bullets, visuals, and notes.
        Maintain the markdown structure exactly as shown.
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

    def develop_module_assessment(
        self,
        design: str,
        module_title: str,
        script: Optional[str] = None,
        slides: Optional[str] = None,
        do_research: bool = True,
        shared_context: Optional[str] = None,
    ) -> str:
        context = shared_context if shared_context is not None else (fast_search(
            f"Assessment best practices for module '{module_title}'. Outline: {design}"
        ) if do_research else "")
        prompt = f"""
        You are an expert instructional designer.
        Produce ONLY the Assessment Package for the module: "{module_title}" using this EXACT structure
        {self.assessment_template}
        Module Design/Outline: {design}
        Previous Output - Script: {script or "[not provided]"}
        Previous Output - Slides: {slides or "[not provided]"}

        Additional Context: {context}   
        Replace bracketed placeholders with specific, measurable assessment items aligned to learning objectives.
        Maintain the markdown structure exactly as shown.
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

    