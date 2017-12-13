import praw
import requests
import threading
import time

start_time = time.time()

# You must create a reddit application as script mode and provide your own client id, secret id and must match your\
# username and password
Client_id = ''
Client_secret = ''
Username = ''
Password = ''

reddit = praw.Reddit(client_id=Client_id,
                     client_secret=Client_secret,
                     username=Username,
                     password=Password,
                     user_agent='subreddit Image downloader by /u/Return_Foo_Bar')
# Just to confirmed you are logged in
print(reddit.user.me())
post_list = []
threads = []


# Keeps track of completed downloads
class Counter(object):
    def __init__(self, start=1):
        self.lock = threading.Lock()
        self.value = start

    def increment(self):
        self.lock.acquire()
        try:
            self.value = self.value + 1
        finally:
            self.lock.release()


# Currently set to download top posts of a subreddit with "EarthPorn" and 10 as the default arguments for sub and limit.
def get_top_posts(s_reddit="EarthPorn", limit=10):
    count = 0
    for submission in reddit.subreddit(s_reddit).top(limit=limit):
        print(f"Adding {submission.url} to list")
        post_list.append({submission.title: submission.url})
        count += 1
        print(f"{count} of {limit}.\n\n")


def print_list():
    for url in post_list:
        print(url)


def download_image(name, address, c):
    img = requests.get(address)
    # Checks to see if the URL ends with an image format and appends it to the first 30 chars of title.
    if address.endswith(".jpg") or address.endswith(".png") or address.endswith(".gif") or address.endswith(".jpeg"):
        print(f"{c.value} of {len(post_list)}\nDownloading {name} from {address}.")
        with open(('images/' + name[:30] + address[-4:]), 'ab') as i:
            i.write(img.content)
        c.increment()

    # If URL does not end with an image extension it adds a .JPG extension because why not?
    else:
        print(f"{c.value} of {len(post_list)}\nDownloading {name} from {address}.")
        with open(("images/" + name[:30] + ".jpg"), "ab") as i:
            i.write(img.content)
        c.increment()


def download_images_from_list(c):
    # iterates to the list of dictionaries and begins a thread targeting function download_image and adds to the counter
    for i in post_list:
        for name, address in i.items():
            t = threading.Thread(target=download_image, args=(name, address, c))
            t.start()
            threads.append(t)


if __name__ == "__main__":

    counter = Counter()
    get_top_posts()
    download_images_from_list(counter)
    main_thread = threading.currentThread()
    for t in threading.enumerate():
        if t is not main_thread:
            t.join()
    print("SUCCESS!")
    print('{0:0.1f}'.format(time.time() - start_time))
