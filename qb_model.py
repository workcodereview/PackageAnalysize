import os
import re
import logging
import json
import codecs
import requests
import xml.etree.ElementTree as ET

# BundleData.txt BundleDownLoad.txt build id 获取
# aba_bundle.json 从StreamingAssets获取

# 构造函数 BundleData.txt BundleDownLoad.txt aba_bundle.json out_path

# load BundleData.txt ---> _load_bundle_data ---> self.APK_DLC_OTHER

# load BundleDownLoad.txt ---> _load_bundle_download  ---> self.DOWNLOAD_FIRST

# load aba_bundle.json   ---> _load_aba_bundle --->  self.BUNDLE_INFO_DICT

# load installpacksize.txt ---> _load_package_file ---> self.PACKAGE_FILE_DICT

# installpacksize.txt 内容来自于 ---> http://10.11.10.86/download/resource_package/1591419425778/original/installpacksize.txt

# result: _save_file ---> parseFile.tab

# result: _save_bundle_file  --->  parseBundle.tab dlc.tab

# result: _save_scene_away ---> dlc.tab
QB_URL = 'http://j3m.rdev.kingsoft.net:8810'
QB_USERNAME = 'foranalyse'
QB_PASSWORD = 'anRes0756'
QB_REQUESTS = requests.Session()
QB_REQUESTS.auth = (QB_USERNAME, QB_PASSWORD)

RESOURCE_URL = 'http://10.11.10.86/download/resource_package'

