
import logging
import os
import shutil
import time
import threading
from pathlib import Path
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class SkillMover:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SkillMover, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "initialized"):
            return
        self.dirPairs      = []  # list of (src, dst)
        self.storageUnit   = "days"
        self.storageValue  = 7
        self.checkInterval = 10
        self.noMoveLimit   = 3
        self.initialized   = True

    # ------------------------------
    # Configuration
    # ------------------------------

    # def setMoveDirs(self, *pairs, chain=None):
    #     """
    #     Configure directory pairs for file moving operations.

    #     Args:
    #         *pairs: Tuples of (sourceDir, destinationDir).
    #         chain (list, optional): List of directories to link in sequence.
    #                                 Example: ["skills", "dynamic", "static"]
    #                                 becomes pairs: (skills -> dynamic), (dynamic -> static).
    #     """
    #     dirPairs = []

    #     # handle explicit pairs
    #     for p in pairs:
    #         if p and all(p):
    #             dirPairs.append(p)

    #     # handle chain definition
    #     if chain and len(chain) > 1:
    #         for i in range(len(chain) - 1):
    #             if chain[i] and chain[i + 1]:
    #                 dirPairs.append((chain[i], chain[i + 1]))

    #     self.dirPairs = dirPairs
    def setMoveDirs(self, *pairs, chain=None, **extraChains):
        dirPairs = []

        for p in pairs:
            if p and all(p):
                dirPairs.append(p)

        # handle main chain
        if chain and len(chain) > 1:
            for i in range(len(chain) - 1):
                dirPairs.append((chain[i], chain[i+1]))

        # handle extra chains
        for ch in extraChains.values():
            if ch and len(ch) > 1:
                for i in range(len(ch) - 1):
                    dirPairs.append((ch[i], ch[i+1]))

        #self.dirPairs = dirPairs
        self.dirPairs.extend(dirPairs)



    def setMoveSettings(self, storageUnit="days", storageValue=7,
                        checkInterval=10, noMoveLimit=3):
        self.storageUnit   = storageUnit
        self.storageValue  = storageValue
        self.checkInterval = checkInterval
        self.noMoveLimit   = noMoveLimit

    # ------------------------------
    # Public Methods
    # ------------------------------

    def manualMove(self, sourceDir, destinationDir, minAge=None):
        """
        Immediately move eligible files from sourceDir to destinationDir.
        """
        filesMoved = 0
        movedFiles = set()
        now = datetime.now()
        for root, _, files in os.walk(sourceDir, topdown=False):
            for file in files:
                try:
                    filePath = self._getDir(root, file)
                    if filePath in movedFiles:
                        continue
                    if minAge:
                        fileAge = now - datetime.fromtimestamp(os.path.getmtime(filePath))
                        if fileAge < minAge:
                            continue
                    relPath = os.path.relpath(root, sourceDir)
                    targetDir = self._getDir(destinationDir, relPath)
                    os.makedirs(targetDir, exist_ok=True)
                    newPath = self._getDir(targetDir, file)
                    shutil.move(filePath, newPath)
                    os.utime(newPath, None)
                    filesMoved += 1
                    movedFiles.add(filePath)
                except Exception as e:
                    #print(f"Error moving file {file}: {e}")
                    logger.error(f"Error moving file {file}: {e}", exc_info=True)
        return filesMoved

    def autoMove(self):
        """
        Start all monitor threads for file moves.
        """
        self._validate()
        self._startMoving()

    # ------------------------------
    # Internal Helpers
    # ------------------------------

    def _validate(self):
        if not self.dirPairs:
            raise ValueError("At least one valid directory pair must be set via setMoveDirs() before starting.")
        if None in (self.storageUnit, self.storageValue, self.checkInterval, self.noMoveLimit):
            raise ValueError("All settings must be set via setMoveSettings() before starting.")

    def _startMoving(self):
        for src, dst in self.dirPairs:
            threading.Thread(
                target=self._monitorMove,
                args=(src, dst, self.storageUnit, self.storageValue),
                daemon=True
            ).start()

    def _getDir(self, *paths):
        return str(Path(*paths).resolve())

    def _getTimedelta(self, unit, value):
        return timedelta(**{unit: value})

    def _monitorMove(self, sourceDir, destinationDir, unit, value):
        noMoveCount = 0
        expireDelta = self._getTimedelta(unit, value)
        while True:
            filesMoved = self._checkAndMoveFiles(sourceDir, destinationDir, expireDelta)
            noMoveCount = noMoveCount + 1 if filesMoved == 0 else 0
            if noMoveCount >= self.noMoveLimit:
                break
            time.sleep(self.checkInterval)

    def _checkAndMoveFiles(self, sourceDir, destinationDir, expireDelta):
        filesMoved = 0
        movedFiles = set()
        for root, _, files in os.walk(sourceDir, topdown=False):
            for file in files:
                try:
                    filePath = self._getDir(root, file)
                    if filePath in movedFiles:
                        continue
                    if datetime.now() - datetime.fromtimestamp(os.path.getmtime(filePath)) < expireDelta:
                        continue
                    relPath = os.path.relpath(root, sourceDir)
                    targetDir = self._getDir(destinationDir, relPath)
                    os.makedirs(targetDir, exist_ok=True)
                    newPath = self._getDir(targetDir, file)
                    shutil.move(filePath, newPath)
                    os.utime(newPath, None)
                    filesMoved += 1
                    movedFiles.add(filePath)
                except Exception as e:
                    #print(f"Error moving file {file}: {e}")
                    logger.error(f"Error moving file {file}: {e}", exc_info=True)
        return filesMoved






