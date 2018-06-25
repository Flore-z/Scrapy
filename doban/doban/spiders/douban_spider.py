import scrapy
import urllib
from PIL import Image


class DoubanLoginSpider(scrapy.Spider):
    name = 'douban'
    allowed_domains = ['douban.com']
    start_urls = ['http://www.douban.com/']
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "\
                            "Chrome/55.0.2883.87 Safari/537.36"}    # 设置浏览器用户代理

    def start_requests(self):
        '''
        重写start_requests，请求登录页面
        '''
        return [scrapy.Request("https://accounts.douban.com/login",
                               headers=self.headers,
                               meta={"cookiejar":1},
                               callback=self.post_login,
                               # dont_filter=True
                               )]

    def post_login(self, response):
        '''
        登录表单填充，查看验证码
        '''
        print("cookie1 =", response.headers.getlist('Set-cookie'))
        print("准备登陆...")
        captcha_id = response.xpath('//*[@id="lzform"]/div[5]/div/div/input[2]/@value').extract_first()
        captcha_image_url = response.xpath('//*[@id="captcha_image"]/@src').extract_first()
        if captcha_image_url is None:
                print("登录时无验证码")
                formdata = {
                            "source": "index_nav",
                            "form_email": "********@sina.com",
                            "form_password": "******",
                        }
        else:
                print("登录时有验证码")
                save_image_path = "E:\Scrapy_workspace\doban\captcha.jpg"
                urllib.request.urlretrieve(captcha_image_url, save_image_path)  # 将图片验证码下载到本地
                try:
                        im = Image.open('captcha.jpg')  # 打开图片，以便我们识别图中验证码
                        im.show()
                except:
                        pass

                captcha_solution = input('输入图片验证码:')   # 手动输入验证码
                formdata = {
                                "source": "None",
                                "redir": "https://www.douban.com",
                                "form_email": "kathyyx11@sina.com",
                                "form_password": "zyq1369#",
                                "captcha-solution": captcha_solution,
                                "captcha-id": captcha_id,
                                "login": "登录",
                        }
        print("登录中...")
        # 提交表单
        return scrapy.FormRequest.from_response(response,
                                                meta={"cookiejar":response.meta["cookiejar"]},
                                                headers=self.headers,
                                                formdata=formdata,
                                                callback=self.after_login,
                                                # dont_filter=True
                                                )

    def after_login(self, response):
        '''
        验证登录是否成功
        '''
        print("cookie2 =", response.headers.getlist('Set-cookie'))
        account = response.xpath('//a[@class="bn-more"]/span/text()').extract_first()
        if account is None:
            print("登录失败")
        else:
            print(u"%s 登录成功" % account)
            filename = "my-douban.html"
            with open(filename, 'wb') as f:
                f.write(response.body)
            self.log("Saved file %s" % filename)
