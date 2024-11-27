# backend/editor/utils/version_control.py
from typing import List, Dict, Any, Optional, Tuple
from ..models import Document, DocumentVersion, Change
from ..models.piece_table import PieceTable
from .diff import create_diff, apply_diff
import json
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

class VersionControl:
    """Handles document versioning and change management"""
    
    def __init__(self, document: Document):
        self.document = document

    def create_version(self) -> DocumentVersion:
        """Create new version from current document state"""
        with transaction.atomic():
            self.document.current_version += 0.1
            self.document.save()
            
            version = DocumentVersion.objects.create(
                document=self.document,
                version=self.document.current_version,
                content=self.document.content
            )
            
            return version

    def get_version(self, version_number: float) -> Optional[DocumentVersion]:
        """Get specific version of document"""
        try:
            return DocumentVersion.objects.get(
                document=self.document,
                version=version_number
            )
        except ObjectDoesNotExist:
            return None

    def restore_version(self, version_number: float) -> bool:
        """Restore document to specific version"""
        version = self.get_version(version_number)
        if not version:
            return False
            
        with transaction.atomic():
            self.document.content = version.content
            self.document.current_version += 0.1
            self.document.save()
            
            DocumentVersion.objects.create(
                document=self.document,
                version=self.document.current_version,
                content=self.document.content
            )
            
            return True

    def record_changes(self, changes: List[Change]) -> bool:
        """Record changes and create new version"""
        with transaction.atomic():
            try:
                base_version = self.get_version(changes[0].source_version)
                if not base_version:
                    return False
                
                piece_table = PieceTable.from_json(base_version.content)
                for change in changes:
                    self._apply_change(piece_table, change)
                
                self.document.content = piece_table.to_json()
                self.document.current_version += 0.1
                self.document.save()
                
                DocumentVersion.objects.create(
                    document=self.document,
                    version=self.document.current_version,
                    content=self.document.content
                )
                
                return True
                
            except Exception:
                transaction.set_rollback(True)
                return False

    def get_changes_between_versions(
        self,
        from_version: float,
        to_version: float
    ) -> List[Change]:
        """Get all changes between two versions"""
        return Change.objects.filter(
            document=self.document,
            source_version__gte=from_version,
            source_version__lt=to_version
        ).order_by('timestamp')

    def get_version_diff(
        self,
        version1: float,
        version2: float
    ) -> Optional[List[Dict[str, Any]]]:
        """Get diff between two versions"""
        v1 = self.get_version(version1)
        v2 = self.get_version(version2)
        
        if not v1 or not v2:
            return None
            
        pt1 = PieceTable.from_json(v1.content)
        pt2 = PieceTable.from_json(v2.content)
        
        return create_diff(pt1, pt2)

    def merge_versions(
        self,
        base_version: float,
        version1: float,
        version2: float
    ) -> Optional[Tuple[PieceTable, List[Dict[str, Any]]]]:
        """Three-way merge between versions"""
        base = self.get_version(base_version)
        v1 = self.get_version(version1)
        v2 = self.get_version(version2)
        
        if not base or not v1 or not v2:
            return None
            
        base_pt = PieceTable.from_json(base.content)
        pt1 = PieceTable.from_json(v1.content)
        pt2 = PieceTable.from_json(v2.content)
        
        diff1 = create_diff(base_pt, pt1)
        diff2 = create_diff(base_pt, pt2)
        
        merged_diff = self._merge_diffs(diff1, diff2)
        
        result_pt = PieceTable.from_json(base.content)
        apply_diff(result_pt, merged_diff)
        
        return result_pt, merged_diff

    def _apply_change(self, piece_table: PieceTable, change: Change) -> None:
        """Apply single change to piece table"""
        if change.operation_type == 'insert':
            piece_table.insert(change.position, change.content)
        elif change.operation_type == 'delete':
            piece_table.delete(change.position, change.attributes.get('length', 1))
        elif change.operation_type == 'style':
            piece_table.styles.append({
                'pieceIndex': piece_table._find_piece_at_position(change.position)[0],
                'startOffset': change.position,
                'length': change.attributes.get('length', 1),
                'attributes': change.attributes.get('styles', {})
            })
        elif change.operation_type == 'line':
            piece_table.lines.append({
                'pieceIndex': piece_table._find_piece_at_position(change.position)[0],
                'offset': change.position,
                'type': change.attributes.get('lineType', 'paragraph'),
                'properties': change.attributes.get('properties', {})
            })

    def _merge_diffs(self, diff1: List[Dict[str, Any]], diff2: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Merge two sets of diffs"""
        # Sort operations by position
        sorted_diff1 = sorted(diff1, key=lambda x: x['position'])
        sorted_diff2 = sorted(diff2, key=lambda x: x['position'])
        
        merged = []
        i = j = 0
        pos_offset = 0
        
        while i < len(sorted_diff1) and j < len(sorted_diff2):
            op1 = sorted_diff1[i]
            op2 = sorted_diff2[j]
            
            # Adjust positions based on previous operations
            adj_pos1 = op1['position'] + pos_offset
            adj_pos2 = op2['position'] + pos_offset
            
            if adj_pos1 < adj_pos2:
                merged.append(self._adjust_operation(op1, pos_offset))
                pos_offset += self._get_position_offset(op1)
                i += 1
            else:
                merged.append(self._adjust_operation(op2, pos_offset))
                pos_offset += self._get_position_offset(op2)
                j += 1
        
        # Add remaining operations
        while i < len(sorted_diff1):
            merged.append(self._adjust_operation(sorted_diff1[i], pos_offset))
            i += 1
            
        while j < len(sorted_diff2):
            merged.append(self._adjust_operation(sorted_diff2[j], pos_offset))
            j += 1
        
        return merged

    def _adjust_operation(self, op: Dict[str, Any], offset: int) -> Dict[str, Any]:
        """Adjust operation position by offset"""
        adjusted = dict(op)
        adjusted['position'] += offset
        return adjusted

    def _get_position_offset(self, op: Dict[str, Any]) -> int:
        """Get position offset caused by operation"""
        if op['type'] == 'insert':
            return len(op['content'])
        elif op['type'] == 'delete':
            return -op['length']
        return 0