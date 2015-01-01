#!/usr/bin/python3

import sys
import requests
from math import pow
from math import sqrt

def hae(tuloksia, *hakusanat, apikey):
    videot = set()
    tulokset = []
    subscribet = {}
    hakukone = requests.Session()

    # Video-ID-haun parametrit
    parametrit = {
        'part': 'id',
        'key': apikey,
        'q': ' '.join(hakusanat),
        #'order': 'date',
        #'order': 'viewCount',
        'order': 'relevance',
        'type': 'video',
        'maxResults': '50',
        'regionCode': 'FI',
        'videoDefinition': 'high',
        'videoEmbeddable': 'true',
        'videoSyndicated': 'true',
    }
    # Hae video-iideet
    while True:
        print('Request: search')
        asd = hakukone.get('https://www.googleapis.com/youtube/v3/search', params=parametrit)
        #print(asd.url)
    
        if int(asd.json()['pageInfo']['totalResults']) == 0:
            print('Virhe: Ei tuloksia :((((')
            return []
        
        for video in asd.json()['items']:
            videot.add(video["id"]["videoId"])
            if len(videot) == tuloksia:
                break
    
        if len(videot) == tuloksia or 'nextPageToken' not in asd.json():
            break
    
        parametrit['pageToken'] = asd.json()['nextPageToken']
    
    # Hae video-statsit
    for chunkki in range(int((len(videot)-1)/50)+1):
        oikeatparamit = {
            'id' : ','.join(list(videot)[chunkki*50:(chunkki+1)*50]),
            'part' : 'id,snippet,statistics',
            'key' : apikey,
        }

        print('Request: videos')
        #print(oikeatparamit)
        oikeatvideot = hakukone.get('https://www.googleapis.com/youtube/v3/videos', params=oikeatparamit)
        #print(oikeatvideot.url)

        for video in oikeatvideot.json()['items']:
            tulokset.append((
                video['id'],
                video['snippet']['title'],
                int(video['statistics']['viewCount']),
                int(video['statistics']['likeCount']),
                int(video['statistics']['dislikeCount']),
                video['snippet']['thumbnails']['medium']['url'],
                video['snippet']['channelId'])
            )
            subscribet[video['snippet']['channelId']] = 10000000000


    for chunkki in range(int(len(list(subscribet.keys()))/50)+1):
        channelparamit = {
            'id' : ','.join(list(subscribet.keys())[chunkki*50:(chunkki+1)*50]),
            'part' : 'id,statistics',
            'key' : apikey,
        }
        
        print('Request: channel')
        #print(channelparamit)
        channelreq = hakukone.get('https://www.googleapis.com/youtube/v3/channels', params=channelparamit)
        #print(channelreq.url)
        for channeli in channelreq.json()['items']:
            if channeli['statistics']['hiddenSubscriberCount'] == 0:
                subscribet[channeli['id']] = int(channeli['statistics']['subscriberCount'])
                
    #likes = 0
    #dislikes = 0
    #for tulos in tulokset:
    #    likes += tulos[3]
    #    dislikes += tulos[4]
    #bias = float(likes)/(dislikes)

    tulokset.sort(key=lambda i: i[3]/pow((i[3]+i[4])*i[2]*subscribet[i[6]], 0.25) if i[2] * i[3] * subscribet[i[6]] > 0 else 0)
    tulokset.reverse()
    return tulokset
