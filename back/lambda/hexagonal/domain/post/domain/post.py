from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class Post:
    id: int
    course_name: str
    course_instructor: str 
    topic: str 