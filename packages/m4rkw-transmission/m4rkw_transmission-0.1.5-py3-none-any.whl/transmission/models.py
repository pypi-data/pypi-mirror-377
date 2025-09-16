import urllib
from enum import Enum, IntEnum
from typing import Optional

from pydantic import BaseModel, field_validator, Field

ATTRIBUTES_LIST = ['id','name','hashString','isFinished','isStalled','leftUntilDone','eta','percentDone','rateDownload',
              'status','totalSize','rateDownload','peersConnected','peersFrom','rateUpload','downloadedEver','peersSendingToUs',
              'peersGettingFromUs','desiredAvailable']

ATTRIBUTES_ALL = ['activityDate','addedDate','bandwidthPriority','comment','corruptEver','creator','dateCreated',
              'desiredAvailable','doneDate','downloadDir','downloadedEver','downloadLimit','downloadLimited','error',
              'errorString','eta','etaIdle','files','fileStats','hashString','haveUnchecked','haveValid','honorsSessionLimits',
              'id','isFinished','isPrivate','isStalled','leftUntilDone','magnetLink','manualAnnounceTime','maxConnectedPeers',
              'metadataPercentComplete','name','peer-limit','peers','peersConnected','peersFrom','peersGettingFromUs',
              'peersSendingToUs','percentDone','pieces','pieceCount','pieceSize','priorities','queuePosition','rateDownload',
              'rateUpload','recheckProgress','secondsDownloading','secondsSeeding','seedIdleLimit','seedIdleMode','seedRatioLimit',
              'seedRatioMode','sizeWhenDone','startDate','status','trackers','trackerStats','totalSize','torrentFile',
              'uploadedEver','uploadLimit','uploadLimited','uploadRatio','wanted','webseeds','webseedsSendingToUs','files-wanted','files-unwanted']

ATTRIBUTES_MUTABLE = ['bandwidthPriority','downloadLimit','downloadLimited','files-wanted','files-unwanted',
              'honorsSessionLimits','location','peer-limit','priority-high','priority-low','priority-normal','queuePosition',
              'seedIdleLimit','seedIdleMode','seedRatioLimit','seedRatioMode','trackerAdd','trackerRemove','trackerReplace',
              'uploadLimit','uploadLimited']

ATTRIBUTES_SESSION = ['alt-speed-down','alt-speed-enabled','alt-speed-time-begin','alt-speed-time-enabled',
              'alt-speed-time-end','alt-speed-time-day','alt-speed-up','blocklist-url','blocklist-enabled','blocklist-size',
              'cache-size-mb','config-dir','download-dir','download-queue-size','download-queue-enabled','dht-enabled',
              'encryption','idle-seeding-limit','idle-seeding-limit-enabled','incomplete-dir','incomplete-dir-enabled',
              'lpd-enabled','peer-limit-global','peer-limit-per-torrent','pex-enabled','peer-port','peer-port-random-on-start',
              'port-forwarding-enabled','queue-stalled-enabled','queue-stalled-minutes','rename-partial-files','rpc-version',
              'rpc-version-minimum','script-torrent-done-filename','script-torrent-done-enabled','seedRatioLimit','seedRatioLimited',
              'seed-queue-size','seed-queue-enabled','speed-limit-down','speed-limit-down-enabled','speed-limit-up',
              'speed-limit-up-enabled','start-added-torrents','trash-original-torrent-files','units','utp-enabled','version','units']

ATTRIBUTES_SESSION_MUTABLE = ['alt-speed-down','alt-speed-enabled','alt-speed-time-begin','alt-speed-time-enabled',
              'alt-speed-time-end','alt-speed-time-day','alt-speed-up','blocklist-url','blocklist-enabled','cache-size-mb',
              'download-dir','download-queue-size','download-queue-enabled','dht-enabled','encryption','idle-seeding-limit',
              'idle-seeding-limit-enabled','incomplete-dir','incomplete-dir-enabled','lpd-enabled','peer-limit-global',
              'peer-limit-per-torrent','pex-enabled','peer-port','peer-port-random-on-start','port-forwarding-enabled',
              'queue-stalled-enabled','queue-stalled-minutes','rename-partial-files','script-torrent-done-filename',
              'script-torrent-done-enabled','seedRatioLimit','seedRatioLimited','seed-queue-size','seed-queue-enabled',
              'speed-limit-down','speed-limit-down-enabled','speed-limit-up','speed-limit-up-enabled','start-added-torrents',
              'trash-original-torrent-files','units','utp-enabled','units']

RPC_METHODS = {
    'start':    'torrent-start',
    'stop':    'torrent-stop',
    'verify':    'torrent-verify',
    'reannounce':    'torrent-reannounce',
    'queue_top':    'queue-move-top',
    'queue_up':    'queue-move-up',
    'queue_down':    'queue-move-down',
    'queue_bottom':    'queue-move-bottom'
}

class TorrentStatus(IntEnum):
    STOPPED = 0
    CHECK_WAIT = 1
    CHECKING = 2
    DOWNLOAD_WAIT = 3
    DOWNLOADING = 4
    SEED_WAIT = 5
    SEEDING = 6


