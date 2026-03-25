// gif_native.go: Minimal GIF writer with LZW compression (hand-written native).
// TODO: Replace with pipeline-generated code when emitter handles bytes ops.
package main

import (
	"bytes"
	"os"
	"path/filepath"
)

func py_grayscale_palette() []byte {
	pal := make([]byte, 256*3)
	for i := 0; i < 256; i++ { pal[i*3] = byte(i); pal[i*3+1] = byte(i); pal[i*3+2] = byte(i) }
	return pal
}

func py_save_gif(path string, width int64, height int64, frames [][]byte, palette []byte, args ...int64) {
	delay_cs := int64(4)
	if len(args) > 0 { delay_cs = args[0] }
	dir := filepath.Dir(path)
	if dir != "" && dir != "." { os.MkdirAll(dir, 0755) }
	w := int(width); h := int(height)
	palSize := len(palette) / 3; if palSize > 256 { palSize = 256 }
	var buf bytes.Buffer
	buf.WriteString("GIF89a"); _writeLE16(&buf, w); _writeLE16(&buf, h)
	gctBits := 7
	for _, lim := range []int{128, 64, 32, 16, 8, 4, 2} { if palSize <= lim { gctBits-- } }
	if gctBits < 0 { gctBits = 0 }
	buf.WriteByte(0x80 | byte(gctBits)<<4 | byte(gctBits)); buf.WriteByte(0); buf.WriteByte(0)
	tableSize := 1 << (gctBits + 1)
	for i := 0; i < tableSize; i++ {
		if i < palSize { buf.Write(palette[i*3 : i*3+3]) } else { buf.Write([]byte{0, 0, 0}) }
	}
	buf.Write([]byte{0x21, 0xFF, 0x0B}); buf.WriteString("NETSCAPE2.0"); buf.Write([]byte{0x03, 0x01, 0x00, 0x00, 0x00})
	minCodeSize := byte(gctBits + 1); if minCodeSize < 2 { minCodeSize = 2 }
	for _, frame := range frames {
		buf.Write([]byte{0x21, 0xF9, 0x04, 0x00}); _writeLE16(&buf, int(delay_cs)); buf.Write([]byte{0x00, 0x00})
		buf.WriteByte(0x2C); _writeLE16(&buf, 0); _writeLE16(&buf, 0); _writeLE16(&buf, w); _writeLE16(&buf, h); buf.WriteByte(0x00)
		buf.WriteByte(minCodeSize); _writeLZW(&buf, frame, int(minCodeSize), w*h); buf.WriteByte(0x00)
	}
	buf.WriteByte(0x3B)
	os.WriteFile(path, buf.Bytes(), 0644)
}

func _writeLE16(buf *bytes.Buffer, v int) { buf.WriteByte(byte(v & 0xFF)); buf.WriteByte(byte((v >> 8) & 0xFF)) }

func _writeLZW(buf *bytes.Buffer, data []byte, minCodeSize int, pixelCount int) {
	clearCode := 1 << minCodeSize; endCode := clearCode + 1
	var bitBuf uint32; var bitCount uint; var subBlock [255]byte; subBlockLen := 0
	flushBits := func(code int, codeSize int) {
		bitBuf |= uint32(code) << bitCount; bitCount += uint(codeSize)
		for bitCount >= 8 {
			subBlock[subBlockLen] = byte(bitBuf & 0xFF); subBlockLen++; bitBuf >>= 8; bitCount -= 8
			if subBlockLen == 255 { buf.WriteByte(byte(subBlockLen)); buf.Write(subBlock[:subBlockLen]); subBlockLen = 0 }
		}
	}
	codeSize := minCodeSize + 1; nextCode := endCode + 1; maxCode := (1 << codeSize) - 1
	type entry struct{ prefix, suffix int }; table := make(map[entry]int)
	flushBits(clearCode, codeSize)
	if len(data) == 0 { flushBits(endCode, codeSize) } else {
		prev := int(data[0])
		for i := 1; i < len(data) && i < pixelCount; i++ {
			cur := int(data[i]); e := entry{prev, cur}
			if code, ok := table[e]; ok { prev = code } else {
				flushBits(prev, codeSize)
				if nextCode <= 4095 { table[e] = nextCode; nextCode++; if nextCode > maxCode+1 && codeSize < 12 { codeSize++; maxCode = (1 << codeSize) - 1 } } else {
					flushBits(clearCode, codeSize); table = make(map[entry]int); codeSize = minCodeSize + 1; nextCode = endCode + 1; maxCode = (1 << codeSize) - 1
				}; prev = cur
			}
		}
		flushBits(prev, codeSize); flushBits(endCode, codeSize)
	}
	if bitCount > 0 { subBlock[subBlockLen] = byte(bitBuf & 0xFF); subBlockLen++ }
	if subBlockLen > 0 { buf.WriteByte(byte(subBlockLen)); buf.Write(subBlock[:subBlockLen]) }
}
