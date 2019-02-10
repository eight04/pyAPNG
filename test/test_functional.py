import json
import subprocess
import pytest
from apng import APNG
from . import get_fixtures

FIXTURES = get_fixtures()

def get_stem(fixture):
	return fixture.stem

@pytest.mark.parametrize("fixture", FIXTURES, ids=get_stem)
def test_assemble(tmp_path, fixture):
	try:
		options = json.loads((fixture / "property.json").read_text())
	except IOError:
		options = {}
		
	im = APNG(**options)
	
	def iter_frames():
		frames = {}
		for file in fixture.glob("frame-*"):
			if file.stem not in frames:
				frames[file.stem] = {"name": file.stem}
			frames[file.stem][file.suffix] = file
		for frame in sorted(frames.values(), key=lambda i: int(i["name"].partition("-")[-1])):
			if ".json" in frame:
				ctrl = json.loads(frame[".json"].read_text())
			else:
				ctrl = {}
			yield frame[".png"], ctrl
			
	for file, ctrl in iter_frames():
		im.append_file(file, **ctrl)
		
	if not im.frames:
		return
		
	filename = "{}-animated.png".format(fixture.stem)
	im.save(tmp_path / filename)
	
	subprocess.check_call(
		subprocess.list2cmdline(["pngcheck", filename]),
		cwd=str(tmp_path), shell=True)

@pytest.mark.parametrize("fixture", FIXTURES, ids=get_stem)
def test_disassemble(tmp_path, fixture):
	im = APNG.open(fixture / "animated.png")
	options_file = fixture / "property.json"
	
	if options_file.exists():
		options = json.loads(options_file.read_text())
		for key, value in options.items():
			assert getattr(im, key) == value
			
	for i, (png, _ctrl) in enumerate(im.frames):
		filename = "{}-{}.png".format(fixture.stem, i + 1)
		png.save(tmp_path / filename)
		subprocess.check_call(
			subprocess.list2cmdline(["pngcheck", filename]),
			cwd=str(tmp_path), shell=True)
