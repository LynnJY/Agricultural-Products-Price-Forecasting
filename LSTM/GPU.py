from selenium import webdriver
# 初始化浏览器为chrome浏览器
browser = webdriver.Chrome()
# 指定绝对路径的方式（可选）
path = r'C:\Users\Gdc\.wdm\drivers\chromedriver\win32\96.0.4664.45\chromedriver.exe'
browser = webdriver.Chrome(path)
# 关闭浏览器
browser.close()