class QB:
    def __init__(self, build_id, bundle_data_path, bundle_download_path, aba_bundle_path,  out_path):
        self.build_id = build_id
        self.bundle_data_path = bundle_data_path
        self.bundle_download_path = bundle_download_path
        self.aba_bundle_path = aba_bundle_path
        self.out_path = out_path
        self._reload()
        self._save_bundle_file()
        self._save_file()
        self._save_scene_away()

    def _reload(self):
        self.build_svn, self.build_time = self._load_build_info()
        self.APK_DLC_OTHER = self._load_bundle_data()
        self.DOWNLOAD_FIRST_DLC = self._load_bundle_download()
        self._set_apk_dlc_other()
        if self.bundle_download_path == '' and self.bundle_data_path == '':
            print('[QB_MODEL]: 更新包资源分析 不需要BundleData.txt BundleDownLoad.txt installpacksize.txt 文件')
        else:
            print('[QB_MODEL]: 全包资源分析 需要BundleData.txt BundleDownLoad.txt installpacksize.txt 文件')
            self.PACKAGE_FILE_DICT = self._load_package_file()
            self._save_package_file()
        self.BUNDLE_INFO_DICT = self._load_aba_bundle()

    def _load_file_message(self, file_path):
        url = '%s/download/%d/artifacts/%s' % (QB_URL, self.build_id, file_path)
        print('url: '+url)
        req = QB_REQUESTS.get(url)
        if req.status_code != 200:
            logging.error(file_path + u'获取失败\nstatus_code=%d\n%s' % (req.status_code, url))
            return ''

        return req.content.decode()

    def _load_build_info(self):
        print('[QB_MODEL]：获取build_svn build_time')
        build_svn, build_time = None, None
        url = QB_URL + '/rest/builds/%d' % self.build_id
        print(url)
        req = QB_REQUESTS.get(url)
        if req.status_code != 200:
            logging.error(u'builds获取失败\nstatus_code=%d\n%s' % (req.status_code, url))
            return build_svn, build_time

        root = ET.fromstring(req.content)
        for item in root.iterfind('version'):
            build_svn = int(item.text)
        for item in root.iterfind('secretAwareVariableValues/entry'):
            if 'var_BuildInfo_UnixTimestampMillis' == item.findtext('string'):
                build_time = int(item.findtext('com.pmease.quickbuild.SecretAwareString/string'))
        return build_svn, build_time

    def _load_package_file(self):
        print('[QB_MODEL]：获取installpacksize.txt--->package_file_dict')
        package_file_dict = {}
        url = RESOURCE_URL + '/'+ str(self.build_time)+'/original/installpacksize.txt'
        req = QB_REQUESTS.get(url)
        if req.status_code != 200:
            logging.error(u'installpacksize.txt 获取失败\nstatus_code=%d\n%s' % (req.status_code, url))
            return package_file_dict

        dir_path = ''
        for line_str in req.content.decode().split('\n'):
            if not line_str:
                continue
            if re.match('^\.', line_str):
                dir_path = line_str.strip('./').split(':')[0]
            if re.match('^\-rw', line_str):
                line_data = re.split(r' +', line_str)
                length = len(line_data)
                if dir_path == '':
                    file_path = line_data[length - 1]
                else:
                    file_path = dir_path + '/' + line_data[length - 1]
                package_file_dict[file_path] = {'file_path': file_path, 'file_size':line_data[4]}

        return package_file_dict

    def _load_bundle_data(self):
        print('[QB_MODEL]：BundleData.txt--->获取apk_dlc_other')
        apk_dlc_other = {}
        file_message = self._load_file_message(self.bundle_data_path)
        if not file_message:
            logging.error('Bundle Data Message Is Null !!!')
            return apk_dlc_other

        data = json.loads(file_message)
        count = 0
        download_type = ''

        for key, values in enumerate(data):
            count = count + 1
            if count < 2:
                continue
            key = values['name'] + '.assetBundle'
            load_from = values['downloadForm']
            if load_from == 0:
                download_type = 'Apk'
            elif load_from == 1:
                download_type = 'Dlc'
            elif load_from == 2:
                download_type = 'Unused'
            apk_dlc_other[key] = download_type
        logging.info('Save APK_DLC_OTHER success!!!')
        return apk_dlc_other

    def _load_bundle_download(self):
        print('[QB_MODEL]：获取BundleDownloadInfo.txt--->download_first_dlc')
        download_first_dlc = {}
        file_message = self._load_file_message(self.bundle_download_path)
        if not file_message:
            logging.error('Bundle DownLoad Data Message Is Null !!!')
            return download_first_dlc

        data = json.loads(file_message)
        for key, values in data.items():
            if key == 'HotUpdateList':
                for k, v in enumerate(values):
                    download_first_dlc[v+'.assetBundle'] = 'First'
            if key == 'DlcChapter':
                for k1, v1 in enumerate(values):
                    i = 0
                    for k2, v2 in v1.items():
                        if k2 == 'bundls':
                            while i < len(v1[k2]):
                                download_first_dlc[v2[i] + '.assetBundle'] = 'Dlc'
                                i = i + 1
        return download_first_dlc

    def _load_aba_bundle(self):
        print('[QB_MODEL]：获取bundle_info_dict')
        bundle_info_dict = {}
        url = RESOURCE_URL + '/%d/original/aba_bundle.json' % self.build_time
        req = requests.get(url)
        if req.status_code != 200:
            logging.error(u'aba_bundle.json 获取失败\nstatus_code=%d\n%s' % (req.status_code, url))
            return bundle_info_dict

        bundle_count = 0
        for bundle_item in req.content.decode().split('\n'):
            bundle_count = bundle_count + 1
            bundle_item = bundle_item.strip()
            if bundle_item == '':
                break
            bundle_data = json.loads(bundle_item)

            if bundle_data['bundle'].find('\\') > 0:
                bundle_info = bundle_data['bundle'].split('\\')
                key = bundle_info[1]
            else:
                key = bundle_data['bundle']
            bundle_info_dict[key] = {'bundlesize': bundle_data['bundleSize'], 'compress': bundle_data['compress'],
                                     'fileCount': bundle_data['fileCount'], 'fileList': bundle_data['fileList']}
        return bundle_info_dict

    def _set_apk_dlc_other(self):
        print('[QB_MODEL]：获取重新set的APK_DLC_OTHER')
        for bundle, load_from in self.DOWNLOAD_FIRST_DLC.items():
            self.APK_DLC_OTHER[bundle] = load_from

    def _save_bundle_file(self):
        print('[QB_MODEL]：获取parseBundle.tab file')
        f_write = codecs.open(self.out_path+'/parseBundle.tab', 'w', 'utf-8')
        f_write.write('bundleName\tbundleSize\tbundleCompress\tfileCount\tLoadFrom\n')
        bundle_name = ''
        for bundle, bundle_message in self.BUNDLE_INFO_DICT.items():
            if bundle_name == bundle:
                continue
            f_write.write(
                str(bundle) + '\t' +
                str(bundle_message['bundlesize']) + '\t' +
                str(bundle_message['compress']) + '\t' +
                str(bundle_message['fileCount']) + '\t' +
                ('NULL' if bundle not in  self.APK_DLC_OTHER else str(
                    self.APK_DLC_OTHER[bundle])) + '\n'
            )
            bundle_name = bundle
        logging.info('Save Bundle File Success!!!')

    def _save_file(self):
        print('[QB_MODEL]：获取parseFile.tab file')
        f_write = codecs.open(self.out_path + '/parseFile.tab', 'w', 'utf-8')
        f_write.write('fileName\tfileSize\tfile_mSize\tbundleName\tbundleSize\tLoadFrom\n')
        with codecs.open(self.out_path+'/parseBundle.tab', 'r', 'utf-8') as f:
            bundle_content = f.read().strip().splitlines()
        load_from = ''
        file_count = 0
        for bundle, bundle_message in self.BUNDLE_INFO_DICT.items():
            file_list = bundle_message['fileList']
            for file_info in file_list:
                file_count = file_count + 1
                key = file_info['f']
                if key == 'ABO':
                    continue
                for line in bundle_content:
                    lineinfo = line.split('\t')
                    if lineinfo[0] == bundle:
                        load_from = lineinfo[4]
                f_write.write(file_info['f'] + '\t' + str(file_info['ds']) + '\t' + str(file_info['s']) +
                              '\t' + bundle + '\t' + str(bundle_message['bundlesize']) + '\t' + load_from + '\n')
        f_write.close()
        print('[QB_MODEL]：Save parseFile.tab Success')

    def _save_package_file(self):
        print('[QB_MODEL]：获取parsePackageFile.tab file')
        file_path = self.out_path + '/parsePackageFile.tab'
        p_file = codecs.open(file_path, 'w', 'utf-8')
        p_file.write('fileName\tfileSize(未解压)\n')
        for file_path, file_list in self.PACKAGE_FILE_DICT.items():
            p_file.write(file_list['file_path'].strip()+'\t'+file_list['file_size'].strip()+'\n')
        p_file.close()

    def _save_scene_away(self):
        print('[QB_MODEL]：获取dlc.tab file')
        file_path = self.out_path+'/parseFile.tab'
        message = u'下载方式\t场景名\t文件大小(KB)\tbundle名\tbundle大小(KB)\n'
        d_file = codecs.open(self.out_path + '/dlc.tab', 'w', 'utf-8')
        d_file.write(message)
        if not os.path.exists(file_path):
            logging.error(file_path+' Not Exist!!!')
        with codecs.open(file_path, 'r', 'utf-8') as f:
            file_content = f.read().strip().splitlines()

        for index, file_item in enumerate(file_content):
            if index == 0:
                continue
            file_info = file_item.split('\t')
            if not file_info[0].endswith('.unity'):
                continue
            d_file.write(file_info[5]+'\t'+file_info[0]+'\t'+str(round(int(file_info[1])/1024, 4)) +
                         '\t' + file_info[3] + '\t' + str(round(int(file_info[4])/1024, 2))+'\n')
        d_file.close()

    @staticmethod
    def print_dict(d):
        if type(d) == dict:
            print('打印字典'+str(d)+'内容')
            for key, value in d.items():
                logging.info('key: ', key)
                logging.info(('values: ', value))
        else:
            print('非字典')

