"""
ssheepdog is a public ssh key management tool for teams of programmers.
Different people need different privileges to different servers. Ssheepdog
allows you to specify these relationships in a simple json file and then sync
the keys to the appropriate servers.
"""
import json
from datetime import datetime
from fabric.api import env, sudo
from fabric.network import disconnect_all


class SsheepDog(object):

    def __init__(self, path=None):
        if not path:
            path = 'data.json'

        self.path = path
        self.data = self._file_to_json()

    def _file_to_json(self):
        f = open(self.path)
        contents = f.read()
        f.close()
        return json.loads(contents)

    def _run_on_server(self, host_string):
        """
        This is where the magic happens. This will ssh into a server and update
        public keys
        """
        # TODO: Implement magic
        # data = self.data['servers'][host_string]
        env.host_string = host_string
        sudo('pwd')

    def _dump_config_file(self):
        now = datetime.now()
        self.data['last_modified'] = now.strftime('%Y-%m-%d %H:%M:%S')
        f = open(self.path, 'w')
        f.write(json.dumps(self.data, indent=4))
        f.close()

    def run(self):
        try:
            for server in self.data['servers'].keys():
                self._run_on_server(server)
        except:
            pass
        finally:
            disconnect_all()

        self._dump_config_file()


def main():
    ssheepdog = SsheepDog()
    ssheepdog.run()


if __name__ == '__main__':
    main()
