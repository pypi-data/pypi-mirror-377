import gzip
import logging
import os
import platform
import shutil
import sys
import time
import warnings
from logging.handlers import SysLogHandler
from pathlib import Path
from typing import Optional

from cryptography.utils import CryptographyDeprecationWarning
from twisted.internet import reactor
from twisted.internet import threads

warnings.filterwarnings("ignore", category=CryptographyDeprecationWarning)

LOG_FORMAT = "%(asctime)s %(levelname)s #%(name)s:%(message)s"
DATE_FORMAT = "%d-%b-%Y %H:%M:%S"


def _makeFormat(childIdentifier: str | None):
    if childIdentifier:
        return LOG_FORMAT.replace("#", childIdentifier + " ")
    else:
        return LOG_FORMAT.replace("#", "")


logger = logging.getLogger(__name__)


class PeekLogRotatingFileHandler(logging.FileHandler):
    SIZE_CHECK_INTERVAL = 60  # Only check file size once per minute

    def __init__(
        self,
        filename,
        daysToKeep,
        rotateAfterMb,
        minFreeSpacePercent,
        minFreeSpaceGB,
    ):
        super().__init__(filename)
        self._daysToKeep = daysToKeep
        self._maxBytes = rotateAfterMb * 1024 * 1024
        self._minFreeSpacePercent = minFreeSpacePercent
        self._minFreeSpaceGB = minFreeSpaceGB * 1024 * 1024 * 1024
        self._isRollingOver = False
        self._lastMidnightRotation = 0
        self._currentDay = time.strftime("%Y-%m-%d")
        self._lastSizeCheck = 0

    def shouldRollover(self, record):
        if self._isRollingOver:
            return False

        currentDay = time.strftime("%Y-%m-%d")

        # Check time-based rollover (midnight) - only once per day
        if currentDay != self._currentDay:
            self._currentDay = currentDay
            return True

        # Check size-based rollover - rate limited to once per minute
        currentTime = time.time()
        if currentTime - self._lastSizeCheck < self.SIZE_CHECK_INTERVAL:
            return False

        self._lastSizeCheck = currentTime

        if self.stream is None:
            self.stream = self._open()

        if self._maxBytes > 0:
            msg = "%s\n" % self.format(record)
            self.stream.seek(0, 2)
            if self.stream.tell() + len(msg.encode("utf-8")) >= self._maxBytes:
                return True

        return False

    def doRollover(self):
        if self._isRollingOver:
            return

        # Get current time for rotation
        currentTime = time.time()

        # Generate rotated filename with YYYY-MM-DD_HH-MM-SS format
        timeStr = time.strftime(
            "%Y-%m-%d_%H-%M-%S", time.localtime(currentTime)
        )
        rotatedName = "%s.%s" % (self.baseFilename, timeStr)
        compressedName = rotatedName + ".gz"

        if Path(rotatedName).exists() or Path(compressedName).exists():
            return

        self._isRollingOver = True
        try:
            # Lock the current log file during rotation
            if self.stream:
                try:
                    self.stream.close()
                finally:
                    self.stream = None

            # Use copy-and-truncate method for multiprocess safety with file locking
            if os.path.exists(self.baseFilename):
                # Copy the file
                shutil.copy2(self.baseFilename, rotatedName)

                # Truncate the original file
                with open(self.baseFilename, "w"):
                    pass

                # Compress and cleanup in background thread
                threads.deferToThread(
                    self._compressAndCleanup, rotatedName, compressedName
                )

            # Open new stream
            self.stream = self._open()

            # Prune old files based on disk space and backup count
            self._pruneOldFiles()

        finally:
            self._isRollingOver = False

    def _compressAndCleanup(self, rotatedName, compressedName):
        if not Path(rotatedName).exists():
            return

        # Compress the rotated file
        READ_CHUNK = 512 * 1024
        with open(rotatedName, "rb") as sf:
            with gzip.open(compressedName, "wb") as f:
                while True:
                    data = sf.read(READ_CHUNK)
                    if not data:
                        break
                    f.write(data)

        # Remove uncompressed rotated file
        if os.path.exists(rotatedName):
            os.remove(rotatedName)

        rootLogger = logging.getLogger()
        reactor.callLater(
            0,
            rootLogger.info,
            f"Finished rotate and compress to: {compressedName}",
        )

    def _getDiskSpace(self):
        statvfs = os.statvfs(os.path.dirname(self.baseFilename))
        freeBytes = statvfs.f_bavail * statvfs.f_frsize
        totalBytes = statvfs.f_blocks * statvfs.f_frsize
        freePercent = (freeBytes / totalBytes) * 100
        return freeBytes, freePercent

    def _getLogFiles(self):
        # Get all compressed log files for this service
        logDir = os.path.dirname(self.baseFilename)
        baseName = os.path.basename(self.baseFilename)

        logFiles = []
        for file in os.listdir(logDir):
            if (
                file.startswith(baseName + ".")
                and file.endswith(".gz")
                and len(file) > len(baseName) + 4
            ):  # baseName + "." + timestamp + ".gz"
                fullPath = os.path.join(logDir, file)
                mtime = os.path.getmtime(fullPath)
                size = os.path.getsize(fullPath)
                logFiles.append((fullPath, mtime, size))

        # Sort by modification time (oldest first)
        logFiles.sort(key=lambda x: x[1])
        return logFiles

    def _pruneOldFiles(self):
        freeBytes, freePercent = self._getDiskSpace()
        logFiles = self._getLogFiles()

        rootLogger = logging.getLogger()

        # Maintain all files for at least 1 day (24 hours)
        oneDaySeconds = 24 * 60 * 60
        currentTime = time.time()

        # Filter files that are older than 1 day and eligible for removal
        eligibleFiles = []
        for filePath, mtime, size in logFiles:
            if currentTime - mtime >= oneDaySeconds:
                eligibleFiles.append((filePath, mtime, size))

        # If no files are eligible for removal, return early
        if not eligibleFiles:
            return

        # Check if we need to prune due to disk space
        needsPruning = (
            freePercent < self._minFreeSpacePercent
            or freeBytes < self._minFreeSpaceGB
        )

        filesToRemove = []

        if needsPruning:
            # Prune eligible files to meet disk space requirements, starting from oldest
            for filePath, mtime, size in eligibleFiles:
                filesToRemove.append((filePath, size))

                # Check if removing these files would satisfy disk space requirements
                totalSizeToFree = sum(size for _, size in filesToRemove)
                projectedFreeBytes = freeBytes + totalSizeToFree
                projectedFreePercent = (
                    projectedFreeBytes
                    / (projectedFreeBytes + (freeBytes - projectedFreeBytes))
                ) * 100

                if (
                    projectedFreeBytes >= self._minFreeSpaceGB
                    and projectedFreePercent >= self._minFreeSpacePercent
                ):
                    break

        # Apply backup count pruning to eligible files if no disk space issues
        elif self._daysToKeep > 0 and len(logFiles) > self._daysToKeep:
            # Only remove eligible files that exceed backup count
            excessCount = len(logFiles) - self._daysToKeep
            filesToRemove = [
                (filePath, size)
                for filePath, mtime, size in eligibleFiles[:excessCount]
            ]

        # Remove the selected files
        for filePath, size in filesToRemove:
            try:
                os.remove(filePath)
                if needsPruning:
                    reactor.callLater(
                        0,
                        rootLogger.info,
                        f"Pruned debug log file {filePath} ({size} bytes) due to disk space constraints",
                    )
                else:
                    reactor.callLater(
                        0,
                        rootLogger.info,
                        f"Pruned debug log file {filePath} (age-based rotation)",
                    )
            except OSError as e:
                reactor.callLater(
                    0,
                    rootLogger.error,
                    f"Failed to remove log file {filePath}: {e}",
                )

    def emit(self, record):
        # Check if rollover is needed before emitting the record
        try:
            if self.shouldRollover(record):
                self.doRollover()
        except Exception:
            # If rollover fails, continue with logging to avoid losing the record
            pass

        # Call parent emit method to actually write the record
        super().emit(record)

    def forceRotation(self):
        if (
            os.path.exists(self.baseFilename)
            and os.path.getsize(self.baseFilename) > 1024
        ):
            self.doRollover()


