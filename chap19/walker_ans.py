import codecs
import html.entities
import re
import sys
from PyQt5.QtCore import (QMutex, QThread, pyqtSignal, Qt)


class Walker(QThread):
    finished = pyqtSignal(bool, int)
    indexed = pyqtSignal(str, int)

    COMMON_WORDS_THRESHOLD = 250
    MIN_WORD_LEN = 3
    MAX_WORD_LEN = 25
    INVALID_FIRST_OR_LAST = frozenset("0123456789_")
    STRIPHTML_RE = re.compile(r"<[^>]*?>", re.IGNORECASE | re.MULTILINE)
    ENTITY_RE = re.compile(r"&(\w+?);|&#(\d+?);")
    SPLIT_RE = re.compile(r"\W+", re.IGNORECASE | re.MULTILINE)

    def __init__(self, index, lock, files, filenamesForWords,
                 commonWords, parent=None):
        super(Walker, self).__init__(parent)

        self.index = index
        self.lock = lock
        self.files = files
        self.filenamesForWords = filenamesForWords
        self.commonWords = commonWords
        self.stopped = False
        self.mutex = QMutex()
        self.completed = False

    def stop(self):
        try:
            self.mutex.lock()
            self.stopped = True
        finally:
            self.mutex.unlock()

    def isStopped(self):
        try:
            self.mutex.lock()
            return self.stopped
        finally:
            self.mutex.unlock()

    def run(self):
        self.processFiles()
        self.stop()
        self.finished.emit(self.completed, self.index)

    def processFiles(self):
        def unichrFromEntity(match):
            text = match.group(match.lastindex)
            if text.isdigit():
                return chr(int(text))
            u = html.entities.name2codepoint.get(text)
            return chr(u) if u is not None else ""

        for fname in self.files:
            if self.isStopped():
                return
            words = set()
            fh = None
            try:
                fh = codecs.open(fname, "r", "UTF8", "ignore")
                text = fh.read()
            except EnvironmentError as e:
                sys.stderr.write("Error: {0}\n".format(e))
                continue
            finally:
                if fh is not None:
                    fh.close()
            if self.isStopped():
                return
            text = self.STRIPHTML_RE.sub("", text)
            text = self.ENTITY_RE.sub(unichrFromEntity, text)
            text = text.lower()
            for word in self.SPLIT_RE.split(text):
                if (self.MIN_WORD_LEN <= len(word) <= self.MAX_WORD_LEN
                    and word[0] not in self.INVALID_FIRST_OR_LAST
                    and word[-1] not in self.INVALID_FIRST_OR_LAST):
                    try:
                        self.lock.lockForRead()
                        new = word not in self.commonWords
                    finally:
                        self.lock.unlock()
                    if new:
                        words.add(word)
            if self.isStopped():
                return
            for word in words:
                try:
                    self.lock.lockForWrite()
                    files = self.filenamesForWords[word]
                    if len(files) > self.COMMON_WORDS_THRESHOLD:
                        del self.filenamesForWords[word]
                        self.commonWords.add(word)
                    else:
                        files.add(str(fname))
                finally:
                    self.lock.unlock()
            self.indexed.emit(fname, self.index)
        self.completed = True
