# provender

## Motivation

The development of websockets is shaped by four principles:

- Correctness: websockets is heavily tested for compliance with RFC 6455. Continuous integration fails under 100% branch coverage.
- Simplicity: all you need to understand is msg = await ws.recv() and await ws.send(msg). websockets takes care of managing connections so you can focus on your application.
- Robustness: websockets is built for production. For example, it was the only library to handle backpressure correctly before the issue became widely known in the Python community.
- Performance: memory usage is optimized and configurable. A C extension accelerates expensive operations. It's pre-compiled for Linux, macOS and Windows and packaged in the wheel format for each system and Python version.

## 🚀 Quick Start

### 1. Install zipzod using the Go toolchain

```bash
# Install Zipzod
go install github.com/xyz/zipzod@latest

# Compress an "input" Directory Into an "output.zip" File
zipzod -i ./input -o ./output.zip
```

## 📖 Usage

Available flags:

- `-i` - The input file or directory
- `-o` - The output file or directory
- `-v` - Verbose output
- `-h` - Show help
- `-p` - The number of parallel workers to use (default 4)
- `-d` - The maximum directory depth to recurse (default 6)
- `-f` - The file extensions to include (default .txt, .md)

## Examples

Unzip a file:

```bash
zipzod -i ./input.zip -o ./output
```

Zip with a different number of workers:

```bash
zipzod -i ./input -o ./output.zip -p 8
```

## 🤝 Contributing

### Clone the repo

```bash
git clone https://github.com/xyz/zipzod@latest
cd zipzod
```

### Build the compiled binary

```bash
go build
```

### Run the test suite

```bash
go test ./...
```

### Submit a pull request

If you'd like to contribute, please fork the repository and open a pull request to the `main` branch.