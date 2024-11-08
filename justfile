set shell := ['pwsh', '-Command']
set dotenv-load

pipeline := 'boilercv_pipeline'
devpy := 'dev'

dev:
  . ./dev.ps1

boilercv-preview-write file $BOILERCV_PREVIEW='true' $BOILERCV_WRITE='true':
  iuv python {{file}}
boilercv-debug-preview-write file $BOILERCV_DEBUG='true' $BOILERCV_PREVIEW='true' $BOILERCV_WRITE='true':
  iuv python {{file}}
boilercv-preview preview $BOILERCV_PREVIEW='true':
  python -m {{pipeline}}.previews.{{preview}}

update-binder:
  (uv pip compile --config-file requirements/binder_uv.toml \
    --constraint requirements/binder_constraints.in \
    --override requirements/binder_overrides.txt \
    --exclude-newer (Get-Date).ToUniversalTime().ToString('o') \
    requirements/binder.in \
  ) -Replace 'opencv-python', 'opencv-python-headless' | Set-Content requirements.txt

dvc-dag: dev
  (iuv dvc dag --md) -Replace 'mermaid', '{mermaid}' | Set-Content 'docs/_static/dag.md'
  markdownlint-cli2 'docs/_static/dag.md'

generate-correlations file correlations: dev
  iuv python {{file}} {{correlations}}
generate-correlation-docs: dev
  iuv -m boilercv_pipeline.equations.make_docs

hide-notebook-inputs: dev
  iuv -m {{devpy}}.docs.patch_nbs

pipeline-sync-dvc: dev
  iuv -m {{pipeline}} sync-dvc

remove-empty-data-folders:
  Get-ChildItem -Path './data', 'docs/data' -Recurse -Directory | \
    Where-Object { \
      ( Get-ChildItem -Path $_ -Recurse -File | Measure-Object ).Count -eq 0 \
    } | Remove-Item -Recurse -Force

sync-contrib: dev
  iuv -Sync -Update

sync-local-dev-configs: dev
  {{devpy}} sync-local-dev-configs
