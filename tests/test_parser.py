"""Test markdown parsing functionality."""
import pytest
from pathlib import Path
from md2electraone.mdparser import (
    parse_cc,
    parse_range,
    parse_choices,
    parse_color,
    parse_frontmatter,
    infer_mode,
    parse_controls_from_md,
)


class TestCCParsing:
    """Test CC number parsing with various formats."""
    
    def test_parse_decimal_cc(self):
        """Test parsing decimal CC numbers."""
        msg_type, cc, device_id = parse_cc("10")
        assert msg_type == "C"
        assert cc == 10
        assert device_id is None
    
    def test_parse_hex_cc_with_prefix(self):
        """Test parsing hex CC numbers with 0x prefix."""
        msg_type, cc, device_id = parse_cc("0x1A")
        assert msg_type == "C"
        assert cc == 26
        assert device_id is None
    
    def test_parse_hex_cc_without_prefix(self):
        """Test parsing hex CC numbers without prefix."""
        msg_type, cc, device_id = parse_cc("1A")
        assert msg_type == "C"
        assert cc == 26
        assert device_id is None
    
    def test_parse_nrpn(self):
        """Test parsing NRPN message type."""
        msg_type, cc, device_id = parse_cc("N100")
        assert msg_type == "N"
        assert cc == 100
        assert device_id is None
    
    def test_parse_cc_with_prefix(self):
        """Test parsing CC with explicit C prefix."""
        msg_type, cc, device_id = parse_cc("C10")
        assert msg_type == "C"
        assert cc == 10
        assert device_id is None
    
    def test_parse_envelope_ccs(self):
        """Test parsing comma-separated CCs for envelopes."""
        msg_type, ccs, device_id = parse_cc("1,2,3,4")
        assert msg_type == "C"
        assert ccs == [1, 2, 3, 4]
        assert device_id is None
    
    def test_parse_invalid_cc(self):
        """Test parsing invalid CC returns None."""
        msg_type, cc, device_id = parse_cc("invalid")
        assert msg_type == "C"
        assert cc is None
        assert device_id is None
    
    def test_parse_device_prefix(self):
        """Test parsing CC with device prefix."""
        msg_type, cc, device_id = parse_cc("1:10")
        assert msg_type == "C"
        assert cc == 10
        assert device_id == 1
    
    def test_parse_device_prefix_with_message_type(self):
        """Test parsing CC with both device prefix and message type."""
        msg_type, cc, device_id = parse_cc("2:N100")
        assert msg_type == "N"
        assert cc == 100
        assert device_id == 2


class TestRangeParsing:
    """Test range parsing with various formats."""
    
    def test_parse_simple_range(self):
        """Test parsing simple range."""
        minv, maxv, default = parse_range("0-127")
        assert minv == 0
        assert maxv == 127
        assert default is None
    
    def test_parse_negative_range(self):
        """Test parsing range with negative values."""
        minv, maxv, default = parse_range("-64-63")
        assert minv == -64
        assert maxv == 63
        assert default is None
    
    def test_parse_range_with_default(self):
        """Test parsing range with default value."""
        minv, maxv, default = parse_range("0-127 (64)")
        assert minv == 0
        assert maxv == 127
        assert default == 64
    
    def test_parse_negative_range_with_default(self):
        """Test parsing negative range with default."""
        minv, maxv, default = parse_range("-64-63 (0)")
        assert minv == -64
        assert maxv == 63
        assert default == 0
    
    def test_parse_single_value(self):
        """Test parsing single value as range."""
        minv, maxv, default = parse_range("64")
        assert minv == 64
        assert maxv == 64
        assert default is None


class TestChoicesParsing:
    """Test choices/options parsing."""
    
    def test_parse_simple_choices(self):
        """Test parsing simple comma-separated choices."""
        choices = parse_choices("Off, On", 0, 127)
        assert len(choices) == 2
        assert (0, "Off") in choices
        assert (1, "On") in choices
    
    def test_parse_choices_with_values(self):
        """Test parsing choices with explicit values."""
        choices = parse_choices("Off(0), On(127)", 0, 127)
        assert len(choices) == 2
        assert (0, "Off") in choices
        assert (127, "On") in choices
    
    def test_parse_choices_with_equals(self):
        """Test parsing choices with = syntax."""
        choices = parse_choices("0=Off, 127=On", 0, 127)
        assert len(choices) == 2
        assert (0, "Off") in choices
        assert (127, "On") in choices
    
    def test_parse_range_expansion(self):
        """Test parsing range expansion like 2-5=USB1-USB4."""
        choices = parse_choices("2-5=USB1-USB4", 0, 127)
        assert len(choices) == 4
        # Check that values 2-5 are present
        values = [v for v, _ in choices]
        assert 2 in values
        assert 5 in values


