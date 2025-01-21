
class YouTubeError():
    pass

class YouTubeInvalidVideoTargetError(YouTubeError):
    pass

class YouTubeInvalidChannelTargetError(YouTubeError):
    pass

class YouTubeDisabledCommentsError(YouTubeError, Exception):
    pass

class YouTubeVideoNotFoundError(YouTubeError):
    pass

class YouTubeExclusiveMemberError(YouTubeError, Exception):
    pass


class YouTubeUnknown403Error(YouTubeError):
    pass

class YouTubeAccessNotConfiguredError(YouTubeError, Exception):
    def __init__(self, message=None, url=None):
        super().__init__(message)
        self.url = url