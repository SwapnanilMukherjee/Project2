# backend/editor/models/formatting.py
from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class StyleRange:
    """Represents a range of styled text"""
    pieceIndex: int
    offsetInPiece: int
    length: int
    priority: int
    styles: Dict[str, Any]

    def overlaps(self, other: 'StyleRange') -> bool:
        """Check if this style range overlaps with another"""
        if self.pieceIndex != other.pieceIndex:
            return False
            
        self_end = self.offsetInPiece + self.length
        other_end = other.offsetInPiece + other.length
        return not (self_end <= other.offsetInPiece or other_end <= self.offsetInPiece)

    def split(self, offset: int) -> tuple['StyleRange', Optional['StyleRange']]:
        """Split style range at given offset"""
        if offset <= 0:
            return None, self
        if offset >= self.length:
            return self, None
            
        first = StyleRange(
            pieceIndex=self.pieceIndex,
            offsetInPiece=self.offsetInPiece,
            length=offset,
            priority=self.priority,
            styles=dict(self.styles)
        )
        
        second = StyleRange(
            pieceIndex=self.pieceIndex,
            offsetInPiece=self.offsetInPiece + offset,
            length=self.length - offset,
            priority=self.priority,
            styles=dict(self.styles)
        )
        
        return first, second

@dataclass
class LineMarker:
    """Represents a line in the document"""
    pieceIndex: int
    offsetInPiece: int
    type: str  # paragraph | bullet | heading
    properties: Dict[str, Any]

    def update_position(self, delta: int) -> None:
        """Update position after text changes"""
        self.offsetInPiece += delta

@dataclass
class BlockDescriptor:
    """Represents a block of text (e.g., code block, quote)"""
    startPieceIndex: int
    startOffset: int
    endPieceIndex: int
    endOffset: int
    type: str  # quote | code | list
    properties: Dict[str, Any]

    def contains_position(self, piece_index: int, offset: int) -> bool:
        """Check if position is within block"""
        if piece_index < self.startPieceIndex or piece_index > self.endPieceIndex:
            return False
            
        if piece_index == self.startPieceIndex and offset < self.startOffset:
            return False
            
        if piece_index == self.endPieceIndex and offset > self.endOffset:
            return False
            
        return True

class FormattingManager:
    """Manages document formatting"""
    def __init__(self):
        self.styles: list[StyleRange] = []
        self.lines: list[LineMarker] = []
        self.blocks: list[BlockDescriptor] = []

    def add_style(self, style: StyleRange) -> None:
        """Add new style range"""
        # Remove any overlapping styles with same properties
        self.styles = [
            s for s in self.styles
            if not (s.overlaps(style) and any(k in s.styles for k in style.styles))
        ]
        self.styles.append(style)
        self._sort_styles()

    def add_line_marker(self, marker: LineMarker) -> None:
        """Add new line marker"""
        # Remove existing marker at same position
        self.lines = [
            l for l in self.lines
            if not (l.pieceIndex == marker.pieceIndex and 
                   l.offsetInPiece == marker.offsetInPiece)
        ]
        self.lines.append(marker)
        self._sort_lines()

    def add_block(self, block: BlockDescriptor) -> None:
        """Add new block descriptor"""
        # Remove overlapping blocks of same type
        self.blocks = [
            b for b in self.blocks
            if not (b.type == block.type and self._blocks_overlap(b, block))
        ]
        self.blocks.append(block)
        self._sort_blocks()

    def get_styles_at_position(self, piece_index: int, offset: int) -> list[StyleRange]:
        """Get all styles applied at position"""
        return [
            style for style in self.styles
            if (style.pieceIndex == piece_index and 
                style.offsetInPiece <= offset < style.offsetInPiece + style.length)
        ]

    def get_line_at_position(self, piece_index: int, offset: int) -> Optional[LineMarker]:
        """Get line marker at position"""
        for line in reversed(self.lines):
            if (line.pieceIndex < piece_index or 
                (line.pieceIndex == piece_index and line.offsetInPiece <= offset)):
                return line
        return None

    def get_block_at_position(self, piece_index: int, offset: int) -> Optional[BlockDescriptor]:
        """Get block at position"""
        for block in self.blocks:
            if block.contains_position(piece_index, offset):
                return block
        return None

    def update_positions(self, piece_index: int, offset: int, delta: int) -> None:
        """Update positions after text changes"""
        for style in self.styles:
            if (style.pieceIndex == piece_index and 
                style.offsetInPiece >= offset):
                style.offsetInPiece += delta

        for line in self.lines:
            if (line.pieceIndex == piece_index and 
                line.offsetInPiece >= offset):
                line.offsetInPiece += delta

        for block in self.blocks:
            if (block.startPieceIndex == piece_index and 
                block.startOffset >= offset):
                block.startOffset += delta
            if (block.endPieceIndex == piece_index and 
                block.endOffset >= offset):
                block.endOffset += delta

    def _sort_styles(self) -> None:
        """Sort styles by piece index and offset"""
        self.styles.sort(key=lambda s: (s.pieceIndex, s.offsetInPiece))

    def _sort_lines(self) -> None:
        """Sort lines by piece index and offset"""
        self.lines.sort(key=lambda l: (l.pieceIndex, l.offsetInPiece))

    def _sort_blocks(self) -> None:
        """Sort blocks by start position"""
        self.blocks.sort(key=lambda b: (b.startPieceIndex, b.startOffset))

    def _blocks_overlap(self, b1: BlockDescriptor, b2: BlockDescriptor) -> bool:
        """Check if two blocks overlap"""
        if b1.startPieceIndex > b2.endPieceIndex or b2.startPieceIndex > b1.endPieceIndex:
            return False
            
        if (b1.startPieceIndex == b2.endPieceIndex and 
            b1.startOffset >= b2.endOffset):
            return False
            
        if (b2.startPieceIndex == b1.endPieceIndex and 
            b2.startOffset >= b1.endOffset):
            return False
            
        return True