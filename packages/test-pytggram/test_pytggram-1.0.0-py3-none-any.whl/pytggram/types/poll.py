from dataclasses import dataclass
from typing import List, Optional
from .user import User

@dataclass
class PollOption:
    """This object contains information about one answer option in a poll"""
    text: str
    voter_count: int

@dataclass
class Poll:
    """This object contains information about a poll"""
    id: str
    question: str
    options: List[PollOption]
    total_voter_count: int
    is_closed: bool
    is_anonymous: bool
    type: str
    allows_multiple_answers: bool
    correct_option_id: Optional[int] = None
    explanation: Optional[str] = None
    explanation_entities: Optional[List[Dict[str, Any]]] = None
    open_period: Optional[int] = None
    close_date: Optional[int] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Poll':
        """Create a Poll object from API response"""
        options = [PollOption(text=opt.get('text'), voter_count=opt.get('voter_count', 0)) 
                  for opt in data.get('options', [])]
        
        return cls(
            id=data.get('id'),
            question=data.get('question'),
            options=options,
            total_voter_count=data.get('total_voter_count', 0),
            is_closed=data.get('is_closed', False),
            is_anonymous=data.get('is_anonymous', True),
            type=data.get('type', 'regular'),
            allows_multiple_answers=data.get('allows_multiple_answers', False),
            correct_option_id=data.get('correct_option_id'),
            explanation=data.get('explanation'),
            explanation_entities=data.get('explanation_entities'),
            open_period=data.get('open_period'),
            close_date=data.get('close_date')
        )

@dataclass
class PollAnswer:
    """This object represents an answer of a user in a non-anonymous poll"""
    poll_id: str
    user: User
    option_ids: List[int]
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PollAnswer':
        """Create a PollAnswer object from API response"""
        user = User.from_dict(data.get('user')) if data.get('user') else None
        
        return cls(
            poll_id=data.get('poll_id'),
            user=user,
            option_ids=data.get('option_ids', [])
        )
