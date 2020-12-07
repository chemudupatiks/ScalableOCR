#!/bin/sh
#
# Sample queries using Curl rather than rest-client.py
#

#
# Use localhost & port 5000 if not specified by environment variable REST
#
REST=${REST:-"localhost:80"}

curl -d '{"url":"https://storage.googleapis.com/cu-csci-5253/lfw/Larry_Brown/Larry_Brown_0001.jpg"}' -H "Content-Type: application/json" -X POST http://$REST/scan/url
curl -d '{"url":"https://storage.googleapis.com/cu-csci-5253/lfw/Larry_Brown/Larry_Brown_0002.jpg"}' -H "Content-Type: application/json" -X POST http://$REST/scan/url
curl -d '{"url":"https://storage.googleapis.com/cu-csci-5253/lfw/Larry_Brown/Larry_Brown_0003.jpg"}' -H "Content-Type: application/json" -X POST http://$REST/scan/url
curl -d '{"url":"https://storage.googleapis.com/cu-csci-5253/lfw/Larry_Brown/Larry_Brown_0004.jpg"}' -H "Content-Type: application/json" -X POST http://$REST/scan/url
curl -d '{"url":"https://storage.googleapis.com/cu-csci-5253/lfw/Larry_Brown/Larry_Brown_0005.jpg"}' -H "Content-Type: application/json" -X POST http://$REST/scan/url
curl -d '{"url":"https://storage.googleapis.com/cu-csci-5253/lfw/Larry_Brown/Larry_Brown_0006.jpg"}' -H "Content-Type: application/json" -X POST http://$REST/scan/url
curl -d '{"url":"https://storage.googleapis.com/cu-csci-5253/lfw/Larry_Brown/Larry_Brown_0007.jpg"}' -H "Content-Type: application/json" -X POST http://$REST/scan/url

curl http://$REST/match/26bcfb91067c8245b6756b0df30b3017ca134d6aa46349fc7df242a5906973de

# curl -d '{"url":"https://storage.googleapis.com/cu-csci-5253/lfw/Zico/Zico_0003.jpg"}' -H "Content-Type: application/json" -X POST http://$REST/scan/url
# #
# # This should match the one above
# curl http://$REST/match/993bea5dfb14412a876f0205d73358be4f092de28b3e88bf69eeb1e0fc299f43
# # And this shouldn't
# curl http://$REST/match/fb82e0120bbf3a26b38f6d939cb510f3ead0aa98b0afdfc972ea277e
# # 
# #
# # Throw in some random samples..
# #
# for url in $(shuf -n 10 ../all-image-urls.txt)
# do
#     curl -d "{\"url\":\"$url\"}" -H "Content-Type: application/json" -X POST http://$REST/scan/url
# done