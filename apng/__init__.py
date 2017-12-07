#! python3

"""This is an APNG module, which can create apng file from pngs

Reference:
http://littlesvr.ca/apng/
http://wiki.mozilla.org/APNG_Specification
https://www.w3.org/TR/PNG/
"""

import struct
import binascii
import itertools
import io

__version__ = "0.1.0"

try:
	import PIL.Image
except ImportError:
	# Without Pillow, apng can only handle PNG images
	pass

PNG_SIGN = b"\x89\x50\x4E\x47\x0D\x0A\x1A\x0A"

# http://www.libpng.org/pub/png/spec/1.2/PNG-Chunks.html#C.Summary-of-standard-chunks
CHUNK_BEFORE_IDAT = {
	"cHRM", "gAMA", "iCCP", "sBIT", "sRGB", "bKGD", "hIST", "tRNS", "pHYs",
	"sPLT", "tIME", "PLTE"
}

def is_png(png):
	"""Test if @png is valid png file by checking signature
	
	@png can be str of the filename, a path-like object, a file-like object, or
	a bytes object.
	"""
	if isinstance(png, str) or hasattr(png, "__fspath__"):
		with open(png, "rb") as f:
			png_header = f.read(8)		
	elif hasattr(png, "read"):
		position = png.tell()
		png_header = png.read(8)
		png.seek(position)
	elif isinstance(png, bytes):
		png_header = png[:8]
	else:
		raise TypeError("Must be file, bytes, or str but get {}"
				.format(type(png)))
			
	return png_header == PNG_SIGN
			
def chunks_read(b):
	"""Parse PNG bytes into different chunks, yielding (type, data). 
	
	@type is a string of chunk type.
	@data is the bytes of the chunk. Including length, type, data, and crc.
	"""
	# skip signature
	i = 8
	# yield chunks
	while i < len(b):
		data_len, = struct.unpack("!I", b[i:i+4])
		type = b[i+4:i+8].decode("latin-1")
		yield type, b[i:i+data_len+12]
		i += data_len + 12

def chunks(png):
	"""Yield chunks from png.
	
	@png can be a string of filename, a path-like object, a file-like object,
	or a bytes bject.
	"""
	if not is_png(png):
		# convert to png
		if isinstance(png, bytes):
			with io.BytesIO(png) as f:
				with io.BytesIO() as f2:
					PIL.Image.open(f).save(f2, "PNG", optimize=True)
					png = f2.getvalue()
		else:
			with io.BytesIO() as f2:
				PIL.Image.open(png).save(f2, "PNG", optimize=True)
				png = f2.getvalue()
	
	if isinstance(png, str) or hasattr(png, "__fspath__"):
		# path like
		with open(png, "rb") as f:
			png = f.read()		
	elif hasattr(png, "read"):
		# file like
		png = png.read()
		
	return chunks_read(png)
		
def make_chunk(type, data):
	"""Create chunk with @type and chunk data @data.
	
	It will calculate length and crc for you. Return bytes.
	
	@type is str and @data is bytes.
	"""
	out = struct.pack("!I", len(data))
	data = type.encode("latin-1") + data
	out += data + struct.pack("!I", binascii.crc32(data))
	return out
	
class PNG:
	"""Construct PNG image"""
	def __init__(self):
		self.hdr = None
		self.end = None
		self.width = None
		self.height = None
		self.chunks = []
		
	def init(self):
		"""Extract some info from chunks"""
		for type, data in self.chunks:
			if type == "IHDR":
				self.hdr = data
			elif type == "IEND":
				self.end = data
				
		if self.hdr:
			# grab w, h info
			self.width, self.height = struct.unpack("!II", self.hdr[8:16])
			
	@classmethod
	def open(cls, file):
		"""Open a png from file. See chunks()."""
		o = cls()
		o.chunks = list(chunks(file))
		o.init()
		return o
		
	@classmethod
	def from_chunks(cls, chunks):
		"""Construct PNG from chunks.
		
		@chunks is a list of (type, data) tuple. See chunks().
		"""
		o = cls()
		o.chunks = chunks
		o.init()
		return o
		
	def to_bytes(self):
		"""Get bytes"""
		chunks = [PNG_SIGN]
		chunks.extend(c[1] for c in self.chunks)
		return b"".join(chunks)
		
	def save(self, file):
		"""Save to file. @file can be a str of filename, a path-like object, or
		a file-like object.
		"""
		if isinstance(file, str) or hasattr(file, "__fspath__"):
			with open(file, "wb") as f:
				f.write(self.to_bytes())
		else:
			file.write(self.to_bytes())
		
