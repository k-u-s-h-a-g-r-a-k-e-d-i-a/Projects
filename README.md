name: Generate Space Invaders Contribution Graph

on:
  schedule:
    - cron: "0 */12 * * *"   # runs every 12 hours
  workflow_dispatch:           # lets you trigger it manually from Actions tab
  push:
    branches:
      - main

jobs:
  generate:
    runs-on: ubuntu-latest
    timeout-minutes: 10

    steps:
      - name: Generate contribution graph (Space Invaders)
        uses: Platane/snk/svg-only@v3
        with:
          github_user_name: k-u-s-h-a-g-r-a-k-e-d-i-a
          outputs: |
            dist/github-contribution-grid-snake-invaders.svg?color_snake=c084fc&color_dots[0]=0a0a0f&color_dots[1]=1a0533&color_dots[2]=4b0082&color_dots[3]=7c3aed&color_dots[4]=c084fc&mode=invaders

      - name: Push output to repo
        uses: crazy-max/ghaction-github-pages@v3
        with:
          target_branch: output
          build_dir: dist
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
