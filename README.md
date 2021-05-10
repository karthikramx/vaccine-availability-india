# vaccine-availbilty-india
A python application to check for vaccine availability on cowin website

The main.py contains a class with methods to 
  + drive the chrome browser
  + accept pincode and weeks as arguments to extract data from the website and store it in a csv file
  + extract informaiton about date, hospital and vaccine type for all age groups and stores it in a notification string
  + A push buttlet function to send notifications to your phone

The available vaccine information in stores in self.notification variable

Dependencies/requirements
  + pandas
  + selenium
  + json
  + BeautifulSoup
  + time

Other instructions
  + You will have to replace the chromedriver.exe with your browser type / version
  + You will have to create a pustbullet account and download the app to get notifications on the phone
  + replace the push_bullet_token with your push button token


Links
  + Chrome driver download: https://chromedriver.chromium.org/downloads - check your chrome browser version in browser settings
  + push bulltet: https://www.pushbullet.com/ - pretty self explanatory


