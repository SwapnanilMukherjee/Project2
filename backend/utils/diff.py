# backend/editor/utils/diff.py
from typing import List, Dict, Any, Tuple
from ..models import PieceTable

class DiffCalculator:
    """Calculates differences between piece tables"""
    
    def create_diff(self, source: PieceTable, target: PieceTable) -> List[Dict[str, Any]]:
        """Create a diff between two piece tables"""
        source_text = source.get_text()
        target_text = target.get_text()
        
        # Convert texts to lists of characters for easier processing
        source_chars = list(source_text)
        target_chars = list(target_text)
        
        # Get longest common subsequence
        lcs = self._get_lcs(source_chars, target_chars)
        
        # Generate operations from LCS
        operations = self._generate_operations(source_chars, target_chars, lcs)
        
        # Add style changes
        style_ops = self._compare_styles(source, target)
        operations.extend(style_ops)
        
        # Add line marker changes
        line_ops = self._compare_lines(source, target)
        operations.extend(line_ops)
        
        return operations

    def apply_diff(self, piece_table: PieceTable, operations: List[Dict[str, Any]]) -> None:
        """Apply diff operations to piece table"""
        position_offset = 0
        
        for op in operations:
            op_type = op['type']
            position = op['position'] + position_offset
            
            if op_type == 'insert':
                piece_table.insert(position, op['content'])
                position_offset += len(op['content'])
            elif op_type == 'delete':
                piece_table.delete(position, op['length'])
                position_offset -= op['length']
            elif op_type == 'style':
                piece_table.styles.append({
                    'pieceIndex': piece_table._find_piece_at_position(position)[0],
                    'startOffset': position,
                    'length': op['length'],
                    'attributes': op['attributes']
                })
            elif op_type == 'line':
                piece_table.lines.append({
                    'pieceIndex': piece_table._find_piece_at_position(position)[0],
                    'offset': position,
                    'type': op['lineType'],
                    'properties': op['properties']
                })

    def _get_lcs(self, seq1: List[str], seq2: List[str]) -> List[Tuple[int, int]]:
        """Get longest common subsequence between two sequences"""
        m, n = len(seq1), len(seq2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        # Fill dp table
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if seq1[i - 1] == seq2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1] + 1
                else:
                    dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
        
        # Backtrack to get LCS positions
        lcs = []
        i, j = m, n
        while i > 0 and j > 0:
            if seq1[i - 1] == seq2[j - 1]:
                lcs.append((i - 1, j - 1))
                i -= 1
                j -= 1
            elif dp[i - 1][j] > dp[i][j - 1]:
                i -= 1
            else:
                j -= 1
                
        return list(reversed(lcs))

    def _generate_operations(
        self,
        source: List[str],
        target: List[str],
        lcs: List[Tuple[int, int]]
    ) -> List[Dict[str, Any]]:
        """Generate insert and delete operations from LCS"""
        operations = []
        source_pos = target_pos = 0
        
        for lcs_source_pos, lcs_target_pos in lcs:
            # Handle deletions
            while source_pos < lcs_source_pos:
                operations.append({
                    'type': 'delete',
                    'position': source_pos,
                    'length': 1
                })
                source_pos += 1
            
            # Handle insertions
            while target_pos < lcs_target_pos:
                operations.append({
                    'type': 'insert',
                    'position': target_pos,
                    'content': target[target_pos]
                })
                target_pos += 1
            
            source_pos += 1
            target_pos += 1
        
        # Handle remaining characters
        while source_pos < len(source):
            operations.append({
                'type': 'delete',
                'position': source_pos,
                'length': 1
            })
            source_pos += 1
            
        while target_pos < len(target):
            operations.append({
                'type': 'insert',
                'position': target_pos,
                'content': target[target_pos]
            })
            target_pos += 1
        
        return self._optimize_operations(operations)

    def _optimize_operations(self, operations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Combine adjacent operations of same type"""
        if not operations:
            return operations
            
        optimized = []
        current_op = dict(operations[0])
        
        for op in operations[1:]:
            if (op['type'] == current_op['type'] and 
                op['position'] == current_op['position'] + 
                (current_op.get('length', len(current_op.get('content', ''))))):
                
                if op['type'] == 'delete':
                    current_op['length'] += op['length']
                else:  # insert
                    current_op['content'] += op['content']
            else:
                optimized.append(current_op)
                current_op = dict(op)
        
        optimized.append(current_op)
        return optimized

    def _compare_styles(self, source: PieceTable, target: PieceTable) -> List[Dict[str, Any]]:
        """Compare style ranges between two piece tables"""
        operations = []
        
        # Track processed styles to detect removals
        processed_styles = set()
        
        for target_style in target.styles:
            matching_source_style = None
            
            for source_style in source.styles:
                if (source_style.pieceIndex == target_style.pieceIndex and
                    source_style.offsetInPiece == target_style.offsetInPiece and
                    source_style.length == target_style.length):
                    matching_source_style = source_style
                    processed_styles.add(id(source_style))
                    break
            
            if not matching_source_style or matching_source_style.styles != target_style.styles:
                operations.append({
                    'type': 'style',
                    'position': target_style.offsetInPiece,
                    'length': target_style.length,
                    'attributes': target_style.styles
                })
        
        # Handle removed styles
        for source_style in source.styles:
            if id(source_style) not in processed_styles:
                operations.append({
                    'type': 'style',
                    'position': source_style.offsetInPiece,
                    'length': source_style.length,
                    'attributes': {}  # Empty attributes to remove style
                })
        
        return operations

    def _compare_lines(self, source: PieceTable, target: PieceTable) -> List[Dict[str, Any]]:
        """Compare line markers between two piece tables"""
        operations = []
        processed_lines = set()
        
        for target_line in target.lines:
            matching_source_line = None
            
            for source_line in source.lines:
                if (source_line.pieceIndex == target_line.pieceIndex and
                    source_line.offsetInPiece == target_line.offsetInPiece):
                    matching_source_line = source_line
                    processed_lines.add(id(source_line))
                    break
            
            if not matching_source_line or (
                matching_source_line.type != target_line.type or
                matching_source_line.properties != target_line.properties
            ):
                operations.append({
                    'type': 'line',
                    'position': target_line.offsetInPiece,
                    'lineType': target_line.type,
                    'properties': target_line.properties
                })
        
        # Handle removed lines
        for source_line in source.lines:
            if id(source_line) not in processed_lines:
                operations.append({
                    'type': 'line',
                    'position': source_line.offsetInPiece,
                    'lineType': 'paragraph',  # Reset to default
                    'properties': {}  # Reset properties
                })
        
        return operations

def create_diff(source: PieceTable, target: PieceTable) -> List[Dict[str, Any]]:
    """Create diff between two piece tables"""
    calculator = DiffCalculator()
    return calculator.create_diff(source, target)

def apply_diff(piece_table: PieceTable, operations: List[Dict[str, Any]]) -> None:
    """Apply diff operations to piece table"""
    calculator = DiffCalculator()
    calculator.apply_diff(piece_table, operations)