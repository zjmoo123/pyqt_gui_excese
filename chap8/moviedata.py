import bisect
import codecs
import copyreg
import pickle
import gzip
from PyQt5.QtCore import *
from PyQt5.QtXml import *
from PyQt5.QtXmlPatterns import *

CODEC = "UTF-8"
NEWPARA = chr(0x2029)
NEWLINE = chr(0x2028)


def encodedNewlines(text):
    return text.replace("\n\n", NEWPARA).replace("\n", NEWLINE)


def decodedNewlines(text):
    return text.replace(NEWPARA, "\n\n").replace(NEWLINE, "\n")


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

    def delete(self, movie):
        if id(movie) not in self.__movieFromId:
            return False
        key = self.key(movie.title, movie.year)
        i = bisect.bisect_left(self.__movies, [key, movie])
        del self.__movies[i]
        del self.__movieFromId[id(movie)]
        self.__dirty = True
        return True

    def updateMovie(self, movie, title, year, minutes=None, notes=None):
        if minutes is not None:
            movie.minutes = minutes
        if notes is not None:
            movie.notes = notes
        if title != movie.title or year != movie.year:
            key = self.key(movie.title, movie.year)
            i = bisect.bisect_left(self.__movies, [key, movie])
            self.__movies[i][0] = self.key(title, year)
            movie.title = title
            movie.year = year
            self.__movies.sort()
        self.__dirty = True

    @staticmethod
    def formats():
        return "*.mqd *.mpd *.mqt *.mpt"

    def save(self, fname=""):
        if not fname.strip() == "":
            self.__fname = fname
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

    def saveQDataStream(self):
        error = None
        fn = None
        try:
            fh = QFile(self.__fname)
            if not fh.open(QIODevice.WriteOnly):
                raise IOError(fh.errorString())
            stream = QDataStream(fh)
            stream.writeInt32(MovieContainer.MAGIC_NUMBER)
            stream.writeInt32(MovieContainer.FILE_VERSION)
            stream.setVersion(QDataStream.Qt_5_8)
            for key, movie in self.__movies:
                stream << movie.title
                stream.writeInt16(movie.year)
                stream.writeInt16(movie.minutes)
                stream << movie.acquired << movie.notes
        except (IOError, OSError) as e:
            error = "Failed to save:%s" % e
        finally:
            if fh is not None:
                fh.close()
            if error is not None:
                return False, error
            self.__dirty = False
            return True, "Saved %d movie records to %s" % (len(self.__movies), QFileInfo(self.__fname).fileName())

    def loadQDataStream(self):
        error = None
        fh = None
        try:
            fh = QFile(self.__fname)
            if not fh.open(QIODevice.ReadOnly):
                raise IOError(fh.errorString())
            stream = QDataStream(fh)
            magic = stream.readInt32()
            if magic != MovieContainer.MAGIC_NUMBER:
                raise IOError("unrecognized file type")
            version = stream.readInt32()
            if version < MovieContainer.FILE_VERSION:
                raise IOError("old and unreadable file format")
            elif version > MovieContainer.FILE_VERSION:
                raise IOError("new and unreadable file format")
            stream.setVersion(QDataStream.Qt_5_8)
            self.clear(False)
            while not stream.atEnd():
                title = ""
                acquired = QDate()
                notes = ""
                stream >> title
                year = stream.readInt16()
                minutes = stream.readInt16()
                stream >> acquired >> notes
                self.add(Movie(title, year, minutes, acquired, notes))
        except (IOError, OSError) as e:
            error = "Failed to load: %s" % e
        finally:
            if fh is not None:
                fh.close()
            if error is not None:
                return False, error
            self.__dirty = False
            return True, "Loaded %d movie records from %s" % (len(self.__movies), QFileInfo(self.__fname).fileName())

    def savePickle(self):
        error = None
        fh = None
        try:
            fh = gzip.open(self.__fname, "wb")
            pickle.dump(self.__movies, fh, 2)
        except (IOError, OSError) as e:
            error = "Failed to save: %s" % e
        finally:
            if fh is not None:
                fh.close()
            if error is not None:
                return False, error
            self.__dirty = False
            return True, "Saved %d movie records to %s" % (len(self.__movies), QFileInfo(self.__fname).fileName())

    def loadPickle(self):
        error = None
        fh = None
        try:
            fh = gzip.open(self.__fname, "rb")
            self.clear(False)
            self.__movies = pickle.load(fh)
            for key, movie in self.__movies:
                self.__movieFromId[id(movie)] = movie
        except (IOError, OSError) as e:
            error = "Failed to load: %s" % e
        finally:
            if fh is not None:
                fh.close()
            if error is not None:
                return False, error
            self.__dirty = False
            return True, "Loaded %d movie records from %s" % (len(self.__movies), QFileInfo(self.__fname).fileName())

    def saveQTextStream(self):
        error = None
        fh = None
        try:
            fh = QFile(self.__fname)
            if not fh.open(QIODevice.WriteOnly):
                raise IOError(fh.errorString())
            stream = QTextStream(fh)
            stream.setCodec(CODEC)
            for key, movie in self.__movies:
                stream << "{{MOVIE}}" << " " << movie.title << "\n" << movie.year << " " << movie.minutes << " " << movie.acquired.toString(
                    Qt.ISODate) << "\n{NOTES}"
                if not movie.notes.strip() == "":
                    stream << "\n" << movie.notes
                stream << "\n{{ENDMOVIE}}\n"
        except (IOError, OSError) as e:
            error = "Failed to load: %s" % e
        finally:
            if fh is not None:
                fh.close()
            if error is not None:
                return False, error
            self.__dirty = False
            return True, "Loaded %d movie records from %s" % (len(self.__movies), QFileInfo(self.__fname).fileName())

    def loadQTextStream(self):
        error = None
        fh = None
        try:
            fh = QFile(self.__fname)
            if not fh.open(QIODevice.ReadOnly):
                raise IOError(fh.errorString())
            stream = QTextStream(fh)
            stream.setCodec(CODEC)
            self.clear(False)
            lino = 0
            while not stream.atEnd():
                title = year = minutes = acquired = notes = None
                line = stream.readLine()
                lino += 1
                if not line.startswith("{{MOVIE}}"):
                    raise ValueError("no movie record found")
                else:
                    title = line[len("{{MOVIE}}"):].strip()
                if stream.atEnd():
                    raise ValueError("premature end of file")
                line = stream.readLine()
                lino += 1
                parts = line.split(" ")
                if parts.count() != 3:
                    raise ValueError("invalid numeric data")
                year = int(parts[0])
                minutes = int(parts[1])
                ymd = parts[2].split("-")
                if ymd.count() != 3:
                    raise ValueError("invalid acquired date")
                acquired = QDate(int(ymd[0]),
                                 int(ymd[1]),
                                 int(ymd[2]))
                if stream.atEnd():
                    raise ValueError("premature end of file")
                line = stream.readLine()
                lino += 1
                if line != "{NOTES}":
                    raise ValueError("notes expected")
                notes = ""
                while not stream.atEnd():
                    line = stream.readLine()
                    lino += 1
                    if line == "{{ENDMOVIE}}":
                        if title is None or year is None or minutes is None or acquired is None or notes is None:
                            raise ValueError("incomplete record")
                        self.add(Movie(title, year, minutes, acquired, notes.strip()))
                        break
                    else:
                        notes += line + "\n"
                else:
                    raise ValueError("missing endmovie marker")
        except (IOError, OSError, ValueError) as e:
            error = "Failed to load: {0} on line {1}".format(e, lino)
        finally:
            if fh is not None:
                fh.close()
            if error is not None:
                return False, error
            self.__dirty = False
            return True, "Loaded {0} movie records from {1}".format(
                len(self.__movies),
                QFileInfo(self.__fname).fileName())

    def saveText(self):
        error = None
        fh = None
        try:
            fh = codecs.open(self.__fname, "w", CODEC)
            for key, movie in self.__movies:
                fh.write("{{MOVIE}} %s\n" % movie.title)
                fh.write("{NOTES}")
                if not movie.notes.strip() == "":
                    fh.write("\n&s" % movie.notes)
                fh.write("\n{{ENDMOVIE}}\n")
        except (IOError, OSError) as e:
            error = "Failed to save: {0}".format(e)
        finally:
            if fh is not None:
                fh.close()
            if error is not None:
                return False, error
            self.__dirty = False
            return True, "Saved {0} movie records to {1}".format(
                len(self.__movies),
                QFileInfo(self.__fname).fileName())

    def loadText(self):
        error = None
        fh = None
        try:
            fh = codecs.open(self.__fname, "rU", CODEC)
            self.clear(False)
            lino = 0
            while True:
                title = year = minutes = acquired = notes = None
                line = fh.readline()
                if not line:
                    break
                lino += 1
                if not line.startswith("{{MOVIE}}"):
                    raise ValueError("no movie record found")
                else:
                    title = line[len("{{MOVIE}}"):].strip()
                line = fh.readline()
                if not line:
                    raise ValueError("premature end of file")
                lino += 1
                parts = line.split(" ")
                if len(parts) != 3:
                    raise ValueError("invalid numeric data")
                year = int(parts[0])
                minutes = int(parts[1])
                ymd = parts[2].split("-")
                if len(ymd) != 3:
                    raise ValueError("invalid acquired date")
                acquired = QDate(int(ymd[0]), int(ymd[1]),
                                 int(ymd[2]))
                line = fh.readline()
                if not line:
                    raise ValueError("premature end of file")
                lino += 1
                if line != "{NOTES}\n":
                    raise ValueError("notes expected")
                notes = ""
                while True:
                    line = fh.readline()
                    if not line:
                        raise ValueError("missing endmovie marker")
                    lino += 1
                    if line == "{{ENDMOVIE}}\n":
                        if (title is None or year is None or
                                    minutes is None or acquired is None or
                                    notes is None):
                            raise ValueError("incomplete record")
                        self.add(Movie(title, year, minutes,
                                       acquired, notes.strip()))
                        break
                    else:
                        notes += line

        except (IOError, OSError, ValueError) as e:
            error = "Failed to load: {0} on line {1}".format(e, lino)
        finally:
            if fh is not None:
                fh.close()
            if error is not None:
                return False, error
            self.__dirty = False
            return True, "Loaded {0} movie records from {1}".format(
                len(self.__movies),
                QFileInfo(self.__fname).fileName())

    def exportXml(self, fname):
        error = None
        fh = None
        try:
            fh = QFile(fname)
            if not fh.open(QIODevice.WriteOnly):
                raise IOError(fh.errorString())
            stream = QTextStream(fh)
            stream.setCodec(CODEC)
            stream << ("<?xml version='1.0' encoding='{0}'?>\n"
                       "<!DOCTYPE MOVIES>\n"
                       "<MOVIES VERSION='1.0'>\n".format(CODEC))
            for key, movie in self.__movies:
                stream << ("<MOVIE YEAR='{0}' MINUTES='{1}' "
                           "ACQUIRED='{2}'>\n".format(movie.year,
                                                      movie.minutes,
                                                      movie.acquired.toString(Qt.ISODate))) \
                << "<TITLE>" << movie.title \
                << "</TITLE>\n<NOTES>"
                if not movie.notes.strip() == "":
                    stream << "\n" << encodedNewlines(movie.notes)
                stream << "\n</NOTES>\n</MOVIE>\n"
            stream << "</MOVIES>\n"
        except (IOError, OSError) as e:
            error = "Failed to export: {0}".format(e)
        finally:
            if fh is not None:
                fh.close()
            if error is not None:
                return False, error
            self.__dirty = False
            return True, "Exported {0} movie records to {1}".format(
                len(self.__movies),
                QFileInfo(fname).fileName())

    def importDom(self, fname):
        dom = QDomDocument()
        error = None
        fh = None
        try:
            fh = QFile(fname)
            if not fh.open(QIODevice.ReadOnly):
                raise IOError(fh.errorString())
            if not dom.setContent(fh):
                raise ValueError("could not parse XML")
        except (IOError, OSError, ValueError) as e:
            error = "Failed to import: %s" % e
        finally:
            if fh is not None:
                fh.close()
            if error is not None:
                return False, error
        try:
            self.populateFromDOM(dom)
        except ValueError as e:
            return False, "Failed to import:%s" % e
        self.__fname = ""
        self.__dirty = True
        return True, "Imported {0} movie records from {1}".format(
            len(self.__movies), QFileInfo(fname).fileName())

    def populateFromDOM(self, dom):
        root = dom.documentElement()
        if root.tagName() != "MOVIES":
            raise ValueError("not a Movies XML file")
        self.clear(False)
        node = root.firstChild()
        while not node.isNull():
            if node.toElement().tagName() == "MOVIE":
                self.readMovieNode(node.toElement())
            node = node.nextSibling()

    def readMovieNode(self, element):
        def getText(node):
            child = node.firstChild()
            text = ""
            while not child.isNull():
                if child.nodeType() == QDomNode.TextNode:
                    text += child.toText().data()
                child = child.nextSibling()
            return text.strip()

        year = int(element.attribute("YEAR"))
        minutes = int(element.attribute("MINUTES"))
        ymd = element.attribute("ACQUIRED").split("-")
        if ymd.count() != 3:
            raise ValueError("invalid acquired date %s" % element.attribute("ACQUIRED"))
        acquired = QDate(int(ymd[0]), int(ymd[1]), int(ymd[2]))
        title = notes = None
        node = element.firstChild()
        while title is None or notes is None:
            if node.isNull():
                raise ValueError("missing title or notes")
            if node.toElement().tagName() == "TITLE":
                title = getText(node)
            elif node.toElement().tagName() == "NOTES":
                notes = getText(node)
            node = node.nextSibling()
        if title.strip() == "":
            raise ValueError("missing title")
        self.add(Movie(title, year, minutes, acquired, decodedNewlines(notes)))

    def importSAX(self, fname):
        error = None
        fh = None
        try:
            handler = SaxMovieHandler(self)
            parser = QXmlSimpleReader()
            parser.setContentHandler(handler)
            parser.setErrorHandler(handler)
            fh = QFile(fname)
            input = QXmlInputSource(fh)
            self.clear(False)
            if not parser.parse(input):
                raise ValueError(handler.error)
        except (IOError, OSError, ValueError) as e:
            error = "Failed to import: %s" % e
        finally:
            if fh is not None:
                fh.close()
            if error is not None:
                return False, error
            self.__fname = ""
            self.__dirty = True
            return True, "Imported %d movie records from %s" % (len(self.__movies), QFileInfo(fname).fileName())


