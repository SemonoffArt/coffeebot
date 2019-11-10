import requests
import json

def getInfoByPhoto(endpoint_url, subscription_key, imagepath):
    # set to your own subscription key value
    assert subscription_key

    # replace <My Endpoint String> with the string from your endpoint URL
    face_api_url = endpoint_url + 'detect'

    headers = {'Ocp-Apim-Subscription-Key': subscription_key, 'Content-Type': 'application/octet-stream'}

    params = {
        'returnFaceId': 'true',
        'returnFaceLandmarks': 'false',
        'returnFaceAttributes': 'age,gender,headPose,smile,facialHair,glasses,emotion,hair,makeup,occlusion,accessories,blur,exposure,noise',
    }

    #response = requests.post(face_api_url, params=params,
    #                         headers=headers, json={"url": image_url})

    data = open(imagepath, 'rb').read()
    response = requests.post(url=face_api_url,
                        data=data,
                        params=params,
                        headers=headers)
    output = {"faceId": response.json()[0]['faceId']}

    #print(json.dumps(response.json()))
#    if response.json()[0]['faceAttributes']['gender'] == "male":
#        output.update({'gender' : "Ты мужчина"})
#    else:
#        output.update({'gender' : "Ты женщина"})

#    output.update({'age' : "Тебе " + str(int(response.json()[0]['faceAttributes']['age']))})

    A = response.json()[0]['faceAttributes']['emotion']
    dominateEmotion = ["neutral", 0.0]
    emotions = {"anger": "злое настроение",
    "contempt": "чувство презрения",
    "disgust": "чувство отвращенния",
    "fear": "чувство страха",
    "happiness": "хорошее настроение",
    "neutral": "нейтральное настроение",
    "sadness": "плохое настроение",
    "surprise": "удивленное настроение"
    }

    for key in A:
        if A[key] > dominateEmotion[1]:
            dominateEmotion = [key, A[key]]

    #output.update({'dominateEmotion' : "У тебя " + emotions[dominateEmotion[0]]})

    if dominateEmotion[0] == "anger":
        if response.json()[0]['faceAttributes']['gender'] == "male":
            output.update({'text' : "Чтобы успокоить нервы, специалисты рекомендуют Зелёный чай!"})
        else:
            output.update({'text' : "Чтобы успокоить нервы, специалисты рекомендуют Зелёный чай!"})
    elif dominateEmotion[0] == "contempt":
        if response.json()[0]['faceAttributes']['gender'] == "male":
            output.update({'text' : "С таким выражением лица выпей-ка вот это - Американо!"})
        else:
            output.update({'text' : "С таким выражением лица выпей-ка вот это - Эспрессо!"})
    elif dominateEmotion[0] == "disgust":
        if response.json()[0]['faceAttributes']['gender'] == "male":
            output.update({'text' : "Что это за кислое выражение лица, сейчас исправь его вот этим Капучино!"})
        else:
            output.update({'text' : "Что это за кислое выражение лица, сейчас исправь его вот этим Раф кофе!"})
    elif dominateEmotion[0] == "fear":
        if response.json()[0]['faceAttributes']['gender'] == "male":
            output.update({'text' : "Не бойся, просто выпей Эспрессо!"})
        else:
            output.update({'text' : "Не бойся, просто выпей Американо!"})
    elif dominateEmotion[0] == "happiness":
        if response.json()[0]['faceAttributes']['gender'] == "male":
            output.update({'text' : "Всё и так хорошо, но может быть лучше с Латте!"})
        else:
            output.update({'text' : "Всё и так хорошо, но может быть лучше с Латте!"})
    elif dominateEmotion[0] == "neutral":
        if response.json()[0]['faceAttributes']['gender'] == "male":
            output.update({'text' : "Всё понял, тебе нужно Капучино!"})
        else:
            output.update({'text' : "Всё понял, тебе Капучино!"})
    elif dominateEmotion[0] == "sadness":
        if response.json()[0]['faceAttributes']['gender'] == "male":
            output.update({'text' : "Не грусти, лучше выпей Горячий Шоколад!"})
        else:
            output.update({'text' : "Не грусти, лучше выпей Горячий Шоколад!"})
    elif dominateEmotion[0] == "surprise":
        if response.json()[0]['faceAttributes']['gender'] == "male":
            output.update({"text":"Ты такой удивленный! Возможно тебя удивит и кружка Мокко!"})
        else:
            output.update({"text":"Ты такая удивленная! Возможно тебя удивит и кружка Мокко!"})

    return output


def useFaceApiFindSimilar(urlService,keyService,faceId,faceIds):
	headers = {"Ocp-Apim-Subscription-Key": keyService, "Content-Type": "application/json"}

	postData = {"faceId": faceId,
				"faceids":faceIds,
				"mode": "matchFace"}

	responce = requests.post(urlService,headers=headers,data=json.dumps(postData))
	result = json.loads(responce.text)

	bestCandidate = None

	for index,value in enumerate(result):
		i = value['confidence']
		if i > result[index-1]['confidence']:
			bestCandidate = value

	return bestCandidate
