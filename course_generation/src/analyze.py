from src.services.llm import client, async_client
from src.utils import fast_search, async_fast_search
from typing import Optional, Dict

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
        
        # Predefined outline templates
        self.objectives_template = """
## Learning Objectives

### Objective Overview
| Attribute | Details |
|-----------|---------|
| **Primary Focus** | [Main learning domain - cognitive/skills/behavioral] |
| **Bloom's Level** | [Highest cognitive level targeted] |
| **Measurability** | [How success will be quantified] |
| **Time to Achieve** | [Expected learning duration] |

### Primary Objectives
| Objective | Action Verb | Specific Outcome | Success Criteria |
|-----------|-------------|------------------|------------------|
| 1 | [Analyze/Create/Evaluate] | [Measurable outcome description] | [How mastery is demonstrated] |
| 2 | [Analyze/Create/Evaluate] | [Measurable outcome description] | [How mastery is demonstrated] |
| 3 | [Analyze/Create/Evaluate] | [Measurable outcome description] | [How mastery is demonstrated] |

### Secondary Objectives
| Objective | Skill Category | Transfer Value | Assessment Method |
|-----------|----------------|----------------|-------------------|
| 1 | [Technical/Soft skill] | [How it applies elsewhere] | [Evaluation approach] |
| 2 | [Technical/Soft skill] | [How it applies elsewhere] | [Evaluation approach] |
| 3 | [Technical/Soft skill] | [How it applies elsewhere] | [Evaluation approach] |

### Assessment Alignment
| Learning Objective | Assessment Type | Performance Indicator | Measurement Tool |
|--------------------|-----------------|----------------------|------------------|
| [Primary Objective 1] | [Formative/Summative] | [Observable behavior] | [Specific instrument] |
| [Primary Objective 2] | [Formative/Summative] | [Observable behavior] | [Specific instrument] |
| [Secondary Objective 1] | [Formative/Summative] | [Observable behavior] | [Specific instrument] |
"""

        self.audience_template = """
## Audience Analysis

### Learner Demographics
| Attribute | Primary Profile | Secondary Profile |
|-----------|----------------|-------------------|
| **Job Roles** | [Primary roles] | [Alternative roles] |
| **Experience Level** | [Years/skill level] | [Range of experience] |
| **Industry** | [Main sector] | [Other applicable sectors] |
| **Education** | [Typical background] | [Minimum requirements] |

### Prior Knowledge Assessment
| Knowledge Area | Required Level | Assumption Basis | Gap Mitigation |
|----------------|----------------|------------------|----------------|
| [Domain Knowledge 1] | [None/Basic/Intermediate/Advanced] | [How we know this] | [If gaps exist, how to address] |
| [Technical Skill 1] | [None/Basic/Intermediate/Advanced] | [How we know this] | [If gaps exist, how to address] |
| [Tool/Platform 1] | [None/Basic/Intermediate/Advanced] | [How we know this] | [If gaps exist, how to address] |

### Learner Characteristics
| Characteristic | Primary Audience | Considerations | Design Implications |
|----------------|------------------|----------------|-------------------|
| **Motivation** | [Why they want to learn] | [Intrinsic vs extrinsic factors] | [How to leverage this] |
| **Time Constraints** | [Available time commitment] | [Competing priorities] | [Flexible scheduling needs] |
| **Learning Style** | [Preferred modalities] | [Visual/auditory/kinesthetic preferences] | [Multi-modal approach] |
| **Technology Access** | [Available tools/platforms] | [Device limitations] | [Platform requirements] |

### Accessibility Requirements
| Need Category | Specific Requirements | Implementation | Success Metrics |
|---------------|----------------------|----------------|-----------------|
| **Visual** | [Screen readers, large text, color contrast] | [Technical specifications] | [Compliance standards] |
| **Auditory** | [Captions, transcripts, audio alternatives] | [Media requirements] | [Accessibility testing] |
| **Motor** | [Keyboard navigation, voice input] | [Interface design] | [Usability testing] |
| **Cognitive** | [Clear structure, multiple formats] | [Content design] | [Comprehension metrics] |
"""

        self.resources_template = """
## Resource Assessment

### Human Resources
| Role | Expertise Required | Time Commitment | Availability | Backup Plan |
|------|-------------------|-----------------|--------------|-------------|
| **Subject Matter Expert** | [Specific domain knowledge] | [Hours/weeks] | [When available] | [Alternative sources] |
| **Instructional Designer** | [Learning design, assessment] | [Hours/weeks] | [When available] | [Team capacity] |
| **Technical Developer** | [Platform, multimedia skills] | [Hours/weeks] | [When available] | [External resources] |
| **Content Reviewer** | [Quality assurance, accuracy] | [Hours/weeks] | [When available] | [Peer review process] |

### Content Resources
| Resource Type | Specific Materials | Source | Quality Rating | Usage Rights |
|---------------|-------------------|--------|----------------|--------------|
| **Primary Materials** | [Core textbooks, research papers] | [Publisher/author] | [Peer-reviewed/industry standard] | [Licensing terms] |
| **Supplementary Content** | [Articles, videos, case studies] | [Platform/creator] | [Relevance score] | [Permission status] |
| **Datasets** | [Practice data, examples] | [Origin/provider] | [Accuracy/currency] | [Usage restrictions] |
| **Tools & Software** | [Required applications] | [Vendor] | [Feature completeness] | [Licensing cost] |

### Technical Infrastructure
| Component | Specification | Current Status | Gap Analysis | Implementation Plan |
|-----------|---------------|----------------|--------------|-------------------|
| **Learning Management System** | [Required features] | [Available/needs upgrade] | [Feature gaps] | [Timeline/budget] |
| **Content Authoring Tools** | [Multimedia capabilities] | [Available/needs purchase] | [Capability gaps] | [Procurement plan] |
| **Assessment Platform** | [Question types, analytics] | [Available/needs integration] | [Functionality gaps] | [Integration timeline] |
| **Communication Tools** | [Discussion, messaging, video] | [Available/needs setup] | [Engagement gaps] | [Setup requirements] |

### Budget & Timeline
| Category | Estimated Cost | Timeline | Dependencies | Risk Factors |
|----------|----------------|----------|--------------|--------------|
| **Development** | [Personnel costs] | [Weeks/months] | [Resource availability] | [Scope creep, delays] |
| **Content Licensing** | [Material costs] | [Procurement time] | [Legal approval] | [Rights availability] |
| **Technology** | [Platform, tool costs] | [Implementation time] | [IT support] | [Technical compatibility] |
| **Quality Assurance** | [Testing, review costs] | [QA timeline] | [Stakeholder availability] | [Standards compliance] |

### Risk Assessment
| Risk Category | Potential Issues | Probability | Impact | Mitigation Strategy |
|---------------|------------------|-------------|--------|-------------------|
| **Resource Availability** | [SME unavailable, timeline conflicts] | [High/Medium/Low] | [High/Medium/Low] | [Specific backup plan] |
| **Technical Challenges** | [Platform limitations, integration issues] | [High/Medium/Low] | [High/Medium/Low] | [Technical workarounds] |
| **Content Quality** | [Outdated materials, accuracy concerns] | [High/Medium/Low] | [High/Medium/Low] | [Review processes] |
| **Learner Engagement** | [Motivation drops, completion rates] | [High/Medium/Low] | [High/Medium/Low] | [Engagement strategies] |
"""

        self.combined_template = f"""
# Course Analysis Report

{self.objectives_template}

{self.audience_template}

{self.resources_template}
"""

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
            Analyze the following course information and provide a detailed analysis following this EXACT structure:

            {self.combined_template}

            Course Name: {course_name}
            Course Description: {course_description}
            Learning Objectives: {learning_objectives}

            Replace the bracketed placeholders with specific, detailed content. Maintain the markdown formatting and section structure exactly as shown.
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
            Analyze the following course information and additional research context following this EXACT structure:

            {self.combined_template}

            Course Name: {course_name}
            Course Description: {course_description}
            Learning Objectives: {learning_objectives}
            Additional Context: {context}
            
            Replace the bracketed placeholders with specific, detailed content. Maintain the markdown formatting and section structure exactly as shown.
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
        Produce ONLY the Objectives definition following this EXACT structure:

        {self.objectives_template}

        Course Name: {course_name}
        Course Description: {course_description}
        Provided Learning Objectives: {learning_objectives}
        Additional Context: {context}
        
        Replace the bracketed placeholders with specific, measurable outcomes. Maintain the markdown formatting exactly as shown.
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
        Produce ONLY the Objectives definition following this EXACT structure:

        {self.objectives_template}

        Course Name: {course_name}
        Course Description: {course_description}
        Provided Learning Objectives: {learning_objectives}
        Additional Context: {context}
        
        Replace the bracketed placeholders with specific, measurable outcomes. Maintain the markdown formatting exactly as shown.
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
        Produce ONLY the Audience analysis following this EXACT structure:

        {self.audience_template}

        Course Name: {course_name}
        Course Description: {course_description}
        Learning Objectives: {learning_objectives}
        Additional Context: {context}
        
        Replace the bracketed placeholders with specific audience insights. Maintain the markdown formatting exactly as shown.
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
        Produce ONLY the Audience analysis following this EXACT structure:

        {self.audience_template}

        Course Name: {course_name}
        Course Description: {course_description}
        Learning Objectives: {learning_objectives}
        Additional Context: {context}
        
        Replace the bracketed placeholders with specific audience insights. Maintain the markdown formatting exactly as shown.
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
        Produce ONLY the Resource assessment following this EXACT structure:

        {self.resources_template}

        Course Name: {course_name}
        Course Description: {course_description}
        Learning Objectives: {learning_objectives}
        Additional Context: {context}
        
        Replace the bracketed placeholders with specific resource requirements. Maintain the markdown formatting exactly as shown.
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
        Produce ONLY the Resource assessment following this EXACT structure:

        {self.resources_template}

        Course Name: {course_name}
        Course Description: {course_description}
        Learning Objectives: {learning_objectives}
        Additional Context: {context}
        
        Replace the bracketed placeholders with specific resource requirements. Maintain the markdown formatting exactly as shown.
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
            Analyze the following course information and provide a detailed analysis following this EXACT structure:

            {self.combined_template}

            Course Name: {course_name}
            Course Description: {course_description}
            Learning Objectives: {learning_objectives}

            Replace the bracketed placeholders with specific, detailed content. Maintain the markdown formatting and section structure exactly as shown.
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
            Analyze the following course information and additional research context following this EXACT structure:

            {self.combined_template}

            Course Name: {course_name}
            Course Description: {course_description}
            Learning Objectives: {learning_objectives}
            Additional Context: {context}
            
            Replace the bracketed placeholders with specific, detailed content. Maintain the markdown formatting and section structure exactly as shown.
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