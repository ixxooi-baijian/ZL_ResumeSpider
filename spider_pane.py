from PyQt5.Qt import *
from spider import Ui_Form
from functions import *


# 爬取线程
class SpiderThread(QThread):
    def __init__(self, ZhiLianSpider):
        super(SpiderThread, self).__init__()
        self.dir_name = None
        self.done = False
        self.zhi_lian_spider = ZhiLianSpider
        self.start_pages = -1
        self.nums = 100
        self.exit_resume = list()
        self.resume_file = None

        self.delay = 2

    def set_delay(self):
        delay_second = self.zhi_lian_spider.delay_comb.currentText()
        if delay_second:
            self.delay = int(delay_second)

    # 初始化文件目录
    def init_dir(self):
        if not os.path.exists('data/'):
            os.mkdir('data/')
        self.resume_file = my_setting.career
        if my_setting.work_type:
            self.resume_file += '_1_' + my_setting.work_type
        if my_setting.company_name:
            self.resume_file += '_2_' + my_setting.company_name
        if my_setting.major_name:
            self.resume_file += '_3_' + my_setting.major_name
        if my_setting.desired_city:
            self.resume_file += '_4_' + my_setting.desired_city

        self.dir_name = 'data/' + self.resume_file
        if not os.path.exists(self.dir_name):
            os.mkdir(self.dir_name)

    # 爬虫线程运行函数
    def run(self):
        self.init_dir()
        while not self.done:
            self.start_pages += 1
            try:
                status_code, resume_list, total_num = get_resume_list(self.start_pages, self.nums)

                if status_code == 200:
                    if len(resume_list) > 0 and '该期望工作地区无简历！' not in resume_list:
                        for candidate in resume_list:
                            if self.done:
                                break
                            rebuild_resume = {
                                'candidate': candidate,
                                'detail': {},
                            }

                            jieli_name = candidate['name'].split('*')[0].split('\\')[0]
                            user_file_name = candidate['userName'] + '.jpg'
                            resume_file_name = candidate['userName'] + '.json'
                            query_list_dir = os.listdir('data/')

                            try:
                                resume_dir = ''.join((''.join(
                                    (jieli_name + candidate['userName'] + str(candidate['userId'])).split())).split('/'))
                                user_dir = self.dir_name + '/' + resume_dir

                                if not os.path.exists(user_dir):
                                    for one_dir in query_list_dir:
                                        if resume_dir in os.listdir('data/' + one_dir):
                                            self.zhi_lian_spider.result_bro.append('【在《{0}》文件夹下，{1}简历已经存在】 '.format(
                                                one_dir, resume_dir))
                                            break
                                    os.mkdir(user_dir)
                                else:
                                    self.zhi_lian_spider.result_bro.append('【在《{0}》文件夹下，{1}简历已经存在】 '.format(
                                        self.resume_file, resume_dir))
                                    continue
                            except Exception as e:
                                print('202:', e)
                                continue

                            status_code_detail, resume_detail = get_resume_detail(candidate['resume_no'])
                            # 数据处理
                            if status_code_detail == 401:
                                self.done = True
                                self.zhi_lian_spider.result_bro.append('▓{0}▓'.format(resume_list[0]))
                                break
                            rebuild_resume['detail']['教育经历'] = resume_detail['EducationExperience']
                            rebuild_resume['detail']['工作经历'] = resume_detail['WorkExperience']
                            rebuild_resume['detail']['项目经历'] = resume_detail['ProjectExperience']
                            rebuild_resume['detail']['培训经历'] = resume_detail['Training']
                            rebuild_resume['detail']['所获证书'] = resume_detail['AchieveCertificate']
                            rebuild_resume['detail']['语言能力'] = resume_detail['LanguageSkill']
                            rebuild_resume['detail']['自我评价'] = resume_detail['SelfEvaluate']
                            rebuild_resume['detail']['兴趣爱好'] = resume_detail['Other']
                            rebuild_resume['detail']['管理经验'] = resume_detail['AdvancedManagement']

                            try:
                                if candidate['havePhoto']:
                                    user_img_url = 'https:' + candidate['portrait']
                                    with requests.get(user_img_url, headers=my_setting.Headers, timeout=5) as img_resp:
                                        user_img = img_resp.content
                                        with open(user_dir + '/' + user_file_name, 'wb') as img_f:
                                            img_f.write(user_img)
                            except Exception as e:
                                print(e)

                            with open(user_dir + '/' + resume_file_name, 'w',
                                      encoding='utf-8') as resume_json_f:
                                json.dump(rebuild_resume, resume_json_f, ensure_ascii=False, indent=4)

                            self.zhi_lian_spider.result_bro.append('▶目录名:{0}，简历:{1}|爬取成功。◀'.format(
                                user_dir, resume_file_name))
                            self.zhi_lian_spider.result_bro.moveCursor(self.zhi_lian_spider.result_bro.textCursor().End)
                            time.sleep(self.delay)
                    else:
                        self.zhi_lian_spider.result_bro.append('▓爬▓取▓玩▓毕▓')
                        self.done = True
                else:
                    self.done = True
                    self.zhi_lian_spider.result_bro.append('▓{0}▓'.format(resume_list[0]))
            except Exception as e:
                print(e)

        time.sleep(3)
        self.zhi_lian_spider.result_bro.append('▓爬▓取▓停▓止▓')

    def stop_spider(self):
        self.done = True


class GetQRThread(QThread):
    get_qt_img_signal = pyqtSignal()

    def __init__(self):
        super().__init__()

    # 这个鬼东西搞死人哦
    def __del__(self):
        self.wait()

    def run(self):
        get_qr()
        self.get_qt_img_signal.emit()


