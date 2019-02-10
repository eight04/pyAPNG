def get_fixtures():
	from pathlib2 import Path
	return list((Path(__file__).parent / "fixtures").iterdir())
