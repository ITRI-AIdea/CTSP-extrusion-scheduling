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

valid_prod_line = ['A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'B4', 'B5', 'C1']
valid_k_line = ['B1', 'B2', 'B3', 'B4']
valid_keys = ['order_code', 'product_code', 'hours', 'mfg_width']
valid_prod_no = [
    'N001',
    'N002',
    'N003',
    'N004',
    'N005',
    'N006',
    'N007',
    'K008',
    'N009',
    'N010',
    'N011',
    'N012',
    'N013',
    'N014',
    'N015',
    'N016',
    'N017',
    'N018',
    'N019',
    'N020',
    'K021',
    'K022',
    'K023',
    'N024',
    'N025',
    'N026',
    'N027',
    'N028',
    'N029',
    'N030',
    'N031',
    'N032',
    'N033',
    'N034',
    'N035',
    'N036',
    'K037',
    'N038',
    'N039',
    'N040',
    'N041',
    'N042',
    'N043',
    'N044',
    'N045',
    'N046',
    'N047',
    'N048',
    'N049'
]
width_constraint = {
    'A1': {'max_mfg_width': {'plate': 1450}, 'max_width': {'plate': 1300}},
    'A2': {'max_mfg_width': {'plate': 1450}, 'max_width': {'plate': 1300}},
    'A3': {'max_mfg_width': {'plate': 1470}, 'max_width': {'plate': 1300}},
    'B1': {'max_mfg_width': {'plate': 1725, 'lenti': 1725}, 'max_width': {'plate': 1575, 'lenti': 1575}},
    'B2': {'max_mfg_width': {'plate': 2000, 'lenti': 2000}, 'max_width': {'plate': 1945, 'lenti': 1945}},
    'B3': {'max_mfg_width': {'plate': 2000, 'lenti': 2000}, 'max_width': {'plate': 1945, 'lenti': 1945}},
    'B4': {'max_mfg_width': {'plate': 1450, 'lenti': 1450}, 'max_width': {'plate': 1300, 'lenti': 1300}},
    'B5': {'max_mfg_width': {'plate': 1450, 'lenti': 1450}, 'max_width': {'plate': 1300, 'lenti': 1300}},
    'C1': {'max_mfg_width': {'plate': 1450, 'lenti': 1450}, 'max_width': {'plate': 1300, 'lenti': 1300}}
}
type_transition = {
    'A1': [],
    'A2': [],
    'A3': [],
    'B1': [],
    'B2': [],
    'B3': [],
    'B4': [],
    'B5': [],
    'C1': []
}
code_type_transition = {
    'A1': [],
    'A2': [],
    'A3': [],
    'B1': [],
    'B2': [],
    'B3': [],
    'B4': [],
    'B5': [],
    'C1': []
}
composition_transition = {
    'A1': [],
    'A2': [],
    'A3': [],
    'B1': [],
    'B2': [],
    'B3': [],
    'B4': [],
    'B5': [],
    'C1': []
}
tune_hour_state = {
    'A1': 0,
    'A2': 0,
    'A3': 0,
    'B1': 0,
    'B2': 0,
    'B3': 0,
    'B4': 0,
    'B5': 0,
    'C1': 0
}
state_transition = {
    'A1': [],
    'A2': [],
    'A3': [],
    'B1': [],
    'B2': [],
    'B3': [],
    'B4': [],
    'B5': [],
    'C1': []
}
mfg_transition = {
    'A1': [],
    'A2': [],
    'A3': [],
    'B1': [],
    'B2': [],
    'B3': [],
    'B4': [],
    'B5': [],
    'C1': []
}
special_order_code = ['stop', 'tune_8', 'tune_48']
tune_order_code = ['tune_8', 'tune_48']
initial_state = {
    'A1': 'plate',
    'A2': 'plate',
    'A3': 'plate',
    'B1': 'plate',
    'B2': 'lenti',
    'B3': 'lenti',
    'B4': 'lenti',
    'B5': 'lenti',
    'C1': 'lenti'
}
