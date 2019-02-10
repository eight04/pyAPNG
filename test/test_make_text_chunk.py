# -*- coding: utf-8 -*-
import zlib
from apng import make_text_chunk, make_chunk

def test_text():
	chunk_type, data = make_text_chunk(value="some text")
	assert chunk_type == "tEXt"
	assert data == make_chunk("tEXt", b"Comment\0some text")
	
def test_ztxt():
	chunk_type, data = make_text_chunk(type="zTXt", value="some text")
	assert chunk_type == "zTXt"
	assert data == make_chunk("zTXt", b"Comment\0\0" + zlib.compress(b"some text"))
	
def test_itxt():
	chunk_type, data = make_text_chunk(type="iTXt", value=u"ＳＯＭＥ　ＴＥＸＴ")
	assert chunk_type == "iTXt"
	assert data == make_chunk("iTXt", b"Comment\0\0\0\0\0" + u"ＳＯＭＥ　ＴＥＸＴ".encode("utf-8"))
	
def test_itxt_compressed():
	chunk_type, data = make_text_chunk(type="iTXt", value=u"ＳＯＭＥ　ＴＥＸＴ", compression_flag=1)
	assert chunk_type == "iTXt"
	assert data == make_chunk(
		"iTXt",
		b"Comment\0\1\0\0\0" +
			zlib.compress(u"ＳＯＭＥ　ＴＥＸＴ".encode("utf-8")))
