name: scrape_data_reli

on:
  push:
    branches:
      - main
  schedule:
    - cron:  '30 4 * * 1,2,3,4,5'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Get current date
        id: date
        run: echo "::set-output name=date::$(date)"
      - name: Test get current date
        run: |
          echo cur-date-${{ steps.date.outputs.date }}
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.7'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Create csv file (scraping for 5.5 hrs)
        run: |
          python scripts/scrape_investing.py --interval-min 1 --limit-sec 21000 --save-dir data/raw --stock RELI
      - uses: EndBug/add-and-commit@v8
        with:
          add: stock_data
          message: 'write to csv'
          push: true