# coding: utf8
import os
import re


class SVN:
    def __init__(self, check_dir):
        self.check_dir = check_dir

    @staticmethod
    def _get_cmd_message(cmd):
        svn_cmd = 'svn ' + cmd
        return svn_cmd

    @staticmethod
    def _get_split_info(message):
        tb_message = message.split(':')
        return str(tb_message[len(tb_message) - 1]).strip().replace('\')', '')

    def _p_open_svn(self, cmd):
        svn_cmd = self._get_cmd_message(cmd)
        out_put_message = os.popen(svn_cmd)
        if out_put_message:
            message = out_put_message.read()
            if message:
                return message

    def info(self, path, username=None, password=None):
        print('[SVN MODEL]: svn info')
        library_url = self.check_dir + '/' + path
        if username and password:
            doc = self._p_open_svn('info ' + library_url + ' --username ' + username + ' --password ' + password)
        else:
            doc = self._p_open_svn('info ' + library_url)

        tb_message = {}
        if doc and doc != '':
            for value in enumerate(doc.strip().split('\n')):
                if re.search('Revision:', str(value)):
                    tb_message['Revision'] = self._get_split_info(str(value))
                    print('[SVN MODEL]: Revision: '+tb_message['Revision'])
                elif re.search('Last Changed Author:', str(value)):
                    tb_message['LastAuthor'] = self._get_split_info(str(value))
                    print('[SVN MODEL]:  LastAuthor: '+tb_message['LastAuthor'])
                elif re.search('Last Changed Date:', str(value)):
                    tb_message['LastDate'] = self._get_split_info(str(value))
        return tb_message

    def first_submit(self, path, username=None, password=None):
        print('[SVN MODEL]: svn info first submit')
        library_url = self.check_dir + '/' + path
        if username and password:
            doc = self._p_open_svn('log ' + library_url + ' --username ' + username + ' --password ' + password)
        else:
            doc = self._p_open_svn('log ' + library_url)

        tb_message = {}
        if doc and doc != '':
            doc_message = doc.split('|')
            length = len(doc_message)
            tb_message['Author'] = doc_message[length - 3]
            number_message = doc_message[length - 1].split('\n')
            tb_message['number_message'] = number_message[2]
            return tb_message

    def last_submit(self, path, username=None, password=None):
        print('[SVN MODEL]: svn info last submit')
        library_url = self.check_dir + '/' + path
        if username and password:
            doc = self._p_open_svn('log ' + library_url + ' --username ' + username + ' --password ' + password)
        else:
            doc = self._p_open_svn('log ' + library_url)

        tb_message = {}
        if doc and doc != '':
            doc_message = doc.split('|')
            tb_message['Author'] = doc_message[1]
            number_message = doc_message[3].split('\n')
            tb_message['number_message'] = number_message[2]
            return tb_message

    def blame(self, path, tb_lines, username=None, password=None):
        print('[SVN MODEL]: svn blame')
        library_url = self.check_dir + '/' + path
        # print('library_url: '+library_url)
        if username and password:
            doc = self._p_open_svn('blame ' + library_url + ' -v'+' --force' + ' --username ' + username + ' --password ' + password)
        else:
            doc = self._p_open_svn('blame ' + library_url + ' -v ' + ' --force')

        tb_message = {}
        if doc and doc != '':
            doc_message = doc.split('\n')
            for index, line_number in enumerate(tb_lines):
                print('line_number: '+str(line_number))
                for line, value in enumerate(doc_message):
                    if line + 1 == line_number and value:
                        line_message = value.split('\t')
                        message = re.sub(r'\s+', ' ', line_message[0])
                        tb_author = message.split(' ')
                        tb_message[line_number] = tb_author[1]
        return tb_message

    def log(self, path, username=None, password=None):
        print('[SVN MODEL]: svn log')
        library_url = self.check_dir + '/' + path
        if username and password:
            doc = self._p_open_svn('log ' + library_url + ' --verbose -q --username ' + username + ' --password ' + password)
        else:
            doc = self._p_open_svn('log ' + library_url + ' --verbose -q')

        if doc and doc != '':
            return doc

    def delete(self, path, username=None, password=None):
        print('[SVN MODEL]: svn delete')
        result_message = self.log(path, username, password)
        line = None
        if result_message:
            tb_message = result_message.split('Changed paths:')
            for index, value in enumerate(tb_message):
                if re.search(r' D', value):
                    line = index
                    break
            print('line: '+str(line))
            author = tb_message[line-1].split('|')[1].strip()
            return author


















