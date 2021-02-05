import urllib.request
def htmlget(x):
    webUrl = urllib.request.urlopen(x)
    html = webUrl.read()
    print(html)

if __name__ == "__main__":
    x = str(input("Enter the URL, you want the html from: "))
    htmlget(x)