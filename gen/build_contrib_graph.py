name: update contribution graph

on:
  schedule:
    # every day at 01:00 UTC (staggered from the other two daily jobs)
    - cron: "0 1 * * *"
  workflow_dispatch: {}

jobs:
  update:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: generate contrib-graph.svg
        env:
          GITHUB_LOGIN: scabber098
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: python gen/build_contrib_graph.py

      - name: pull latest changes
        run: git pull --rebase origin main

      - name: commit if changed
        uses: stefanzweifel/git-auto-commit-action@v5
        with:
          commit_message: "chore: update contribution graph"
          file_pattern: contrib-graph.svg
