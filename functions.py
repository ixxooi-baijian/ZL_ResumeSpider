import json
import time
import my_setting
import os
import requests
from PIL import Image
from io import BytesIO
import re


def init_certification(spider):
    if os.path.exists('certification.txt'):
        with open('certification.txt', 'r') as cerf:
            my_setting.Headers['Cookie'] = cerf.read()
            get_resume_summary_list = set_filter('test', '')
            if get_resume_summary_list['code'] == 0:
                spider.login_status_bro.setText('账号未失效，可继续使用！')
                spider.pushButton.setEnabled(True)


# 获取登录二维码
def get_qr():
    get_qr_url = 'https://passport.zhaopin.com/jsonp/imgQrCodeWx?type=50&scene=101013&clientType=n&businessSystem=1'
    get_qr_response = requests.get(get_qr_url, headers=my_setting.LoginHeaders)
    get_qr_response.close()
    QR_response_dict = json.loads(get_qr_response.text.split('(')[1].split(')')[0])
    qr_response = requests.get(QR_response_dict['data']['path'])
    qr_response.close()
    img = Image.open(BytesIO(qr_response.content))
    img.save('qr.jpg')
    my_setting.validate_id = QR_response_dict['data']['validateId']


def get_certification():
    # 未扫码 ,成功, 已过期
    vail_url = 'https://passport.zhaopin.com/jsonp/qrCodeScanWx?validateId={0}&clientType=n&businessSystem=1&' \
               'bkurl=https://rd5.zhaopin.com/login/bind/account?bkurl=https://rd5.zhaopin.com&isValidate=false'.format(
        my_setting.validate_id)
    vail_response = requests.get(vail_url, headers=my_setting.LoginHeaders)

    vail_response_dict = json.loads(vail_response.text.split('(')[1].split(')')[0])
    message = vail_response_dict['message']
    if message == '成功':
        cookie = vail_response.headers['set-cookie']
        at = re.findall('.*?at=(.*?);.*?', cookie)[0]
        token = re.findall('.*?Token=(.*?);.*?', cookie)[0]
        rt = re.findall('.*?rt=(.*?);.*?', cookie)[0]
        uiioit = re.findall('.*?uiioit=(.*?);.*?', cookie)[0]
        my_setting.Headers['Cookie'] = 'at={0}; Token={1}; rt={2}; uiioit={3};'.format(at, token, rt, uiioit)

        # 伪装成正常用户解密方法
        my_setting.Headers['Host'] = 'passport.zhaopin.com'
        response_a = requests.get(
            'https://passport.zhaopin.com/org/login/bind/account?bkurl=https%3A%2F%2Frd5.zhaopin.com&isValidate=false',
            headers=my_setting.Headers)
        print(response_a.headers)

        my_setting.Headers['Host'] = 'ihr.zhaopin.com'
        response_b = requests.get('https://ihr.zhaopin.com/loginTran.do?bkurl=https%3A%2F%2Frd5.zhaopin.com',
                                 headers=my_setting.Headers)
        print(response_b.headers)

        response_c = requests.get('https://ihr.zhaopin.com/loginPoint/choose.do?bkurl=https%3A%2F%2Frd5.zhaopin.com',
                                 headers=my_setting.Headers)
        print(response_c.headers)
        my_setting.Headers['Host'] = 'rd5.zhaopin.com'

        with open('certification.txt', 'w') as cerf:
            cerf.write(my_setting.Headers['Cookie'])
        return 200
    elif message == '已过期':
        return 201
    elif message == '未扫码':
        print('请扫码!!!')
        return 202


def get_headers():
    return my_setting.Headers


