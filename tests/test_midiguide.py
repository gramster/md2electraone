"""Tests for midi.guide CSV import support."""

import json
import sys

from md2electraone.main import main as cli_main
from md2electraone.midiguide import parse_midiguide_csv


SAMPLE_CSV = """manufacturer,device,section,parameter_name,parameter_description,cc_msb,cc_lsb,cc_min_value,cc_max_value,cc_default_value,nrpn_msb,nrpn_lsb,nrpn_min_value,nrpn_max_value,nrpn_default_value,orientation,notes,usage
Lofty,Trundler,Oscillators,Oscillator 1 shape,Switches between sine sawtooth square and morph,5,,0,127,,,,,,,0-based,,0: Sine; 1: Sawtooth; 2: Square; 3~127: Morph
Lofty,Trundler,Oscillators,Glide switch,Enables or disables glide,65,,0,127,0,,,,,,0-based,Typo in manual (says CC 66; 65 is correct),0-63: Off; 64-127: On
Lofty,Trundler,Oscillators,Note sync,Enables and disables note sync,81,,0,1,1,,,,,,0-based,,0: Off; 1: On
Lofty,Trundler,Amp,Pan,Pans between left to right channel,66,,0,127,64,1,3,0,16383,8192,centered,Left..Centered..Right,0~127: Pan amount
"""


class TestMidiGuideImport:
    """Test midi.guide CSV parsing."""

    def test_parse_midiguide_csv_metadata_and_sections(self):
        title, meta, specs, by_section = parse_midiguide_csv(SAMPLE_CSV)

        assert title == "Trundler"
        assert meta == {"name": "Trundler", "manufacturer": "Lofty"}
        assert [section_name for section_name, _ in by_section] == ["Oscillators", "Amp"]
        assert len(specs) == 4  # Pan yields only one control (CC preferred over NRPN)

    def test_parse_midiguide_csv_usage_and_dual_mapping(self):
        _, _, specs, _ = parse_midiguide_csv(SAMPLE_CSV)

        osc_shape = next(spec for spec in specs if spec.label == "Oscillator 1 shape")
        assert osc_shape.msg_type == "C"
        assert osc_shape.cc == 5
        assert osc_shape.choices == []
        assert "Usage: 0: Sine; 1: Sawtooth; 2: Square; 3~127: Morph" in osc_shape.description

        glide = next(spec for spec in specs if spec.label == "Glide switch")
        assert glide.choices == [(0, "Off"), (64, "On")]
        assert glide.default_value == 0
        assert "Typo in manual" in glide.description

        note_sync = next(spec for spec in specs if spec.label == "Note sync")
        assert note_sync.choices == [(0, "Off"), (1, "On")]
        assert note_sync.default_value == 1

        # Pan supports both CC (66) and NRPN — only the CC version is included,
        # with the plain "Pan" label (no "(CC)" suffix).
        pan = next(spec for spec in specs if spec.label == "Pan")
        assert pan.msg_type == "C"
        assert pan.cc == 66
        assert pan.min_val == 0
        assert pan.max_val == 127
        assert pan.default_value == 64
        assert "Orientation: centered" in pan.description
        assert not any(spec.label == "Pan (CC)" or spec.label == "Pan (NRPN)" for spec in specs)

    def test_cli_accepts_midiguide_csv(self, tmp_path, monkeypatch):
        csv_path = tmp_path / "trundler.csv"
        output_json = tmp_path / "trundler.json"
        output_md = tmp_path / "trundler.md"
        csv_path.write_text(SAMPLE_CSV, encoding="utf-8")

        monkeypatch.setattr(
            sys,
            "argv",
            [
                "md2electraone",
                str(csv_path),
                "-o",
                str(output_json),
                "--clean-md",
                str(output_md),
            ],
        )

        assert cli_main() == 0

        preset = json.loads(output_json.read_text(encoding="utf-8"))
        control_names = {control["name"] for control in preset["controls"]}
        assert preset["name"] == "Trundler"
        assert [page["name"] for page in preset["pages"]] == ["Oscillators", "Amp"]
        assert "Glide switch" in control_names
        assert "Pan" in control_names
        assert "Pan (CC)" not in control_names
        assert "Pan (NRPN)" not in control_names

        markdown = output_md.read_text(encoding="utf-8")
        assert "## Oscillators" in markdown
        assert "## Amp" in markdown
        assert "Pan (NRPN)" not in markdown