class TestColorParsing:
    """Test color value parsing."""
    
    def test_parse_color_with_hash(self):
        """Test parsing color with # prefix."""
        color = parse_color("#FF0000")
        assert color == "FF0000"
    
    def test_parse_color_without_hash(self):
        """Test parsing color without # prefix."""
        color = parse_color("FF0000")
        assert color == "FF0000"
    
    def test_parse_lowercase_color(self):
        """Test parsing lowercase color."""
        color = parse_color("ff0000")
        assert color == "FF0000"
    
    def test_parse_invalid_color(self):
        """Test parsing invalid color returns None."""
        color = parse_color("invalid")
        assert color is None
    
    def test_parse_empty_color(self):
        """Test parsing empty color returns None."""
        color = parse_color("")
        assert color is None


class TestFrontmatterParsing:
    """Test YAML frontmatter parsing."""
    
    def test_parse_simple_frontmatter(self):
        """Test parsing simple frontmatter."""
        md = """---
name: Test Device
version: 2
port: 1
channel: 5
---

# Test"""
        meta, remaining = parse_frontmatter(md)
        assert meta["name"] == "Test Device"
        assert meta["version"] == 2
        assert meta["port"] == 1
        assert meta["channel"] == 5
        assert "# Test" in remaining
    
    def test_parse_nested_frontmatter(self):
        """Test parsing nested frontmatter."""
        md = """---
name: Test
midi:
  port: 1
  channel: 5
---

# Test"""
        meta, remaining = parse_frontmatter(md)
        assert meta["name"] == "Test"
        assert "midi" in meta
        assert meta["midi"]["port"] == 1
        assert meta["midi"]["channel"] == 5
    
    def test_parse_no_frontmatter(self):
        """Test parsing markdown without frontmatter."""
        md = "# Test\n\nNo frontmatter here"
        meta, remaining = parse_frontmatter(md)
        assert meta == {}
        assert remaining == md


class TestModeInference:
    """Test control mode inference."""
    
    def test_infer_bipolar_mode(self):
        """Test inferring bipolar mode for negative ranges."""
        mode = infer_mode(-64, 63, [])
        assert mode == "bipolar"
    
    def test_infer_momentary_mode(self):
        """Test inferring momentary mode."""
        choices = [(0, "Released"), (127, "Momentary")]
        mode = infer_mode(0, 127, choices)
        assert mode == "momentary"
    
    def test_infer_no_mode_for_toggle(self):
        """Test that toggle controls return None (handled elsewhere)."""
        choices = [(0, "Off"), (127, "On")]
        mode = infer_mode(0, 127, choices)
        assert mode is None
    
    def test_infer_no_mode_for_positive_range(self):
        """Test that positive ranges return None (use default)."""
        mode = infer_mode(0, 127, [])
        assert mode is None


class TestGroupColorInheritance:
    """Test that group colors are inherited by group members."""
    
    def test_group_color_inheritance(self):
        """Test that group members without explicit colors inherit the group color."""
        fixture_path = Path(__file__).parent / "fixtures" / "test_group_color.md"
        md_content = fixture_path.read_text()
        
        title, meta, all_specs, by_section = parse_controls_from_md(md_content)
        
        # Find controls by label
        controls = {spec.label: spec for spec in all_specs if not spec.is_group}
        
        # Waveform should inherit group color FF0000
        assert controls["Waveform"].color == "FF0000"
        assert controls["Waveform"].group_id == "osc"
        
        # Octave should inherit group color FF0000
        assert controls["Octave"].color == "FF0000"
        assert controls["Octave"].group_id == "osc"
        
        # Filter Cutoff has explicit color 00FF00 (not in group)
        assert controls["Filter Cutoff"].color == "00FF00"
        assert controls["Filter Cutoff"].group_id is None
        
        # Detune has explicit color 0000FF (overrides group color)
        assert controls["Detune"].color == "0000FF"
        assert controls["Detune"].group_id == "osc"
        
        # Filter Resonance inherits from previous row's explicit color (current_color)
        assert controls["Filter Resonance"].color == "0000FF"
        assert controls["Filter Resonance"].group_id is None
        
        # Level should inherit group color FF0000
        assert controls["Level"].color == "FF0000"
        assert controls["Level"].group_id == "osc"
