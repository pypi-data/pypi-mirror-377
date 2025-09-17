import time
import requests
import requests.cookies
import hashlib
import base64
from Crypto.Cipher import AES
from ustcjwxt import log, request_info


class StudentSession:
    def __init__(self, username=None, password=None, session=None, smcode_hook=None):
        self.request_session = requests.Session()
        self.password_useable = False
        self.cache = dict()
        self.smcode_hook = smcode_hook
        for k, v in request_info.base_cookie.items():
            self.request_session.cookies.set(k, v)
        # login with session
        if session is not None:
            self.login_with_session(session)
        # login with username and password
        if username is not None and password is not None:
            self.login_with_password(username, password)
        elif username is not None or password is not None:
            log.log_error('username 和 password 必须同时提供')
    
    def get_cookies(self) -> requests.cookies.RequestsCookieJar:
        return self.request_session.cookies

    def get(self, url, params=None, data=None, headers=request_info.header_uaonly, **kwargs) -> requests.Response:
        response = self.request_session.get(url, headers=headers, params=params, data=data, **kwargs)
        if response.url.startswith('https://jw.ustc.edu.cn/login'):
            log.log_warning(f'get {url} redirect to {response.url}')
            if self.password_useable:
                log.log_warning('session 无效, 正在尝试重新用密码登录')
                self.clear_cache()
                if self.login_with_password(self.username, self.password):
                    response = self.request_session.get(url, headers=headers, params=params, data=data, **kwargs)
                else:
                    log.log_error('密码登录失败')
            else:
                log.log_error('session 无效')
                self.clear_cache()
        return response
    
    def post(self, url, data=None, params=None, headers=request_info.header_uaonly, content_type='', **kwargs) -> requests.Response:
        if content_type:
            headers['content-type'] = content_type + '; charset=UTF-8'
        response = self.request_session.post(url, headers=headers, params=params, data=data, **kwargs)
        if response.url.startswith('https://jw.ustc.edu.cn/login'):
            log.log_warning(f'post {url} redirect to {response.url}')
            if self.password_useable:
                log.log_warning('session 无效, 正在尝试重新用密码登录')
                self.clear_cache()
                if self.login_with_password(self.username, self.password):
                    response = self.request_session.post(url, headers=headers, params=params, data=data, **kwargs)
                else:
                    log.log_error('密码登录失败')
            else:
                log.log_error('session 无效')
                self.clear_cache()
        return response

    def clear_cache(self) -> None:
        self.request_session.cookies.clear()
        for key in request_info.base_cookie:
            self.request_session.cookies.set(key, request_info.base_cookie[key])
        self.cache = dict()

    def login_with_password(self, username: str, password: str, smcode_hook=None) -> bool:
        self.clear_cache()
        self.username = username
        self.password = password
        smcode_hook = smcode_hook or self.smcode_hook
        # 自 2024.7 之后，教务系统经历了一次彻底的更新
        # passport.ustc.edu.cn ---> id.ustc.edu.cn
        
        response = self.get('https://id.ustc.edu.cn/cas/login?service=https:%2F%2Fjw.ustc.edu.cn%2Fucas-sso%2Flogin')
        aes_key = response.text.split('<p id="login-croypto">')[1].split('</p>')[0]
        aes_key = base64.b64decode(aes_key)
        execution = response.text.split('<p id="login-page-flowkey">')[1].split('</p>')[0]
        
        log.log_debug(f'获取到一次性秘钥: aes_key = {aes_key.hex()}')
        log.log_debug(f'获取到追溯 flowkey: execution = {execution[:36+1+5]}...{execution[-8:]}')
                
        platform_info = {
            "userAgent": request_info.header_uaonly['User-Agent'],
            "timezone": "\"Asia/Shanghai\"",
            "platform": "\"Win32\"",
            "language": "\"zh-CN\"",
            "screenResolution": "[1080,1920]"
        }

        response = self.post('https://analytics.ustc.edu.cn/fp', json=platform_info)
        risk_value = response.json()['responsetoken']
        log.log_debug(f'获取到 challenge token: {risk_value = } (status_code = {response.status_code})')
        
        def pad(x):
            t = 16 - len(x) % 16
            return x + bytes([t]) * t

        aes = AES.new(aes_key, mode=AES.MODE_ECB)
        encrypted_password = aes.encrypt(pad(password.encode()))
        captcha_payload = aes.encrypt(pad('{}'.encode()))
        risk_payload = aes.encrypt(pad(f'{{"token":"{risk_value}","groupId":""}}'.encode()))

        log.log_debug(f'已生成并加密认证三元组 (password, captcha_payload, risk_payload)')

        login_form = {
            'username': username,
            'type': 'UsernamePassword',
            '_eventId': 'submit',
            'geolocation': '',
            'execution': execution,
            'captcha_code': '',
            'croypto': base64.b64encode(aes_key).decode(),
            'password': base64.b64encode(encrypted_password).decode(),
            'captcha_payload': base64.b64encode(captcha_payload).decode(),
            'risk_payload': base64.b64encode(risk_payload).decode(),
            'targetSystem': 'sso',
            'siteId': 'sourceId',
            'riskEngine': 'true'
        }
        
        response = self.post('https://id.ustc.edu.cn/cas/login', data=login_form)
        log.log_debug(f'login redirect to {response.url}')
        log.log_debug(f'login response status code {response.status_code}')
        if '<p id="current-login-type">smsLogin</p>' in response.text:
            # 检测二步验证相关设置
            log.log_info('需要二步验证')
            if smcode_hook is None:
                log.log_error('无法获取验证码, 登录失败')
                log.log_error('suggest: 请传入钩子函数 smcode_hook 以获取验证码')
                return False
            # 获取验证码
            phone_number = response.text.split('<p id="phone-number">')[1].split('</p>')[0]
            execution_2 = response.text.split('<p id="login-page-flowkey">')[1].split('</p>')[0]
            need_sms = {
                'businessNo': "0008",
                'phone': phone_number
            }
            headers = {
                'Csrf-Key': 'IZXwJDXbypKPSqpSUFKTWwAaBVBmeGYP',
                'Csrf-Value': '1c1b43a001d568b035b484d21098121c',
            }
            log.log_debug(f'获取到追溯 flowkey: execution_2 = {execution_2[:36+1+10]}...{execution_2[-7:]}')
            log.log_info(f'正在向手机 {phone_number} 发送验证码短信')
            response = self.post('https://id.ustc.edu.cn/cas/api/protected/sms/publicNoToken/sendSmsCode', json=need_sms, headers=headers)
            log.log_debug(f'二维码发送请求 | 返回: {response.text}')
            sms_value = smcode_hook()
            second_form = {
                'username': username,
                'password': sms_value,
                'type': 'smsLogin',
                '_eventId': 'submit',
                'geolocation': '',
                'execution': execution_2,
                'captcha_code': '',
                'trustDevice': 'true'
            }
            response = self.post('https://id.ustc.edu.cn/cas/login', data=second_form)
        else:
            log.log_info('不需要二步验证')
            
        if self.check_cookie_useable():
            log.log_info('登陆成功')
            self.password_useable = True
            time.sleep(1) # 应等待教务系统缓存更新
            return True
        else:
            log.log_error('username 和 password 无效, 登陆失败')
            self.password_useable = False
            self.clear_cache()
            return False

    def login_with_session(self, session: str) -> bool:
        self.clear_cache()
        self.request_session.cookies['SESSION'] = session
        if not self.check_cookie_useable():
            log.log_error('session 无效')
            self.clear_cache()
            return False
        return True
        
    def check_cookie_useable(self) -> bool:
        response = self.get('https://jw.ustc.edu.cn/my/profile')
        if response.url.startswith('https://jw.ustc.edu.cn/login'):
            return False
        return True
    
    # return binary data with jpg format(will not cache avatar)
    def get_student_avatar(self) -> bytes:
        response = self.get('https://jw.ustc.edu.cn/my/avatar')
        return response.content

    def get_student_info(self, force_retrieve = False) -> dict:
        if not force_retrieve and 'profile_info' in self.cache:
            return self.cache['profile_info']
        response = self.get('https://jw.ustc.edu.cn/my/profile')
        stuinfo_list = ['名称', '性别', '证件类型', '证件号', '生日', '政治面貌', '邮箱', '电话', '手机', '地址', '邮编', '简介']
        stuinfo = {}
        for dtype in stuinfo_list:
            specify = f'<span class="pull-left"><strong>{dtype}</strong></span>'
            p = response.text.find(specify)
            if p == -1:
                log.log_warning(f'get_student_info: {dtype} not found')
                continue
            data = response.text[p+len(specify):].split('</span>')[0].split('<span>')[-1]
            stuinfo[dtype] = data
        self.cache['profile_info'] = stuinfo
        return stuinfo
    
    def get_student_ID(self, force_retrieve = False) -> str:
        if not force_retrieve and 'student_ID' in self.cache:
            return self.cache['student_ID']
        # 从选课界面中获得学号
        response = self.get('https://jw.ustc.edu.cn/for-std/course-select')
        if response.url.startswith('https://jw.ustc.edu.cn/for-std/course-select/turns/'):
            p = response.text.find('<span class="pull-left"><strong>学号</strong></span>')
            if p != -1:
                p = response.text.find('<span>', p + 50) + 6
                q = response.text.find('</span>', p)
                student_ID = response.text[p:q]
                self.cache['student_ID'] = student_ID
                return student_ID
        log.log_warning('未能在选课界面中找到学号')
        # 从课表页面获取学号
        courseTablePage = self.get(f'https://jw.ustc.edu.cn/for-std/course-table/info/{self.get_student_assocID()}').text
        p = courseTablePage.find('<h2 class="info-title">')
        if p != -1:
            log.log_debug('从课表页面成功获取学号')
            student_ID = courseTablePage[p:].split('(')[1].split(')')[0]
            self.cache['student_ID'] = student_ID
            return student_ID
        log.log_warning('未能在课表页面找到学号')
        # 从 cookie 中获得学号
        if 'uc' in self.request_session.cookies:
            log.log_debug('从 cookies 中成功获取学号')
            student_ID = self.request_session.cookies['uc']
            self.cache['student_ID'] = student_ID
            return student_ID
        log.log_warning('未能在 cookies 中找到学号')
        # 均失败
        log.log_warning('未能获得学号')
        return ''
    
    def get_student_assocID(self, force_retrieve = False) -> int:
        if not force_retrieve and 'assocID' in self.cache:
            return self.cache['assocID']
        response = self.get('https://jw.ustc.edu.cn/for-std/course-select')
        if response.url.startswith('https://jw.ustc.edu.cn/for-std/course-select/turns/'):
            assocID = int(response.url.split('/')[-1])
            log.log_info(f'学生唯一 assocID 获取成功: {assocID}')
            self.cache['assocID'] = assocID
            return assocID
        log.log_error(f'学生唯一 assocID 获取失败')
        return -1