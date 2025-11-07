from src.services.llm import client, async_client
from src.utils import fast_search, async_fast_search
from typing import Optional, Dict
# New imports for checkpointing
import os
import json
import hashlib
import asyncio
from typing import Any

from src.analyze import Analyze
from src.design import Design
from src.develop import Develop
        



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
    
    

    def develop_modules_materials(
        self,
        course_name: str,
        course_description: str,
        learning_objectives: str,
        syllabus: Optional[str] = None,
        slides_plan: Optional[str] = None,
        assessment_plan: Optional[str] = None,
        do_research: bool = True,
        use_checkpoint: bool = True,
        checkpoint_dir: Optional[str] = None,
    ) -> str:
        """
        Build a Module Design (the 'design' input for Develop phase) by reading syllabus, slides_plan,
        and assessment_plan. Falls back to generate_course if those artifacts are missing.
        Saves result as module_design-<module>.md in the course folder.
        """
        key = self._make_checkpoint_key(course_name, course_description, learning_objectives, do_research, stage="parts")
        course_path = self._course_dir(course_name, key, checkpoint_dir)

        # Load inputs from checkpointed .md if not provided
        def _read_or_value(value: Optional[str], filename: str) -> Optional[str]:
            if value and value.strip():
                return value
            return self._read_md(os.path.join(course_path, filename))

        syllabus_text = _read_or_value(syllabus, "syllabus.md")
        slides_text = _read_or_value(slides_plan, "slides_plan.md")
        assessment_text = _read_or_value(assessment_plan, "assessment_plan.md")

        # If any input missing, generate course artifacts first
        if not all([syllabus_text, slides_text, assessment_text]):
            _ = self.generate_course(
                course_name=course_name,
                course_description=course_description,
                learning_objectives=learning_objectives,
                do_research=do_research,
                use_checkpoint=use_checkpoint,
                checkpoint_dir=checkpoint_dir,
            )
            syllabus_text = self._read_md(os.path.join(course_path, "syllabus.md")) or ""
            slides_text = self._read_md(os.path.join(course_path, "slides_plan.md")) or ""
            assessment_text = self._read_md(os.path.join(course_path, "assessment_plan.md")) or ""

        # Seperate modules design from above syllabus, slides, assessment
        modules = self.design.extract_modules_from_design_output(
            syllabus_text, slides_text, assessment_text
        )

        # Generate Modules Design via Develop
        modules_materials = []  # ensure defined even if not found
        for module in modules:
            # Create module checkpoint dir
            module_path = os.path.join(course_path, module["title"])
            if not os.path.exists(module_path):
                os.makedirs(module_path, exist_ok=True)

            # Generate Module materials
            module_materials = self.develop.develop_module(
                module_title=module["title"],
                design = f"Syllabus:\n{module['script']}\n\nSlides Plan:\n{module['slides_plan']}\n\nAssessment Plan:\n{module['assessment_plan']}",
                course_name=course_name,
                do_research=do_research,
                use_checkpoint=use_checkpoint,
                checkpoint_dir=module_path,
            )
            modules_materials.append(module_materials)


        return modules_materials

    async def async_develop_modules_materials(
        self,
        course_name: str,
        course_description: str,
        learning_objectives: str,
        module_title: str,
        syllabus: Optional[str] = None,
        slides_plan: Optional[str] = None,
        assessment_plan: Optional[str] = None,
        do_research: bool = True,
        use_checkpoint: bool = True,
        checkpoint_dir: Optional[str] = None,
    ) -> str:
        """
        Async variant. Builds a Module Design (the 'design' input for Develop phase) by reading syllabus,
        slides_plan, and assessment_plan. Falls back to async_generate_course if missing. Saves to .md.
        """
        key = self._make_checkpoint_key(course_name, course_description, learning_objectives, do_research, stage="parts")
        course_path = self._course_dir(course_name, key, checkpoint_dir)

        def _read_or_value(value: Optional[str], filename: str) -> Optional[str]:
            if value and value.strip():
                return value
            return self._read_md(os.path.join(course_path, filename))

        syllabus_text = _read_or_value(syllabus, "syllabus.md")
        slides_text = _read_or_value(slides_plan, "slides_plan.md")
        assessment_text = _read_or_value(assessment_plan, "assessment_plan.md")

        if not all([syllabus_text, slides_text, assessment_text]):
            _ = await self.async_generate_course(
                course_name=course_name,
                course_description=course_description,
                learning_objectives=learning_objectives,
                do_research=do_research,
                use_checkpoint=use_checkpoint,
                checkpoint_dir=checkpoint_dir,
            )
            syllabus_text = self._read_md(os.path.join(course_path, "syllabus.md")) or ""
            slides_text = self._read_md(os.path.join(course_path, "slides_plan.md")) or ""
            assessment_text = self._read_md(os.path.join(course_path, "assessment_plan.md")) or ""

        # Seperate modules design from above syllabus, slides, assessment
        modules = self.design.extract_modules_from_design_output(
            syllabus_text, slides_text, assessment_text
        )

        # Generate Modules Design via Develop (async)
        modules_materials = []
        for module in modules:
            module_path = os.path.join(course_path, module["title"])
            if not os.path.exists(module_path):
                os.makedirs(module_path, exist_ok=True)

            module_materials = await self.develop.async_develop_module(
                module_title=module["title"],
                design = f"Syllabus:\n{module['script']}\n\nSlides Plan:\n{module['slides_plan']}\n\nAssessment Plan:\n{module['assessment_plan']}",
                course_name=course_name,
                do_research=do_research,
                use_checkpoint=use_checkpoint,
                checkpoint_dir=module_path,
            )
            modules_materials.append(module_materials)

        return module_materials
    

    # Deprecated wrappers for backward compatibility
    def generate_chapter_design(self, *args, **kwargs) -> str:
        return self.generate_module_design(*args, **kwargs)

    async def async_generate_chapter_design(self, *args, **kwargs) -> str:
        return await self.async_generate_module_design(*args, **kwargs)

