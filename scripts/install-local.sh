#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_dir="$(cd -- "${script_dir}/.." && pwd)"
skills_dir="${repo_dir}/skills"
target_dir="${HOME}/.agents/skills"

mkdir -p "${target_dir}"

for skill_dir in "${skills_dir}"/*/; do
  skill_path="${skill_dir%/}"
  skill_name="${skill_path##*/}"
  ln -s "${skill_path}" "${target_dir}/${skill_name}"
done