class GetCookieThread(QThread):
    get_cookie_signal = pyqtSignal(int)

    def __init__(self):
        super().__init__()

    # 这个鬼东西搞死人哦
    def __del__(self):
        self.wait()

    def run(self):
        status_code = get_certification()
        self.get_cookie_signal.emit(status_code)


class GetSummaryThread(QThread):
    get_summary_signal = pyqtSignal(dict)

    def __init__(self):
        super().__init__()

    # 这个鬼东西搞死人哦
    def __del__(self):
        self.wait()

    def run(self):
        resume_summary_dict = get_resume_summary()
        self.get_summary_signal.emit(resume_summary_dict)


class ZhiLianSpider(QWidget, Ui_Form):
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.setupUi(self)

        self.spider_thread = SpiderThread(self)
        self.desired_city = None
        self.provice_list = None
        self.city_list = None
        self.area_list = None

        get_qr()
        pix_map = QPixmap('qr.jpg')
        self.qr_label.setPixmap(pix_map)
        self.qr_label.setScaledContents(True)

        self.init_desired_city()
        self.init_delay()
        init_certification(self)

        self.setWindowIcon(QIcon('whitespace.ico'))

    def init_delay(self):
        delay_options = ['', '0', '1', '2', '4', '8']
        self.delay_comb.addItems(delay_options)

    def init_desired_city(self):
        with open('desired_city.json', 'r', encoding='utf-8') as json_f:
            city_dict = json.load(json_f)
            self.desired_city = city_dict

        self.provice_list = [provice[2] for provice in self.desired_city['data']['parents']]
        self.provice_list.insert(0, '')
        self.provice_comb.addItems(self.provice_list)

    def update_qr(self):
        def get_qr_func():
            pix_map = QPixmap('qr.jpg')
            self.qr_label.setPixmap(pix_map)
            self.qr_label.setScaledContents(True)

        get_qr_thread = GetQRThread()
        get_qr_thread.get_qt_img_signal.connect(get_qr_func)
        get_qr_thread.start()

    def get_cookie(self):
        # 未扫码 ,成功, 已过期
        def get_cookie_func(status):
            if status == 200:
                self.login_status_bro.setText('登录成功！！！')
                self.pushButton.setEnabled(True)
            elif status == 201:
                self.login_status_bro.setText('验证码已过期，请刷新验证码后再登录！！！')
                self.pushButton.setEnabled(False)
            elif status == 202:
                self.login_status_bro.setText('未扫码，请使用微信扫码登录！！！')
                self.pushButton.setEnabled(False)

        get_cookie_thread = GetCookieThread()
        get_cookie_thread.get_cookie_signal.connect(get_cookie_func)
        get_cookie_thread.start()

    def set_city_items(self):
        provice_name = self.provice_comb.currentText()
        if provice_name:
            for provice in self.desired_city['data']['parents']:
                if provice[2] == provice_name:
                    self.provice_index = self.desired_city['data']['parents'].index(provice)
                    break

            self.city_comb.clear()
            self.city_list = [city[2] for city in self.desired_city['data']['children'][self.provice_index]]
            self.city_list.insert(0, '')
            self.city_comb.addItems(self.city_list)
        else:
            self.provice_index = ''
            self.city_comb.clear()

    def set_area_items(self):
        city_name = self.city_comb.currentText()
        if city_name:
            for city in self.desired_city['data']['children'][self.provice_index]:
                if city[2] == city_name:
                    self.city_index = self.desired_city['data']['children'][self.provice_index].index(city)
                    break

            self.area_comb.clear()
            self.area_list = [area[2] for area in self.desired_city['data']['leaves'][self.provice_index][self.city_index]]
            self.area_list.insert(0, '')
            self.area_comb.addItems(self.area_list)
        else:
            self.city_index = ''
            self.area_comb.clear()

    def talents_search(self):
        # 获取输入
        my_setting.career = self.career_edit.text()
        my_setting.work_type = self.work_type_edit.text()
        my_setting.company_name = self.comp_edit.text()
        my_setting.major_name = self.major_edit.text()

        area_name = self.area_comb.currentText()

        if area_name:
            for area in self.desired_city['data']['leaves'][self.provice_index][self.city_index]:
                if area[2] == area_name:
                    self.area_index = self.desired_city['data']['leaves'][self.provice_index][self.city_index].index(
                        area)
                    my_setting.desired_city = area[0]
                    break
        else:
            if self.city_comb.currentText():
                my_setting.desired_city = self.desired_city['data']['children'][self.provice_index][self.city_index][0]
            else:
                if self.provice_comb.currentText():
                    my_setting.desired_city = self.desired_city['data']['parents'][self.provice_index][0]
                else:
                    my_setting.desired_city = ''

        def get_summary_func(summary_dict):
            self.exmple_display_bro.setText('【总数：{0}】\n'.format(summary_dict['total']) + '【' + str(summary_dict['resume_list']) + '】')

        get_summary_thread = GetSummaryThread()

        get_summary_thread.get_summary_signal.connect(get_summary_func)
        get_summary_thread.start()

    def resume_spider(self):
        self.spider_thread = SpiderThread(self)
        self.spider_thread.set_delay()
        self.spider_thread.start()

    def stop_spider(self):
        self.spider_thread.stop_spider()

    def clear_result_browser(self):
        self.result_bro.clear()


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)

    zhilian = ZhiLianSpider()
    zhilian.show()

    sys.exit(app.exec_())
