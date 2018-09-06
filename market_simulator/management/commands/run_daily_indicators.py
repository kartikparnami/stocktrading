import csv
import datetime

from django.core.management.base      import BaseCommand, CommandError
from django.conf                      import settings

from strategies.utils                 import Indicators
from market_simulator.models          import Index, Symbol, MarketDataSource, DailySymbolData


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--date', type=str)
        parser.add_argument('--month', type=str)
        parser.add_argument('--year', type=str)
        parser.add_argument('--symbol', type=str)
        parser.add_argument('--index', type=str)
        parser.add_argument('--data_source', type=str)
        parser.add_argument('--file_name', type=str)
        parser.add_argument('--id', type=str)

    def get_cuts(self, data_dict1, data_dict2, window_size1, window_size2):
        cuts = []
        sorted_dates = list(sorted(data_dict1.keys()))
        for i in range(len(sorted_dates) - 1):
            date = sorted_dates[i]
            for counter in sorted_dates[(i + 1):]:
                if (data_dict1[date] < data_dict2[date] and
                    data_dict1[counter] >= data_dict2[counter]):
                    cuts.append((window_size1, window_size2))
                if (data_dict1[date] <= data_dict2[date] and
                    data_dict1[counter] > data_dict2[counter]):
                    cuts.append((window_size1, window_size2))
                if (data_dict2[date] < data_dict1[date] and
                    data_dict2[counter] >= data_dict1[counter]):
                    cuts.append((window_size2, window_size1))
                if (data_dict2[date] <= data_dict1[date] and
                    data_dict2[counter] > data_dict1[counter]):
                    cuts.append((window_size2, window_size1))
        return list(set(cuts))

    def handle(self, *args, **options):
        file_name = options['file_name']
        gte_id = options['id']
        if gte_id:
            gte_id = int(gte_id)

        # Check for symbol, index and data source validity
        index = options['index']
        if not Index.objects.filter(index_code=index).count() == 1:
            raise CommandError('Index "%s" does not exist or exists more than once.' % index)

        data_source = options['data_source']
        if not MarketDataSource.objects.filter(market_data_source_code=data_source).count() == 1:
            raise CommandError(
                'Market data source "%s" does not exist or exists more than once.' % data_source
            )

        run_for_all_symbols = False
        symbol = options['symbol']
        if symbol:
            if not Symbol.objects.filter(symbol_code=symbol).count() == 1:
                raise CommandError('Symbol "%s" does not exist or exists more than once.' % symbol)
        else:
            run_for_all_symbols = True
            print ('Running for all symbols in index {0} from market data source {1}'.format(
                index,
                data_source
            ))

        if run_for_all_symbols:
            sy = Symbol.objects.filter(index__index_code=index, is_active=True)
            if gte_id:
                sy = sy.filter(id__gte=gte_id)
            symbols = sy.values_list(
                'symbol_code',
                flat=True
            )
        else:
            symbols = [symbol]

        input_date_string = (str(options['date']) +
                             '-' +
                             str(options['month']) +
                             '-' +
                             str(options['year']))
        input_date = datetime.datetime.strptime(input_date_string, '%d-%m-%Y').date()
        indicators = Indicators()
        all_ema_crossovers = {}
        for counter, symbol in enumerate(symbols):
            print ('Calculating emas for symbol no. %s: %s' % (str(counter), symbol))
            all_ema_crossovers[symbol] = {}
            exp_window_values = {}
            # Fetch all expoenential moving averages.
            max_window_size = -1
            window_sizes = set()
            for window in settings.EXPONENTIAL_MOVING_AVERAGE_WINDOWS:
                max_window_size = max(max_window_size, window[0], window[1])
                window_sizes.add(window[0])
                window_sizes.add(window[1])
            dsd = DailySymbolData.objects.filter(symbol__symbol_code=symbol,
                                                 data_souce__market_data_source_code=data_source,
                                                 date=input_date).first()
            if dsd:
                all_dsds = dsd.get_all_dsds_for_last_x_days(
                    (max_window_size + settings.EXPONENTIAL_MOVING_AVERAGE_WINDOW_LOOKBACK_PERIOD) * 3
                )
                if all_dsds:
                    # Get all data points and ema for all unique windows
                    all_data_points, all_dates = list(), list()
                    for dsd in all_dsds:
                        all_data_points.append(dsd.close_price)
                        all_dates.append(dsd.date)
                    for days_back in range(settings.EXPONENTIAL_MOVING_AVERAGE_WINDOW_LOOKBACK_PERIOD):
                        date = all_dates[-(days_back + 1)]
                        for window_size in window_sizes:
                            if window_size not in exp_window_values:
                                exp_window_values[window_size] = {}
                            data_points = list(reversed(list(reversed(all_data_points))[days_back:]))
                            # dates = list(reversed(list(reversed(all_dates))[days_back:]))
                            ema = indicators.ema(data_points, window_size)
                            exp_window_values[window_size][date] = ema

                    # EMA crossovers
                    ema_crossovers = []
                    for windows in settings.EXPONENTIAL_MOVING_AVERAGE_WINDOWS:
                        cuts = self.get_cuts(exp_window_values[windows[0]],
                                             exp_window_values[windows[1]],
                                             windows[0],
                                             windows[1])
                        if cuts:
                            ema_crossovers.append(cuts)

                    all_ema_crossovers[symbol] = ema_crossovers
                    if ema_crossovers:
                        # Write results to CSV.
                        f = open(file_name + '-EMA-Indicators.csv', 'a+')
                        csv_writer = csv.writer(f)
                        csv_writer.writerow([symbol])
                        csv_writer.writerows(ema_crossovers)
                        csv_writer.writerow([])
                        f.close()

                    # Get macd line
                    ema_values_line = {}
                    macd_line = []
                    for i in range(50):
                        data_points = list(reversed(list(reversed(all_data_points))[i:]))
                        date = all_dates[-(i + 1)]
                        ema_12 = indicators.ema(data_points, 12)
                        ema_26 = indicators.ema(data_points, 26)
                        macd_line.append(ema_12 - ema_26)
                        ema_values_line[date] = ema_12 - ema_26

                    # Get macd signal line
                    ema_values_signal = {}
                    if macd_line:
                        for days_back in range(settings.EXPONENTIAL_MOVING_AVERAGE_WINDOW_LOOKBACK_PERIOD):
                            date = all_dates[-(days_back + 1)]
                            data_points = list(reversed(macd_line[days_back:]))
                            ema = indicators.ema(data_points, 9)
                            ema_values_signal[date] = ema

                    # Get macd line and macd signal line crossover
                    macd_signal_crossovers = []
                    if macd_line and ema_values_signal:
                        cuts = self.get_cuts(ema_values_signal,
                                             ema_values_line,
                                             'macd signal',
                                             'macd line')
                        if cuts:
                            macd_signal_crossovers.append(cuts)

                    if macd_signal_crossovers:
                        # Write results to CSV.
                        f = open(file_name + '-EMA-Indicators.csv', 'a+')
                        csv_writer = csv.writer(f)
                        csv_writer.writerow([symbol + ' - MACD crossover'])
                        csv_writer.writerows(macd_signal_crossovers)
                        csv_writer.writerow([])
                        f.close()

                    # Check if macd is signaling buy.
                    is_macd_positive = False
                    sorted_dates = list(sorted(ema_values_signal.keys()))
                    last_date = sorted_dates[-1]
                    if ema_values_line[last_date] > ema_values_signal[last_date]:
                        is_macd_positive = True

                    # Get true range values
                    true_range_data_points = []
                    true_range_dates = []
                    true_range_dsds = []
                    for counter, dsd in enumerate(all_dsds[1:]):
                        true_range_val = max(abs(dsd.high_price - dsd.low_price),
                                             abs(dsd.high_price - all_dsds[counter].close_price),
                                             abs(dsd.low_price - all_dsds[counter].close_price))
                        true_range_data_points.append(true_range_val)
                        true_range_dates.append(dsd.date)
                        true_range_dsds.append(dsd)

                    # Get average true range values.
                    atr_values_line = {}
                    atr_vals_arr = []
                    atr_dates_arr = []
                    atr_dsds_arr = []
                    for i in range(200):
                        data_points = list(reversed(list(reversed(true_range_data_points))[i:]))
                        date = true_range_dates[-(i + 1)]
                        dsd = true_range_dsds[-(i + 1)]
                        ema_14 = indicators.ema(data_points, 7)
                        atr_vals_arr.append(ema_14)
                        atr_dates_arr.append(date)
                        atr_dsds_arr.append(dsd)
                        atr_values_line[date] = ema_14

                    atr_vals_arr = list(reversed(atr_vals_arr))
                    atr_dates_arr = list(reversed(atr_dates_arr))
                    atr_dsds_arr = list(reversed(atr_dsds_arr))

                    print ('MACD is %s' % 'positive' if is_macd_positive else 'negative')
                    for multiplier in settings.SUPERTREND_MULTIPLIERS:
                        last_basic_upperband = (((atr_dsds_arr[0].high_price + atr_dsds_arr[0].low_price) / 2) +
                                                (multiplier * atr_vals_arr[0]))
                        last_basic_lowerband = (((atr_dsds_arr[0].high_price + atr_dsds_arr[0].low_price) / 2) -
                                                (multiplier * atr_vals_arr[0]))
                        last_final_upperband = last_basic_upperband
                        last_final_lowerband = last_basic_lowerband
                        last_supertrend = last_basic_upperband
                        all_supertrends = [last_supertrend]
                        for counter, atr in enumerate(atr_vals_arr[1:]):
                            curr_index = counter + 1
                            curr_basic_upperband = (((atr_dsds_arr[curr_index].high_price +
                                                      atr_dsds_arr[curr_index].low_price) / 2) +
                                                    (multiplier * atr_vals_arr[curr_index]))
                            curr_basic_lowerband = (((atr_dsds_arr[curr_index].high_price +
                                                      atr_dsds_arr[curr_index].low_price) / 2) -
                                                    (multiplier * atr_vals_arr[curr_index]))

                            if ((curr_basic_upperband < last_final_upperband) or
                                (atr_dsds_arr[curr_index - 1].close_price > last_final_upperband)):
                                curr_final_upperband = curr_basic_upperband
                            else:
                                curr_final_upperband = last_final_upperband

                            if ((curr_basic_lowerband > last_final_lowerband) or
                                (atr_dsds_arr[curr_index - 1].close_price < last_final_lowerband)):
                                curr_final_lowerband = curr_basic_lowerband
                            else:
                                curr_final_lowerband = last_final_lowerband

                            if ((last_supertrend == last_final_upperband) and
                                (atr_dsds_arr[curr_index].close_price <= curr_final_upperband)):
                                curr_supertrend = curr_final_upperband
                            else:
                                if ((last_supertrend == last_final_upperband) and
                                    (atr_dsds_arr[curr_index].close_price > curr_final_upperband)):
                                    curr_supertrend = curr_final_lowerband
                                else:
                                    if ((last_supertrend == last_final_lowerband) and
                                        (atr_dsds_arr[curr_index].close_price >= curr_final_lowerband)):
                                        curr_supertrend = curr_final_lowerband
                                    else:
                                        if ((last_supertrend == last_final_lowerband) and
                                            (atr_dsds_arr[curr_index].close_price < curr_final_lowerband)):
                                            curr_supertrend = curr_final_upperband
                            last_basic_upperband = curr_basic_upperband
                            last_basic_lowerband = curr_basic_lowerband
                            last_final_upperband = curr_final_upperband
                            last_final_lowerband = curr_final_lowerband
                            last_supertrend = curr_supertrend
                            all_supertrends.append(last_supertrend)
                        print ('Working on multiplier %s' % multiplier)
                        if last_supertrend < atr_dsds_arr[-1].close_price:
                            # print ('Positive supertrend.')
                            if ((all_supertrends[-2] >= atr_dsds_arr[-2].close_price) or
                                (all_supertrends[-3] >= atr_dsds_arr[-3].close_price)):
                                print (all_supertrends[-3], all_supertrends[-2])
                                print ('Newly crossed over positive supertrend')
                        else:
                            # print ('Crossover expected')
                            pass