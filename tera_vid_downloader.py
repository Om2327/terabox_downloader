import requests
import time
import re
# import requests
import json
# import time
from pprint import pprint
terabox_api_url = 'https://terabox-dl.qtcloud.workers.dev/api/get-download'

TOKEN = input("ENTER TOKEN : ")
directory = "" # path for videos to download
base_url =  f"https://api.telegram.org/{TOKEN}"
terabox_api_url = 'https://terabox-dl.qtcloud.workers.dev/api/'
get_update = "/getUpdates"
send_message = "/sendMessage"

def read_msg():

  parameters = {
      "offset" : " "
  }

  resp = requests.get(base_url + "/getUpdates", data = parameters)
  data = resp.json()
  print(data)


def send_reply_msg(message_id, answer: str, chat_id ):
  parameters = {
      "chat_id" : chat_id,
      "text" : answer,
      "reply_to_message_id" : message_id
  }

  resp = requests.get(base_url + "/sendMessage", data = parameters)
  print(resp.text)


def send_edit_msg(message_id, answer, chat_id):
    url = f"{base_url}/editMessageText"
    parameters = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": answer,
    }
    resp = requests.post(url, data=parameters)
    # pprint(resp.json())
    response_data = resp.json()
    edited_msg = answer
    message_id = response_data["result"]["message_id"]
    chat_id = response_data["result"]["chat"]["id"]
    original_message = response_data["result"]["text"]

    resp = {'message_id' : message_id, 'chat_id': chat_id ,'original_message' : original_message, 'edited_msg' : answer}
    print(f' Message Id ->" {message_id}, "\n Chat ID -> " {chat_id},"\n Original_message -> " {original_message}, "\n edited_msg -> " {answer}')


def check_url(url):
    match = re.search(r'/s/([^/]+)', url)
    if match:
        unique_identifier = match.group(1)
        print("Unique Identifier:", unique_identifier)
        return unique_identifier

    else:
        print("No match found in the URL.")
        return False

def send_Video(download_url , local_filename, caption, chat_id, message_id):


  response = requests.get(download_url)
  video_url = directory +local_filename+".mp4"


  if response.status_code == 200:
        # Open the local file in binary write mode and write the content from the response
          with open(video_url, 'wb') as file:
            file.write(response.content)

            parameters = {
                        "chat_id" : chat_id,
                        "caption" : caption,
                       "reply_to_message_id" : message_id
                    }

            files = {
                'document': (local_filename, open(video_url, 'rb')),
            }

            resp = requests.post(base_url+ "/sendDocument", data = parameters, files=files)

            send_reply_msg(message_id,chat_id,"Status" + str(response.status_code) + resp.text )
            print(resp.text)

                  # print(f"Downloaded video to {local_path}")
  else:
    print(f"Failed to download video. Status code: {response.status_code}")
    send_reply_msg(message_id, "Download Link : "+ download_url,chat_id)
    send_reply_msg(message_id,f"Failed to download video. Status code: {response.status_code}",chat_id)

from pprint import pprint
terabox_api_url = 'https://terabox-dl.qtcloud.workers.dev/api/get-download'



def get_download(short_url: str, pwd: str) -> str:
    url = 'https://terabox-dl.qtcloud.workers.dev/api/get-download'
    extData = get_info(short_url=short_url,pwd=pwd)
    print(extData)

    body = {
          'shareid': extData["shareid"],
          'uk': extData["uk"],
          'sign': extData["sign"],
          'timestamp': extData["timestamp"],
          'fs_id': extData["fs_id"],
      }

    headers = {
          'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
      }

    max_retries = 3  # Maximum number of attempts

    for attempt in range(1, max_retries + 1):
          try:
              response = requests.post(url, json=body, headers=headers)
              response.raise_for_status()
              data = response.json()
              if data['ok'] is False:
                  raise CustomError(data['message'])
              pprint(data)
              return data['downloadLink']

          except requests.exceptions.RequestException as e:
              return (f'Error making API request (attempt {attempt}/{max_retries})')

          except CustomError as e:
              print(f'{e} (attempt {attempt}/{max_retries})')

          if attempt < max_retries:
              time.sleep(2)
          else:
              return ('Max retries reached. Giving up.')


class CustomError(Exception):
    pass

def dl_lk(body):
      headers = {
          'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
      }
      max_retries = 3
      for attempt in range(1, max_retries + 1):
          try:
              response = requests.post(terabox_api_url, json=body, headers=headers)
              response.raise_for_status()
              data = response.json()
              if data['ok'] is False:
                  raise CustomError(data['message'])
              pprint(data)
              return data['downloadLink']

          except requests.exceptions.RequestException as e:
              return (f'Error making API request (attempt {attempt}/{max_retries})')

          except CustomError as e:
              print(f'{e} (attempt {attempt}/{max_retries})')

          if attempt < max_retries:
              time.sleep(2)
          else:
              return ('Max retries reached. Giving up.')