def setupPeekLogger(
    serviceName: Optional[str] = None,
    childIdentifier: str | None = None,
    logToStdout=True,
):
    logging.basicConfig(
        stream=sys.stdout,
        format=_makeFormat(childIdentifier),
        datefmt=DATE_FORMAT,
        level=logging.DEBUG,
    )

    logging.getLogger("peek_plugin_worker.peek_worker_process").setLevel(
        logging.INFO
    )
    logging.getLogger("peek_worker_service.peek_worker_request_queue").setLevel(
        logging.INFO
    )

    if serviceName:
        updatePeekLoggerHandlers(
            serviceName,
            childIdentifier=childIdentifier,
            logToStdout=logToStdout,
        )


def _namer(name):
    return name + ".gz"


def _rotator(source, dest):
    READ_CHUNK = 512 * 1024
    if not os.path.exists(source):
        return
    if os.path.exists(dest):
        return

    with open(source, "rb") as sf:
        with gzip.open(dest, "wb") as f:
            data = sf.read(READ_CHUNK)
            while data:
                f.write(data)
                data = sf.read(READ_CHUNK)

    if os.path.exists(source):
        os.remove(source)


def updatePeekLoggerHandlers(
    serviceName: Optional[str] = None,
    daysToKeep=28,
    rotateAfterMb=500,
    minFreeSpacePercent=20,
    minFreeSpaceGB=5,
    logToStdout=True,
    childIdentifier: str | None = None,
    forceRotateNow: bool = False,
):
    rootLogger = logging.getLogger()
    logFormatter = logging.Formatter(_makeFormat(childIdentifier), DATE_FORMAT)

    for handler in list(rootLogger.handlers):
        if isinstance(handler, PeekLogRotatingFileHandler):
            # Setup the file logging output
            rootLogger.removeHandler(handler)

        elif not sys.stdout.isatty() and not logToStdout:
            # Remove the stdout handler
            logger.info(
                "Logging to stdout disabled, see 'logToStdout' in config.json"
            )
            rootLogger.removeHandler(handler)

    serviceNameNoService = serviceName.replace("-service", "")
    fileName = (
        (
            Path("~/peek/log").expanduser()
            if platform.system() == "Darwin"
            else Path("~/log").expanduser()
        )
        / serviceNameNoService
        / ("%s.log" % serviceNameNoService)
    )
    fileName.parent.mkdir(parents=True, exist_ok=True)

    fh = PeekLogRotatingFileHandler(
        str(fileName),
        daysToKeep=daysToKeep,
        rotateAfterMb=rotateAfterMb,
        minFreeSpacePercent=minFreeSpacePercent,
        minFreeSpaceGB=minFreeSpaceGB,
    )
    fh.setFormatter(logFormatter)
    rootLogger.addHandler(fh)

    # Force rotation on service startup
    if forceRotateNow:
        fh.forceRotation()


def setupLoggingToSyslogServer(host: str, port: int, facility: str):
    rootLogger = logging.getLogger()
    # TODO, Syslog server needs _makeFormat(childIdentifier)
    logFormatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)

    logging.getLogger().addHandler(logging.StreamHandler())

    if facility not in SysLogHandler.facility_names:
        logger.info(list(SysLogHandler.facility_names))
        raise Exception("Syslog facility name is a valid facility")

    facilityNum = SysLogHandler.facility_names[facility]

    fh = SysLogHandler(address=(host, port), facility=facilityNum)
    fh.setFormatter(logFormatter)
    rootLogger.addHandler(fh)