def set_filter(career, work_type):
    headers = get_headers()
    # 选定地区
    filter_conditions_url = 'https://rd5.zhaopin.com/api/custom/search/saveFilterConditions?_={0}'.format(
        int(time.time() * 1000))
    my_setting.career = career
    my_setting.work_type = work_type
    if not work_type:
        work_type_style = '[ 工作内容：{0} ]'.format(work_type)
    else:
        work_type_style = ''
    filter_conditions_post_data = {
        'filterName': '[ 职位名称：{0} ]{1}'.format(career, work_type_style),
        'expression': [{'filterId': -3, 'input': career},
                       {'filterId': -2, 'input': work_type},
                       {'filterId': 38},
                       {'filterId': 9},
                       {'filterId': 11},
                       {'filterId': 12},
                       {'filterId': 13},
                       {'filterId': 14},
                       {'filterId': 16},
                       {'filterId': 35}],
        'searchType': 1}
    filter_conditions_response = requests.post(url=filter_conditions_url, headers=headers,
                                               data=json.dumps(filter_conditions_post_data), timeout=10)
    filter_conditions_response.close()

    return filter_conditions_response.json()


def get_resume_summary():
    status_code, resume_list, total_num = get_resume_list()
    if status_code == 200:
        return {'code': 200, 'resume_list': resume_list[0], 'total': total_num}
    elif status_code == 402:
        return {'code': 402, 'resume_list': resume_list[0], 'total': total_num}


def get_resume_detail(resume_no):
    headers = get_headers()
    resume_detail_url = 'https://rd5.zhaopin.com/api/rd/resume/detail?resumeNo={0}'.format(resume_no)

    resume_detail_response = requests.get(url=resume_detail_url, headers=headers, timeout=10)
    resume_detail_dict = resume_detail_response.json()
    resume_detail_response.close()
    if 'data' in resume_detail_dict:
        resume_detail_dict_result = resume_detail_dict['data']['detail']
        return 200, resume_detail_dict_result
    else:
        return 401, '身份失效请1:重新开启程序获取凭证！'


def get_resume_list(start=0, resume_nums=30):
    headers = get_headers()
    # time.sleep(5)
    # resume_list_url = 'https://rd5.zhaopin.com/api/custom/search/resumeListV2?_={0}&x-zp-page-request-id={1}'.format(
    #     int(time.time() * 1000), my_setting.xzr_id)
    resume_list_url = 'https://rd5.zhaopin.com/api/rd/search/resumeList?_={0}'.format(int(time.time() * 1000))

    resume_list_post_data = {
        'start': start,
        'rows': resume_nums,
        'S_DISCLOSURE_LEVEL': 2,
        'S_EXCLUSIVE_COMPANY': '上海乐助人力资源有限公司',
        'S_KEYWORD_JOBNAME': my_setting.career,
        'S_KEYWORD_JOBDESC': my_setting.work_type,
        'S_COMPANY_NAME_ALL': my_setting.company_name,
        'S_DESIRED_CITY': my_setting.desired_city,
        'S_MAJOR_NAME_ALL': my_setting.major_name,
        'S_ENGLISH_RESUME': '1',
        'isrepeat': 1,
        'sort': 'complex_v22',
    }

    resume_list_response = requests.post(url=resume_list_url, headers=headers,
                                         data=json.dumps(resume_list_post_data), timeout=10)
    resume_list_result = resume_list_response.json()
    resume_list_response.close()
    if 'data' in resume_list_result:
        resume_list = resume_list_result['data']['dataList']
        total_num = resume_list_result['data']['total']
        if resume_list:
            for one_resume in resume_list:
                resume_no = one_resume['id'] + '_' + str(one_resume['version']) + '_' + str(
                    one_resume['language']) + ';' + one_resume['k'] + ';' + one_resume['t']
                one_resume['resume_no'] = resume_no

                # 删除无用信息
                del (one_resume['t'])
                del (one_resume['k'])
                del (one_resume['version'])
                del (one_resume['language'])
                del (one_resume['hasRead'])
        else:
            resume_list.append('该期望工作地区无简历！')
        return 200, resume_list, total_num
    else:
        return 402, ['身份失效2:请重新开启程序获取凭证！'], '0'