class FrameControl:
	"""Construct fcTL info"""
	def __init__(self, width=None, height=None, x_offset=0, y_offset=0, delay=100, delay_den=1000, depose_op=1, blend_op=0):
		self.width = width
		self.height = height
		self.x_offset = x_offset
		self.y_offset = y_offset
		self.delay = delay
		self.delay_den = delay_den
		self.depose_op = depose_op
		self.blend_op = blend_op
		
	def to_bytes(self):
		"""Return bytes"""
		return struct.pack("!IIIIHHbb", self.width, self.height, self.x_offset, self.y_offset, self.delay, self.delay_den, self.depose_op, self.blend_op)
		
	@classmethod
	def from_bytes(cls, b):
		"""Contruct fcTL info from bytes.
		
		@b should be a 28 length bytes object, excluding sequence number and crc.
		"""
		return cls(*struct.unpack("!IIIIHHbb", b))

class APNG:
	"""Construct APNG image"""
	def __init__(self):
		self.frames = []
		
	def append(self, png, **options):
		"""Append one frame.
		
		@png      See PNG.open.
		@options  See FrameControl.
		"""
		png = PNG.open(png)
		control = FrameControl(**options)
		if control.width is None:
			control.width = png.width
		if control.height is None:
			control.height = png.height
		self.frames.append((png, control))
		
	def to_bytes(self):
		"""Return binary."""
		
		# grab the chunks we needs
		out = [PNG_SIGN]
		# FIXME: it's tricky to define "other_chunks". HoneyView stop the 
		# animation if it sees chunks other than fctl or idat, so we put other
		# chunks to the end of the file
		other_chunks = []
		seq = 0
		
		# for first frame
		png, control = self.frames[0]
		
		# header
		out.append(png.hdr)
		
		# acTL
		out.append(make_chunk("acTL", struct.pack("!II", len(self.frames), 0)))
		
		# fcTL
		if control:
			out.append(make_chunk("fcTL", struct.pack("!I", seq) + control.to_bytes()))
			seq += 1
		
		# and others...
		idat_chunks = []
		for type, data in png.chunks:
			if type in ("IHDR", "IEND"):
				continue
			if type == "IDAT":
				# put at last
				idat_chunks.append(data)
				continue
			out.append(data)
		out.extend(idat_chunks)
		
		# FIXME: we should do some optimization to frames...
		# for other frames
		for png, control in self.frames[1:]:
			# fcTL
			out.append(
				make_chunk("fcTL", struct.pack("!I", seq) + control.to_bytes())
			)
			seq += 1
			
			# and others...
			for type, data in png.chunks:
				if type in ("IHDR", "IEND") or type in CHUNK_BEFORE_IDAT:
					continue
				elif type == "IDAT":
					# convert IDAT to fdAT
					out.append(
						make_chunk("fdAT", struct.pack("!I", seq) + data[8:-4])
					)
					seq += 1
				else:
					other_chunks.append(data)
		
		# end
		out.extend(other_chunks)
		out.append(png.end)
		
		return b"".join(out)
		
	@classmethod
	def from_files(cls, files, **options):
		"""Create APNG instance from multiple files.
		
		You can convert a series of image into apng by:
		  APNG.from_files(files, delay=100).save(out_file_name)
		  
		Note that if you want to use different delays between each frames, you
		have to use APNG.append separately to construct different frame
		control.
		  
		See APNG.append for valid params.
		"""
		o = cls()
		for file in files:
			o.append(file, **options)
		return o
		
	@classmethod
	def open(cls, file):
		"""Open a apng file.

		@file can be a str of filename, a file-like object, or a bytes object.
		"""
		hdr = None
		head_chunks = []
		end = ("IEND", make_chunk("IEND", b""))
		
		frame_chunks = []
		frames = []
		
		control = None
		
		for type, data in PNG.open(file).chunks:
			if type == "IHDR":
				hdr = data
				frame_chunks.append((type, data))
			elif type == "acTL":
				continue
			elif type == "fcTL":
				if any(type == "IDAT" for type, data in frame_chunks):
					# IDAT inside chunk, go to next frame
					frame_chunks.append(end)
					frames.append((PNG.from_chunks(frame_chunks), control))
					
					control = FrameControl.from_bytes(data[12:-4])
					hdr = make_chunk("IHDR", struct.pack("!II", control.width, control.height) + hdr[16:-4])
					frame_chunks = [("IHDR", hdr)]
				else:
					control = FrameControl.from_bytes(data[12:-4])
			elif type == "IDAT":
				frame_chunks.extend(head_chunks)
				frame_chunks.append((type, data))
			elif type == "fdAT":
				# convert to IDAT
				frame_chunks.extend(head_chunks)
				frame_chunks.append(("IDAT", make_chunk("IDAT", data[12:-4])))
			elif type == "IEND":
				# end
				frame_chunks.append(end)
				frames.append((PNG.from_chunks(frame_chunks), control))
				break
			elif type in CHUNK_BEFORE_IDAT:
				head_chunks.append((type, data))
			else:
				frame_chunks.append((type, data))
				
		o = cls()
		o.frames = frames
		return o
		
	def save(self, file):
		"""Save to file. @file can be a str of filename or a file-like object.
		"""
		if isinstance(file, str) or hasattr(file, "__fspath__"):
			with open(file, "wb") as f:
				f.write(self.to_bytes())
		else:
			file.write(self.to_bytes())
