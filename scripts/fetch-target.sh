#!/usr/bin/env bash

set -euo pipefail

version="${1:-20.2.0}"
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
project_root="$(cd -- "$script_dir/.." && pwd)"
target_root="$project_root/target"
target_dir="$target_root/juice-shop"
package_file="$target_dir/package.json"

read_package_version() {
  sed -n 's/^[[:space:]]*"version"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' "$1" | head -n 1
}

if [[ -f "$package_file" ]]; then
  current_version="$(read_package_version "$package_file")"
  if [[ "$current_version" == "$version" ]]; then
    printf 'OWASP Juice Shop v%s já está preparado.\n' "$version"
    exit 0
  fi
  printf 'Erro: target/juice-shop contém a versão %s, não %s. Revise-a antes de substituir.\n' \
    "${current_version:-desconhecida}" "$version" >&2
  exit 1
fi

if [[ -e "$target_dir" ]]; then
  printf 'Erro: %s já existe, mas não contém um package.json válido.\n' "$target_dir" >&2
  exit 1
fi

for command_name in tar sed head; do
  if ! command -v "$command_name" >/dev/null 2>&1; then
    printf 'Erro: comando obrigatório não encontrado: %s\n' "$command_name" >&2
    exit 1
  fi
done

if command -v curl >/dev/null 2>&1; then
  download() { curl --fail --location --silent --show-error "$1" --output "$2"; }
elif command -v wget >/dev/null 2>&1; then
  download() { wget --quiet "$1" --output-document "$2"; }
else
  printf 'Erro: instale curl ou wget para baixar o release oficial.\n' >&2
  exit 1
fi

mkdir -p "$target_root"
temporary_dir="$(mktemp -d "${TMPDIR:-/tmp}/grupo4-juice-shop.XXXXXX")"
trap 'rm -rf -- "$temporary_dir"' EXIT

archive="$temporary_dir/juice-shop-v$version.tar.gz"
uri="https://codeload.github.com/juice-shop/juice-shop/tar.gz/refs/tags/v$version"

printf 'Baixando o código oficial: %s\n' "$uri"
download "$uri" "$archive"
tar -xzf "$archive" -C "$temporary_dir"

extracted_dir="$temporary_dir/juice-shop-$version"
extracted_package="$extracted_dir/package.json"
if [[ ! -f "$extracted_package" ]]; then
  printf 'Erro: estrutura inesperada no arquivo oficial baixado.\n' >&2
  exit 1
fi

downloaded_version="$(read_package_version "$extracted_package")"
if [[ "$downloaded_version" != "$version" ]]; then
  printf 'Erro: a versão interna %s não corresponde ao release solicitado %s.\n' \
    "${downloaded_version:-desconhecida}" "$version" >&2
  exit 1
fi

mv -- "$extracted_dir" "$target_dir"
printf 'OWASP Juice Shop v%s preparado em target/juice-shop.\n' "$version"
