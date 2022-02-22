import argparse
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from pprint import pprint
import pandas as pd
import schedule

sys.path.insert(1, str(Path('src/marktech').resolve()))      
import scrape_static


scraper = scrape_static.StaticPageScraper(verbose=0)


def get_stocks(filter=None):
    stocks = {
        'HLL': {
            'url': 'https://www.investing.com/equities/hindustan-unilever-technical',
            'html_locations': {
                "current_values": [
                    "#quotes_summary_current_data",
                ],
                "secondary_data": [
                    "#quotes_summary_secondary_data",
                ],
                "hr1_tech_content": [
                    "#techinalContent",
                ],
            },
        },
        'RELI': {
            'url': 'https://www.investing.com/equities/reliance-industries-technical',
            'html_locations': {
                "current_values": [
                    "#quotes_summary_current_data",
                ],
                "secondary_data": [
                    "#quotes_summary_secondary_data",
                ],
                "hr1_tech_content": [
                    "#techinalContent",
                ],
            },
        },
        'INFY': {
            'url': 'https://www.investing.com/equities/infosys-technical',
            'html_locations': {
                "current_values": [
                    "#quotes_summary_current_data",
                ],
                "secondary_data": [
                    "#quotes_summary_secondary_data",
                ],
                "hr1_tech_content": [
                    "#techinalContent",
                ],
            },
        },
    }

    if not filter:
        return stocks
    return {filter: stocks[filter]}


def generate_lists(stocks):
    # size of all the arrays arrays is same.
    # size of all the elements of i-th index of `STATIC_PAGE_LOCATIONS`
    # is same as size of all the elements of i-th index of  `STATIC_PAGE_LOCATION_NAMES`.
    STATIC_PAGE_SYMBOLS = []
    STATIC_PAGE_URLS = []
    STATIC_PAGE_LOCATIONS = []
    STATIC_PAGE_LOCATION_NAMES = []
    for symbol in sorted(list(stocks.keys())):
        STATIC_PAGE_SYMBOLS.append(symbol)
        STATIC_PAGE_URLS.append(stocks[symbol]['url'])
        url_loc_names = []
        url_locations = []
        for loc_name in sorted(list(stocks[symbol]['html_locations'].keys())):
            url_locations.append(stocks[symbol]['html_locations'][loc_name])
            url_loc_names.append(loc_name)
        STATIC_PAGE_LOCATIONS.append(url_locations)
        STATIC_PAGE_LOCATION_NAMES.append(url_loc_names)
    return STATIC_PAGE_SYMBOLS, STATIC_PAGE_URLS, STATIC_PAGE_LOCATIONS, STATIC_PAGE_LOCATION_NAMES



def write_data(utc_time, data, STATIC_PAGE_SYMBOLS, STATIC_PAGE_URLS, STATIC_PAGE_LOCATIONS, STATIC_PAGE_LOCATION_NAMES, SAVE_DIR):
    for idx in range(len(data)):
        symbol = STATIC_PAGE_SYMBOLS[idx]
        write_path = SAVE_DIR / f'{symbol}.csv'

        raw_texts = data[idx]
        names = STATIC_PAGE_LOCATION_NAMES[idx]
        row = {'utc_time': [utc_time]}
        for name, raw in zip(names, raw_texts):
            row[name] = [raw]
        
        mode, header = 'a', False
        if not write_path.exists():
            mode, header = 'w', True
        pd.DataFrame(row).to_csv(str(write_path), mode=mode, index=False, header=header)


def process(stock=None, SAVE_DIR=Path('data/raw')):
    utc_time = datetime.utcnow()
    print('proc @', utc_time)
    stocks = get_stocks(filter=stock)
    STATIC_PAGE_SYMBOLS, STATIC_PAGE_URLS, STATIC_PAGE_LOCATIONS, STATIC_PAGE_LOCATION_NAMES = generate_lists(stocks)
    data = scraper.scrape_all(STATIC_PAGE_URLS).find_all(STATIC_PAGE_LOCATIONS)
    write_data(utc_time, data, STATIC_PAGE_SYMBOLS, STATIC_PAGE_URLS, STATIC_PAGE_LOCATIONS, STATIC_PAGE_LOCATION_NAMES, SAVE_DIR)


def parse_arguments():
    """ use for concurrent github action jobs
    python scripts/scrape_investing.py --interval-min 1 --limit-sec 21000 --save-dir data/raw --stock HLL
    python scripts/scrape_investing.py --interval-min 1 --limit-sec 21000 --save-dir data/raw --stock HLL
    """
    parser = argparse.ArgumentParser(description='Process command line arguments.')
    parser.add_argument('--save-dir', type=str, default="stock_data")
    parser.add_argument('--limit-sec', type=int, default=60*5)
    parser.add_argument('--interval-min', type=int, default=1)
    parser.add_argument('--stock', type=str, required=True)
    return parser.parse_args()


def validate_arguments(args):
    if args.stock not in get_stocks().keys():
        return False
    return True


def main():
    args = parse_arguments()
    if not validate_arguments(args):
        return

    SAVE_DIR = Path(args.save_dir)
    SAVE_DIR.mkdir(exist_ok=True, parents=True)

    start_time = datetime.utcnow()
    time_limit = args.limit_sec
    time_to_stop = start_time + timedelta(seconds=time_limit)

    print("###########################################################################################")
    print('Process started @', start_time)
    print('Process will stop @', time_to_stop)
    print("###########################################################################################")

    schedule.every(args.interval_min).minutes.do(process, SAVE_DIR=SAVE_DIR, stock=args.stock)
    while datetime.utcnow()<time_to_stop:
        # print(datetime.utcnow())
        if datetime.utcnow().second==0:
            schedule.run_pending()
            time.sleep(1)

    prefix = datetime.datetime.utcnow().strftime('%Y-%m-%d-%H%-M%')
    if (SAVE_DIR/f'{args.symbol}.csv').exists():
        print("###########################################################################################")
        print('renaming file', str(SAVE_DIR/f'{args.stock}.csv'), '-->', str(SAVE_DIR/f'{prefix}-{args.stock}.csv'))
        print("###########################################################################################")
        os.rename(str(SAVE_DIR/f'{args.stock}.csv'), str(SAVE_DIR/f'{prefix}-{args.stock}.csv'))


if __name__=='__main__':
    main()
