# backend/editor/services/merge_service.py
from typing import List, Dict, Any, Optional
from ..models import Document, Change, PieceTable
from ..utils.diff import create_diff, apply_diff

class MergeService:
    def apply_change(self, document: Document, change: Change) -> bool:
        """Apply a change to the document using three-way merge"""
        # Get the base version (when change was made)
        base_version = document.versions.filter(version=change.source_version).first()
        if not base_version:
            return False
            
        # Get current version's piece table
        current_table = document.get_piece_table()
        
        # Get base version's piece table
        base_table = PieceTable.from_json(base_version.content)
        
        # Create diffs
        current_diff = create_diff(base_table, current_table)
        change_diff = self._change_to_diff(change)
        
        # Merge diffs
        merged_diff = self._merge_diffs(current_diff, change_diff)
        if not merged_diff:
            return False
            
        # Apply merged changes
        try:
            self._apply_merged_changes(document, merged_diff)
            return True
        except Exception:
            return False

    def _change_to_diff(self, change: Change) -> Dict[str, Any]:
        """Convert a Change object to a diff format"""
        return {
            'type': change.operation_type,
            'position': change.position,
            'content': change.content,
            'attributes': change.attributes
        }

    def _merge_diffs(
        self,
        current_diff: Dict[str, Any],
        change_diff: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Merge two diffs using operational transformation"""
        # If changes don't overlap, apply both
        if not self._changes_overlap(current_diff, change_diff):
            return self._combine_non_overlapping_diffs(current_diff, change_diff)
            
        # If changes overlap, apply conflict resolution rules
        return self._resolve_conflict(current_diff, change_diff)

    def _changes_overlap(
        self,
        diff1: Dict[str, Any],
        diff2: Dict[str, Any]
    ) -> bool:
        """Check if two changes overlap in the document"""
        pos1 = diff1['position']
        pos2 = diff2['position']
        
        # Calculate affected ranges
        len1 = len(diff1.get('content', '')) if diff1['type'] == 'insert' else diff1.get('length', 0)
        len2 = len(diff2.get('content', '')) if diff2['type'] == 'insert' else diff2.get('length', 0)
        
        # Check for overlap
        return not (pos1 + len1 <= pos2 or pos2 + len2 <= pos1)

    def _combine_non_overlapping_diffs(
        self,
        diff1: Dict[str, Any],
        diff2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Combine two non-overlapping diffs"""
        # Sort diffs by position
        diffs = sorted([diff1, diff2], key=lambda x: x['position'])
        
        # Adjust second diff position based on first diff
        if diffs[0]['type'] == 'insert':
            length = len(diffs[0]['content'])
            diffs[1]['position'] += length
        elif diffs[0]['type'] == 'delete':
            length = diffs[0].get('length', 0)
            diffs[1]['position'] -= length
            
        return {
            'type': 'compound',
            'operations': diffs
        }

    def _resolve_conflict(
        self,
        current_diff: Dict[str, Any],
        change_diff: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Resolve conflict between overlapping changes"""
        # For this implementation, we'll use a simple "latest wins" strategy
        # More sophisticated conflict resolution can be implemented here
        
        # If both are style changes, merge them
        if current_diff['type'] == 'style' and change_diff['type'] == 'style':
            return self._merge_style_changes(current_diff, change_diff)
            
        # For text changes, take the latest change
        return change_diff

    def _merge_style_changes(
        self,
        style1: Dict[str, Any],
        style2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merge two style changes"""
        # Combine style attributes, with style2 taking precedence
        merged_attributes = {
            **style1.get('attributes', {}),
            **style2.get('attributes', {})
        }
        
        return {
            'type': 'style',
            'position': style1['position'],
            'length': style1['length'],
            'attributes': merged_attributes
        }

    def _apply_merged_changes(self, document: Document, merged_diff: Dict[str, Any]):
        """Apply merged changes to the document"""
        piece_table = document.get_piece_table()
        
        if merged_diff['type'] == 'compound':
            # Apply each operation in sequence
            for op in merged_diff['operations']:
                self._apply_single_operation(piece_table, op)
        else:
            # Apply single operation
            self._apply_single_operation(piece_table, merged_diff)
            
        # Update document version
        document.current_version += 0.1
        document.update_content(piece_table)
        
        # Create new version record
        document.versions.create(
            version=document.current_version,
            content=document.content
        )

    def _apply_single_operation(self, piece_table: PieceTable, operation: Dict[str, Any]):
        """Apply a single operation to the piece table"""
        op_type = operation['type']
        position = operation['position']
        
        if op_type == 'insert':
            piece_table.insert(position, operation['content'])
        elif op_type == 'delete':
            piece_table.delete(position, operation['length'])
        elif op_type == 'style':
            self._apply_style(piece_table, operation)

    def _apply_style(self, piece_table: PieceTable, style_op: Dict[str, Any]):
        """Apply a style operation to the piece table"""
        piece_index, offset = piece_table._find_piece_at_position(style_op['position'])
        
        style_range = StyleRange(
            piece_index=piece_index,
            start_offset=offset,
            length=style_op['length'],
            attributes=style_op['attributes']
        )
        
        # Remove any overlapping styles for same attributes
        piece_table.styles = [
            s for s in piece_table.styles
            if not (s.overlaps(style_range) and 
                   any(k in s.attributes for k in style_range.attributes))
        ]
        
        # Add new style range
        piece_table.styles.append(style_range)