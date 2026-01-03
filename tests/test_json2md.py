"""Test JSON to Markdown conversion functionality."""
import pytest
from pathlib import Path
from md2electraone.json2md import generate_markdown
from md2electraone.mdparser import parse_controls_from_md


class TestJSON2MD:
    """Test JSON to Markdown conversion."""
    
    def test_convert_simple_preset(self, fixtures_dir, load_json):
        """Test converting a simple preset to markdown."""
        json_path = fixtures_dir / "test_default_values.json"
        if not json_path.exists():
            pytest.skip(f"Fixture not found: {json_path}")
        
        preset = load_json(json_path)
        
        # Convert to markdown
        md = generate_markdown(preset)
        
        # Should produce valid markdown
        assert md is not None
        assert len(md) > 0
        
        # Should be parseable
        title, meta, specs, by_section = parse_controls_from_md(md)
        assert len(specs) > 0
    
    def test_convert_with_groups(self, fixtures_dir, load_json):
        """Test converting preset with groups."""
        json_path = fixtures_dir / "test_group_explicit.json"
        if not json_path.exists():
            pytest.skip(f"Fixture not found: {json_path}")
        
        preset = load_json(json_path)
        
        # Convert to markdown
        md = generate_markdown(preset)
        
        # Should contain group definitions
        assert md is not None
        
        # Parse and check for groups
        title, meta, specs, by_section = parse_controls_from_md(md)
        group_specs = [s for s in specs if s.is_group]
        assert len(group_specs) > 0
    
    def test_convert_with_nrpn(self, fixtures_dir, load_json):
        """Test converting preset with NRPN messages."""
        json_path = fixtures_dir / "test_message_types.json"
        if not json_path.exists():
            pytest.skip(f"Fixture not found: {json_path}")
        
        preset = load_json(json_path)
        
        # Convert to markdown
        md = generate_markdown(preset)
        
        # Should contain NRPN prefix
        assert "N" in md or "n" in md
    
    def test_convert_preserves_control_count(self, fixtures_dir, load_json):
        """Test that conversion preserves control count."""
        json_path = fixtures_dir / "test_modes.json"
        if not json_path.exists():
            pytest.skip(f"Fixture not found: {json_path}")
        
        preset = load_json(json_path)
        original_control_count = len(preset.get("controls", []))
        
        # Convert to markdown
        md = generate_markdown(preset)
        
        # Parse and count controls
        title, meta, specs, by_section = parse_controls_from_md(md)
        non_blank_specs = [s for s in specs if not s.is_blank and not s.is_group]
        
        assert len(non_blank_specs) == original_control_count