# import os
# import shutil
# import time
# import threading
# from pathlib import Path
# from datetime import datetime, timedelta

# class SkillMover:
#     _instance = None

#     def __new__(cls, *args, **kwargs):
#         if not cls._instance:
#             cls._instance = super(SkillMover, cls).__new__(cls)
#         return cls._instance

#     def __init__(self):
#         if hasattr(self, "initialized"):
#             return
#         self._initComponents()
#         self.initialized = True

#     def _initComponents(self):
#         self.primarySkillDir     = None
#         self.primaryDynamicDir   = None
#         self.primaryStaticDir    = None
#         self.secondarySkillDir   = None
#         self.secondaryDynamicDir = None
#         self.secondaryStaticDir  = None

#         self.storageUnit   = None
#         self.storageValue  = None
#         self.checkInterval = None
#         self.noMoveLimit   = None

#     def setMoveDirs(self, primarySkillDir=None, primaryDynamicDir=None, primaryStaticDir=None,
#                     secondarySkillDir=None, secondaryDynamicDir=None, secondaryStaticDir=None):
#         """
#         Configure directory pairs for file moving operations.
#         Only the pairs you want to use need to be set (both source and destination).
#         """
#         self.primarySkillDir     = primarySkillDir
#         self.primaryDynamicDir   = primaryDynamicDir
#         self.primaryStaticDir    = primaryStaticDir
#         self.secondarySkillDir   = secondarySkillDir
#         self.secondaryDynamicDir = secondaryDynamicDir
#         self.secondaryStaticDir  = secondaryStaticDir


#     def setMoveSettings(self, storageUnit="days", storageValue=7, 
#                         checkInterval=10, noMoveLimit=3):
#         """
#         Set storage/move timing and check parameters.
#         """
#         self.storageUnit   = storageUnit
#         self.storageValue  = storageValue
#         self.checkInterval = checkInterval
#         self.noMoveLimit   = noMoveLimit

#     def manualMove(self, sourceDir, destinationDir, minAge=None):
#         """
#         Immediately move eligible files from sourceDir to destinationDir.
        
