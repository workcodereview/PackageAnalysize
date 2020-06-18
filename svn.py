import os

svn_path = 'svn'

class svn:
    def __init__(self, cmd, username, password):
        self.svn_path = 'svn'
        self.cmd = cmd
        self.username = username
        self.password = password

    def _to_svn_cmd(self):
        svn_cmd = self.svn_path + ' ' + self.cmd
        return svn_cmd

    def popen_svn(self):
        svn_cmd = self._to_svn_cmd()
        out_put = os.popen(svn_cmd)
        if output:
            contents = out_put.read()
            if contents:
                return contents

    def _get_library_url(self):
        tmpinfo = self.popen_svn('info'+' --username '+self.username+'--password' + self.password)
        lib_url = string.match(tmpinfo,"URL:%s(%S+JX3Pocket/).")




if __name__ == '__main__':
    # file_path = 'svn://xsjreposvr3.rdev.kingsoft.net/JX3M/trunk/JX3Pocket/Assets/JX3Game/Source/File/Stage/Global_Stage.xls'
    file_path = 'svn info zhangyin Zy97.Zyd02'
    username = 'zhangyin'
    passwd = 'Zy97.Zyd02'
    cmd = 'svn info ' +file_path
    output = os.popen(cmd)
    if output:
        content = output.read()
        print('content: '+content)