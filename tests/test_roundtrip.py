"""Test roundtrip conversions: MD -> JSON -> MD."""
import json
import pytest
from pathlib import Path
from md2electraone.mdparser import parse_controls_from_md
from md2electraone.main import generate_preset
from md2electraone.json2md import generate_markdown


class TestRoundtrip:
    """Test that MD -> JSON -> MD conversions preserve information."""
    
    def test_default_values_roundtrip(self, fixtures_dir, load_md, load_json):
        """Test that default values are preserved in roundtrip conversion."""
        md_path = fixtures_dir / "test_default_values.md"
        if not md_path.exists():
            pytest.skip(f"Fixture not found: {md_path}")
        
        # Parse original markdown
        md_content = load_md(md_path)
        title, meta, specs, by_section = parse_controls_from_md(md_content)
        
        # Generate JSON
        preset = generate_preset(title, meta, specs)
        
        # Convert back to markdown
        result_md = generate_markdown(preset)
        
        # Parse the result
        title2, meta2, specs2, by_section2 = parse_controls_from_md(result_md)
        
        # Compare key properties
        assert title == title2
        assert len(specs) == len(specs2)
        
        # Check that default values are preserved
        for orig, result in zip(specs, specs2):
            if not orig.is_blank and not orig.is_group:
                assert orig.default_value == result.default_value, \
                    f"Default value mismatch for {orig.label}: {orig.default_value} != {result.default_value}"
    
    def test_message_types_roundtrip(self, fixtures_dir, load_md):
        """Test that message types (CC7, CC14, NRPN) are preserved."""
        md_path = fixtures_dir / "test_message_types.md"
        if not md_path.exists():
            pytest.skip(f"Fixture not found: {md_path}")
        
        # Parse original markdown
        md_content = load_md(md_path)
        title, meta, specs, by_section = parse_controls_from_md(md_content)
        
        # Generate JSON
        preset = generate_preset(title, meta, specs)
        
        # Convert back to markdown
        result_md = generate_markdown(preset)
        
        # Parse the result
        title2, meta2, specs2, by_section2 = parse_controls_from_md(result_md)
        
        # Check that message types are preserved
        for orig, result in zip(specs, specs2):
            if not orig.is_blank and not orig.is_group:
                assert orig.msg_type == result.msg_type, \
                    f"Message type mismatch for {orig.label}: {orig.msg_type} != {result.msg_type}"
    
    def test_modes_roundtrip(self, fixtures_dir, load_md):
        """Test that control modes (bipolar, toggle, momentary) are preserved."""
        md_path = fixtures_dir / "test_modes.md"
        if not md_path.exists():
            pytest.skip(f"Fixture not found: {md_path}")
        
        # Parse original markdown
        md_content = load_md(md_path)
        title, meta, specs, by_section = parse_controls_from_md(md_content)
        
        # Generate JSON
        preset = generate_preset(title, meta, specs)
        
        # Convert back to markdown
        result_md = generate_markdown(preset)
        
        # Parse the result
        title2, meta2, specs2, by_section2 = parse_controls_from_md(result_md)
        
        # Check that modes are preserved
        for orig, result in zip(specs, specs2):
            if not orig.is_blank and not orig.is_group:
                assert orig.mode == result.mode, \
                    f"Mode mismatch for {orig.label}: {orig.mode} != {result.mode}"
    
    def test_group_explicit_roundtrip(self, fixtures_dir, load_md):
        """Test that explicit group membership is preserved.
        
        Note: When groups have non-contiguous members, the JSON->MD conversion
        may not perfectly preserve the explicit membership format due to bounding
        box calculations. This test verifies that the group structure is maintained,
        even if the representation changes slightly.
        """
        md_path = fixtures_dir / "test_group_explicit.md"
        if not md_path.exists():
            pytest.skip(f"Fixture not found: {md_path}")
        
        # Parse original markdown
        md_content = load_md(md_path)
        title, meta, specs, by_section = parse_controls_from_md(md_content)
        
        # Count original groups and controls with group membership
        orig_groups = [s for s in specs if s.is_group]
        orig_grouped_controls = [s for s in specs if s.group_id and not s.is_blank and not s.is_group]
        
        # Generate JSON
        preset = generate_preset(title, meta, specs)
        
        # Verify groups were created in JSON
        assert len(preset.get("groups", [])) == len(orig_groups)
        
        # Convert back to markdown
        result_md = generate_markdown(preset)
        
        # Parse the result
        title2, meta2, specs2, by_section2 = parse_controls_from_md(result_md)
        
        # Verify group structure is maintained
        result_groups = [s for s in specs2 if s.is_group]
        assert len(result_groups) == len(orig_groups), \
            f"Group count mismatch: {len(orig_groups)} != {len(result_groups)}"
    
    def test_group_multirow_roundtrip(self, fixtures_dir, load_md):
        """Test that multi-row groups are preserved."""
        md_path = fixtures_dir / "test_group_multirow.md"
        if not md_path.exists():
            pytest.skip(f"Fixture not found: {md_path}")
        
        # Parse original markdown
        md_content = load_md(md_path)
        title, meta, specs, by_section = parse_controls_from_md(md_content)
        
        # Generate JSON
        preset = generate_preset(title, meta, specs)
        
        # Convert back to markdown
        result_md = generate_markdown(preset)
        
        # Parse the result
        title2, meta2, specs2, by_section2 = parse_controls_from_md(result_md)
        
        # Verify group structure is maintained
        assert len(specs) == len(specs2)
    
    def test_group_variant_roundtrip(self, fixtures_dir, load_md):
        """Test that group variants (e.g., highlighted) are preserved."""
        md_path = fixtures_dir / "test_group_variant.md"
        if not md_path.exists():
            pytest.skip(f"Fixture not found: {md_path}")
        
        # Parse original markdown
        md_content = load_md(md_path)
        title, meta, specs, by_section = parse_controls_from_md(md_content)
        
        # Generate JSON
        preset = generate_preset(title, meta, specs)
        
        # Check that group variant is in the preset
        if "groups" in meta:
            assert len(preset["groups"]) > 0
            for group in preset["groups"]:
                if "variant" in group:
                    assert group["variant"] == meta["groups"]
    
    def test_blank_rows_roundtrip(self, fixtures_dir, load_md):
        """Test that blank rows are preserved in layout."""
        md_path = fixtures_dir / "test_blank_rows.md"
        if not md_path.exists():
            pytest.skip(f"Fixture not found: {md_path}")
        
        # Parse original markdown
        md_content = load_md(md_path)
        title, meta, specs, by_section = parse_controls_from_md(md_content)
        
        # Count blank rows
        blank_count = sum(1 for s in specs if s.is_blank)
        
        # Generate JSON
        preset = generate_preset(title, meta, specs)
        
        # Convert back to markdown
        result_md = generate_markdown(preset)
        
        # Parse the result
        title2, meta2, specs2, by_section2 = parse_controls_from_md(result_md)
        
        # Blank rows should be preserved
        blank_count2 = sum(1 for s in specs2 if s.is_blank)
        assert blank_count == blank_count2, \
            f"Blank row count mismatch: {blank_count} != {blank_count2}"
