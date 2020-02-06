from pyfcm import FCMNotification

push_service = FCMNotification(api_key="AAAATh5i6ic:APA91bH3X0mufDL5lxZD8YlkiJuG3HMWGJrSrr1AqU8gNHVWXvxMeh19TBP2qcP49O_cZiSP2ew1g81c2-Ahhi2ZI6-YJPNqX8PEFio2pCeoCuYbTZ8OUm4bch90TMwY5tvSDMT4Sx6W")

registration_id = "cE3Jq4tvxU8:APA91bF4PXjhmHnkKeH6NS1nKJrjSp-WAWQQQlF9Qld6IIPAoOXKuNXAyoV2OpacE5RixkRifDKOkmS98bDCzG90QUNuzopTt7kX-SiidfZiMhJRtxqUoo615P-ChuctpFbfWf2koZd9"
message_title = "pruebaa"
message_body = "asdasds"
#result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title, message_body=message_body)

result = push_service.notify_topic_subscribers(topic_name="quipu", message_title=message_title, message_body=message_body)

print(result)