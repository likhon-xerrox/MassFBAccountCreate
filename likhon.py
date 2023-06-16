import mechanize
import requests
import re
import logging
import argparse
import sys
import time
import telegram
from telegram import ParseMode

class Create:
    def __init__(self):
        logging.basicConfig(
            level={
                True: logging.DEBUG,
                False: logging.INFO
            }[arg.level],
            format='\r%(levelname)s:%(name)s: %(message)s'
        )
        self.create_total = 0
        self.blacklist_email = []  # Add any blacklisted email domains here
        self.temp_email_url = 'https://tempmail.net'

        self.telegram_bot_token = '6271169252:AAG31mEfayv1qxI7Tiquema0mzj1XWumh2Q'  # Replace with your Telegram bot token
        self.telegram_channel_id = '-1001768382602'  # Replace with your Telegram channel username or ID

        self._main()

    def _browser_options(self):
        br = mechanize.Browser()
        br.set_handle_robots(False)
        br.set_handle_equiv(True)
        br.set_handle_referer(True)
        br.set_handle_redirect(True)
        if arg.proxy:
            br.set_proxies({"http": arg.proxy, "https": arg.proxy})
        br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=5)
        br.addheaders = [('User-agent',
                          'Mozilla/5.0 (Linux; Android 5.0; ASUS_T00G Build/LRX21V) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.98 Mobile Safari/537.36')]
        return br

    def _get_info_account(self):
        logging.info('Looking for account information')
        res = requests.get('https://randomuser.me/api').json()

        pwd = res['results'][0]['login']['password']
        return {
            'username': res['results'][0]['login']['username'],
            'password': pwd + '-zvtyrdt.id' if len(pwd) < 6 else pwd,
            'firstname': res['results'][0]['name']['first'],
            'lastname': res['results'][0]['name']['last'],
            'gender': '1' if res['results'][0]['gender'] == 'female' else '2',
            'date': res['results'][0]['dob']['date'].split('T')[0].split('-')
        }

    def _create_account_facebook(self, email):
        data = self._get_info_account()

        self._password = data['password']
        logging.info('Name: %s', data['firstname'] + ' ' + data['lastname'])
        logging.info('Creating a Facebook account')
        self.br.open('https://mbasic.facebook.com/reg/?cid=102&refid=8')

        self.br.select_form(nr=0)
        self.br.form['firstname'] = data['firstname'] + ' ' + data['lastname']
        try:
            self.br.form['reg_email__'] = email
        except mechanize._form_controls.ControlNotFoundError as ex:
            logging.warning(str(ex))
            return False

        self.br.form['sex'] = [data['gender']]
        self.br.form['birthday_day'] = [data['date'][2][1:] if data['date'][2][0] == '0' else data['date'][2]]
        self.br.form['birthday_month'] = [data['date'][1][1:] if data['date'][1][0] == '0' else data['date'][1]]
        self.br.form['birthday_year'] = [data['date'][0]]
        self.br.form['reg_passwd__'] = data['password']
        self.br.submit()

        if 'captcha' in self.br.response().read().lower().decode('utf-8'):
            sys.exit(logging.error('You are caught making fake accounts and spamming users. '
                                    'Sorry, try again tomorrow... Goodbye!\n'))

        for i in range(3):
            self.br.select_form(nr=0)
            self.br.submit()

        failed_message = re.findall(r'id="registration-error"><div class="bl">(.+?)<', self.br.response().read().decode('utf-8'))
        if failed_message:
            logging.error(failed_message[0])
            return False

        return True

    def _check_email_fb(self, email):
        self.br.open('https://mbasic.facebook.com/login/identify')
        self.br._factory.is_html = True
        self.br.select_form(nr=0)
        self.br.form['email'] = email
        self.br.submit()

        if 'recover_method' in self.br.response().read().decode('utf-8'):
            logging.info('Waiting for the OTP code')
            time.sleep(15)  # Wait for 15 seconds to receive the OTP code

            # Fetch the OTP code from the email
            res_em = self._open_temp_mail()
            otp_code = self._get_otp_code(res_em)

            if otp_code:
                logging.info('OTP Code: %s', otp_code)

                # Submit the OTP code
                self.br._factory.is_html = True
                self.br.select_form(nr=0)
                self.br.form['n'] = otp_code
                self.br.submit()

                self._send_to_telegram(email, self._password, otp_code)  # Send to Telegram channel
                return True
            else:
                logging.warning('OTP code not found in email')
                return False

        return True

    def _send_to_telegram(self, email, password, otp_code):
        bot = telegram.Bot(token=self.telegram_bot_token)
        
        message = f"<b>New Account Created!</b>\n\n" \
                  f"<b>Account:</b>\n" \
                  f"Name: {data['firstname']} {data['lastname']}\n" \
                  f"Email: {email}\n\n" \
                  f"<b>Password:</b>\n" \
                  f"<code>{password}</code>\n\n" \
                  f"<b>OTP Code:</b>\n" \
                  f"<code>{otp_code}</code>"
        
        bot.send_message(chat_id=self.telegram_channel_id, text=message, parse_mode=ParseMode.HTML)

    def _open_temp_mail(self):
        return self.br.open(self.temp_email_url).read()

    def _find_email(self, text):
        decoded_text = text.decode('utf-8')
        return re.findall(r'value="(.+@.+)"', decoded_text)[0]

    def _get_otp_code(self, text):
        decoded_text = text.decode('utf-8')
        otp_codes = re.findall(r'Your OTP code is: ([0-9]+)', decoded_text)
        if otp_codes:
            return otp_codes[0]
        return None

    def _save_to_file(self, email, password):
        with open('akun.txt', 'a') as f:
            f.write('%s|%s\n' % (email, password))

    def _main(self):
        while True:
            self.br = self._browser_options()
            logging.info('Searching for new emails')

            email_found, check, max_ = False, True, 0
            while True:
                res_em = self._open_temp_mail()
                self._mail = self._find_email(res_em)

                if '@' + self._mail.split('@')[1].split('.')[0] in self.blacklist_email:
                    logging.error('Blacklisted email: %s', self._mail)
                    break

                if not email_found:
                    logging.info('Obtained email: %s', self._mail)
                    if self._check_email_fb(self._mail):
                        if self._create_account_facebook(self._mail):
                            email_found = True
                    else:
                        logging.info('Waiting for incoming email')

                if max_ == 10:
                    logging.error('No response!')
                    break

                if check and email_found:
                    self.create_total += 1
                    logging.info('Account created:\n\t   Email: %s\n\t   Password: %s',
                                 self._mail, self._password)
                    self._save_to_file(self._mail, self._password)
                    check = False
                    max_ += 1
                else:
                    break

            if self.create_total == arg.count:
                logging.info('Finished\n')
                break


if __name__ == '__main__':
    parse = argparse.ArgumentParser()
    parse.add_argument('-c', metavar='<COUNT>', type=int, dest='count',
                       help='number of accounts you want to create')
    parse.add_argument('-p', metavar='<IP:PORT>', dest='proxy',
                       help='set proxy')
    parse.add_argument('--debug', action='store_true', dest='level',
                       help='set logging level to debug')
    arg = parse.parse_args()

    if arg.count:
        try:
            print('')  # new line
            Create()
        except KeyboardInterrupt:
            logging.error('User interrupted...\n')
    else:
        parse.print_help()
