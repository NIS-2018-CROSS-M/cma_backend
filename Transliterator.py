class Transliterator(object):
    def __init__(self, transliteration_table_path):
        self.trans_dict = {}
        print(transliteration_table_path)
        with open(transliteration_table_path) as f:
            for line in f.readlines():
                line = line.strip('\n')
                items = line.split('\t')
                self.trans_dict[items[0]] = items[1]
                self.trans_dict[items[0].upper()] = items[1].upper()

    def transliterate(self, input_file_path, capitalize=False, sep='\t', cols=None):
        output = None
        with open(input_file_path) as c:
            for line in c.readlines():
                line = line.strip()
                if cols:
                    line_after = []
                    for i, part in enumerate(line.split(sep)):
                        if i in cols:
                            part_cap = part[0].isupper()
                            part_after = self._transliterate_line(part)
                            if part_cap and capitalize:
                                part_after = part_after.capitalize()
                        else:
                            part_after = part
                        line_after = line_after.append(part_after)
                    line_after = sep.join(part_after)
                else:
                    line_cap = line[0].isupper()
                    line_after = self._transliterate_line(line)
                    if line_cap and capitalize:
                        line_after = line_after.capitalize()

                if output:
                    output = output + '\n' + line_after
                else:
                    output = line_after
        return output

    def _transliterate_line(self, text):
        transliterated = ''
        for letter in text:
            if letter in self.trans_dict:
                transliterated += self.trans_dict[letter]
            else:
                transliterated += letter
        return transliterated
