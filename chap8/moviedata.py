import bisect
import codecs
import copyreg
import pickle
import gzip
from PyQt5.QtCore import *
from PyQt5.QtXml import *

CODEC = "UTF-8"
NEWPARA = "\r"
NEWLINE = "\n"


class Movie(object):
    UNKNOWNYEAR = 1800
    UNKNOWNMINUTES = 0

    def __init__(self, title=None, year=UNKNOWNYEAR, minutes=UNKNOWNMINUTES, acquired=None, notes=None):
        self.title = title
        self.year = year
        self.minutes = minutes
        self.acquired = acquired if acquired is not None else QDate.currentDate()
        self.notes = notes


class MovieContainer(object):
    MAGIC_NUMBER = 0x3051E
    FILE_VERSION = 100

    def __init__(self):
        self.__fname = ""
        self.__movies = []
        self.__movieFromId = {}
        self.__dirty = False

    def __iter__(self):
        for pair in iter(self.__movies):
            yield pair[1]

    def __len__(self):
        return len(self.__movies)

    def clear(self, clearFilename=True):
        self.__movies = []
        self.__movieFromId = {}
        if clearFilename:
            self.__fname = ""
        self.__dirty = False

    def add(self, movie):
        if id(movie) in self.__movieFromId:
            return False
        key = self.key(movie.title, movie.year)
        bisect.insort_left(self.__movies, [key, movie])
        self.__movieFromId[id(movie)] = movie
        self.__dirty = True
        return True

    def key(self, title, year):
        text = title.lower()
        if text.startswith("a "):
            text = text[2:]
        elif text.startswith("an "):
            text = text[3:]
        elif text.startswith("the "):
            text = text[4:]
        parts = text.split(" ", 1)
        if parts[0].isdigit():
            text = "%08d " % int(parts[0])
            if len(parts) > 1:
                text += parts[1]
        return "%s\t%d" % (text.replace(" ", ""), year)

    def delete(self,movie):
        if id(movie) not in self.__movieFromId:
            return False
        key = self.key(movie.title,movie.year)
        i = bisect.bisect_left(self.__movies,[key,movie])
        del self.__movies[i]
        del self.__movieFromId[id(movie)]
        self.__dirty=True
        return True

    def updateMovie(self,movie,title,year,minutes=None,notes=None):
        if minutes is not None:
            movie.minutes=minutes
        if notes is not None:
            movie.notes=notes
        if title !=movie.title or year !=movie.year:
            key = self.key(movie.title,movie.year)
            i = bisect.bisect_left(self.__movies,[key,movie])
            self.__movies[i][0]=self.key(title,year)
            movie.title = title
            movie.year = year
            self.__movies.sort()
        self.__dirty=True

    @staticmethod
    def formats():
        return "*.mqd *.mpd *.mqt *.mpt"

    def save(self,fname=""):
        if not fname.strip() == "":
            self.__fname=fname
        if self.__fname.endswith(".mqd"):
            return self.saveQDataStream()
        elif self.__fname.endswith(".mpd"):
            return self.savePickle()
        elif self.__fname.endswith(".mqt"):
            return self.saveQTextStream()
        elif self.__fname.endswith(".mpt"):
            return self.saveText()
        return False, "Failed to save: invalid file extension"

    def load(self, fname=""):
        if not fname.strip() == "":
            self.__fname = fname
        if self.__fname.endswith(".mqb"):
            return self.loadQDataStream()
        elif self.__fname.endswith(".mpb"):
            return self.loadPickle()
        elif self.__fname.endswith(".mqt"):
            return self.loadQTextStream()
        elif self.__fname.endswith(".mpt"):
            return self.loadText()
        return False, "Failed to load: invalid file extension"