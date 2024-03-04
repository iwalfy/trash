/*
 * Simple program to brute "fancy" X25519 Keys (e.g. for WireGuard)
 *
 * (c) Mikhail Lebedinets, 2023
 */

package main

import (
	"fmt"
	"crypto/rand"
	"io"
	"encoding/base64"
	"strings"
	"time"
	"os"
	"strconv"

	"golang.org/x/crypto/curve25519"
	"github.com/fatih/color"
)

var (
	cGreen = color.New(color.FgGreen).SprintFunc()
	cCyan = color.New(color.FgCyan).SprintFunc()
)

func main() {
	if len(os.Args) < 2 {
		fmt.Printf("Usage: %s <prefix> [<threads>]\n", os.Args[0])
		os.Exit(1)
	}

	brutePrefix := os.Args[1]
	threads := 1

	if len(os.Args) > 2 {
		t, err := strconv.Atoi(os.Args[2])
		threads = t
		if err != nil {
			panic(err)
		}
	}

	i := 1
	for i <= threads {
		fmt.Printf("Starting thread %d...\n", i)
		go brute(brutePrefix)
		i++
	}

	for { time.Sleep(time.Hour) }
}

func brute(brutePrefix string) {
	start_nsec := time.Now().UnixNano()

	for {
		secretBytes := make([]byte, 32)
		io.ReadFull(rand.Reader, secretBytes)

		publicBytes, _ := curve25519.X25519(secretBytes, curve25519.Basepoint)
		publicKey := base64.StdEncoding.EncodeToString(publicBytes)

		if strings.HasPrefix(publicKey, brutePrefix) {
			secretKey := base64.StdEncoding.EncodeToString(secretBytes)
			publicNoPrefix := publicKey[len([]rune(brutePrefix)):]

			durr := time.Now().UnixNano() - start_nsec
			durr_str := time.Duration(durr).String()

			fmt.Printf("%s [%s]\n", cGreen("!!! FOUND !!!"), durr_str)
			fmt.Printf("Private: %s\n", secretKey)
			fmt.Printf("Public:  %s%s\n", cCyan(brutePrefix), publicNoPrefix)
			fmt.Printf("---\n")
		}
	}
}
