from qb_model import QB
from analy_model import Analysis
from calc_model import Calc
import argparse
import re
import os
import sys




if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-B', '--baseline-buildid', help="baseline buildid", type=int, required=True)
    parser.add_argument('-O', '--out-path', help="out_path", required=True)
    args = parser.parse_args()

    status = 1
    if args.out_path.find('\\'):
        args.out_path = args.out_path.replace('\\', '/')
    if not os.path.exists(args.out_path):
        os.mkdir(args.out_path)


    # 生成parseFile.tab parseBundle.tab parsePackageFile.tab
    Qb_Message = QB(args.baseline_buildid, 'BundleData.txt', 'BundleDownloadInfo.txt', 'aba_bundle.json', args.out_path)
    # 读取parseFile.tab parseBundle.tab 分类分析
    Analysis_message = Analysis(args.out_path+'/'+'parseFile.tab', args.out_path+'/'+'parsePackageFile.tab')
    package_flag = Analysis_message.flag
    Calc_Message = Calc(args.out_path, package_flag)
    status = 0
    sys.exit(status)





