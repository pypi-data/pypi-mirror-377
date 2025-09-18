import json
import os
# import pytest

from postprocessing_seismo_lib import (
    update_dataretrieval_input,
    extract_body_from_file,
    wrap_data
)

def test_update_dataretrieval_input(tmp_path):
    input_file = tmp_path / "input.json"
    output_file = tmp_path / "output.json"
    json.dump({"RetrieveParameters": {}}, open(input_file, "w"))

    updated = update_dataretrieval_input(
        str(input_file), str(output_file),
        Host="localhost", Method="GET", Port=8080, Window="w1"
    )

    assert updated["RetrieveParameters"]["Host"] == "localhost"
    assert os.path.exists(output_file)

def test_extract_body_from_file(tmp_path):
    filepath = tmp_path / "test.json"
    json.dump({"body": {"foo": "bar"}}, open(filepath, "w"))
    body = extract_body_from_file(filepath)
    assert body == {"foo": "bar"}

def test_wrap_data_associator(tmp_path):
    input_file = tmp_path / "picks.json"
    output_file = tmp_path / "wrapped.json"

    pick_data = [{
        "Amplitude": {"Amplitude": 1.2, "SNR": 3.4},
        "Filter": [{"HighPass": 0.1, "Type": "LP"}],
        "Phase": "P",
        "Picker": "auto",
        "Polarity": "positive",
        "Quality": [{"Standard": "Q1", "Value": 1}],
        "Site": {"Channel": "EHZ", "Location": "00", "Network": "CI", "Station": "ABC"},
        "Source": {"AgencyID": "USGS", "Author": "analyst"},
        "Time": "2021-01-01T00:00:00Z",
        "Type": "manual"
    }]
    json.dump(pick_data, open(input_file, "w"))

    wrap_data(str(input_file), str(output_file), evid="ev123", module="associator")
    wrapped = json.load(open(output_file))
    assert "RetrieveParameters" in wrapped
    assert "pickDataStr" in wrapped["RetrieveParameters"]