class TorrentPeersFrom(BaseModel):
    fromCache: int = 0
    fromDht: int = 0
    fromIncoming: int = 0
    fromLpd: int = 0
    fromLtep: int = 0
    fromPex: int = 0
    fromTracker: int = 0


class File(BaseModel):
    bytesCompleted: int
    length: int
    name: str


class FileStat(BaseModel):
    bytesCompleted: int
    wanted: bool
    priority: int


class Peer(BaseModel):
    address: str
    clientName: str
    clientIsChoked: bool | None = None
    clientIsInterested: bool | None = None
    flagStr: str | None = None
    isDownloadingFrom: bool | None = None
    isEncrypted: bool | None = None
    isIncoming: bool | None = None
    isUploadingTo: bool | None = None
    peerIsChoked: bool | None = None
    peerIsInterested: bool | None = None
    port: int | None = None
    progress: float | None = None
    rateToClient: int | None = None
    rateToPeer: int | None = None


class Tracker(BaseModel):
    announce: str
    id: int
    scrape: str
    tier: int


class Torrent(BaseModel):

    activityDate: Optional[int] = None
    addedDate: Optional[int] = None
    bandwidthPriority: Optional[int] = None
    comment: Optional[str] = None
    corruptEver: Optional[int] = None
    creator: Optional[str] = None
    dateCreated: Optional[int] = None
    desiredAvailable: int = 0
    doneDate: Optional[int] = None
    downloadDir: Optional[str] = None
    downloadedEver: int = 0
    downloadLimit: Optional[int] = None
    downloadLimited: bool = False
    error: int = 0
    errorString: Optional[str] = None
    eta: int = -1
    etaIdle: Optional[int] = None
    files: Optional[list[File]] = None
    fileStats: Optional[list[FileStat]] = None
    hashString: Optional[str] = None
    haveUnchecked: Optional[int] = None
    haveValid: Optional[int] = None
    honorsSessionLimits: Optional[bool] = None
    id: Optional[int] = 0
    isFinished: bool = False
    isPrivate: Optional[bool] = None
    isStalled: Optional[bool] = None
    leftUntilDone: Optional[int] = None
    magnetLink: Optional[str] = None
    manualAnnounceTime: Optional[int] = None
    maxConnectedPeers: Optional[int] = None
    metadataPercentComplete: Optional[float] = None
    name: Optional[str] = None
    peer_limit: Optional[int] = None
    peers: Optional[list[Peer]] = None
    peersConnected: int = 0
    peersFrom: Optional[dict[str, int]] = None
    peersGettingFromUs: int = 0
    peersSendingToUs: int = 0
    percentDone: float = 0.0
    pieces: Optional[str] = None
    pieceCount: Optional[int] = None
    pieceSize: Optional[int] = None
    priorities: Optional[list[int]] = None
    queuePosition: Optional[int] = None
    rateDownload: int = 0
    rateUpload: int = 0
    recheckProgress: Optional[float] = None
    secondsDownloading: Optional[int] = None
    secondsSeeding: Optional[int] = None
    seedIdleLimit: Optional[int] = None
    seedIdleMode: Optional[int] = None
    seedRatioLimit: Optional[float] = None
    seedRatioMode: Optional[int] = None
    sizeWhenDone: Optional[int] = None
    startDate: Optional[int] = None
    status: int = 0
    trackers: Optional[list[Tracker]] = None
    trackerStats: Optional[list[dict]] = None
    totalSize: int = 0
    torrentFile: Optional[str] = None
    uploadedEver: Optional[int] = None
    uploadLimit: Optional[int] = None
    uploadLimited: Optional[bool] = None
    uploadRatio: Optional[float] = None
    wanted: Optional[list[bool]] = None
    webseeds: Optional[list[str]] = None
    webseedsSendingToUs: Optional[int] = None
    files_wanted: Optional[list[int]] = None
    files_unwanted: Optional[list[int]] = None

    @field_validator("name", mode="before")
    @classmethod
    def normalise_name(cls, v: str) -> str:
        return urllib.parse.unquote(v).replace('+',' ')


    @field_validator("percentDone", mode="before")
    @classmethod
    def normalise_percentDone(cls, v: str) -> str:
        return v * 100


class TransmissionResponseStatus(str, Enum):
    SUCCESS = "success"
    DUPLICATE_TORRENT = "duplicate torrent"
    INVALID_ARGUMENT = "invalid argument"
    METHOD_NOT_FOUND = "method not found"
    SERVER_ERROR = "server error"


class TorrentAddedResponse(BaseModel):
    hashString: str
    id: int
    name: str


class TransmissionArguments(BaseModel):
    torrents: Optional[list[Torrent]] = None
    torrent_added: Optional[TorrentAddedResponse] = Field(None, alias="torrent-added")


class TransmissionResponse(BaseModel):
    arguments: TransmissionArguments
    result: TransmissionResponseStatus
