"""Pruebas de export metrics."""

import json
import csv
import pytest

from tnfr.metrics import export_metrics


def test_export_metrics_creates_directory_csv(tmp_path, graph_canon):
    base = tmp_path / "non" / "existing" / "run"
    dir_path = base.parent
    assert not dir_path.exists()
    G = graph_canon()
    export_metrics(G, str(base), fmt="csv")
    assert dir_path.exists()
    assert (dir_path / (base.name + "_glyphogram.csv")).is_file()
    assert (dir_path / (base.name + "_sigma.csv")).is_file()


def test_export_metrics_creates_directory_json(tmp_path, graph_canon):
    base = tmp_path / "other" / "path" / "history"
    dir_path = base.parent
    assert not dir_path.exists()
    G = graph_canon()
    export_metrics(G, str(base), fmt="json")
    assert dir_path.exists()
    assert (base.with_suffix(".json")).is_file()


def test_export_metrics_writes_optional_files(tmp_path, graph_canon):
    base = tmp_path / "extras" / "run"
    G = graph_canon()
    hist = G.graph.setdefault("history", {})
    hist["morph"] = [{"t": 0, "ID": 1, "CM": 2, "NE": 3, "PP": 4}]
    hist["EPI_support"] = [{"t": 0, "size": 1, "epi_norm": 0.5}]
    export_metrics(G, str(base), fmt="csv")
    dir_path = base.parent
    assert (dir_path / (base.name + "_morph.csv")).is_file()
    assert (dir_path / (base.name + "_epi_support.csv")).is_file()


def test_export_metrics_json_contains_optional(tmp_path, graph_canon):
    base = tmp_path / "extras" / "jsonrun"
    G = graph_canon()
    hist = G.graph.setdefault("history", {})
    hist["morph"] = [{"t": 0, "ID": 1, "CM": 2, "NE": 3, "PP": 4}]
    hist["EPI_support"] = [{"t": 0, "size": 1, "epi_norm": 0.5}]
    export_metrics(G, str(base), fmt="json")
    data = json.loads((base.with_suffix(".json")).read_text())
    assert data["morph"]
    assert data["epi_support"]


def test_export_metrics_extends_sigma(tmp_path, graph_canon):
    base = tmp_path / "short" / "run"
    G = graph_canon()
    hist = G.graph.setdefault("history", {})
    hist["sense_sigma_x"] = [1, 2]
    hist["sense_sigma_y"] = [3]
    hist["sense_sigma_mag"] = [4, 5, 6]
    hist["sense_sigma_angle"] = [7, 8]
    export_metrics(G, str(base), fmt="csv")
    sigma_path = base.parent / (base.name + "_sigma.csv")
    with open(sigma_path, newline="") as f:
        rows = list(csv.reader(f))
    assert rows[1] == ["0", "1", "3", "4", "7"]
    assert rows[2] == ["1", "2", "0", "5", "8"]
    assert rows[3] == ["2", "0", "0", "6", "0"]
    assert len(rows) == 4


def test_export_metrics_preserves_timestamps(tmp_path, graph_canon):
    base = tmp_path / "ts" / "run"
    G = graph_canon()
    hist = G.graph.setdefault("history", {})
    hist["sense_sigma_t"] = [10, 20]
    hist["sense_sigma_x"] = [1, 2]
    hist["sense_sigma_y"] = []
    hist["sense_sigma_mag"] = []
    hist["sense_sigma_angle"] = []
    export_metrics(G, str(base), fmt="csv")
    sigma_path = base.parent / (base.name + "_sigma.csv")
    with open(sigma_path, newline="") as f:
        rows = list(csv.reader(f))
    assert rows[1][0] == "10"
    assert rows[2][0] == "20"


def test_export_metrics_invalid_format(tmp_path, graph_canon):
    G = graph_canon()
    with pytest.raises(ValueError):
        export_metrics(G, str(tmp_path / "base"), fmt="xml")
