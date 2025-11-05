# Special Course Generation (ADDIE Model)

This project automates the generation of special courses using the ADDIE instructional design model (Analyze, Design, Develop, Implement, Evaluate). It leverages LLMs and research tools to produce high-quality course artifacts.

## Features

- **Analyze**: Defines objectives, analyzes audience, and assesses resources for a given course.
- **Design**: Generates syllabus, slide plans, and assessment plans based on analysis.
- **Develop**: Produces scripts, slides, and assessment questions for each chapter.
- **Checkpointing**: Saves and loads generated artifacts as Markdown files for reproducibility and incremental development.
- **Async Support**: Asynchronous variants for faster batch processing.

## Usage

1. Install dependencies (see requirements.txt).
2. Set up your `.env` file with necessary API keys.
3. Run the main script:

   ```bash
   python main.py
   ```

4. Generated course artifacts are saved in `.addie_checkpoints/<course-name>-<key>/` as Markdown files.

## Example

See `main.py` for a sample invocation:

```python
from src.addie import ADDIE

addie = ADDIE()
result = addie.generate_course(
    course_name="Agile and Scrum",
    course_description="Introduce approaches to project management along with hands-on exercises and real-life case studies and practices.",
    learning_objectives="Understand Agile principles, Implement Scrum framework, Apply Agile practices in real-world scenarios",
    do_research=True,
    use_checkpoint=True
)
print(result)
```

## Directory Structure

- `src/addie.py`: Core ADDIE model implementation.
- `main.py`: Example usage.
- `.addie_checkpoints/`: Generated course artifacts.

## Requirements

- Python 3.8+
- OpenAI-compatible LLM client
- dotenv

## License

MIT License
