from dataclasses import dataclass, field
from typing import Optional, Any
from datetime import timedelta

def format_time(seconds: float) -> str:
    """Format seconds as HH:MM:SS."""
    return str(timedelta(seconds=int(seconds)))


@dataclass
class TimedText:
    start: Optional[float] = 0
    end: Optional[float] = 0
    text: Optional[str] = ''
    speaker: Optional[int] = -1
    probability: Optional[float] = None
    is_dummy: Optional[bool] = False
    
    def overlaps_with(self, other: 'TimedText') -> bool:
        return not (self.end <= other.start or other.end <= self.start)
    
    def is_within(self, other: 'TimedText') -> bool:
        return other.contains_timespan(self)

    def duration(self) -> float:
        return self.end - self.start

    def contains_time(self, time: float) -> bool:
        return self.start <= time <= self.end

    def contains_timespan(self, other: 'TimedText') -> bool:
        return self.start <= other.start and self.end >= other.end

@dataclass
class ASRToken(TimedText):
    def with_offset(self, offset: float) -> "ASRToken":
        """Return a new token with the time offset added."""
        return ASRToken(self.start + offset, self.end + offset, self.text, self.speaker, self.probability)

@dataclass
class Sentence(TimedText):
    pass

@dataclass
class Transcript(TimedText):
    pass

@dataclass
class SpeakerSegment(TimedText):
    """Represents a segment of audio attributed to a specific speaker.
    No text nor probability is associated with this segment.
    """
    pass

@dataclass
class Translation(TimedText):
    pass

    def approximate_cut_at(self, cut_time):
        """
        Each word in text is considered to be of duration (end-start)/len(words in text)
        """
        if not self.text or not self.contains_time(cut_time):
            return self, None

        words = self.text.split()
        num_words = len(words)
        if num_words == 0:
            return self, None

        duration_per_word = self.duration() / num_words
        
        cut_word_index = int((cut_time - self.start) / duration_per_word)
        
        if cut_word_index >= num_words:
            cut_word_index = num_words -1
        
        text0 = " ".join(words[:cut_word_index])
        text1 = " ".join(words[cut_word_index:])

        segment0 = Translation(start=self.start, end=cut_time, text=text0)
        segment1 = Translation(start=cut_time, end=self.end, text=text1)

        return segment0, segment1
        

@dataclass
class Silence():
    duration: float
    
    
@dataclass
class Line(TimedText):
    translation: str = ''
    
    def to_dict(self):
        return {
            'speaker': int(self.speaker),
            'text': self.text,
            'translation': self.translation,
            'start': format_time(self.start),
            'end': format_time(self.end),
        }
        
@dataclass  
class FrontData():
    status: str = ''
    error: str = ''
    lines: list[Line] = field(default_factory=list)
    buffer_transcription: str = ''
    buffer_diarization: str = ''
    remaining_time_transcription: float = 0.
    remaining_time_diarization: float = 0.
    
    def to_dict(self):
        _dict = {
            'status': self.status,
            'lines': [line.to_dict() for line in self.lines],
            'buffer_transcription': self.buffer_transcription,
            'buffer_diarization': self.buffer_diarization,
            'remaining_time_transcription': self.remaining_time_transcription,
            'remaining_time_diarization': self.remaining_time_diarization,
        }
        if self.error:
            _dict['error'] = self.error
        return _dict
    
@dataclass  
class State():
    tokens: list
    translated_segments: list
    buffer_transcription: str
    buffer_diarization: str
    end_buffer: float
    end_attributed_speaker: float
    remaining_time_transcription: float
    remaining_time_diarization: float
