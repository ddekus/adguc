import requests, random, json, string
from datetime import datetime
from subprocess import Popen, PIPE
import time

class McDonaldsCoupon:

    def __init__(self):
        # Application coupons API
        self.DEVICEREGISTRATION_URL = "https://con-West-Europe-GMA.vmobapps.com/v3/DeviceRegistration"
        self.EMAILREGISTRATION_URL = "https://con-West-Europe-GMA.vmobapps.com/v3/emailRegistrations"
        self.REDEEMEDOFFERS = "https://con-West-Europe-GMA.vmobapps.com/v3/consumers/redeemedOffers"
        # Survey coupons API
        self.HASH = "https://mcdonalds.fast-insight.com/voc/bs/v6/italy/webhook?svid=GVQ8N&hash="
        self.SUBMIT = "https://voice.fast-insight.com/api/v1/s/submit"
        self.HEADERS = {
            "Content-Type": "application/json",
            "x-vmob-device_network_type": "wifi",
            "x-vmob-device_utc_offset": "+2:00",
            "x-vmob-application_version": "2561",
            "x-vmob-mobile_operator": "Telecom Italia Mobile",
            "x-vmob-cost-center": "merchantId587",
            "x-vmob-device_timezone_id": "Africa/Harare",
            "x-vmob-device_type": "a",
            "x-vmob-device": "lge LGM-V300K",
            "x-vmob-sdk_version": "4.37.2",
            "Accept": "application/json",
            "x-vmob-device_os_version": "5.1.1",
            #"x-vmob-authorization": "5853342c-d3ef-421c-b23d-5c6036b8ebd5",
            "Accept-Language": "it-IT",
            "x-vmob-device_screen_resolution": "720x1280",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 5.1.1; Nexus 6 Build/LYZ28N)",
            "Host": "con-West-Europe-GMA.vmobapps.com",
            "Connection": "Keep-Alive",
            "x-vmob-uid": "a6Gb3zVRMcNtqbDSZ_J_psINoJILobhES-Leg1e1ko" + self.random_characters(12, "L_lFeB9itX6g") + "==_",
        }
        self.HEADERS.update({"x-plexure-api-key": self.get_plexure_key(self.HEADERS["x-vmob-uid"])})
        self.authorization = ""

    @staticmethod
    def random_characters(size, scope=string.ascii_letters + string.digits):
        random_string = ''.join([random.choice(scope)
                                 for n in range(size)])
        return random_string

    @staticmethod
    def is_working(coupon):
        return "Errore" not in coupon

    @staticmethod
    def is_italian_coupon(coupon):
        return coupon['Mercato'] == "587" or coupon['Mercato'] == 587

    @staticmethod
    def get_plexure_key(x_vmob_uid):
        return Popen([r'C:\Program Files\Java\jdk-12.0.1\bin\java.exe',
                      '-Dfile.encoding=UTF-8',
                      '-classpath',
                      r'Main',
                      'Main',
                      x_vmob_uid],
                     stdout=PIPE).stdout.read().decode('utf-8').splitlines()[0]

    def get_randomauthenticationdata_device(self):
        randomauthenticationdata_device = {
            "username": self.random_characters(21, "Q3psgEGOmDThosb2t48bR") + "R0OFtT1j11MOS-Leg1e1koL9HbgBJjPD1Q==_",
            "password": self.random_characters(21, "eLf7GWgA8_MuTr0CybW03") + "0OFtT1j11MOS--Leg1e1koL9HbgBJjPD1Q==_",
            "grant_type": "password"
        }
        return json.dumps(randomauthenticationdata_device)

    def get_randomauthenticationdata_user(self):

        emailAddress = self.random_characters(10, string.ascii_lowercase) + "@gmail.com"
        password = self.random_characters(10, string.ascii_lowercase)
        firstName = self.random_characters(7, string.ascii_lowercase)
        lastName = self.random_characters(8, string.ascii_lowercase)

        randomauthenticationdata_user = {
            "emailRegistration": {
                "emailAddress": emailAddress,
                "firstName": firstName,
                "gender": "",
                "lastName": lastName,
                "password": password,
                "tagValueAddReferenceCodes": ["merchantId587"]
            },
            "grant_type": "password",
            "password": password,
            "username": emailAddress
        }
        return json.dumps(randomauthenticationdata_user)

    def get_authorizationtoken_device(self):
        headers = self.HEADERS.copy()
        r = requests.post(self.DEVICEREGISTRATION_URL,
                          data=self.get_randomauthenticationdata_device(),
                          headers=headers)

        return json.loads(r.text)['access_token']

    def get_authorizationtoken_user(self):
        headers = self.HEADERS.copy()
        r = requests.post(self.EMAILREGISTRATION_URL,
                          data=self.get_randomauthenticationdata_user(),
                          headers=headers)

        return json.loads(r.text)['access_token']

    def get_authenticatedheaders(self, mode = 0):
        self.authorization = self.get_authorizationtoken_device() if mode == 0 else self.get_authorizationtoken_user()
        headers = self.HEADERS.copy()
        headers.update({"Authorization": "bearer " + self.authorization})
        return headers

    def get_application_coupon(self, id):

        def get_couponrequest_data(id):
            return json.dumps({"offerInstanceUniqueId": "{}".format(id),
                                "offerId" : id})

        coupon_request = requests.post(self.REDEEMEDOFFERS,
                          data=get_couponrequest_data(id),
                          headers=self.get_authenticatedheaders())

        # Controllo se la richiesta ha generato un coupon valido
        if 'error' not in coupon_request.json():
            coupon = {
                "ID": id,
                "Titolo": coupon_request.json()['title'],
                "Descrizione": coupon_request.json()['description'],
                "Codice": coupon_request.json()['redemptionText'],
                "Mercato": coupon_request.json()['merchantId']
            }
        elif 'error' in coupon_request.json():
            coupon = {
                "Errore": coupon_request.json()['error']
            }
        else:
            coupon = {
                "Errore": coupon_request.text
            }

        return coupon

    def get_survey_coupon(self, id):

        def get_pdfcouponrequest_request(hash):
            return self.HASH + hash.json()["data"]["fileHash"]

        def get_submit_data_request(ansobj, csrftoken):
            return {
                "ansobj": ansobj,
                "csrftoken": csrftoken
            }

        def get_submit_cookie_request(csrftoken):
            return {
                "csrftoken": csrftoken
            }

        def get_coupon_data_request(invoice, token):
            return {
                    "invoice": invoice,
                    "token": token.headers["location"].split("=")[1]
            }

        invoice = self.random_characters(13, string.ascii_uppercase)
        submit_body = '{"svid":"GVQ8N","initime":"2019-04-02 14:52:15","svend":"thankyou","endsopts":"","sbj_1001829":["it"],"sbj_1001830":["0031"],"sbj_1002660":["' + datetime.now().strftime("%Y-%m-%d")\
                      +'"],"sbj_1002365":["' + invoice \
                      + '"],"sbj_1001833":["opt_1006166"],"sbj_1001834":["opt_1006168"],"sbj_1001835":["opt_1006173"],"sbj_1001836":["opt_1006178"],"sbj_1001840":["opt_1006201"],' \
                        '"sbj_1001842":["opt_1006209"],"sbj_1001844":["opt_1006217"],"sbj_1001838":["opt_1006190"],"sbj_1001890":["opt_1006387"],"sbj_1001850":["AAAAA"],"sbj_1005670":' \
                        '["opt_1019194"],"sbj_1005671":["opt_1019196"],"sbj_1005457":["opt_1018670"],"sbj_1001851":["opt_1006386"],"sbj_1001852":["opt_1006244"],"sbj_1001853":["opt_1006248"],' \
                        '"sbj_1005451":["80100"],"sbj_1001860":["' + id + '"]}'

        csrftoken = self.random_characters(13, "r0d86asa1gs3v")

        submit_request = requests.post(self.SUBMIT,
                                       data=get_submit_data_request(submit_body, csrftoken),
                                       cookies=get_submit_cookie_request(csrftoken))

        pdf_coupon_request = requests.get(get_pdfcouponrequest_request(submit_request),
                                          allow_redirects=False)

        coupon = requests.post("https://mcdonalds.fast-insight.com/voc/bs/api/italy/coupon",
                               data=get_coupon_data_request(invoice, pdf_coupon_request))

        if coupon.status_code != 500:
            if "status" in coupon.json() and coupon.json()["status"] == 200:
                coupon = {
                    "Codice": coupon.json()['data']['code'],
                    "URL": pdf_coupon_request.headers['location']
                }
            else:
                coupon = {
                    "Errore": coupon.text
                }

            return coupon
        else:
            coupon = {
                "Errore": coupon.text
            }
            return coupon


if __name__ == "__main__":
    mc = McDonaldsCoupon()
    coupon = mc.get_application_coupon(15956)
    print(coupon)


