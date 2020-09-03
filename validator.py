#  Copyright (c) 2020 Industrial Technology Research Institute.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import datetime
import json
import argparse
import pandas as pd
from query_table import valid_prod_no, valid_prod_line, valid_keys, valid_k_line, \
    width_constraint, type_transition, composition_transition, tune_hour_state, code_type_transition, \
    state_transition, special_order_code, initial_state, mfg_transition


def handle_validation_errors(obj, msg):
    """Wrap validation errors.
    """
    obj.check_pass = False
    obj.check_msg = msg
    return obj.check_pass, obj.check_msg


def generate_date_list(start_date, end_date):
    date_list = []
    end_date = end_date + datetime.timedelta(1)
    for n in range(int((end_date - start_date).days)):
        date_list.append((start_date + datetime.timedelta(n)).strftime('%Y-%m-%d'))
    return date_list


class DatetimeRange:
    def __init__(self, dt1, dt2):
        self._dt1 = dt1
        self._dt2 = dt2

    def __contains__(self, dt):
        """Check if the date is in valid date range"""
        return self._dt1 <= dt <= self._dt2


class Validator:
    """Validate submission file"""

    def __init__(self, order_file, json_file, start_date, end_date):
        # 1. Check for JSON format.
        try:
            with open(json_file) as f:
                self.data = json.load(f)
                self.check_pass = True
                self.check_msg = 'Submission file is valid.'
        except Exception as e:
            self.data = None
            self.check_pass = False
            self.check_msg = str(e)

        self.start_date = start_date
        self.end_date = end_date

        try:
            self.order_df = pd.read_csv(order_file, index_col='order_code')  # Get order information
        except Exception as e:
            self.order_df = None
            self.check_pass = False
            self.check_msg = str(e)

    def validate_dates(self):
        """2. Check the scheduled date is valid."""
        tmp_date = None
        if self.check_pass:
            for date, v in self.data.items():
                try:
                    datetime.datetime.strptime(date, '%Y-%m-%d')
                except ValueError:
                    msg = '{}: Wrong datetime format.'.format(date)
                    return handle_validation_errors(self, msg)

                current_date = datetime.datetime.strptime(date, '%Y-%m-%d')
                start_date = datetime.datetime.strptime(self.start_date, '%Y-%m-%d')
                end_date = datetime.datetime.strptime(self.end_date, '%Y-%m-%d')

                if current_date not in DatetimeRange(start_date, end_date):
                    msg = 'Scheduled date is not in valid range. ({} to {})'.format(self.start_date, self.end_date)
                    return handle_validation_errors(self, msg)

                if not tmp_date:
                    tmp_date = date
                else:
                    if datetime.datetime.strptime(date, '%Y-%m-%d') < datetime.datetime.strptime(tmp_date, '%Y-%m-%d'):
                        msg = '{}, {}: Wrong date order.'.format(date, tmp_date)
                        return handle_validation_errors(self, msg)
                    tmp_date = date

            valid_date = generate_date_list(start_date, end_date)
            if not all(list(i in list(self.data.keys()) for i in valid_date)):
                msg = 'Not all dates are included.'
                return handle_validation_errors(self, msg)
        return self.check_pass, self.check_msg

    def check_valid_schedule(self):
        init_count = 0
        order_set = set()
        amount_dict = {}
        if self.check_pass:
            for date, lines in self.data.items():
                line_per_day = []
                open_line_per_day = set()
                init_count = init_count + 1
                for line_no, line_data in lines.items():
                    line_per_day.append(line_no)

                    # 3. Check for production lines.
                    if line_no not in valid_prod_line:
                        msg = '{}, {}: Wrong production lines.'.format(date, line_no)
                        return handle_validation_errors(self, msg)
                    if not isinstance(line_data, list):
                        msg = '{}, {}: Scheduled items should be a list.'.format(date, line_no)
                        return handle_validation_errors(self, msg)
                    if len(line_data) == 0:
                        msg = '{}, {}: Scheduled items should not be empty.'.format(date, line_no)
                        return handle_validation_errors(self, msg)

                    cul_hours = 0
                    for data in line_data:
                        type_change = False
                        df_composition = None
                        header = '{},{}: '.format(date, line_no)
                        #  4. Check for order code, product code, hours and mfg_width.
                        if set(valid_keys) != set(data.keys()):
                            msg = header + 'Some keys are missing in {}.'.format(valid_keys)
                            return handle_validation_errors(self, msg)

                        header = '{},{},{}: '.format(date, line_no, data['order_code'])
                        if not isinstance(data['order_code'], str):
                            msg = header + '"order_code" is not string.'
                            return handle_validation_errors(self, msg)
                        if data['order_code'] not in special_order_code + self.order_df.index.tolist():
                            msg = header + 'Invalid "order_code".'
                            return handle_validation_errors(self, msg)
                        if data['order_code'] not in special_order_code:
                            order_set.add(data['order_code'])
                        if not isinstance(data['product_code'], str):
                            msg = header + '"product_code" is not string.'
                            return handle_validation_errors(self, msg)
                        if data['product_code'] not in valid_prod_no and data['product_code'] not in special_order_code:
                            msg = header + 'Invalid "product_code".'
                            return handle_validation_errors(self, msg)
                        if not isinstance(data['hours'], int):
                            msg = header + '"hours" is not integer.'
                            return handle_validation_errors(self, msg)
                        if data['hours'] < 0:
                            msg = header + 'Invalid "hours".'
                            return handle_validation_errors(self, msg)
                        if not isinstance(data['mfg_width'], int):
                            msg = header + '"mfg_width" is not integer.'
                            return handle_validation_errors(self, msg)
                        if data['mfg_width'] < 0:
                            msg = header + 'Invalid "mfg_width".'
                            return handle_validation_errors(self, msg)
                        # 5. Check for date constraints.
                        code_type_transition[line_no].append(data['order_code'])
                        if data['order_code'] != 'stop':
                            open_line_per_day.add(line_no)
                            if data['order_code'] not in special_order_code:
                                if len(code_type_transition[line_no]) > 0:
                                    if len(code_type_transition[line_no]) == 1 or code_type_transition[line_no][-2] == 'stop':
                                        msg = header + 'You should tune the machine (tune_8 or tune_48) before start.'
                                        return handle_validation_errors(self, msg)
                                if self.order_df.loc[data['order_code'], 'product_code'] != data['product_code']:
                                    msg = header + 'Mismatched "order_code" and "product_code".'
                                    return handle_validation_errors(self, msg)
                                tune_hours = tune_hour_state[line_no]
                                tune_hour_state[line_no] = 0
                                try:
                                    not_before = datetime.datetime.strptime(
                                        self.order_df.loc[data['order_code'], 'not_before'].split('T')[0], '%Y-%m-%d')
                                    not_after = datetime.datetime.strptime(
                                        self.order_df.loc[data['order_code'], 'not_after'].split('T')[0], '%Y-%m-%d')
                                    prod_date = datetime.datetime.strptime(date, '%Y-%m-%d')
                                    if prod_date not in DatetimeRange(not_before, not_after):
                                        msg = header + 'Production schedule is out of range.'
                                        return handle_validation_errors(self, msg)
                                except Exception as e:
                                    msg = str(e)
                                    return handle_validation_errors(self, msg)

                                df_code = self.order_df.loc[data['order_code'], 'material']
                                df_composition = self.order_df.loc[data['order_code'], 'composition']
                                #     6. Check for production line constraints.
                                if df_code == 'MS':
                                    if line_no != 'C1':
                                        msg = header + 'Invalid line assignment for MS material.'
                                        return handle_validation_errors(self, msg)
                                if 'K' in data['product_code']:
                                    if line_no not in valid_k_line:
                                        msg = header + 'Invalid line assignment for product code starting with K.'
                                        return handle_validation_errors(self, msg)

                                # 7. Check for width constraints.
                                try:
                                    product_type = self.order_df.loc[data['order_code'], 'type']
                                    width = self.order_df.loc[data['order_code'], 'width']
                                    type_transition[line_no].append(product_type)
                                    if not width_constraint[line_no]['max_mfg_width'].get(product_type, None):
                                        msg = header + 'Mismatched "type: {}" and "line: {}".'.format(product_type, line_no)
                                        return handle_validation_errors(self, msg)
                                    if data['mfg_width'] > width_constraint[line_no]['max_mfg_width'][product_type]:
                                        msg = header + '"mfg_width" exceeds production limit.'
                                        return handle_validation_errors(self, msg)
                                    if width > width_constraint[line_no]['max_width'][product_type]:
                                        msg = header + '"width" exceeds production limit.'
                                        return handle_validation_errors(self, msg)
                                    if product_type == 'lenti' and (data['mfg_width'] - width) < 70:
                                        msg = header + '"mfg_width" should be at least 70mm wider than "width" for type "lenti".'
                                        return handle_validation_errors(self, msg)
                                    elif product_type == 'plate' and (data['mfg_width'] - width) < 50:
                                        msg = header + '"mfg_width" should be at least 50mm wider than "width" for type "plate".'
                                        return handle_validation_errors(self, msg)
                                except Exception as e:
                                    msg = str(e)
                                    return handle_validation_errors(self, msg)

                                last_type = initial_state[line_no]
                                if len(type_transition[line_no]) > 1:
                                    type_list = type_transition[line_no]
                                    last_type = type_list[-2]

                                """  8. Check if the machine of specific production line restart while:
                                         a. The type of product changed. (tune for 48 hours)
                                """

                                if last_type and last_type != product_type:
                                    type_change = True
                                    if code_type_transition[line_no][-2] != 'tune_48' or tune_hours != 48:
                                        msg = header + 'Type changed, you should tune the machine for 48 hours (tune_48).'
                                        return handle_validation_errors(self, msg)

                                """  8. Check if the machine of specific production line restart while:
                                         b. The composition of product changed from 8% or 100% to 0%. (tune for 8 hours)
                                """
                                last_composition = None
                                last_state = None
                                if len(state_transition[line_no]) > 0:
                                    last_state = state_transition[line_no][-1]
                                if len(composition_transition[line_no]) > 0:
                                    last_composition = composition_transition[line_no][-1]
                                if last_composition and last_composition != '0%':
                                    if df_composition and df_composition == '0%':
                                        valid_state = 'tune_8'
                                        valid_tune_hours = 8
                                        if type_change:
                                            valid_state = 'tune_48'
                                            valid_tune_hours = 48
                                        if last_state != valid_state or tune_hours != valid_tune_hours:
                                            msg = header + 'Composition changed to 0%, you should tune the machine for {} hours. ({})'.format(
                                                valid_tune_hours, valid_state)
                                            return handle_validation_errors(self, msg)

                                if len(mfg_transition[line_no]) > 0:
                                    valid_tune_state = 'tune_8'
                                    valid_tune_hours = 8
                                    if type_change:
                                        valid_tune_state = 'tune_48'
                                        valid_tune_hours = 48
                                    if data['mfg_width'] != mfg_transition[line_no][-1]:
                                        if last_state != valid_tune_state or tune_hours != valid_tune_hours:
                                            msg = header + '"mfg_width" changed, you should tune the machine for {} hours. ({})'.format(
                                                valid_tune_hours, valid_tune_state)
                                            return handle_validation_errors(self, msg)
                                mfg_transition[line_no].append(data['mfg_width'])

                                # Calculate production quantity for each order
                                amount_dict[data['order_code']] = data['hours'] * 125 + amount_dict.get(
                                    data['order_code'], 0)

                            elif data['order_code'] == 'tune_8':
                                if data['product_code'] != 'tune_8':
                                    msg = header + 'Mismatched "order_code" and "product_code".'
                                    return handle_validation_errors(self, msg)
                                if len(code_type_transition[line_no]) > 1 and code_type_transition[line_no][-2] == 'tune_48':
                                    msg = header + '"tune_48" cannot be followed by "tune_8".'
                                    return handle_validation_errors(self, msg)
                                if data['hours'] > 8:
                                    msg = header + 'Invalid tune hours for "tune_8".'
                                    return handle_validation_errors(self, msg)
                                tune_hour_state[line_no] += data['hours']
                                if tune_hour_state[line_no] > 8:
                                    msg = header + 'You cannot tune more than 8 hours for "tune_8".'
                                    return handle_validation_errors(self, msg)
                            elif data['order_code'] == 'tune_48':
                                if data['product_code'] != 'tune_48':
                                    msg = header + 'Mismatched "order_code" and "product_code".'
                                    return handle_validation_errors(self, msg)
                                if len(code_type_transition[line_no]) > 1 and code_type_transition[line_no][-2] == 'tune_8':
                                    msg = header + '"tune_8" cannot be followed by "tune_48".'
                                    return handle_validation_errors(self, msg)
                                if data['hours'] > 24:
                                    msg = header + 'Invalid tune hours for "tune_48".'
                                    return handle_validation_errors(self, msg)
                                tune_hour_state[line_no] += data['hours']
                                if tune_hour_state[line_no] > 48:
                                    msg = header + 'You cannot tune more than 48 hours for "tune_48".'
                                    return handle_validation_errors(self, msg)

                        cul_hours += data['hours']
                        state_transition[line_no].append(data['order_code'])
                        if df_composition:
                            composition_transition[line_no].append(df_composition)

                    header = '{},{}: '.format(date, line_no)
                    if cul_hours != 24:
                        msg = header + 'Working hours should be equal to 24 per day.'
                        return handle_validation_errors(self, msg)
                #  9. Check if the number of opened production lines are between 2~6.
                if set(line_per_day) != set(valid_prod_line):
                    msg = 'Missing schedule for some production lines.'
                    return handle_validation_errors(self, msg)
                if len(open_line_per_day) not in range(2, 7):
                    msg = 'The number of open production lines should be between 2 and 6.'
                    return handle_validation_errors(self, msg)

            order_in_range = self.order_df

            #  10. Check if all orders are included.
            if order_set != set(order_in_range.index):
                msg = 'Not all order are included.'
                return handle_validation_errors(self, msg)

            #  11. Check if the product amount is valid.
            for order, amount in amount_dict.items():
                if amount != order_in_range.loc[order, 'quantity']:
                    msg = 'Wrong production quantity for order: {}.'.format(order)
                    return handle_validation_errors(self, msg)

        return self.check_pass, self.check_msg


if __name__ == '__main__':
    parser = argparse.ArgumentParser("validator")
    parser.add_argument("--order_file", default='orders_2019.csv', type=str)
    parser.add_argument("--submit_file", default='submission_example.json', type=str)
    parser.add_argument("--start_date", default='2019-07-01', type=str)
    parser.add_argument("--end_date", default='2019-12-31', type=str)
    args = parser.parse_args()
    val = Validator(args.order_file, args.submit_file, args.start_date, args.end_date)
    val.validate_dates()
    val.check_valid_schedule()
    print(val.check_msg)
