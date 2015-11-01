import argparse
from sound_sync.clients.base import BaseSender
from sound_sync.audio.pcm.record import PCMRecorder


class Sender(BaseSender):
    def __init__(self, host=None, manager_port=None):
        BaseSender.__init__(self, host, manager_port)
        self.recorder = PCMRecorder()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--hostname",
                        default="localhost",
                        type=str,
                        help="Hostname of the management server.",
                        dest="hostname")
    parser.add_argument("-p", "--port",
                        default=8888,
                        type=int,
                        help="Port of the management socket on the management server. Default 8888.",
                        dest="manager_port")
    parser.add_argument("-n", "--name",
                        default="Untitled",
                        type=str,
                        help="Name of this channel in the channel list. Default Untitled.",
                        dest="name")
    parser.add_argument("-d", "--description",
                        default="No Description",
                        type=str,
                        help="Description of this channel in the channel list. Default No Description.",
                        dest="description")
    args = parser.parse_args()
    sender = Sender(args.host, args.manager_port)
    sender.name = args.name
    sender.description = args.description
    sender.initialize()
    try:
        sender.main_loop()
    finally:
        sender.terminate()


if __name__ == "__main__":
    main()