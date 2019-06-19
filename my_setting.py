Headers = {
    'Host': 'rd5.zhaopin.com',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Origin': 'https://rd5.zhaopin.com',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://rd5.zhaopin.com/custom/searchv2/result',
    'Accept-Encoding': 'gzip, deflate',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)',
    'Cookie': None,
}


LoginHeaders = {
    'Host': 'passport.zhaopin.com',
    'Accept': 'text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://passport.zhaopin.com/wxLogin?bkurl=https%3A%2F%2Frd5.zhaopin.com%2Flogin%2Fbind%2Faccount%3Fbkurl%3Dhttps%253A%252F%252Frd5.zhaopin.com%26isValidate%3Dfalse',
    'Accept-Encoding': 'gzip, deflate',
}

validate_id = None

# login_status = False

resume_result_list = list()

xzr_id = None

career = ''

work_type = ''

company_name = ''

major_name = ''

desired_city = ''

resume_info = 'init'

