
# backend/editor/models/piece_table.py
from dataclasses import dataclass
from typing import List, Dict, Optional
import json

@dataclass
class Piece:
    buffer_type: str  # 'original' or 'add'
    start: int
    length: int
    line_start: bool = False
    
    def split(self, offset: int) -> tuple['Piece', 'Piece']:
        """Split piece at given offset"""
        if offset <= 0 or offset >= self.length:
            raise ValueError("Invalid split offset")
            
        first = Piece(
            buffer_type=self.buffer_type,
            start=self.start,
            length=offset,
            line_start=self.line_start
        )
        
        second = Piece(
            buffer_type=self.buffer_type,
            start=self.start + offset,
            length=self.length - offset,
            line_start=False
        )
        
        return first, second

@dataclass
class StyleRange:
    piece_index: int
    start_offset: int
    length: int
    attributes: Dict

    def overlaps(self, other: 'StyleRange') -> bool:
        """Check if this style range overlaps with another"""
        self_end = self.start_offset + self.length
        other_end = other.start_offset + other.length
        return not (self_end <= other.start_offset or other_end <= self.start_offset)

@dataclass
class LineMarker:
    piece_index: int
    offset: int
    type: str  # paragraph, bullet, heading
    properties: Dict

class PieceTable:
    def __init__(self):
        self.original_buffer = ""
        self.add_buffer = ""
        self.pieces: List[Piece] = []
        self.styles: List[StyleRange] = []
        self.lines: List[LineMarker] = []
    
    def insert(self, position: int, text: str) -> None:
        """Insert text at given position"""
        if not text:
            return
            
        piece_index, offset = self._find_piece_at_position(position)
        
        # Add text to add buffer
        add_buffer_pos = len(self.add_buffer)
        self.add_buffer += text
        
        # Create new piece for inserted text
        new_piece = Piece(
            buffer_type='add',
            start=add_buffer_pos,
            length=len(text)
        )
        
        if offset > 0:
            # Split existing piece
            curr_piece = self.pieces[piece_index]
            first, second = curr_piece.split(offset)
            self.pieces[piece_index] = first
            self.pieces.insert(piece_index + 1, new_piece)
            self.pieces.insert(piece_index + 2, second)
        else:
            # Insert before current piece
            self.pieces.insert(piece_index, new_piece)
            
        self._update_markers(piece_index, len(text))
    
    def delete(self, position: int, length: int) -> None:
        """Delete text at given position"""
        if length <= 0:
            return
            
        start_piece_index, start_offset = self._find_piece_at_position(position)
        end_piece_index, end_offset = self._find_piece_at_position(position + length)
        
        # Handle start piece
        if start_offset > 0:
            curr_piece = self.pieces[start_piece_index]
            first, _ = curr_piece.split(start_offset)
            self.pieces[start_piece_index] = first
            start_piece_index += 1
            
        # Handle end piece
        if end_offset < self.pieces[end_piece_index].length:
            curr_piece = self.pieces[end_piece_index]
            _, second = curr_piece.split(end_offset)
            self.pieces[end_piece_index] = second
        else:
            end_piece_index += 1
            
        # Remove pieces in between
        del self.pieces[start_piece_index:end_piece_index]
        
        self._update_markers(start_piece_index, -length)
    
    def _find_piece_at_position(self, position: int) -> tuple[int, int]:
        """Find piece and offset within piece for given position"""
        curr_pos = 0
        for i, piece in enumerate(self.pieces):
            if curr_pos <= position < curr_pos + piece.length:
                return i, position - curr_pos
            curr_pos += piece.length
        return len(self.pieces), 0
    
    def _update_markers(self, piece_index: int, delta: int) -> None:
        """Update style ranges and line markers after an edit"""
        # Update style ranges
        for style in self.styles:
            if style.piece_index > piece_index:
                style.start_offset += delta
                
        # Update line markers
        for marker in self.lines:
            if marker.piece_index > piece_index:
                marker.offset += delta
    
    def get_text(self) -> str:
        """Get complete text from piece table"""
        result = []
        for piece in self.pieces:
            buffer = self.original_buffer if piece.buffer_type == 'original' else self.add_buffer
            result.append(buffer[piece.start:piece.start + piece.length])
        return ''.join(result)
    
    def to_json(self) -> dict:
        """Convert piece table to JSON representation"""
        return {
            'originalBuffer': self.original_buffer,
            'addBuffer': self.add_buffer,
            'pieces': [vars(p) for p in self.pieces],
            'styles': [vars(s) for s in self.styles],
            'lines': [vars(l) for l in self.lines]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> 'PieceTable':
        """Create piece table from JSON representation"""
        table = cls()
        table.original_buffer = data['originalBuffer']
        table.add_buffer = data['addBuffer']
        table.pieces = [Piece(**p) for p in data['pieces']]
        table.styles = [StyleRange(**s) for s in data['styles']]
        table.lines = [LineMarker(**l) for l in data['lines']]
        return table