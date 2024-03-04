BINDIR=bin
BINARY_NAME=wg-brute

all: build

get:
	go mod download

build: get
	 CGO_ENABLED=0 go build -v -ldflags "-w -s" -o ${BINDIR}/${BINARY_NAME} main.go

compile: get
	GOOS=darwin GOARCH=amd64 CGO_ENABLED=0 go build -v -ldflags "-w -s" -o ${BINDIR}/${BINARY_NAME}-darwin-amd64 main.go
	GOOS=linux GOARCH=amd64 CGO_ENABLED=0 go build -v -ldflags "-w -s" -o ${BINDIR}/${BINARY_NAME}-linux-amd64 main.go
	GOOS=windows GOARCH=amd64 CGO_ENABLED=0 go build -v -ldflags "-w -s" -o ${BINDIR}/${BINARY_NAME}-win32-amd64 main.go

	GOOS=darwin GOARCH=arm64 CGO_ENABLED=0 go build -v -ldflags "-w -s" -o ${BINDIR}/${BINARY_NAME}-darwin-arm64 main.go
	GOOS=linux GOARCH=arm64 CGO_ENABLED=0 go build -v -ldflags "-w -s" -o ${BINDIR}/${BINARY_NAME}-linux-arm64 main.go
	GOOS=windows GOARCH=arm64 CGO_ENABLED=0 go build -v -ldflags "-w -s" -o ${BINDIR}/${BINARY_NAME}-win32-arm64 main.go

clean:
	go clean
	rm ${BINDIR}/${BINARY_NAME}*
