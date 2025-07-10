import re
from typing import List, Optional, Union

# Define the type for a student line
def parse_class(student_line: Optional[str]) -> Optional[str]:
    """Extract class identifier from the student line."""
    if not student_line:
        return None
    match = re.search(r"TURMA:\s*([^\n\r:]+)", student_line)
    return match.group(1).strip() if match else None