#         Args:
#             sourceDir (str): Directory to move files from.
#             destinationDir (str): Directory to move files to.
#             minAge (timedelta, optional): Only move files older than this age.
#                                           If None, move all files.
#         Returns:
#             int: Number of files moved.
#         """
#         filesMoved = 0
#         movedFiles = set()
#         now = datetime.now()
#         for root, _, files in os.walk(sourceDir, topdown=False):
#             for file in files:
#                 try:
#                     filePath = self._getDir(root, file)
#                     if filePath in movedFiles:
#                         continue
#                     if minAge:
#                         fileAge = now - datetime.fromtimestamp(os.path.getmtime(filePath))
#                         if fileAge < minAge:
#                             continue
#                     relPath = os.path.relpath(root, sourceDir)
#                     targetDir = self._getDir(destinationDir, relPath)
#                     os.makedirs(targetDir, exist_ok=True)
#                     newPath = self._getDir(targetDir, file)
#                     shutil.move(filePath, newPath)
#                     os.utime(newPath, None)
#                     filesMoved += 1
#                     movedFiles.add(filePath)
#                 except Exception as e:
#                     print(f"Error moving file {file}: {e}")
#         return filesMoved


#     def autoMove(self):
#         """
#         Start all monitor threads for file moves.
#         """
#         self._validate()
#         self._startMoving()

#     def _validate(self):
#         dirPairs = [
#             (self.primarySkillDir, self.primaryDynamicDir),
#             (self.primaryDynamicDir, self.primaryStaticDir),
#             (self.secondarySkillDir, self.secondaryDynamicDir),
#             (self.secondaryDynamicDir, self.secondaryStaticDir),
#         ]
#         # At least one valid pair must be set (both not None)
#         if not any(a and b for a, b in dirPairs):
#             raise ValueError("At least one valid directory pair must be set via setMoveDirs() before starting.")
#         if None in (self.storageUnit, self.storageValue, self.checkInterval, self.noMoveLimit):
#             raise ValueError("All settings must be set via setMoveSettings() before starting.")

#     def _startMoving(self):
#         pairs = [
#             (self.primarySkillDir, self.primaryDynamicDir),
#             (self.primaryDynamicDir, self.primaryStaticDir),
#             (self.secondarySkillDir, self.secondaryDynamicDir),
#             (self.secondaryDynamicDir, self.secondaryStaticDir),
#         ]
#         for src, dst in pairs:
#             if src and dst:
#                 threading.Thread(target=self._monitorMove, args=(src, dst, self.storageUnit, self.storageValue), daemon=True).start()

#     def _getDir(self, *paths):
#         return str(Path(*paths).resolve())

#     def _getTimedelta(self, unit, value):
#         return timedelta(**{unit: value})

#     def _monitorMove(self, sourceDir, destinationDir, unit, value):
#         noMoveCount = 0
#         expireDelta = self._getTimedelta(unit, value)
#         while True:
#             filesMoved = self._checkAndMoveFiles(sourceDir, destinationDir, expireDelta)
#             noMoveCount = noMoveCount + 1 if filesMoved == 0 else 0
#             if noMoveCount >= self.noMoveLimit:
#                 break
#             time.sleep(self.checkInterval)

#     def _checkAndMoveFiles(self, sourceDir, destinationDir, expireDelta):
#         filesMoved = 0
#         movedFiles = set()
#         for root, _, files in os.walk(sourceDir, topdown=False):
#             for file in files:
#                 try:
#                     filePath = self._getDir(root, file)
#                     if filePath in movedFiles:
#                         continue
#                     if datetime.now() - datetime.fromtimestamp(os.path.getmtime(filePath)) < expireDelta:
#                         continue
#                     relPath = os.path.relpath(root, sourceDir)
#                     targetDir = self._getDir(destinationDir, relPath)
#                     os.makedirs(targetDir, exist_ok=True)
#                     newPath = self._getDir(targetDir, file)
#                     shutil.move(filePath, newPath)
#                     os.utime(newPath, None)
#                     filesMoved += 1
#                     movedFiles.add(filePath)
#                 except Exception as e:
#                     print(f"Error moving file {file}: {e}")
#         return filesMoved
