#!/usr/bin/env bash

set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
project_root="$(cd -- "$script_dir/.." && pwd)"
source_file="$project_root/target/juice-shop/routes/search.ts"
fixed_dir="$project_root/target/juice-shop-fixed/routes"
fixed_file="$fixed_dir/search.ts"

if [[ ! -f "$source_file" ]]; then
  printf 'Erro: código do Juice Shop ausente. Execute scripts/fetch-target.sh primeiro.\n' >&2
  exit 1
fi

if ! command -v awk >/dev/null 2>&1; then
  printf 'Erro: comando obrigatório não encontrado: awk\n' >&2
  exit 1
fi

unsafe='models.sequelize.query(`SELECT * FROM Products WHERE ((name LIKE '\''%${criteria}%'\'' OR description LIKE '\''%${criteria}%'\'') AND deletedAt IS NULL) ORDER BY name`)'
safe='models.sequelize.query(`SELECT * FROM Products WHERE ((name LIKE :criteria OR description LIKE :criteria) AND deletedAt IS NULL) ORDER BY name`, { replacements: { criteria: `%${criteria}%` } })'

mkdir -p "$fixed_dir"
temporary_file="$(mktemp "$fixed_dir/search.ts.XXXXXX")"
trap 'rm -f -- "$temporary_file"' EXIT

if ! awk -v old="$unsafe" -v new="$safe" '
  {
    position = index($0, old)
    if (position > 0) {
      replacements += 1
      $0 = substr($0, 1, position - 1) new substr($0, position + length(old))
    }
    print
  }
  END {
    if (replacements != 1) {
      exit 42
    }
  }
' "$source_file" > "$temporary_file"; then
  printf 'Erro: o trecho vulnerável esperado não foi encontrado exatamente uma vez no Juice Shop v20.2.0.\n' >&2
  exit 1
fi

mv -- "$temporary_file" "$fixed_file"
trap - EXIT
printf 'Cópia corrigida criada em target/juice-shop-fixed/routes/search.ts.\n'
