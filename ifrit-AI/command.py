from gamedata import GameData


class Command():
    PARAM_COLOR = "#8a1624"

    def __init__(self, op_id: int, op_code: list, game_data: GameData, battle_text=(), info_stat_data_monster_name=(), line_index = 0):
        self.__op_id = op_id
        self.__op_code = op_code
        self.__battle_text = battle_text
        self.__text = ""
        self.__text_colored = ""
        self.__game_data = game_data
        self.info_stat_data_monster_name = info_stat_data_monster_name
        self.__analyse_op_data()
        self.op_id_widget = None
        self.op_code_widget = []
        self.text_widget = None
        self.line_index = line_index
        self.if_index = 0

    def __str__(self):
        return f"ID: {self.__op_id}, op_code: {self.__op_code}, text: {self.__text}"

    def __repr__(self):
        return self.__str__()

    def set_op_id(self, op_id):
        self.__op_id = op_id
        op_info = self.__get_op_code_line_info()
        self.__op_code = [0]* op_info["size"]
        self.__analyse_op_data()

    def set_op_code(self, op_code):
        self.__op_code = op_code
        self.__analyse_op_data()

    def get_id(self):
        return self.__op_id

    def get_op_code(self):
        return self.__op_code

    def get_text(self):
        return self.__text

    def __get_op_code_line_info(self):
        all_op_code_info = self.__game_data.ai_data_json["op_code_info"]
        op_research = [x for x in all_op_code_info if x["op_code"] == self.__op_id]
        if op_research:
            op_research = op_research[0]
        else:
            print("No op_code defined for op_id: {}".format(self.__op_id))
            op_research = [x for x in all_op_code_info if x["op_code"] == 255][0]
        return op_research

    def __analyse_op_data(self,):

        op_info = self.__get_op_code_line_info()
        # Searching for errors in json file
        if len(op_info["param_type"]) != op_info["size"] and op_info['complexity'] == 'simple':
            print(f"Error on JSON for op_code_id: {self.__op_id}")
        if op_info["complexity"] == "simple":
            param_value = []
            for index, type in enumerate(op_info["param_type"]):
                op_index = op_info["param_index"][index]
                if type == "int":
                    param_value.append(str(self.__op_code[op_index]))
                elif type == "var":
                    # There is specific var known, if not in the list it means it's a generic one
                    param_value.append("var"+self.__get_var_name(self.__op_code[op_index]))
                elif type == "special_action":
                    if self.__op_code[op_index] < len(self.__game_data.special_action):
                        param_value.append(self.__game_data.special_action[self.__op_code[op_index]]['name'])
                    else:
                        param_value.append("UNKNOWN SPECIAL_ACTION")
                elif type == "card":
                    if self.__op_code[op_index] < len(self.__game_data.card_values):
                        param_value.append(self.__game_data.card_values[self.__op_code[op_index]]['name'])
                    else:
                        param_value.append("UNKNOWN CARD")
                elif type == "monster":
                    if self.__op_code[op_index] < len(self.__game_data.monster_values):
                        param_value.append(self.__game_data.monster_values[self.__op_code[op_index]])
                    else:
                        param_value.append("UNKNOWN MONSTER")
                elif type == "item":
                    if self.__op_code[op_index] < len(self.__game_data.item_values):
                        param_value.append(self.__game_data.item_values[self.__op_code[op_index]]['name'])
                    else:
                        param_value.append("UNKNOWN ITEM")
                elif type == "gforce":
                    if self.__op_code[op_index] < len(self.__game_data.gforce_values):
                        param_value.append(self.__game_data.gforce_values[self.__op_code[op_index]])
                    else:
                        param_value.append("UNKNOWN GFORCE")
                elif type == "target":
                    param_value.append(self.__get_target(self.__op_code[op_index], self.__game_data))
                else:
                    print("Unknown type, considering a int")
                    param_value.append(self.__op_code[op_index])
            for i in range(len(param_value)):
                param_value[i] = '<span style="color:#8a1624;">' + param_value[i] + '</span>'
            self.__text = op_info['text'].format(*param_value)
        elif op_info["complexity"] == "complex":
            call_function = getattr(self, "_Command__op_" + "{:02X}".format(op_info["op_code"]) + "_analysis")
            self.__text = call_function(self.__op_code)

    def __op_17_analysis(self, op_code):
        if op_code[0] > 0:
            ret = "DEACTIVATE RUN"
        else:
            ret = "ACTIVATE RUN"
        return ret

    def __op_26_analysis(self, op_code):
        if op_code[3] < len(self.__game_data.status_ia_values):
            status = self.__game_data.status_ia_values[op_code[3]]['name']
        else:
            status = "UNKNOWN STATUS"
        if op_code[0] + op_code[2]:
            info = ''
        else:
            info = " unknown <span style=\"color:#8a1624;\">{}</span>|<span style=\"color:#8a1624;\">{}</span>".format(op_code[0], op_code[2])
        ret = "TARGET <span style=\"color:#8a1624;\">{}</span> WITH STATUS <span style=\"color:#8a1624;\">{}</span><span style=\"color:#8a1624;\">{}</span>".format(
            self.__get_target(op_code[1], self.__game_data), status, info)
        return ret

    def __op_18_analysis(self, op_code):
        ret = self.__op_01_analysis(op_code)
        if op_code[0] != 0:
            ret += (''
                    ' debug: <span style=\"color:#8a1624;\">{}</span>').format(str(op_code[0]))
        return ret

    def __op_28_analysis(self, op_code):
        if op_code[0] == 0:
            aptitude = 'Strength'
        elif op_code[0] == 1:
            aptitude = 'Vitality'
        elif op_code[0] == 2:
            aptitude = 'Magic'
        elif op_code[0] == 3:
            aptitude = 'Spirit'
        elif op_code[0] == 4:
            aptitude = 'Speed'
        elif op_code[0] == 5:
            aptitude = 'Evade'
        else:
            aptitude = "Unknown aptitude"

        if op_code[1] == 10:
            mod_change = "REINIT <span style=\"color:#8a1624;\">{}</span> TO BASE VALUE".format(aptitude)
        else:
            mod_change = "MULTIPLY <span style=\"color:#8a1624;\">{}</span> BY <span style=\"color:#8a1624;\">{}</span>".format(aptitude, op_code[1] / 10)
        return mod_change

    def __op_23_analysis(self, op_code):
        jump = int.from_bytes(bytearray([op_code[0], op_code[1]]), byteorder='little')
        if jump == 0:
            text = 'ENDIF'
        else:
            text = 'ELSE'
        return text

    def __op_2D_analysis(self, op_code):
        # op_2D = ['element', 'elementval', '?']
        if op_code[0] < len(self.__game_data.magic_type_values):
            element = self.__game_data.magic_type_values[op_code[0]]
        else:
            element = "UNKNOWN ELEMENT TYPE"
        element_val = op_code[1]
        op_code_unknown = op_code[2]
        return 'Resist element <span style=\"color:#8a1624;\">{}</span> at <span style=\"color:#8a1624;\">{}</span>'.format(element, element_val)

    def __op_1A_analysis(self, op_code):
        analysis = self.__op_01_analysis(op_code)
        analysis += 'LOCK BATTLE'
        return analysis

    def __op_01_analysis(self, op_code):
        if op_code[0] < len(self.__battle_text):
            ret = 'SHOW BATTLE TEXT: <span style=\"color:#8a1624;\">{}</span>'.format(self.__battle_text[op_code[0]])
        else:
            ret = "/!\\SHOW BATTLE BUT NO BATTLE TO SHOW"
        return ret

    def __op_02_analysis(self, op_code):
        # op_02 = ['subject_id', 'target', 'comparator', 'value', 'debug']
        subject_id = op_code[0]
        target = self.__get_target(op_code[1], self.__game_data)
        target_reverse = self.__get_target(op_code[1], self.__game_data, True)
        op_code_comparator = op_code[2]
        op_code_value = op_code[3]
        op_code_debug = int.from_bytes(bytearray([op_code[5], op_code[6]]), byteorder='little')
        if op_code_comparator < len(self.__game_data.ai_data_json['list_comparator']):
            comparator = self.__game_data.ai_data_json['list_comparator'][op_code_comparator]
        else:
            comparator = 'UNKNOWN OPERATOR'
        if subject_id == 0:
            left_subject = {'text': 'HP of <span style=\"color:#8a1624;\">{}</span>'.format(target), 'param': [target]}
            right_subject = {'text': '<span style=\"color:#8a1624;\">{}</span> %', 'param': [op_code_value * 10]}
        elif subject_id == 1:
            left_subject = {'text': 'HP of <span style=\"color:#8a1624;\">{}</span>'.format(target), 'param': [target]}
            right_subject = {'text': '<span style=\"color:#8a1624;\">{}</span> %', 'param': [op_code_value * 10]}
        elif subject_id == 2:
            left_subject = {'text': 'RANDOM VALUE BETWEEN 0 AND <span style=\"color:#8a1624;\">{}</span>', 'param': [op_code[1]]}
            right_subject = {'text': '<span style=\"color:#8a1624;\">{}</span>', 'param': [op_code_value]}
        elif subject_id == 3:
            left_subject = {'text': 'Combat scene', 'param': []}
            right_subject = {'text': '<span style=\"color:#8a1624;\">{}</span>', 'param': [op_code_value]}
        elif subject_id == 4:
            left_subject = {'text': 'STATUS OF <span style=\"color:#8a1624;\">{}</span>', 'param': [target]}
            right_subject = {'text': '<span style=\"color:#8a1624;\">{}</span>', 'param': [self.__game_data.status_ia_values[op_code_value]['name']]}
        elif subject_id == 5:
            left_subject = {'text': 'STATUS OF <span style=\"color:#8a1624;\">{}</span>', 'param': [target_reverse]}
            right_subject = {'text': '<span style=\"color:#8a1624;\">{}</span>', 'param': [self.__game_data.status_ia_values[op_code_value]['name']]}
        elif subject_id == 6:
            left_subject = {'text': 'NUMBER OF MEMBER OF <span style=\"color:#8a1624;\">{}</span>', 'param': [target_reverse]}
            right_subject = {'text': '<span style=\"color:#8a1624;\">{}</span>', 'param': [op_code_value]}
        elif subject_id == 9:
            left_subject = {'text': "<span style=\"color:#8a1624;\">{}</span>", 'param': [self.__get_target(op_code[3], self.__game_data)]}
            right_subject = {'text': 'ALIVE', 'param': []}
        elif subject_id == 10:
            if op_code[1] == 0:
                attack_condition = "ATTACKER WAS TEAM MEMBER N°"
                attack_type = op_code_value
            elif op_code[1] == 1:
                attack_condition = "ATTACKER IS"
                attack_type = target
            elif op_code[1] == 3:
                attack_condition = "Last attack was of type"
                if op_code_value == 1:
                    attack_type = "Physical damage"
                    self.was_physical = True
                elif op_code_value == 2:
                    attack_type = "Magical damage"
                    self.was_magic = True
                elif op_code_value == 4:
                    attack_type = "Item"
                    self.was_item = True
                elif op_code_value == 254:
                    attack_type = "G-Force"
                    self.was_force = True
                else:
                    attack_type = "Unknown <span style=\"color:#8a1624;\">{}</span>"
            elif op_code[1] == 4:
                if op_code_value >= 64:
                    attack_condition = "LAST GFORCE LAUNCH WAS"
                    attack_type = self.__game_data.gforce_values[op_code_value - 64]
                else:
                    if self.was_magic:
                        ret = self.__game_data.magic_values[op_code_value]['name']
                    elif self.was_item:
                        ret = self.__game_data.item_values[op_code_value]['name']
                    elif self.was_physical:
                        ret = self.__game_data.special_action[op_code_value]['name']
                    else:
                        ret = op_code_value
                    attack_condition = "LAST ACTION LAUNCH WAS"
                    attack_type = ret
                    self.was_magic = False
                    self.was_item = False
                    self.was_physical = False
            elif op_code[1] == 5:
                attack_condition = "Last attack was of element"
                attack_type = self.__game_data.magic_type_values[op_code_value]
            else:
                attack_condition = "Unknown last attack <span style=\"color:#8a1624;\">{}</span>"
                attack_type = "Unknown attack type <span style=\"color:#8a1624;\">{}</span>"
            left_subject = {'text': attack_condition, 'param': [op_code[1]]}
            right_subject = {'text': attack_type, 'param': [op_code_value]}
        elif subject_id == 14:
            left_subject = {'text': "Group level <span style=\"color:#8a1624;\">{}</span>", 'param': [target]}
            right_subject = {'text': '<span style=\"color:#8a1624;\">{}</span>', 'param': [op_code_value]}
        elif subject_id == 15:
            left_subject = {'text': "<span style=\"color:#8a1624;\">{}</span> CAN ATTACK WITH HIS ALLY", 'param': [target]}
            right_subject = {'text': '<span style=\"color:#8a1624;\">{}</span>', 'param': [op_code_value]}
        elif subject_id == 17:
            left_subject = {'text': "GFORCE STOLEN (TARGET: <span style=\"color:#8a1624;\">{}</span>)", 'param': [target]}
            right_subject = {'text': '<span style=\"color:#8a1624;\">{}</span>', 'param': [op_code_value]}
        elif subject_id == 18:
            left_subject = {'text': "Odin attaque ?", 'param': [target]}
            right_subject = {'text': '<span style=\"color:#8a1624;\">{}</span>', 'param': [op_code_value]}
        elif subject_id == 19:
            left_subject = {'text': "COUNTDOWN", 'param': [target]}
            right_subject = {'text': '<span style=\"color:#8a1624;\">{}</span>', 'param': [op_code_value]}
        elif subject_id <= 19:
            left_subject = {'text': 'UNKNOWN SUBJECT', 'param': []}
            right_subject = {'text': '<span style=\"color:#8a1624;\">{}</span>', 'param': [op_code_value]}
        else:
            left_subject = {'text': '<span style=\"color:#8a1624;\">{}</span>', 'param': [self.__get_var_name(subject_id)]}
            right_subject = {'text': '<span style=\"color:#8a1624;\">{}</span>', 'param': [op_code_value]}
        left_subject = left_subject['text'].format(*left_subject['param'])
        right_subject = right_subject['text'].format(*right_subject['param'])

        return f"IF - Subject ID: <span style=\"color:#8a1624;\">{subject_id}</span>,{left_subject} {comparator} {right_subject}, Jump <span style=\"color:#8a1624;\">{op_code_debug}</span> bytes forward, Debug: <span style=\"color:#8a1624;\">{op_code[4]}</span>"

    def __op_27_analysis(self, op_code):
        if op_code[0] == 23:
            ret = 'auto-boomerang'
        else:
            ret = "unknown flag <span style=\"color:#8a1624;\">{}</span>".format(op_code[0])
        return 'MAKE <span style=\"color:#8a1624;\">{}</span> of <span style=\"color:#8a1624;\">{}</span> to <span style=\"color:#8a1624;\">{}</span>'.format(
            ret, self.info_stat_data_monster_name, op_code[1])

    def __get_var_name(self, id):
        # There is specific var known, if not in the list it means it's a generic one
        all_var_info = self.__game_data.ai_data_json["list_var"]
        var_info_specific = [x for x in all_var_info if x["op_code"] == id]
        if var_info_specific:
            var_info_specific = var_info_specific[0]['var_name']
        else:
            var_info_specific = str(id)
        return var_info_specific

    def __get_target(self, id, game_data: GameData, reverse=False):
        if reverse:
            c8_data = "ALL ENNEMY"
        else:
            c8_data = self.info_stat_data_monster_name
        list_target_other = [c8_data,  # 0xC8
                             'RANDOM ENNEMY',  # 0xC9
                             'RANDOM ALLY',  # 0xCA
                             'LAST ENNEMY TO HAVE ATTACK',  # 0xCB
                             'ALL ENNEMY',  # 0xCC
                             'ALL ALLY',  # 0xCD
                             'UNKNOWN',  # 0xCE
                             'ALLY OR ' + self.info_stat_data_monster_name + ' RANDOMLY',  # 0xCF arconada
                             'RANDOM ENNEMY',  # 0xD0 Marsupial with meteor
                             'NEW ALLY']  # 0xD1 shiva

        if id < len(game_data.ai_data_json['list_target_char']):
            return game_data.ai_data_json['list_target_char'][id]
        elif 0xC8 <= id < 0xC8 + len(list_target_other):
            return list_target_other[id - 0xC8]
        elif id >= 16:
            if id - 16 < len(game_data.monster_values):
                ret = game_data.monster_values[id - 16]
            else:
                ret = "UNKNOWN TARGET"
            return ret