class SaxMovieHandler(QXmlDefaultHandler):
    def __init__(self, movies):
        super(SaxMovieHandler, self).__init__()
        self.movies = movies
        self.text = ""
        self.error = None

    def clear(self):
        self.year = None
        self.minutes = None
        self.acquired = None
        self.title = None
        self.notes = None

    def startElement(self, p_str, p_str_1, p_str_2, QXmlAttributes):
        if p_str_2 == "MOVIE":
            self.clear()
            self.year = int(QXmlAttributes.value("YEAR"))
            self.minutes = int(QXmlAttributes.value("MINUTES"))
            ymd = QXmlAttributes.value("ACQUIRED").split("-")
            if ymd.count() != 3:
                raise ValueError("invalid acquired date %s" % QXmlAttributes.value("ACQUIRED"))
            self.acquired = QDate(int(ymd[0]), int(ymd[1]), int(ymd[2]))
        elif p_str_2 in ("TITLE", "NOTES"):
            self.text = ""
        return True

    def characters(self, p_str):
        self.text += p_str
        return True

    def endElement(self, p_str, p_str_1, p_str_2):
        if p_str_2 == "MOVIE":
            if (self.year is None or self.minutes is None or
                        self.acquired is None or self.title is None or
                        self.notes is None or self.title.strip() == ""):
                raise ValueError("incomplete movie record")
            self.movies.add(Movie(self.title, self.year, self.minutes, self.acquired, decodedNewlines(self.notes)))
            self.clear()
        elif p_str_2 == "TITLE":
            self.title = self.text.strip()
        elif p_str_2 == "NOTES":
            self.notes = self.text.strip()
        return True

    def fatalError(self, QXmlParseException):
        self.error = "parse error at line %d column %d: %s" % (
        QXmlParseException.lineNumber(), QXmlParseException.columnNumber(), QXmlParseException.message())
        return False