def get_info(short_url, pwd) -> dict: # returing metadata of terabox download link

      url = 'https://terabox-dl.qtcloud.workers.dev/api/get-info'

      params = {
          'shorturl': short_url,
          'pwd': pwd
      }
      dic = {"status" : True }
      try:
          response = requests.get(url, params=params)
          response.raise_for_status()

          data = response.json()
          # data = response.json()
          # print(data)
          fs_id = data["list"][0]["fs_id"]
          # print(data["list"][0]["filename"])
          dic["fileName"] = data["list"][0]["filename"]
          extracted_data = {
          "shareid": data.get("shareid"),
          "uk": data.get("uk"),
          "sign": data.get("sign"),
          "timestamp": data.get("timestamp"),
          "fs_id": fs_id  # Assuming there is only one item in the list
          }

          pprint(extracted_data)

          # return extracted_data
          dic["download_link"] = dl_lk( extracted_data)
          pprint(dic)
          # dic = {"download_link" : download_link, "filename" :fileName }
          return dic

      except requests.exceptions.RequestException as e:
          print(f'Error making API request: {e}')
          return dic
          # return None

def send_Video_directly(download_url, local_filename, caption, chat_id, message_id):
    response = requests.get(download_url)

    if response.status_code == 200:
        # Get the content of the downloaded video
        video_content = response.content

        parameters = {
            "chat_id": chat_id,
            "caption": caption,
            "reply_to_message_id": message_id
        }

        # Set the file's content type as 'video/mp4'
        files = {
            'document': (local_filename + '.mp4', video_content, 'video/mp4')
        }

        resp = requests.post(base_url + "/sendDocument", data=parameters, files=files)

        send_reply_msg(message_id, chat_id, "Status " + str(response.status_code) + resp.text)
        print(resp.text)
    else:
        print(f"Failed to download video. Status code: {response.status_code}")
        # print("Download link: ",download_url)
        send_reply_msg(message_id, "Download Link : "+ download_url,chat_id)
        send_reply_msg(message_id, f"Failed to download video. Status code: {response.status_code}", chat_id)


# 

# Initialize a variable to keep track of the latest update ID
latest_update_id = None

while True:
    # Make a request to get updates with an offset to only receive new updates
    url = f"https://api.telegram.org/{TOKEN}/getUpdates?offset={latest_update_id + 1 if latest_update_id else ''}"
    response = requests.get(url)
    text = 'No'
    if response.status_code == 200:
        data = response.json()
        print(data)
        if "result" in data and len(data["result"]) > 0:
            for update in data["result"]:
                latest_update_id = update["update_id"]
                message = update.get("message")
                # pprint(message)
                print(message.get("text"))
                text = message.get("text")
                message_id = message["message_id"]
                chat_id = message["chat"]["id"]
                send_reply_msg(message_id, "Please Wait while Processing >>>>",chat_id)


                if text != 'No':
                  if check_url(str(text)):
                      flag = check_url(str(text))
                      data = get_info(flag,'')
                      print("==========================================================")
                      print("data variable  ",data)
                     # send_reply_msg(message_id, "Download Link : ", data['download_link'],chat_id)

                      filename = data.get("fileName")
                      dwnl = data.get("download_link")
                      status = data.get("status")
                          # print(type(status))
                      if status:
                        # send_reply_msg(message_id, "Processing >>>>",chat_id)
                        send_Video_directly(dwnl,filename,filename,chat_id,message_id)
                      else:
                        send_reply_msg(message_id, "Failed to Download",chat_id)
                        send_reply_msg(message_id, "Download Link : "+ dwnl,chat_id)


                # print(f"chat_id {chat_id} : message_id :{message_id} \nmessages : {text} ")
                if message and "caption" in message:
                    caption = message["caption"]
                    text = message.get("text")
                    pprint(text)
                    flag = check_url(caption)
                    flag2 = check_url(str(text))
                    pprint(flag2)
                    if flag:
                        # send_reply_msg(message_id, "Please Wait >>>>",chat_id)

                        print(flag)
                        data = get_info(flag,'')
                        pprint(data)
                        filename = data.get("fileName")
                        dwnl = data.get("download_link")
                        status = data.get("status")
                        # print(type(status))
                        if status:
                          send_reply_msg(message_id, "Processing >>>>",chat_id)

                          send_Video_directly(dwnl,filename,filename,chat_id,message_id)
                        else:
                          send_reply_msg(message_id, "Failed to Download",chat_id)
                          send_reply_msg(message_id, "Download Link : "+ dwnl,chat_id)

                    elif flag2:
                        print(flag)
                        data = get_info(flag,'')
                        pprint(data)
                        filename = data.get("fileName")
                        dwnl = data.get("download_link")
                        status = data.get("status")
                        send_reply_msg(message_id, "Download Link : "+ dwnl,chat_id)

                        # print(type(status))
                        if status:
                          send_reply_msg(message_id, "Processing >>>>",chat_id)

                          send_Video_directly(dwnl,filename,filename,chat_id,message_id)
                        else:
                          send_reply_msg(message_id, "Failed to Download",chat_id)
                          send_reply_msg(message_id, "Download Link : "+ dwnl,chat_id)

                    else:
                        send_reply_msg(message_id, "Not Supported",chat_id)
                      # sendV(dl, str(message_id )+ "_"+str(chat_id)+".mp4",str(chat_id),chat_id,message_id)
                      # else:
                      #   send_reply_msg(message_id,"Failed to Download. Status code:",chat_id)


        else:
            print(f"{text} new messages.")
    else:
        send_reply_msg(message_id,"Failed to fetch updates. Status code:" +str(response.status_code),chat_id)
        print("Failed to fetch updates. Status code:", response.status_code)

    # Sleep for a few seconds before checking again (to avoid excessive API requests)
    time.sleep(3)  # You can adjust the interval as needed