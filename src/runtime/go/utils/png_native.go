// png_native.go: Minimal RGB PNG writer (hand-written native).
// TODO: Replace with pipeline-generated code when emitter handles bytes ops.
package main

import (
	"bytes"
	"compress/zlib"
	"encoding/binary"
	"hash/crc32"
	"os"
	"path/filepath"
)

func py_write_rgb_png(path string, width int64, height int64, pixels []byte) {
	dir := filepath.Dir(path)
	if dir != "" && dir != "." { os.MkdirAll(dir, 0755) }
	w := int(width); h := int(height)
	var buf bytes.Buffer
	buf.Write([]byte{0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A})
	ihdr := make([]byte, 13)
	binary.BigEndian.PutUint32(ihdr[0:4], uint32(w))
	binary.BigEndian.PutUint32(ihdr[4:8], uint32(h))
	ihdr[8] = 8; ihdr[9] = 2
	_writePNGChunk(&buf, "IHDR", ihdr)
	var raw bytes.Buffer
	for y := 0; y < h; y++ {
		raw.WriteByte(0)
		raw.Write(pixels[y*w*3 : (y+1)*w*3])
	}
	var compressed bytes.Buffer
	zw, _ := zlib.NewWriterLevel(&compressed, zlib.BestSpeed)
	zw.Write(raw.Bytes()); zw.Close()
	_writePNGChunk(&buf, "IDAT", compressed.Bytes())
	_writePNGChunk(&buf, "IEND", nil)
	os.WriteFile(path, buf.Bytes(), 0644)
}

func _writePNGChunk(buf *bytes.Buffer, chunkType string, data []byte) {
	length := make([]byte, 4)
	binary.BigEndian.PutUint32(length, uint32(len(data)))
	buf.Write(length); buf.WriteString(chunkType)
	if data != nil { buf.Write(data) }
	crc := crc32.NewIEEE(); crc.Write([]byte(chunkType))
	if data != nil { crc.Write(data) }
	crcBytes := make([]byte, 4)
	binary.BigEndian.PutUint32(crcBytes, crc.Sum32())
	buf.Write(crcBytes)
}
