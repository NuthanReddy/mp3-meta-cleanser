from __future__ import print_function
import os, re, argparse
from eyed3.id3 import Tag


class CleanMyMusic:
    def __init__(self):
        self.regex = r""
        self.t = Tag()
        self.parser = argparse.ArgumentParser(description='A Python Script to clean/format mp3 file metadata',
                                              prog='mp3clean', usage='python %(prog)s.py [options]',
                                              formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                              epilog="And that's how its done")
        self.args = None
        self.t_map = {'Title': 'title', 'Album': 'album', 'Artist': 'artist', 'AlbumArtist': 'album_artist',
                      'Genre': 'genre.name'}

    def main(self):
        self._parse_args()
        if self.args.case:
            self._title_case()
        if self.args.trim == 'r':
            self._rtrim()
        if self.args.trim == 'l':
            self._ltrim()
        if self.args.nocomments:
            self._no_comments()
        if self.args.set:
            self._set_value()
        if self.args.cleanse:
            self._cleanse()
        if self.args.trackno:
            self._get_track()
        if self.args.invtrackno:
            self._inv_track()
        if self.args.gettrack:
            self._set_track()
        if self.args.newtrack:
            self._new_track()
        if self.args.gettitle:
            self._get_title()

    def _title_case(self):
        for filename in os.listdir(self.args.dir):
            if filename.endswith(".mp3"):
                file_path = os.path.join(self.args.dir, filename)
                self.t.parse(file_path)
                if "All" in self.args.entity:
                    for et in self.t_map:
                        eval('self.t._set' + et + '(self.t.' + self.t_map[et] + '.title())')
                else:
                    for et in self.args.entity:
                        if et != "Filename":
                            try:
                                eval('self.t._set' + et + '(self.t.' + self.t_map[et] + '.title())')
                            except NotImplementedError:
                                continue
                self.t.save()
                if "Filename" in self.args.entity or "All" in self.args.entity:
                    os.rename(file_path, file_path[:-4].title() + ".mp3")

    def _rtrim(self):
        for filename in os.listdir(self.args.dir):
            if filename.endswith(".mp3"):
                file_path = os.path.join(self.args.dir, filename)
                self.t.parse(file_path)
                if "All" in self.args.entity:
                    for et in self.t_map:
                        eval('self.t._set' + et + '(self.t.' + self.t_map[et] + '[:-self.args.num])')
                else:
                    for et in self.args.entity:
                        if et != "Filename":
                            eval('self.t._set' + et + '(self.t.' + self.t_map[et] + '[:-self.args.num])')
                self.t.save()
                if "Filename" in self.args.entity or "All" in self.args.entity:
                    os.rename(file_path, os.path.join(self.args.dir, filename[:-4 - self.args.num]) + ".mp3")

    def _ltrim(self):
        for filename in os.listdir(self.args.dir):
            if filename.endswith(".mp3"):
                file_path = os.path.join(self.args.dir, filename)
                self.t.parse(file_path)
                if "All" in self.args.entity:
                    for et in self.t_map:
                        eval('self.t._set' + et + '(self.t.' + self.t_map[et] + '[self.args.num:])')
                else:
                    for et in self.args.entity:
                        if et != "Filename":
                            eval('self.t._set' + et + '(self.t.' + self.t_map[et] + '[self.args.num:])')
                self.t.save()
                if "Filename" in self.args.entity or "All" in self.args.entity:
                    os.rename(file_path, os.path.join(self.args.dir, filename[self.args.num:]))

    def _no_comments(self):
        for filename in os.listdir(self.args.dir):
            if filename.endswith(".mp3"):
                file_path = os.path.join(self.args.dir, filename)
                self.t.parse(file_path)
                self.t.comments.set(u"")
                self.t.save()

    def _set_value(self):
        for filename in os.listdir(self.args.dir):
            if filename.endswith(".mp3"):
                file_path = os.path.join(self.args.dir, filename)
                self.t.parse(file_path)
                for et in self.args.set:
                    eval('self.t._set' + et + '(u"\u0020".join(self.args.value))')
                self.t.save()

    @staticmethod
    def _clean_using_regex(strng, regex):
        if regex == "[*]":
            return re.sub(r"\[*\]", '', strng)
        elif regex == "(*)":
            return re.sub(r"\(*\)", '', strng)
        elif regex == "* -":
            return strng.split(" -")[-1].strip()
        elif regex == "- *":
            return strng.split("- ")[0].strip()
        elif regex == ":: *":
            return strng.split(":: ")[0].strip()
        elif regex == '-':
            return re.sub("-", '', strng)
        elif regex == '-':
            return re.sub("_", ' ', strng)
        else:
            return strng

    def _cleanse(self):
        for filename in os.listdir(self.args.dir):
            if filename.endswith(".mp3"):
                file_path = os.path.join(self.args.dir, filename)
                self.t.parse(file_path.strip())
                for et in self.args.entity:
                    if et == "Filename":
                        old = filename
                        new = self._clean_using_regex(old, self.args.cleanse)
                        os.rename(file_path, os.path.join(self.args.dir, new) + ".mp3")
                    else:
                        old = eval('self.t.' + self.t_map[et])
                        new = re.sub(' ', u"\u0020", self._clean_using_regex(old, self.args.cleanse))
                        eval('self.t._set' + et + '(u\"' + new + '\")')
                self.t.save()

    def _get_track(self):
        for filename in os.listdir(self.args.dir):
            if filename.endswith(".mp3"):
                file_path = os.path.join(self.args.dir, filename)
                self.t.parse(file_path)
                self.t.track_num = (filename[:2], 5)
                self.t.save()

    def _set_track(self):
        for filename in os.listdir(self.args.dir):
            if filename.endswith(".mp3"):
                file_path = os.path.join(self.args.dir, filename)
                self.t.parse(file_path)
                self.t.track_num = (self.t.title[:2], 5)
                self.t.save()

    def _inv_track(self):
        for filename in os.listdir(self.args.dir):
            if filename.endswith(".mp3"):
                file_path = os.path.join(self.args.dir, filename)
                self.t.parse(file_path)
                if len(str(self.t.track_num[0])) == 1:
                    new_name = "0" + str(self.t.track_num[0]) + " " + filename
                else:
                    new_name = str(self.t.track_num[0]) + " " + filename
                new_path = os.path.join(self.args.dir, new_name)
                os.rename(file_path, new_path)

    def _new_track(self):
        i = 1
        for filename in os.listdir(self.args.dir):
            if filename.endswith(".mp3"):
                file_path = os.path.join(self.args.dir, filename)
                self.t.parse(file_path)
                self.t.track_num = (i, 5)
                self.t.save()
                if len(str(self.t.track_num[0])) == 1:
                    new_name = "0" + str(i) + " " + filename
                else:
                    new_name = str(i) + " " + filename
                new_path = os.path.join(self.args.dir, new_name)
                os.rename(file_path, new_path)
                i += 1

    def _get_title(self):
        # fails for single word titles
        for filename in os.listdir(self.args.dir):
            if filename.endswith(".mp3"):
                file_path = os.path.join(self.args.dir, filename)
                try:
                    self.t.parse(file_path)
                    new_title = re.sub(' ', u"\u0020", filename[:-4])
                    self.t._setTitle(new_title)
                    self.t.save()
                except TypeError:
                    continue

    def _parse_args(self):
        group = self.parser.add_argument_group('options')
        self.parser.add_argument('--version', action='version', version='%(prog)s 0.5.0')
        self.parser.add_argument('dir', help='Directory of the files to be formatted', type=str)
        group.add_argument('-c', '--case', help='Change the case to Title Case', action='store_true')
        group.add_argument('-nc', '--nocomments', help='Remove comments if any', action='store_true')
        group.add_argument('-tn', '--trackno', help='Get Track No from Filename', action='store_true')
        group.add_argument('-itn', '--invtrackno', help='Add Track No to Filename', action='store_true')
        group.add_argument('-cl', '--cleanse', help='Remove unwanted characters that match a pattern',
                           choices=['[*]', '(*)', '- *', '* -', ':: *', '_', '-'], type=str)
        group.add_argument('-gt', '--gettrack', help='Gets track number from Title', action='store_true')
        group.add_argument('-gtn', '--gettitle', help='Gets Title from Filename', action='store_true')
        group.add_argument('-nt', '--newtrack', help='Adds new track numbers', action='store_true')
        group.add_argument('-e', '--entity', help='What to format', required=False, action='append',
                           choices=['Title', 'Filename', 'Album', 'Artist', 'AlbumArtist', 'Genre', 'All'], type=str)
        group.add_argument('-t', '--trim', help='Trim characters to left or right', choices=['l', 'r'],
                           type=str)
        group.add_argument('-n', '--num', help='Number of character to be trimmed', type=int)
        group.add_argument('-s', '--set', help='Set any option',
                           choices=['Album', 'Artist', 'AlbumArtist', 'Genre'], type=str)
        group.add_argument('-v', '--value', nargs="*", help='Value of choice given in set', type=str)
        self.args = self.parser.parse_args()
        if self.args.entity == "All":
            self.args.entity = self.t_map.keys()


if __name__ == '__main__':
    CleanMyMusic().main()
